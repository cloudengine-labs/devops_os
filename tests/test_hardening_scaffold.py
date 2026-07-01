"""
Unit tests for the DevOps-OS Hardening Scaffold Generator.

Tests cover:
  - Individual standard generators (CIS K8s, STIG, NSA, Pod Security, Image Signing,
    Docker CIS, RHEL9 CIS, Ubuntu22 CIS, Essential Eight)
  - Compliance mapping generation
  - Top-level dispatcher (generate_hardening)
  - Environment enforcement action logic
  - Standard/type filtering logic
"""

import argparse
import os
import sys
import tempfile
import yaml
import pytest
from pathlib import Path

# Ensure repo root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli import scaffold_hardening


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hardening_args(**kwargs):
    defaults = dict(
        standard="all",
        output_type="all",
        output=os.path.join(tempfile.gettempdir(), "test-hardening"),
        compliance_framework="",
        severity="medium",
        environment="production",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Enforcement action helper
# ---------------------------------------------------------------------------

class TestEnforcementAction:
    def test_production_returns_enforce(self):
        assert scaffold_hardening._enforcement_action("production") == "Enforce"

    def test_staging_returns_audit(self):
        assert scaffold_hardening._enforcement_action("staging") == "Audit"

    def test_dev_returns_audit(self):
        assert scaffold_hardening._enforcement_action("dev") == "Audit"


# ---------------------------------------------------------------------------
# Should-generate filter
# ---------------------------------------------------------------------------

class TestShouldGenerate:
    def test_all_type_accepts_kyverno_standard(self):
        assert scaffold_hardening._should_generate("cis-k8s", "all") is True

    def test_all_type_accepts_inspec_standard(self):
        assert scaffold_hardening._should_generate("cis-rhel9", "all") is True

    def test_kyverno_type_accepts_kyverno_standard(self):
        assert scaffold_hardening._should_generate("cis-k8s", "kyverno") is True

    def test_kyverno_type_rejects_inspec_standard(self):
        assert scaffold_hardening._should_generate("cis-rhel9", "kyverno") is False

    def test_inspec_type_accepts_inspec_standard(self):
        assert scaffold_hardening._should_generate("cis-docker", "inspec") is True

    def test_inspec_type_rejects_kyverno_standard(self):
        assert scaffold_hardening._should_generate("stig-k8s", "inspec") is False

    def test_checkov_type_accepts_essential_eight(self):
        assert scaffold_hardening._should_generate("essential-eight", "checkov") is True

    def test_checkov_type_rejects_kyverno_standard(self):
        assert scaffold_hardening._should_generate("pod-security", "checkov") is False


# ---------------------------------------------------------------------------
# CIS Kubernetes generators
# ---------------------------------------------------------------------------

class TestKyvernoCisK8s:
    def test_generates_five_policy_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="production")
        paths = scaffold_hardening.generate_kyverno_cis_k8s(args)
        assert len(paths) == 5

    def test_output_files_exist(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="production")
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        cis_dir = tmp_path / "kyverno" / "cis-k8s"
        for fname in [
            "1-master-node-config.yaml",
            "2-etcd-config.yaml",
            "3-control-plane-config.yaml",
            "4-worker-node-config.yaml",
            "5-policies.yaml",
        ]:
            assert (cis_dir / fname).exists(), f"Expected {fname} to be generated"

    def test_policy_kind_is_cluster_policy(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "cis-k8s" / "4-worker-node-config.yaml")
        assert policy["kind"] == "ClusterPolicy"

    def test_production_enforcement_is_enforce(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="production")
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "cis-k8s" / "1-master-node-config.yaml")
        assert policy["spec"]["validationFailureAction"] == "Enforce"

    def test_dev_enforcement_is_audit(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="dev")
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "cis-k8s" / "1-master-node-config.yaml")
        assert policy["spec"]["validationFailureAction"] == "Audit"

    def test_policy_has_compliance_annotation(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "cis-k8s" / "4-worker-node-config.yaml")
        annotations = policy["metadata"]["annotations"]
        assert "devops-os/compliance" in annotations
        assert "cis-k8s" in annotations["devops-os/compliance"]

    def test_policy_has_category_annotation(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_cis_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "cis-k8s" / "5-policies.yaml")
        assert "CIS Kubernetes Benchmark" in policy["metadata"]["annotations"]["policies.kyverno.io/category"]


# ---------------------------------------------------------------------------
# DISA STIG generators
# ---------------------------------------------------------------------------

