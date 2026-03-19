"""
Comprehensive DevOps-OS test suite.

Covers CLI scaffold tools (gha, jenkins, gitlab, argocd, sre),
MCP server tools, skills definitions, and edge/boundary cases.
Bugs discovered are annotated with BUG-<N> markers.
"""

import json
import sys
import os
import argparse
import tempfile
import pytest
import yaml
from pathlib import Path

# Ensure repo root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli import (
    scaffold_gha,
    scaffold_jenkins,
    scaffold_gitlab,
    scaffold_argocd,
    scaffold_sre,
    scaffold_unittest,
)
from mcp_server.server import (
    generate_github_actions_workflow,
    generate_gitlab_ci_pipeline,
    generate_jenkins_pipeline,
    generate_k8s_config,
    generate_argocd_config,
    generate_sre_configs,
    scaffold_devcontainer,
    generate_unittest_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(args):
    import subprocess
    return subprocess.run(
        [sys.executable] + args,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )


def _run_module(module, extra_args=None):
    return _run(["-m", module] + (extra_args or []))


def _gha_args(**kwargs):
    defaults = dict(
        name="test-app",
        type="complete",
        languages="python",
        kubernetes=False,
        k8s_method="kubectl",
        branches="main",
        matrix=False,
        reusable=False,
        output="/tmp/test-gha",
        image="ghcr.io/yourorg/devops-os:latest",
        registry="ghcr.io",
        custom_values=None,
        env_file=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _jenkins_args(**kwargs):
    defaults = dict(
        name="test-app",
        type="complete",
        languages="python",
        kubernetes=False,
        k8s_method="kubectl",
        output="/tmp/Jenkinsfile",
        parameters=False,
        image="docker.io/yourorg/devops-os:latest",
        scm="git",
        registry="docker.io",
        custom_values=None,
        env_file=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _sre_args(**kwargs):
    defaults = dict(
        name="my-svc",
        team="platform",
        namespace="default",
        slo_type="all",
        slo_target=99.9,
        latency_threshold=0.5,
        slack_channel="#alerts",
        pagerduty_key="",
        output_dir="/tmp/sre",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _argocd_args(**kwargs):
    defaults = dict(
        name="my-app",
        method="argocd",
        repo="https://github.com/myorg/my-app.git",
        revision="HEAD",
        path="k8s",
        namespace="default",
        project="default",
        server="https://kubernetes.default.svc",
        auto_sync=False,
        rollouts=False,
        image="ghcr.io/myorg/my-app",
        output_dir="/tmp/argocd",
        allow_any_source_repo=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ===========================================================================
# CLI: scaffold_gha (GitHub Actions)
# ===========================================================================

class TestScaffoldGHA:
    """Tests for the GitHub Actions workflow generator."""

    def test_build_workflow_has_build_job(self):
        args = _gha_args(type="build")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "build" in wf.get("jobs", {})
        assert wf["name"].endswith("Build")

    def test_test_workflow_has_test_job(self):
        args = _gha_args(type="test", languages="python,java")
        configs = {
            "languages": scaffold_gha.generate_language_config("python,java", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "test" in wf.get("jobs", {})

    def test_complete_workflow_has_build_test_deploy_jobs(self):
        args = _gha_args(type="complete")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "build" in wf["jobs"]
        assert "test" in wf["jobs"]
        assert "deploy" in wf["jobs"]

    def test_deploy_workflow_has_deploy_job(self):
        args = _gha_args(type="deploy", kubernetes=True, k8s_method="kubectl")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(True, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "deploy" in wf["jobs"]

    def test_reusable_workflow_uses_workflow_call_trigger(self):
        args = _gha_args(type="reusable", reusable=True)
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "workflow_call" in wf["on"]

    def test_matrix_build_adds_strategy(self):
        args = _gha_args(type="build", matrix=True)
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        assert "strategy" in wf["jobs"]["build"]
        assert "matrix" in wf["jobs"]["build"]["strategy"]

    def test_multiple_branches_trigger(self):
        args = _gha_args(type="build", branches="main,develop,release")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        push_branches = wf["on"]["push"]["branches"]
        assert "main" in push_branches
        assert "develop" in push_branches
        assert "release" in push_branches

    def test_kubernetes_kustomize_deploy_step(self):
        args = _gha_args(type="complete", kubernetes=True, k8s_method="kustomize")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(True, "kustomize", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        deploy_steps = wf["jobs"]["deploy"]["steps"]
        step_names = [s["name"] for s in deploy_steps]
        assert any("kustomize" in n.lower() for n in step_names)

    def test_kubernetes_argocd_deploy_step(self):
        args = _gha_args(type="complete", kubernetes=True, k8s_method="argocd")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(True, "argocd", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        deploy_steps = wf["jobs"]["deploy"]["steps"]
        step_names = [s["name"] for s in deploy_steps]
        assert any("argocd" in n.lower() for n in step_names)

    def test_kubernetes_flux_deploy_step(self):
        args = _gha_args(type="complete", kubernetes=True, k8s_method="flux")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(True, "flux", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        deploy_steps = wf["jobs"]["deploy"]["steps"]
        step_names = [s["name"] for s in deploy_steps]
        assert any("flux" in n.lower() for n in step_names)

    def test_multi_language_build_steps_python_go(self):
        args = _gha_args(type="build", languages="python,go")
        configs = {
            "languages": scaffold_gha.generate_language_config("python,go", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        step_names = [s["name"] for s in wf["jobs"]["build"]["steps"]]
        python_steps = [n for n in step_names if "python" in n.lower()]
        go_steps = [n for n in step_names if "go" in n.lower()]
        assert python_steps, "Expected Python build steps"
        assert go_steps, "Expected Go build steps"

    def test_cli_gha_scaffold_via_module(self):
        """Test CLI invocation of scaffold gha via module."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_gha",
                ["--name", "cli-test", "--type", "build", "--output", tmp],
            )
            assert result.returncode == 0
            files = list(Path(tmp).glob("*.yml"))
            assert len(files) >= 1

    def test_language_config_correctly_maps_languages(self):
        cfg = scaffold_gha.generate_language_config("python,java,go", {})
        assert cfg["python"] is True
        assert cfg["java"] is True
        assert cfg["go"] is True
        assert cfg["javascript"] is False

    def test_kubernetes_config_no_k8s(self):
        cfg = scaffold_gha.generate_kubernetes_config(False, "kubectl", {})
        assert cfg["k9s"] is False
        assert cfg["kustomize"] is False

    def test_kubernetes_config_argocd_method(self):
        cfg = scaffold_gha.generate_kubernetes_config(True, "argocd", {})
        assert cfg["argocd_cli"] is True
        assert cfg["kustomize"] is False
        assert cfg["flux"] is False

    def test_yaml_output_has_no_anchors_or_aliases(self):
        """Verify that the serialised YAML does not contain anchor/alias syntax.

        When the same ``branches`` list is shared between the ``push`` and
        ``pull_request`` trigger blocks PyYAML would normally emit YAML anchors
        (``&id001``) and aliases (``*id001``).  GitHub Actions does not support
        this syntax and it is confusing to users, so the generator must
        suppress it.
        """
        args = _gha_args(type="build", branches="main")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        yaml_str = yaml.dump(wf, sort_keys=False, Dumper=scaffold_gha._NoAliasDumper)
        assert "&id" not in yaml_str, "YAML output must not contain anchors (&id...)"
        assert "*id" not in yaml_str, "YAML output must not contain aliases (*id...)"
        # Also verify both push and pull_request branches are present
        parsed = yaml.safe_load(yaml_str)
        assert parsed["on"]["push"]["branches"] == ["main"]
        assert parsed["on"]["pull_request"]["branches"] == ["main"]

    def test_yaml_output_no_anchors_multiple_branches(self):
        """Same anchor/alias check with multiple branches."""
        args = _gha_args(type="complete", branches="main,develop,release")
        configs = {
            "languages": scaffold_gha.generate_language_config("python", {}),
            "kubernetes": scaffold_gha.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_gha.generate_cicd_config({}),
            "build_tools": scaffold_gha.generate_build_tools_config({}),
            "code_analysis": scaffold_gha.generate_code_analysis_config({}),
            "devops_tools": scaffold_gha.generate_devops_tools_config({}),
        }
        wf = scaffold_gha.generate_workflow(args, {}, configs)
        yaml_str = yaml.dump(wf, sort_keys=False, Dumper=scaffold_gha._NoAliasDumper)
        assert "&id" not in yaml_str, "YAML output must not contain anchors (&id...)"
        assert "*id" not in yaml_str, "YAML output must not contain aliases (*id...)"


# ===========================================================================
# CLI: scaffold_jenkins
# ===========================================================================

class TestScaffoldJenkins:
    """Tests for the Jenkins pipeline generator."""

    def test_basic_pipeline_contains_pipeline_keyword(self):
        args = _jenkins_args()
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "pipeline {" in content

    def test_build_pipeline_contains_build_stage(self):
        args = _jenkins_args(type="build")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "Build" in content

    def test_test_pipeline_contains_test_stage(self):
        args = _jenkins_args(type="test")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "Test" in content

    def test_deploy_pipeline_contains_deploy_stage(self):
        args = _jenkins_args(type="deploy", kubernetes=True, k8s_method="kubectl")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(True, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "Deploy" in content

    def test_parameterized_pipeline_adds_parameters_block(self):
        args = _jenkins_args(type="parameterized", parameters=True)
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "parameters" in content

    def test_complete_pipeline_has_all_stages(self):
        args = _jenkins_args(type="complete", kubernetes=True, k8s_method="kubectl")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python,java", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(True, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "Build" in content
        assert "Test" in content
        assert "Deploy" in content

    def test_java_build_step_included(self):
        args = _jenkins_args(type="build", languages="java")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("java", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "mvn" in content or "gradle" in content.lower()

    def test_kubernetes_argocd_deploy(self):
        args = _jenkins_args(type="deploy", kubernetes=True, k8s_method="argocd")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(True, "argocd", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "argocd" in content.lower()

    def test_kubernetes_flux_deploy(self):
        args = _jenkins_args(type="deploy", kubernetes=True, k8s_method="flux")
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(True, "flux", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "flux" in content.lower()

    def test_post_block_always_cleanup(self):
        args = _jenkins_args()
        configs = {
            "languages": scaffold_jenkins.generate_language_config("python", {}),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(False, "kubectl", {}),
            "cicd": scaffold_jenkins.generate_cicd_config({}),
            "build_tools": scaffold_jenkins.generate_build_tools_config({}),
        }
        content = scaffold_jenkins.generate_pipeline(args, configs)
        assert "cleanWs()" in content

    def test_cli_jenkins_scaffold_via_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "Jenkinsfile")
            result = _run_module(
                "cli.scaffold_jenkins",
                ["--name", "cli-test", "--type", "build", "--output", out],
            )
            assert result.returncode == 0
            assert os.path.exists(out)
            with open(out) as fh:
                content = fh.read()
            assert "pipeline {" in content


# ===========================================================================
# CLI: scaffold_gitlab (extended)
# ===========================================================================

class TestScaffoldGitlabExtended:
    """Extended tests for the GitLab CI generator."""

    def test_javascript_test_job_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "js-app", "--type", "test",
                 "--languages", "javascript", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "test:javascript" in data

    def test_go_test_job_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "go-app", "--type", "test",
                 "--languages", "go", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "test:go" in data

    def test_deploy_stage_included_for_kubectl(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "my-api", "--type", "deploy",
                 "--kubernetes", "--k8s-method", "kubectl",
                 "--languages", "python", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "deploy" in (data.get("stages") or [])

    def test_deploy_stage_included_for_argocd(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "my-api", "--type", "complete",
                 "--kubernetes", "--k8s-method", "argocd",
                 "--languages", "python", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "deploy" in (data.get("stages") or [])
            assert "deploy:kubernetes" in data
            deploy_script = data["deploy:kubernetes"]["script"]
            assert any("argocd" in s for s in deploy_script)

    def test_deploy_stage_included_for_flux(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "my-api", "--type", "complete",
                 "--kubernetes", "--k8s-method", "flux",
                 "--languages", "python", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "deploy:kubernetes" in data
            deploy_script = data["deploy:kubernetes"]["script"]
            assert any("flux" in s for s in deploy_script)

    def test_multi_language_complete_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "full-stack", "--type", "complete",
                 "--languages", "python,java,javascript,go",
                 "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "test:python" in data
            assert "test:java" in data
            assert "test:javascript" in data
            assert "test:go" in data

    def test_build_job_docker_services(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "svc", "--type", "build",
                 "--languages", "python", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            assert "build" in data
            # Build job uses docker-in-docker services
            assert "services" in data["build"]

    # BUG-1 regression: deploy pipeline with no kubernetes must still have stages
    def test_deploy_pipeline_no_kubernetes_empty_stages(self):
        """
        BUG-1: When type='deploy' and kubernetes=False, the generated
        pipeline has an empty stages list, which is invalid for GitLab CI.
        Expected: at least one stage should be present even for non-k8s deploy,
        and a deploy job stub must be present in the pipeline.
        """
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, ".gitlab-ci.yml")
            result = _run_module(
                "cli.scaffold_gitlab",
                ["--name", "my-app", "--type", "deploy",
                 "--languages", "python", "--output", out],
            )
            assert result.returncode == 0
            with open(out) as fh:
                data = yaml.safe_load(fh)
            stages = data.get("stages") or []
            # Correct expected behavior: there should be at least one stage
            assert len(stages) > 0, (
                "Expected at least one stage in a deploy pipeline, got: {!r}".format(stages)
            )
            # A deploy job stub must be present so the pipeline is valid
            assert "deploy" in data, (
                "Expected a deploy job in the pipeline, got keys: {!r}".format(list(data.keys()))
            )


# ===========================================================================
# CLI: scaffold_argocd (extended)
# ===========================================================================

class TestScaffoldArgoCDExtended:
    """Extended tests for the ArgoCD/Flux config generator."""

    def test_argocd_auto_sync_enabled(self):
        args = _argocd_args(auto_sync=True)
        app = scaffold_argocd.generate_argocd_application(args)
        assert "automated" in app["spec"]["syncPolicy"]

    def test_argocd_auto_sync_disabled(self):
        args = _argocd_args(auto_sync=False)
        app = scaffold_argocd.generate_argocd_application(args)
        assert "automated" not in app["spec"]["syncPolicy"]

    def test_argocd_custom_revision(self):
        args = _argocd_args(revision="v1.2.3")
        app = scaffold_argocd.generate_argocd_application(args)
        assert app["spec"]["source"]["targetRevision"] == "v1.2.3"

    def test_argocd_custom_path(self):
        args = _argocd_args(path="manifests/prod")
        app = scaffold_argocd.generate_argocd_application(args)
        assert app["spec"]["source"]["path"] == "manifests/prod"

    def test_argocd_custom_namespace(self):
        args = _argocd_args(namespace="production")
        app = scaffold_argocd.generate_argocd_application(args)
        assert app["spec"]["destination"]["namespace"] == "production"

    def test_argocd_appproject_least_privilege_by_default(self):
        """Default AppProject should NOT include wildcard source repo."""
        args = _argocd_args(allow_any_source_repo=False)
        proj = scaffold_argocd.generate_argocd_appproject(args)
        assert "*" not in proj["spec"]["sourceRepos"]

    def test_argocd_appproject_allow_any_source_repo(self):
        args = _argocd_args(allow_any_source_repo=True)
        proj = scaffold_argocd.generate_argocd_appproject(args)
        assert "*" in proj["spec"]["sourceRepos"]

    def test_argocd_rollout_has_canary_strategy(self):
        args = _argocd_args(rollouts=True)
        rollout = scaffold_argocd.generate_argo_rollout(args)
        assert "canary" in rollout["spec"]["strategy"]
        steps = rollout["spec"]["strategy"]["canary"]["steps"]
        assert len(steps) > 0

    def test_argocd_rollout_image_is_stable_tag(self):
        args = _argocd_args(rollouts=True, image="ghcr.io/myorg/app")
        rollout = scaffold_argocd.generate_argo_rollout(args)
        container_image = rollout["spec"]["template"]["spec"]["containers"][0]["image"]
        assert "stable" in container_image

    def test_flux_kustomization_structure(self):
        args = _argocd_args(method="flux")
        kust = scaffold_argocd.generate_flux_kustomization(args)
        assert kust["kind"] == "Kustomization"
        assert "interval" in kust["spec"]
        assert "prune" in kust["spec"]

    def test_flux_git_repository_uses_main_for_head(self):
        args = _argocd_args(method="flux", revision="HEAD")
        git_repo = scaffold_argocd.generate_flux_git_repository(args)
        assert git_repo["spec"]["ref"]["branch"] == "main"

    def test_flux_git_repository_uses_custom_revision(self):
        args = _argocd_args(method="flux", revision="release-1.0")
        git_repo = scaffold_argocd.generate_flux_git_repository(args)
        assert git_repo["spec"]["ref"]["branch"] == "release-1.0"

    def test_flux_image_automation_returns_three_resources(self):
        args = _argocd_args(method="flux")
        img_repo, img_policy, img_update = scaffold_argocd.generate_flux_image_automation(args)
        assert img_repo["kind"] == "ImageRepository"
        assert img_policy["kind"] == "ImagePolicy"
        assert img_update["kind"] == "ImageUpdateAutomation"

    def test_cli_argocd_output_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_argocd",
                ["--name", "ext-app",
                 "--repo", "https://github.com/test/ext-app.git",
                 "--auto-sync", "--output-dir", tmp],
            )
            assert result.returncode == 0
            assert (Path(tmp) / "argocd" / "application.yaml").exists()
            assert (Path(tmp) / "argocd" / "appproject.yaml").exists()

    def test_cli_flux_output_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_argocd",
                ["--name", "flux-app", "--method", "flux",
                 "--repo", "https://github.com/test/flux-app.git",
                 "--output-dir", tmp],
            )
            assert result.returncode == 0
            assert (Path(tmp) / "flux" / "kustomization.yaml").exists()
            assert (Path(tmp) / "flux" / "git-repository.yaml").exists()


# ===========================================================================
# CLI: scaffold_sre (extended + bug tests)
# ===========================================================================

class TestScaffoldSREExtended:
    """Extended tests for the SRE configuration generator."""

    def test_alert_rules_availability_group_present(self):
        args = _sre_args(slo_type="availability")
        rules = scaffold_sre.generate_alert_rules(args)
        group_names = [g["name"] for g in rules["spec"]["groups"]]
        assert any("availability" in n for n in group_names)

    def test_alert_rules_latency_group_present(self):
        args = _sre_args(slo_type="latency")
        rules = scaffold_sre.generate_alert_rules(args)
        group_names = [g["name"] for g in rules["spec"]["groups"]]
        assert any("latency" in n for n in group_names)

    def test_alert_rules_error_rate_group_present(self):
        """error_rate type should generate availability/error-rate alert rules."""
        args = _sre_args(slo_type="error_rate")
        rules = scaffold_sre.generate_alert_rules(args)
        group_names = [g["name"] for g in rules["spec"]["groups"]]
        assert any("availability" in n or "error_rate" in n for n in group_names)

    def test_alert_rules_all_type_has_multiple_groups(self):
        args = _sre_args(slo_type="all")
        rules = scaffold_sre.generate_alert_rules(args)
        assert len(rules["spec"]["groups"]) >= 3  # availability, latency, infrastructure

    def test_alert_rules_invalid_slo_target_zero_raises(self):
        """slo_target=0 should raise ValueError."""
        args = _sre_args(slo_target=0.0)
        with pytest.raises(ValueError):
            scaffold_sre.generate_alert_rules(args)

    def test_alert_rules_invalid_slo_target_100_raises(self):
        """slo_target=100 should raise ValueError."""
        args = _sre_args(slo_target=100.0)
        with pytest.raises(ValueError):
            scaffold_sre.generate_alert_rules(args)

    def test_alert_rules_minimum_valid_slo_target(self):
        """slo_target just above 0 should be valid."""
        args = _sre_args(slo_target=0.001)
        rules = scaffold_sre.generate_alert_rules(args)
        assert rules["kind"] == "PrometheusRule"

    def test_alert_rules_maximum_valid_slo_target(self):
        """slo_target just below 100 should be valid."""
        args = _sre_args(slo_target=99.999)
        rules = scaffold_sre.generate_alert_rules(args)
        assert rules["kind"] == "PrometheusRule"

    def test_alert_rules_infrastructure_group_always_present(self):
        """Infrastructure rules should always be generated regardless of slo_type."""
        for slo_type in ("availability", "latency", "error_rate", "all"):
            args = _sre_args(slo_type=slo_type)
            rules = scaffold_sre.generate_alert_rules(args)
            group_names = [g["name"] for g in rules["spec"]["groups"]]
            assert any("infrastructure" in n for n in group_names), (
                f"Expected infrastructure group for slo_type={slo_type}"
            )

    def test_alert_rules_prometheus_rule_metadata(self):
        args = _sre_args(name="my-api", team="sre-team")
        rules = scaffold_sre.generate_alert_rules(args)
        assert rules["metadata"]["labels"]["team"] == "sre-team"
        assert "my-api" in rules["metadata"]["name"]

    def test_grafana_dashboard_has_required_keys(self):
        args = _sre_args(name="dash-svc")
        dash = scaffold_sre.generate_grafana_dashboard(args)
        assert "panels" in dash
        assert "title" in dash
        assert "uid" in dash
        assert len(dash["panels"]) >= 6  # 6 standard panels

    def test_grafana_dashboard_title_contains_service_name(self):
        args = _sre_args(name="checkout-service")
        dash = scaffold_sre.generate_grafana_dashboard(args)
        assert "checkout-service" in dash["title"].lower()

    def test_grafana_dashboard_slo_stat_panel_present(self):
        """SLO target stat panel (id=7) should be present."""
        args = _sre_args(name="api-gw", slo_target=99.95)
        dash = scaffold_sre.generate_grafana_dashboard(args)
        stat_panels = [p for p in dash["panels"] if p.get("type") == "stat"]
        assert len(stat_panels) >= 1
        assert "99.95" in stat_panels[0]["title"]

    def test_slo_manifest_availability_entry(self):
        args = _sre_args(slo_type="availability")
        manifest = scaffold_sre.generate_slo_manifest(args)
        slo_names = [s["name"] for s in manifest["slos"]]
        assert "availability" in slo_names

    def test_slo_manifest_latency_entry(self):
        args = _sre_args(slo_type="latency", latency_threshold=0.2)
        manifest = scaffold_sre.generate_slo_manifest(args)
        slo_names = [s["name"] for s in manifest["slos"]]
        assert "latency" in slo_names

    def test_slo_manifest_error_rate_bug(self):
        """
        BUG-2: When slo_type='error_rate', generate_slo_manifest() should
        return at least one SLO entry capturing the error rate objective,
        and that entry should have name == 'error_rate'.
        """
        args = _sre_args(slo_type="error_rate")
        manifest = scaffold_sre.generate_slo_manifest(args)
        # Correct expected behavior: error_rate should produce at least one SLO
        assert len(manifest["slos"]) > 0, (
            "Expected at least one SLO entry for error_rate type, "
            "got empty list."
        )
        slo_names = [s["name"] for s in manifest["slos"]]
        assert "error_rate" in slo_names

    def test_slo_manifest_all_type_has_both_slos(self):
        args = _sre_args(slo_type="all")
        manifest = scaffold_sre.generate_slo_manifest(args)
        slo_names = [s["name"] for s in manifest["slos"]]
        assert "availability" in slo_names
        assert "latency" in slo_names

    def test_alertmanager_config_slack_receiver(self):
        args = _sre_args(slack_channel="#platform-alerts")
        config = scaffold_sre.generate_alertmanager_config(args)
        assert any(
            r["name"].endswith("-slack") for r in config["receivers"]
        )
        slack_receiver = next(
            r for r in config["receivers"] if r["name"].endswith("-slack")
        )
        assert slack_receiver["slack_configs"][0]["channel"] == "#platform-alerts"

    def test_alertmanager_config_pagerduty_receiver_when_key_set(self):
        args = _sre_args(pagerduty_key="test-pd-key")
        config = scaffold_sre.generate_alertmanager_config(args)
        pd_receivers = [r for r in config["receivers"] if "pagerduty" in r["name"]]
        assert len(pd_receivers) >= 1

    def test_alertmanager_config_no_pagerduty_when_key_empty(self):
        args = _sre_args(pagerduty_key="")
        config = scaffold_sre.generate_alertmanager_config(args)
        pd_receivers = [r for r in config["receivers"] if "pagerduty" in r["name"]]
        assert len(pd_receivers) == 0

    def test_alertmanager_config_inhibit_rules_present(self):
        args = _sre_args()
        config = scaffold_sre.generate_alertmanager_config(args)
        assert len(config.get("inhibit_rules", [])) >= 1

    def test_cli_sre_custom_latency_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_sre",
                ["--name", "latency-api", "--slo-type", "latency",
                 "--latency-threshold", "0.1", "--output-dir", tmp],
            )
            assert result.returncode == 0
            with open(Path(tmp) / "alert-rules.yaml") as fh:
                rules = yaml.safe_load(fh)
            # threshold = 0.1s should appear in the latency expression
            latency_group = next(
                g for g in rules["spec"]["groups"] if "latency" in g["name"]
            )
            expr = latency_group["rules"][0]["expr"]
            assert "0.1" in expr

    def test_cli_sre_output_all_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_sre",
                ["--name", "full-sre", "--team", "infra", "--output-dir", tmp],
            )
            assert result.returncode == 0
            for fname in ("alert-rules.yaml", "grafana-dashboard.json",
                          "slo.yaml", "alertmanager-config.yaml"):
                assert (Path(tmp) / fname).exists(), f"Missing: {fname}"


# ===========================================================================
# MCP Server: extended coverage
# ===========================================================================

class TestMCPServerGHA:
    """Extended MCP server tests for GitHub Actions generator."""

    def test_build_workflow_type(self):
        result = generate_github_actions_workflow(
            name="build-app", workflow_type="build", languages="python"
        )
        assert "build" in result.lower()

    def test_test_workflow_type(self):
        result = generate_github_actions_workflow(
            name="test-app", workflow_type="test", languages="python,javascript"
        )
        assert "test" in result.lower()

    def test_deploy_workflow_type_with_k8s(self):
        result = generate_github_actions_workflow(
            name="deploy-app", workflow_type="deploy",
            kubernetes=True, k8s_method="kubectl"
        )
        assert "deploy" in result.lower()

    def test_reusable_workflow_type(self):
        result = generate_github_actions_workflow(
            name="reusable-app", workflow_type="reusable"
        )
        assert "workflow_call" in result

    def test_matrix_build_flag(self):
        result = generate_github_actions_workflow(
            name="matrix-app", workflow_type="build", matrix=True
        )
        assert "matrix" in result

    def test_multi_branch_trigger(self):
        result = generate_github_actions_workflow(
            name="multi-branch", workflow_type="build",
            branches="main,develop"
        )
        # Both branches should appear in output
        assert "main" in result
        assert "develop" in result

    def test_kustomize_deploy(self):
        result = generate_github_actions_workflow(
            name="kust-app", workflow_type="complete",
            kubernetes=True, k8s_method="kustomize"
        )
        assert "kustomize" in result.lower()

    def test_argocd_deploy(self):
        result = generate_github_actions_workflow(
            name="argo-app", workflow_type="complete",
            kubernetes=True, k8s_method="argocd"
        )
        assert "argocd" in result.lower()

    def test_flux_deploy(self):
        result = generate_github_actions_workflow(
            name="flux-app", workflow_type="complete",
            kubernetes=True, k8s_method="flux"
        )
        assert "flux" in result.lower()

    def test_go_java_languages(self):
        result = generate_github_actions_workflow(
            name="multi-lang", workflow_type="build",
            languages="go,java"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mcp_yaml_output_has_no_anchors_or_aliases(self):
        """MCP server must not emit YAML anchors/aliases in GHA workflow output."""
        result = generate_github_actions_workflow(
            name="no-alias-app", workflow_type="build", branches="main"
        )
        assert "&id" not in result, "MCP GHA output must not contain YAML anchors (&id...)"
        assert "*id" not in result, "MCP GHA output must not contain YAML aliases (*id...)"
        # Both triggers must carry explicit branch lists
        parsed = yaml.safe_load(result)
        assert parsed["on"]["push"]["branches"] == ["main"]
        assert parsed["on"]["pull_request"]["branches"] == ["main"]


class TestMCPServerJenkins:
    """Extended MCP server tests for Jenkins pipeline generator."""

    def test_build_pipeline_type(self):
        result = generate_jenkins_pipeline(
            name="build-svc", pipeline_type="build", languages="python"
        )
        assert "Build" in result

    def test_test_pipeline_type(self):
        result = generate_jenkins_pipeline(
            name="test-svc", pipeline_type="test", languages="java"
        )
        assert "Test" in result

    def test_deploy_pipeline_with_k8s(self):
        result = generate_jenkins_pipeline(
            name="deploy-svc", pipeline_type="deploy",
            kubernetes=True, k8s_method="kubectl"
        )
        assert "Deploy" in result

    def test_parameterized_pipeline(self):
        result = generate_jenkins_pipeline(
            name="param-svc", pipeline_type="parameterized", parameters=True
        )
        assert "parameters" in result

    def test_kustomize_k8s_method(self):
        result = generate_jenkins_pipeline(
            name="kust-svc", pipeline_type="complete",
            kubernetes=True, k8s_method="kustomize"
        )
        assert "kustomize" in result.lower()

    def test_argocd_k8s_method(self):
        result = generate_jenkins_pipeline(
            name="argo-svc", pipeline_type="complete",
            kubernetes=True, k8s_method="argocd"
        )
        assert "argocd" in result.lower()

    def test_flux_k8s_method(self):
        result = generate_jenkins_pipeline(
            name="flux-svc", pipeline_type="complete",
            kubernetes=True, k8s_method="flux"
        )
        assert "flux" in result.lower()


class TestMCPServerK8s:
    """Tests for the Kubernetes config generator."""

    def test_custom_namespace(self):
        result = generate_k8s_config(
            app_name="ns-app",
            image="ns-app:latest",
            namespace="production",
        )
        assert "production" in result

    def test_custom_replicas(self):
        result = generate_k8s_config(
            app_name="scaled-app",
            image="scaled-app:v1",
            replicas=5,
            expose_service=False,
        )
        assert "5" in result

    def test_argocd_method_no_kustomization(self):
        result = generate_k8s_config(
            app_name="argo-app",
            image="argo-app:v1",
            deployment_method="argocd",
        )
        assert "Deployment" in result
        # argocd method doesn't add extra manifests like kustomize does
        assert "Kustomization" not in result

    def test_flux_method_no_kustomization(self):
        result = generate_k8s_config(
            app_name="flux-app",
            image="flux-app:v1",
            deployment_method="flux",
        )
        assert "Deployment" in result

    def test_resource_limits_present(self):
        result = generate_k8s_config(
            app_name="limited-app",
            image="limited-app:v1",
        )
        assert "resources" in result
        assert "limits" in result
        assert "requests" in result

    def test_container_port_is_correct(self):
        result = generate_k8s_config(
            app_name="port-app",
            image="port-app:v1",
            port=3000,
            expose_service=True,
        )
        assert "3000" in result

    def test_app_label_in_deployment(self):
        result = generate_k8s_config(
            app_name="labeled-app",
            image="labeled-app:v1",
            expose_service=False,
        )
        assert "labeled-app" in result


class TestMCPServerDevcontainer:
    """Tests for the devcontainer scaffold tool."""

    def test_all_languages_installed(self):
        result = scaffold_devcontainer(
            languages="python,java,javascript,go,rust,csharp,php,typescript,kotlin,c,cpp,ruby"
        )
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        for lang in ("python", "java", "javascript", "go", "rust", "csharp",
                     "php", "typescript", "kotlin", "c", "cpp", "ruby"):
            assert env["languages"][lang] is True, f"Expected {lang} to be True"

    def test_unselected_languages_are_false(self):
        result = scaffold_devcontainer(languages="python")
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        assert env["languages"]["java"] is False
        assert env["languages"]["go"] is False

    def test_cicd_tools_correctly_set(self):
        result = scaffold_devcontainer(
            languages="python",
            cicd_tools="docker,terraform,kubectl,helm",
        )
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        assert env["cicd"]["docker"] is True
        assert env["cicd"]["terraform"] is True
        assert env["cicd"]["kubectl"] is True
        assert env["cicd"]["helm"] is True
        assert env["cicd"]["jenkins"] is False

    def test_kubernetes_tools_correctly_set(self):
        result = scaffold_devcontainer(
            languages="python",
            kubernetes_tools="k9s,kustomize,argocd_cli,flux",
        )
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        assert env["kubernetes"]["k9s"] is True
        assert env["kubernetes"]["kustomize"] is True
        assert env["kubernetes"]["argocd_cli"] is True
        assert env["kubernetes"]["flux"] is True
        assert env["kubernetes"]["minikube"] is False

    def test_version_overrides(self):
        result = scaffold_devcontainer(
            languages="python,java,go",
            python_version="3.12",
            java_version="21",
            go_version="1.22",
        )
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        assert env["versions"]["python"] == "3.12"
        assert env["versions"]["java"] == "21"
        assert env["versions"]["go"] == "1.22"

    def test_devcontainer_json_has_extensions(self):
        result = scaffold_devcontainer(
            languages="python,java,go",
            cicd_tools="docker,terraform",
            kubernetes_tools="k9s",
        )
        data = json.loads(result)
        dc = json.loads(data["devcontainer_json"])
        extensions = dc["customizations"]["vscode"]["extensions"]
        assert "ms-python.python" in extensions
        assert "redhat.java" in extensions
        assert "golang.go" in extensions
        assert "hashicorp.terraform" in extensions
        assert "ms-kubernetes-tools.vscode-kubernetes-tools" in extensions

    def test_devcontainer_json_docker_mount(self):
        result = scaffold_devcontainer(languages="python")
        data = json.loads(result)
        dc = json.loads(data["devcontainer_json"])
        mounts = dc.get("mounts", [])
        assert any("docker.sock" in m for m in mounts)


class TestMCPServerGitLab:
    """Extended MCP server tests for GitLab CI generator."""

    def test_complete_pipeline_has_all_stages(self):
        result = generate_gitlab_ci_pipeline(
            name="full-app", pipeline_type="complete",
            languages="python", kubernetes=True, k8s_method="kubectl"
        )
        data = yaml.safe_load(result)
        stages = data.get("stages", [])
        assert "build" in stages
        assert "test" in stages
        assert "deploy" in stages

    def test_build_pipeline_has_build_stage(self):
        result = generate_gitlab_ci_pipeline(
            name="build-app", pipeline_type="build", languages="python"
        )
        data = yaml.safe_load(result)
        assert "build" in (data.get("stages") or [])

    def test_test_pipeline_has_test_stage(self):
        result = generate_gitlab_ci_pipeline(
            name="test-app", pipeline_type="test", languages="python"
        )
        data = yaml.safe_load(result)
        assert "test" in (data.get("stages") or [])

    def test_golang_test_job(self):
        result = generate_gitlab_ci_pipeline(
            name="go-app", pipeline_type="test", languages="go"
        )
        assert "go" in result.lower()

    def test_javascript_test_job(self):
        result = generate_gitlab_ci_pipeline(
            name="js-app", pipeline_type="test", languages="javascript"
        )
        assert "javascript" in result.lower() or "node" in result.lower()


class TestMCPServerArgoCD:
    """Extended MCP server tests for ArgoCD config generator."""

    def test_auto_sync_in_application_yaml(self):
        result = generate_argocd_config(
            name="sync-app",
            auto_sync=True,
            repo="https://github.com/test/sync-app.git",
        )
        data = json.loads(result)
        app_yaml = data["argocd/application.yaml"]
        assert "automated" in app_yaml

    def test_custom_path_and_namespace(self):
        result = generate_argocd_config(
            name="custom-app",
            repo="https://github.com/test/custom-app.git",
            path="manifests/production",
            namespace="production",
        )
        data = json.loads(result)
        assert "manifests/production" in data["argocd/application.yaml"]
        assert "production" in data["argocd/application.yaml"]

    def test_custom_project(self):
        result = generate_argocd_config(
            name="proj-app",
            repo="https://github.com/test/proj-app.git",
            project="team-b",
        )
        data = json.loads(result)
        assert "team-b" in data["argocd/appproject.yaml"]

    def test_appproject_repo_is_scoped_by_default(self):
        """AppProject sourceRepos should be scoped to the given repo by default."""
        result = generate_argocd_config(
            name="scoped-app",
            repo="https://github.com/test/scoped-app.git",
        )
        data = json.loads(result)
        proj_yaml = data["argocd/appproject.yaml"]
        # Wildcard should NOT be in default appproject
        assert "- '*'" not in proj_yaml

    # BUG-3: allow_any_source_repo is not exposed in MCP server generate_argocd_config
    @pytest.mark.xfail(
        strict=True,
        reason=(
            "BUG-3: generate_argocd_config() in the MCP server does not expose "
            "the allow_any_source_repo parameter. Users cannot opt-in to wildcard "
            "source repos via the MCP interface. The parameter exists in "
            "scaffold_argocd but is not wired through the MCP tool."
        ),
    )
    def test_allow_any_source_repo_not_available_in_mcp(self):
        """
        BUG-3: generate_argocd_config should expose allow_any_source_repo
        so users can opt-in to wildcard source repos via the MCP interface.
        """
        import inspect
        sig = inspect.signature(generate_argocd_config)
        # Correct expected behavior: the parameter should be present
        assert "allow_any_source_repo" in sig.parameters, (
            "generate_argocd_config should expose allow_any_source_repo "
            "so users can opt-in to wildcard source repos."
        )

    def test_flux_kustomization_present(self):
        result = generate_argocd_config(
            name="flux-app",
            method="flux",
            repo="https://github.com/test/flux-app.git",
        )
        data = json.loads(result)
        assert "flux/kustomization.yaml" in data
        assert "Kustomization" in data["flux/kustomization.yaml"]

    def test_flux_git_repository_present(self):
        result = generate_argocd_config(
            name="flux-app",
            method="flux",
            repo="https://github.com/test/flux-app.git",
        )
        data = json.loads(result)
        assert "flux/git-repository.yaml" in data


class TestMCPServerSRE:
    """Extended MCP server tests for SRE configs generator."""

    def test_availability_only(self):
        result = generate_sre_configs(
            name="avail-svc", slo_type="availability", slo_target=99.5
        )
        data = json.loads(result)
        assert "PrometheusRule" in data["alert_rules_yaml"]
        slo = yaml.safe_load(data["slo_yaml"])
        assert any(s["name"] == "availability" for s in slo["slos"])

    def test_latency_only(self):
        result = generate_sre_configs(
            name="latency-svc", slo_type="latency",
            slo_target=99.9, latency_threshold=0.25
        )
        data = json.loads(result)
        slo = yaml.safe_load(data["slo_yaml"])
        assert any(s["name"] == "latency" for s in slo["slos"])

    def test_error_rate_alert_rules_generated(self):
        """error_rate type should still generate Prometheus alert rules."""
        result = generate_sre_configs(
            name="err-svc", slo_type="error_rate", slo_target=99.0
        )
        data = json.loads(result)
        assert "PrometheusRule" in data["alert_rules_yaml"]

    def test_grafana_dashboard_valid_json(self):
        result = generate_sre_configs(name="dash-svc")
        data = json.loads(result)
        dash = json.loads(data["grafana_dashboard_json"])
        assert "panels" in dash
        assert "title" in dash

    def test_alertmanager_config_has_route(self):
        result = generate_sre_configs(name="route-svc", team="ops")
        data = json.loads(result)
        am = yaml.safe_load(data["alertmanager_config_yaml"])
        assert "route" in am
        assert "receivers" in am

    def test_custom_slack_channel(self):
        result = generate_sre_configs(
            name="slack-svc", slack_channel="#my-custom-channel"
        )
        data = json.loads(result)
        am = yaml.safe_load(data["alertmanager_config_yaml"])
        slack_configs = am["receivers"][0]["slack_configs"]
        assert slack_configs[0]["channel"] == "#my-custom-channel"

    def test_slo_service_field_correct(self):
        result = generate_sre_configs(name="my-unique-service")
        data = json.loads(result)
        slo = yaml.safe_load(data["slo_yaml"])
        assert slo["service"] == "my-unique-service"


# ===========================================================================
# Skills definition tests
# ===========================================================================

class TestSkillsDefinitions:
    """Tests to validate AI skills definition files."""

    SKILLS_DIR = Path(__file__).parent.parent / "skills"

    def test_openai_functions_json_is_valid(self):
        with open(self.SKILLS_DIR / "openai_functions.json") as fh:
            tools = json.load(fh)
        assert isinstance(tools, list)
        assert len(tools) >= 7  # 7 tools exposed

    def test_openai_functions_have_required_fields(self):
        with open(self.SKILLS_DIR / "openai_functions.json") as fh:
            tools = json.load(fh)
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            fn = tool["function"]
            assert "name" in fn
            assert "description" in fn
            assert "parameters" in fn

    def test_claude_tools_json_is_valid(self):
        with open(self.SKILLS_DIR / "claude_tools.json") as fh:
            tools = json.load(fh)
        assert isinstance(tools, list)
        assert len(tools) >= 7

    def test_claude_tools_have_required_fields(self):
        with open(self.SKILLS_DIR / "claude_tools.json") as fh:
            tools = json.load(fh)
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_tool_names_match_between_openai_and_claude(self):
        """Both skill files should expose the same set of tools."""
        with open(self.SKILLS_DIR / "openai_functions.json") as fh:
            openai_tools = {t["function"]["name"] for t in json.load(fh)}
        with open(self.SKILLS_DIR / "claude_tools.json") as fh:
            claude_tools = {t["name"] for t in json.load(fh)}
        assert openai_tools == claude_tools, (
            f"Tool name mismatch.\n"
            f"Only in OpenAI: {openai_tools - claude_tools}\n"
            f"Only in Claude: {claude_tools - openai_tools}"
        )

    def test_all_expected_tools_present(self):
        expected = {
            "generate_github_actions_workflow",
            "generate_jenkins_pipeline",
            "generate_k8s_config",
            "scaffold_devcontainer",
            "generate_gitlab_ci_pipeline",
            "generate_argocd_config",
            "generate_sre_configs",
        }
        with open(self.SKILLS_DIR / "openai_functions.json") as fh:
            openai_tools = {t["function"]["name"] for t in json.load(fh)}
        assert expected.issubset(openai_tools), (
            f"Missing tools: {expected - openai_tools}"
        )

    def test_openai_sre_tool_has_slo_type_enum(self):
        with open(self.SKILLS_DIR / "openai_functions.json") as fh:
            tools = json.load(fh)
        sre_tool = next(t for t in tools if t["function"]["name"] == "generate_sre_configs")
        slo_type_prop = sre_tool["function"]["parameters"]["properties"]["slo_type"]
        assert "enum" in slo_type_prop
        assert "error_rate" in slo_type_prop["enum"]

    def test_claude_argocd_tool_has_method_enum(self):
        with open(self.SKILLS_DIR / "claude_tools.json") as fh:
            tools = json.load(fh)
        argocd_tool = next(t for t in tools if t["name"] == "generate_argocd_config")
        method_prop = argocd_tool["input_schema"]["properties"]["method"]
        assert "enum" in method_prop
        assert "argocd" in method_prop["enum"]
        assert "flux" in method_prop["enum"]


# ===========================================================================
# CLI: scaffold_unittest
# ===========================================================================

class TestScaffoldUnittest:
    """Tests for the unit testing scaffold generator."""

    # ── Python / pytest ──────────────────────────────────────────────────────

    def test_pytest_ini_contains_testpaths(self):
        content = scaffold_unittest.generate_pytest_ini("my-app", coverage=True)
        assert "testpaths = tests" in content

    def test_pytest_ini_contains_coverage_options(self):
        content = scaffold_unittest.generate_pytest_ini("my-app", coverage=True)
        assert "--cov=" in content
        assert "--cov-report=xml" in content

    def test_pytest_ini_no_coverage_when_disabled(self):
        content = scaffold_unittest.generate_pytest_ini("my-app", coverage=False)
        assert "--cov=" not in content

    def test_conftest_py_contains_fixture(self):
        content = scaffold_unittest.generate_conftest_py("my-app")
        assert "@pytest.fixture" in content
        assert "sample_config" in content

    def test_conftest_py_uses_app_name(self):
        content = scaffold_unittest.generate_conftest_py("my-svc")
        assert "my-svc" in content

    def test_python_test_sample_has_test_class(self):
        content = scaffold_unittest.generate_python_test_sample("my-app")
        assert "class Test" in content
        assert "def test_" in content

    def test_python_test_sample_has_parametrize(self):
        content = scaffold_unittest.generate_python_test_sample("my-app")
        assert "parametrize" in content

    # ── JavaScript / Jest ────────────────────────────────────────────────────

    def test_jest_config_has_test_environment(self):
        content = scaffold_unittest.generate_jest_config("my-app", is_typescript=False, coverage=True)
        assert "testEnvironment" in content
        assert "node" in content

    def test_jest_config_with_coverage(self):
        content = scaffold_unittest.generate_jest_config("my-app", is_typescript=False, coverage=True)
        assert "collectCoverage" in content
        assert "coverageThreshold" in content

    def test_jest_config_without_coverage(self):
        content = scaffold_unittest.generate_jest_config("my-app", is_typescript=False, coverage=False)
        assert "collectCoverage" not in content

    def test_jest_config_typescript_transform(self):
        content = scaffold_unittest.generate_jest_config("my-app", is_typescript=True, coverage=False)
        assert "ts-jest" in content
        assert "moduleFileExtensions" in content

    def test_js_test_sample_jest_uses_expect(self):
        content = scaffold_unittest.generate_js_test_sample("my-app", "jest", is_typescript=False)
        assert "expect(" in content
        assert "toBe(" in content
        assert "describe(" in content

    def test_js_test_sample_mocha_uses_chai(self):
        content = scaffold_unittest.generate_js_test_sample("my-app", "mocha", is_typescript=False)
        assert "require('chai')" in content
        assert ".to.equal" in content

    def test_js_test_sample_vitest_import(self):
        content = scaffold_unittest.generate_js_test_sample("my-app", "vitest", is_typescript=False)
        assert "from 'vitest'" in content

    # ── JavaScript / Vitest ──────────────────────────────────────────────────

    def test_vitest_config_has_defineconfig(self):
        content = scaffold_unittest.generate_vitest_config("my-app", coverage=True)
        assert "defineConfig" in content
        assert "vitest/config" in content

    def test_vitest_config_coverage_block(self):
        content = scaffold_unittest.generate_vitest_config("my-app", coverage=True)
        assert "coverage" in content
        assert "thresholds" in content

    def test_vitest_config_no_coverage(self):
        content = scaffold_unittest.generate_vitest_config("my-app", coverage=False)
        assert "thresholds" not in content

    # ── JavaScript / Mocha ───────────────────────────────────────────────────

    def test_mocha_rc_has_spec_glob(self):
        content = scaffold_unittest.generate_mocha_rc("my-app", coverage=True)
        assert "spec" in content
        assert "tests/**" in content

    def test_mocha_rc_mentions_nyc_when_coverage(self):
        content = scaffold_unittest.generate_mocha_rc("my-app", coverage=True)
        assert "nyc" in content

    # ── Go / go test ─────────────────────────────────────────────────────────

    def test_go_test_sample_has_testing_import(self):
        content = scaffold_unittest.generate_go_test_sample("my-service")
        assert '"testing"' in content

    def test_go_test_sample_has_table_driven_test(self):
        content = scaffold_unittest.generate_go_test_sample("my-service")
        assert "TestTableDriven" in content

    def test_go_test_sample_uses_package_name(self):
        content = scaffold_unittest.generate_go_test_sample("my-service")
        assert "my_service_test" in content

    def test_go_makefile_has_test_target(self):
        content = scaffold_unittest.generate_go_makefile("my-service", coverage=True)
        assert "test:" in content
        assert "go test" in content

    def test_go_makefile_has_coverage_target(self):
        content = scaffold_unittest.generate_go_makefile("my-service", coverage=True)
        assert "test-cov:" in content
        assert "coverprofile" in content

    def test_go_makefile_no_coverage_when_disabled(self):
        content = scaffold_unittest.generate_go_makefile("my-service", coverage=False)
        assert "coverprofile" not in content

    # ── generate_unittest_scaffold (file-system) ─────────────────────────────

    def test_generate_scaffold_python_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-app",
                languages="python",
                framework="",
                coverage=True,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            assert any("pytest.ini" in p for p in paths)
            assert any("conftest.py" in p for p in paths)
            assert any("test_sample.py" in p for p in paths)

    def test_generate_scaffold_javascript_jest_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-app",
                languages="javascript",
                framework="jest",
                coverage=True,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            assert any("jest.config.js" in p for p in paths)
            assert any("sample.test.js" in p for p in paths)

    def test_generate_scaffold_typescript_vitest_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-app",
                languages="typescript",
                framework="vitest",
                coverage=False,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            assert any("vitest.config.js" in p for p in paths)
            assert any("sample.test.ts" in p for p in paths)

    def test_generate_scaffold_go_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-service",
                languages="go",
                framework="",
                coverage=True,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            assert any("_test.go" in p for p in paths)
            assert any("Makefile.test" in p for p in paths)

    def test_generate_scaffold_multi_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="full-stack",
                languages="python,javascript,go",
                framework="",
                coverage=True,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            # Python
            assert any("pytest.ini" in p for p in paths)
            # JavaScript
            assert any("jest.config.js" in p for p in paths)
            # Go
            assert any("_test.go" in p for p in paths)

    def test_generate_scaffold_unsupported_language_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-app",
                languages="rust",
                framework="",
                coverage=True,
                output_dir=tmp,
            )
            assert written == []

    def test_generate_scaffold_mocha_framework(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold_unittest.generate_unittest_scaffold(
                name="my-app",
                languages="javascript",
                framework="mocha",
                coverage=True,
                output_dir=tmp,
            )
            paths = [str(p) for p, _ in written]
            assert any(".mocharc.js" in p for p in paths)
            assert not any("jest.config.js" in p for p in paths)

    # ── CLI module invocation ─────────────────────────────────────────────────

    def test_cli_python_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_unittest",
                ["--name", "my-app", "--languages", "python", "--output-dir", tmp],
            )
            assert result.returncode == 0
            assert "pytest.ini" in result.stdout
            assert os.path.exists(os.path.join(tmp, "pytest.ini"))

    def test_cli_javascript_jest_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_unittest",
                ["--name", "my-lib", "--languages", "javascript",
                 "--framework", "jest", "--output-dir", tmp],
            )
            assert result.returncode == 0
            assert os.path.exists(os.path.join(tmp, "jest.config.js"))

    def test_cli_go_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_unittest",
                ["--name", "my-api", "--languages", "go", "--output-dir", tmp],
            )
            assert result.returncode == 0
            assert os.path.exists(os.path.join(tmp, "my_api_test.go"))

    def test_cli_no_coverage_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_module(
                "cli.scaffold_unittest",
                ["--name", "my-app", "--languages", "python",
                 "--no-coverage", "--output-dir", tmp],
            )
            assert result.returncode == 0
            content = open(os.path.join(tmp, "pytest.ini")).read()
            assert "--cov=" not in content


# ===========================================================================
# MCP Server: generate_unittest_config
# ===========================================================================

class TestMCPServerUnittest:
    """Tests for the MCP server generate_unittest_config tool."""

    def test_python_returns_pytest_ini(self):
        result = json.loads(generate_unittest_config(name="my-api", languages="python"))
        assert "pytest.ini" in result
        assert "conftest.py" in result
        assert "tests/test_sample.py" in result

    def test_javascript_jest_returns_jest_config(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="javascript", framework="jest"))
        assert "jest.config.js" in result
        assert "tests/sample.test.js" in result

    def test_javascript_mocha_returns_mocharc(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="javascript", framework="mocha"))
        assert ".mocharc.js" in result

    def test_javascript_vitest_returns_vitest_config(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="javascript", framework="vitest"))
        assert "vitest.config.js" in result

    def test_typescript_jest_returns_ts_test_file(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="typescript", framework="jest"))
        assert "tests/sample.test.ts" in result
        assert "jest.config.js" in result

    def test_go_returns_test_file_and_makefile(self):
        result = json.loads(generate_unittest_config(
            name="my-service", languages="go"))
        assert "my_service_test.go" in result
        assert "Makefile.test" in result

    def test_multi_language_returns_all_files(self):
        result = json.loads(generate_unittest_config(
            name="full-stack", languages="python,javascript,go"))
        assert "pytest.ini" in result
        assert "jest.config.js" in result
        assert "full_stack_test.go" in result

    def test_coverage_true_includes_coverage_config(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="python", coverage=True))
        assert "--cov=" in result["pytest.ini"]

    def test_coverage_false_excludes_coverage_config(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="python", coverage=False))
        assert "--cov=" not in result["pytest.ini"]

    def test_go_test_file_content_has_testing_import(self):
        result = json.loads(generate_unittest_config(
            name="my-svc", languages="go"))
        assert '"testing"' in result["my_svc_test.go"]

    def test_unsupported_language_returns_empty(self):
        result = json.loads(generate_unittest_config(
            name="my-app", languages="rust"))
        assert result == {}
