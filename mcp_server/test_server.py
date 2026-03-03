"""Tests for DevOps-OS MCP server tools."""
import json
import sys
import os

# Ensure repo root is on path when run from CLI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_server.server import (
    generate_github_actions_workflow,
    generate_jenkins_pipeline,
    generate_k8s_config,
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
        kubernetes_tools="kubectl,helm",
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