class TestKyvernoStigK8s:
    def test_generates_one_file(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_kyverno_stig_k8s(args)
        assert len(paths) == 1

    def test_output_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_stig_k8s(args)
        assert (tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml").exists()

    def test_stig_policy_has_three_rules(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_stig_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml")
        assert len(policy["spec"]["rules"]) == 3

    def test_stig_disallow_latest_tag_rule_present(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_stig_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml")
        rule_names = [r["name"] for r in policy["spec"]["rules"]]
        assert "stig-disallow-latest-image-tag" in rule_names


# ---------------------------------------------------------------------------
# NSA generators
# ---------------------------------------------------------------------------

class TestKyvernoNsaK8s:
    def test_generates_two_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_kyverno_nsa_k8s(args)
        assert len(paths) == 2

    def test_pod_security_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_nsa_k8s(args)
        assert (tmp_path / "kyverno" / "nsa-k8s" / "pod-security.yaml").exists()

    def test_network_policies_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_nsa_k8s(args)
        assert (tmp_path / "kyverno" / "nsa-k8s" / "network-policies.yaml").exists()

    def test_nsa_pod_policy_name(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_nsa_k8s(args)
        policy = _load_yaml(tmp_path / "kyverno" / "nsa-k8s" / "pod-security.yaml")
        assert policy["metadata"]["name"] == "nsa-pod-security"


# ---------------------------------------------------------------------------
# Pod Security Standards generator
# ---------------------------------------------------------------------------

class TestKyvernoPodSecurity:
    def test_generates_one_file(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_kyverno_pod_security(args)
        assert len(paths) == 1

    def test_output_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_pod_security(args)
        assert (tmp_path / "kyverno" / "pod-security-standards.yaml").exists()

    def test_production_uses_restricted_profile(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="production")
        scaffold_hardening.generate_kyverno_pod_security(args)
        policy = _load_yaml(tmp_path / "kyverno" / "pod-security-standards.yaml")
        assert "restricted" in policy["metadata"]["annotations"]["policies.kyverno.io/title"].lower()

    def test_dev_uses_baseline_profile(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), environment="dev")
        scaffold_hardening.generate_kyverno_pod_security(args)
        policy = _load_yaml(tmp_path / "kyverno" / "pod-security-standards.yaml")
        assert "baseline" in policy["metadata"]["annotations"]["policies.kyverno.io/title"].lower()


# ---------------------------------------------------------------------------
# Image signing generator
# ---------------------------------------------------------------------------

class TestKyvernoImageSigning:
    def test_generates_one_file(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_kyverno_image_signing(args)
        assert len(paths) == 1

    def test_output_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_image_signing(args)
        assert (tmp_path / "kyverno" / "image-signing.yaml").exists()

    def test_policy_has_verify_images_rule(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_kyverno_image_signing(args)
        policy = _load_yaml(tmp_path / "kyverno" / "image-signing.yaml")
        rules = policy["spec"]["rules"]
        assert any("verifyImages" in r for r in rules)


# ---------------------------------------------------------------------------
# InSpec Docker CIS
# ---------------------------------------------------------------------------

class TestInspecDockerCis:
    def test_generates_six_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_inspec_docker_cis(args)
        assert len(paths) == 6  # inspec.yml + 5 controls

    def test_inspec_yml_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_docker_cis(args)
        assert (tmp_path / "inspec" / "docker-cis" / "inspec.yml").exists()

    def test_inspec_yml_has_correct_name(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_docker_cis(args)
        content = (tmp_path / "inspec" / "docker-cis" / "inspec.yml").read_text()
        assert "name: docker-cis" in content

    def test_all_control_files_exist(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_docker_cis(args)
        controls_dir = tmp_path / "inspec" / "docker-cis" / "controls"
        for fname in [
            "1_host_configuration.rb",
            "2_docker_daemon.rb",
            "3_docker_daemon_files.rb",
            "4_container_images.rb",
            "5_container_runtime.rb",
        ]:
            assert (controls_dir / fname).exists()

    def test_control_file_has_inspec_controls(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_docker_cis(args)
        content = (tmp_path / "inspec" / "docker-cis" / "controls" / "1_host_configuration.rb").read_text()
        assert "control" in content
        assert "cis-docker-1" in content


# ---------------------------------------------------------------------------
# InSpec RHEL9 CIS
# ---------------------------------------------------------------------------

class TestInspecRhel9Cis:
    def test_generates_six_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_inspec_rhel9_cis(args)
        assert len(paths) == 6

    def test_inspec_yml_has_correct_name(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_rhel9_cis(args)
        content = (tmp_path / "inspec" / "rhel9-cis" / "inspec.yml").read_text()
        assert "name: rhel9-cis" in content

    def test_logging_control_has_auditd_check(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_rhel9_cis(args)
        content = (tmp_path / "inspec" / "rhel9-cis" / "controls" / "4_logging.rb").read_text()
        assert "auditd" in content

    def test_network_control_has_ip_forward_check(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_rhel9_cis(args)
        content = (tmp_path / "inspec" / "rhel9-cis" / "controls" / "3_network.rb").read_text()
        assert "net.ipv4.ip_forward" in content


# ---------------------------------------------------------------------------
# InSpec Ubuntu 22 CIS
# ---------------------------------------------------------------------------

class TestInspecUbuntu22Cis:
    def test_generates_six_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_inspec_ubuntu22_cis(args)
        assert len(paths) == 6

    def test_inspec_yml_has_correct_name(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_ubuntu22_cis(args)
        content = (tmp_path / "inspec" / "ubuntu22-cis" / "inspec.yml").read_text()
        assert "name: ubuntu22-cis" in content

    def test_all_control_files_exist(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_inspec_ubuntu22_cis(args)
        controls_dir = tmp_path / "inspec" / "ubuntu22-cis" / "controls"
        for fname in ["1_filesystem.rb", "2_services.rb", "3_network.rb", "4_logging.rb", "5_access.rb"]:
            assert (controls_dir / fname).exists()


# ---------------------------------------------------------------------------
# Essential Eight
# ---------------------------------------------------------------------------

class TestEssentialEight:
    def test_generates_two_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_essential_eight(args)
        assert len(paths) == 2

    def test_readme_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_essential_eight(args)
        assert (tmp_path / "essential-eight" / "README.md").exists()

    def test_readme_has_maturity_levels(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_essential_eight(args)
        content = (tmp_path / "essential-eight" / "README.md").read_text()
        assert "Maturity" in content

    def test_checkov_checks_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_essential_eight(args)
        assert (tmp_path / "essential-eight" / "checkov" / "essential-eight-checks.py").exists()

    def test_checkov_checks_has_e8_classes(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_essential_eight(args)
        content = (tmp_path / "essential-eight" / "checkov" / "essential-eight-checks.py").read_text()
        assert "E8RestrictAdminPrivileges" in content
        assert "E8MultiFactorAuthentication" in content
        assert "E8RegularBackups" in content


# ---------------------------------------------------------------------------
# Compliance mapping
# ---------------------------------------------------------------------------

class TestComplianceMapping:
    def test_generates_one_file(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        paths = scaffold_hardening.generate_compliance_mapping(args)
        assert len(paths) == 1

    def test_output_file_exists(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_compliance_mapping(args)
        assert (tmp_path / "compliance-mapping.yaml").exists()

    def test_mapping_is_valid_yaml(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_compliance_mapping(args)
        mapping = _load_yaml(tmp_path / "compliance-mapping.yaml")
        assert mapping is not None
        assert "mappings" in mapping

    def test_mapping_covers_all_standards(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_compliance_mapping(args)
        mapping = _load_yaml(tmp_path / "compliance-mapping.yaml")
        for standard in ["cis-k8s", "stig-k8s", "nsa-k8s", "cis-docker",
                          "cis-rhel9", "cis-ubuntu22", "essential-eight"]:
            assert standard in mapping["mappings"], f"Standard {standard} missing from compliance mapping"

    def test_mapping_entries_have_title(self, tmp_path):
        args = _hardening_args(output=str(tmp_path))
        scaffold_hardening.generate_compliance_mapping(args)
        mapping = _load_yaml(tmp_path / "compliance-mapping.yaml")
        for control in mapping["mappings"]["cis-k8s"].values():
            assert "title" in control


# ---------------------------------------------------------------------------
# Top-level dispatcher
# ---------------------------------------------------------------------------

class TestGenerateHardening:
    def test_all_standard_generates_files(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="all", output_type="all")
        paths = scaffold_hardening.generate_hardening(args)
        assert len(paths) > 0

    def test_single_standard_generates_only_that_standard(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="stig-k8s", output_type="all")
        scaffold_hardening.generate_hardening(args)
        assert (tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml").exists()
        assert not (tmp_path / "kyverno" / "cis-k8s").exists()

    def test_kyverno_type_filter_skips_inspec(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="all", output_type="kyverno")
        scaffold_hardening.generate_hardening(args)
        assert not (tmp_path / "inspec").exists()

    def test_inspec_type_filter_skips_kyverno(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="all", output_type="inspec")
        scaffold_hardening.generate_hardening(args)
        assert not (tmp_path / "kyverno").exists()

    def test_all_standards_creates_compliance_mapping(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="all", output_type="all")
        scaffold_hardening.generate_hardening(args)
        assert (tmp_path / "compliance-mapping.yaml").exists()

    def test_empty_result_for_mismatched_standard_and_type(self, tmp_path):
        # cis-rhel9 is InSpec only, but we request kyverno type
        args = _hardening_args(output=str(tmp_path), standard="cis-rhel9", output_type="kyverno")
        paths = scaffold_hardening.generate_hardening(args)
        # Only compliance mapping should be generated (no standard-specific files)
        kyverno_dir = tmp_path / "kyverno"
        inspec_dir = tmp_path / "inspec"
        assert not kyverno_dir.exists()
        assert not inspec_dir.exists()

    def test_production_environment_enforces_kyverno_policies(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="stig-k8s",
                               output_type="kyverno", environment="production")
        scaffold_hardening.generate_hardening(args)
        policy = _load_yaml(tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml")
        assert policy["spec"]["validationFailureAction"] == "Enforce"

    def test_staging_environment_audits_kyverno_policies(self, tmp_path):
        args = _hardening_args(output=str(tmp_path), standard="stig-k8s",
                               output_type="kyverno", environment="staging")
        scaffold_hardening.generate_hardening(args)
        policy = _load_yaml(tmp_path / "kyverno" / "stig-k8s" / "stig-cluster-policies.yaml")
        assert policy["spec"]["validationFailureAction"] == "Audit"
