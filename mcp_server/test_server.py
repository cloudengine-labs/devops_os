"""Tests for DevOps-OS MCP server tools."""
import json
import sys
import os

# Ensure repo root is on path when run from CLI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_server.server import (
    generate_github_actions_workflow,
    generate_gitlab_ci_pipeline,
    generate_jenkins_pipeline,
    generate_k8s_config,
    generate_argocd_config,
    generate_sre_configs,
    scaffold_devcontainer,
)


def test_generate_github_actions_workflow_default():
    result = generate_github_actions_workflow()
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_github_actions_workflow_with_k8s():
    result = generate_github_actions_workflow(
        name="my-api",
        workflow_type="complete",
        languages="python,javascript",
        kubernetes=True,
        k8s_method="kustomize",
    )
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_jenkins_pipeline_default():
    result = generate_jenkins_pipeline()
    assert isinstance(result, str)
    assert "pipeline" in result.lower()


def test_generate_jenkins_pipeline_parameterized():
    result = generate_jenkins_pipeline(
        name="java-app", pipeline_type="parameterized", languages="java", parameters=True
    )
    assert isinstance(result, str)
    assert "pipeline" in result.lower()


def test_generate_k8s_config_deployment_only():
    result = generate_k8s_config(
        app_name="my-service",
        image="ghcr.io/org/my-service:v1",
        replicas=1,
        port=3000,
        expose_service=False,
    )
    assert "my-service" in result
    assert "Deployment" in result
    assert "Service" not in result


def test_generate_k8s_config_with_service():
    result = generate_k8s_config(
        app_name="api",
        image="api:latest",
        replicas=2,
        port=8080,
        expose_service=True,
    )
    assert "Deployment" in result
    assert "Service" in result


def test_generate_k8s_config_kustomize():
    result = generate_k8s_config(
        app_name="frontend",
        image="frontend:latest",
        deployment_method="kustomize",
    )
    assert "Kustomization" in result


def test_scaffold_devcontainer_returns_valid_json():
    result = scaffold_devcontainer(
        languages="python,go",
        cicd_tools="docker,github_actions",
        kubernetes_tools="k9s,kustomize",
    )
    data = json.loads(result)
    assert "devcontainer_json" in data
    assert "devcontainer_env_json" in data


def test_scaffold_devcontainer_language_flags():
    result = scaffold_devcontainer(languages="python,go")
    data = json.loads(result)
    env = json.loads(data["devcontainer_env_json"])
    assert env["languages"]["python"] is True
    assert env["languages"]["go"] is True
    assert env["languages"]["java"] is False


# ---------------------------------------------------------------------------
# GitLab CI
# ---------------------------------------------------------------------------

def test_generate_gitlab_ci_default():
    result = generate_gitlab_ci_pipeline()
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_gitlab_ci_with_k8s():
    result = generate_gitlab_ci_pipeline(
        name="api", pipeline_type="complete",
        languages="python,go", kubernetes=True, k8s_method="argocd"
    )
    assert "deploy" in result.lower()


def test_generate_gitlab_ci_test_java():
    result = generate_gitlab_ci_pipeline(
        name="java-app", pipeline_type="test", languages="java"
    )
    assert "java" in result.lower()


# ---------------------------------------------------------------------------
# ArgoCD
# ---------------------------------------------------------------------------

def test_generate_argocd_config_default():
    result = generate_argocd_config()
    data = json.loads(result)
    assert "argocd/application.yaml" in data
    assert "argocd/appproject.yaml" in data


def test_generate_argocd_config_auto_sync():
    result = generate_argocd_config(auto_sync=True)
    data = json.loads(result)
    assert "automated" in data["argocd/application.yaml"]


def test_generate_argocd_config_rollouts():
    result = generate_argocd_config(rollouts=True)
    data = json.loads(result)
    assert "argocd/rollout.yaml" in data
    assert "Rollout" in data["argocd/rollout.yaml"]


def test_generate_argocd_config_flux():
    result = generate_argocd_config(method="flux")
    data = json.loads(result)
    assert "flux/kustomization.yaml" in data
    assert "Kustomization" in data["flux/kustomization.yaml"]


def test_generate_argocd_config_allow_any_source_repo():
    result = generate_argocd_config(allow_any_source_repo=True)
    data = json.loads(result)
    assert "*" in data["argocd/appproject.yaml"]


# ---------------------------------------------------------------------------
# SRE configs
# ---------------------------------------------------------------------------

def test_generate_sre_configs_default():
    result = generate_sre_configs()
    data = json.loads(result)
    assert "alert_rules_yaml" in data
    assert "grafana_dashboard_json" in data
    assert "slo_yaml" in data
    assert "alertmanager_config_yaml" in data


def test_generate_sre_configs_alert_rules_kind():
    result = generate_sre_configs(name="web-api", slo_type="availability")
    data = json.loads(result)
    assert "PrometheusRule" in data["alert_rules_yaml"]


def test_generate_sre_configs_grafana_panels():
    result = generate_sre_configs(name="web-api")
    data = json.loads(result)
    dash = json.loads(data["grafana_dashboard_json"])
    assert len(dash.get("panels", [])) > 0


def test_generate_sre_configs_slo_service():
    result = generate_sre_configs(name="my-svc", slo_type="latency", slo_target=99.5)
    data = json.loads(result)
    import yaml
    slo = yaml.safe_load(data["slo_yaml"])
    assert slo["service"] == "my-svc"
