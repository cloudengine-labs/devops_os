#!/usr/bin/env python3
"""
DevOps-OS MCP Server

A Model Context Protocol (MCP) server that exposes DevOps-OS tools to AI
assistants like Claude and ChatGPT. Enables automated DevOps pipeline
creation from CI/CD to SRE dashboards through conversational AI.

Tools exposed:
  - generate_github_actions_workflow  : Create GitHub Actions workflow YAML
  - generate_gitlab_ci_pipeline       : Create a GitLab CI .gitlab-ci.yml
  - generate_jenkins_pipeline         : Create a Jenkins Declarative Pipeline
  - generate_k8s_config               : Create Kubernetes manifests
  - generate_argocd_config            : Create ArgoCD Application / AppProject CRs
  - generate_sre_configs              : Create Prometheus rules, Grafana dashboard, SLO manifest
  - scaffold_devcontainer             : Create a dev-container configuration
"""

import sys
import os
import json
import tempfile
import argparse
import logging
from pathlib import Path
from typing import Any

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP
import yaml

from mcp_server.config import Config
from mcp_server.validators import ValidationError, validate_tool_inputs
from mcp_server.logging import get_logger, CorrelationContext
from mcp_server.auth import create_token_verifier
from mcp_server.response_enhancer import ResponseEnhancer
from mcp_server.concurrency import ConcurrencyManager

# Use structured logger instead of standard logging
logger = get_logger(__name__)


class _NoAliasDumper(yaml.Dumper):
    """Custom YAML Dumper that never emits anchors or aliases.

    Prevents PyYAML from collapsing shared object references (e.g. the same
    ``branches`` list used in both ``push`` and ``pull_request`` triggers) into
    anchor/alias pairs like ``&id001`` / ``*id001`` that are not supported by
    GitHub Actions and confuse users.
    """

    def ignore_aliases(self, data):  # noqa: ARG002
        return True

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_gha_args(
    name: str,
    workflow_type: str,
    languages: str,
    kubernetes: bool,
    k8s_method: str,
    branches: str,
    matrix: bool,
    output_dir: str,
) -> argparse.Namespace:
    """Build an argparse.Namespace compatible with scaffold_gha functions."""
    return argparse.Namespace(
        name=name,
        type=workflow_type,
        languages=languages,
        kubernetes=kubernetes,
        k8s_method=k8s_method,
        output=output_dir,
        branches=branches,
        matrix=matrix,
        custom_values=None,
        image="ghcr.io/yourorg/devops-os:latest",
        reusable=(workflow_type == "reusable"),
        env_file=None,
        registry="ghcr.io",
    )


def _build_jenkins_args(
    name: str,
    pipeline_type: str,
    languages: str,
    kubernetes: bool,
    k8s_method: str,
    parameters: bool,
    output_path: str,
) -> argparse.Namespace:
    """Build an argparse.Namespace compatible with scaffold_jenkins functions."""
    return argparse.Namespace(
        name=name,
        type=pipeline_type,
        languages=languages,
        kubernetes=kubernetes,
        k8s_method=k8s_method,
        output=output_path,
        parameters=parameters or (pipeline_type == "parameterized"),
        custom_values=None,
        image="docker.io/yourorg/devops-os:latest",
        scm="git",
        env_file=None,
        registry="docker.io",
    )


# ---------------------------------------------------------------------------
# MCP Server Factory
# ---------------------------------------------------------------------------

# Global config and server instances (set during create_mcp_server)
_config: Config | None = None
_mcp: FastMCP | None = None
_response_enhancer: ResponseEnhancer | None = None
_concurrency_manager: ConcurrencyManager | None = None


def create_mcp_server(config: Config | None = None) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        config: Configuration object. If None, loads from environment.

    Returns:
        Configured FastMCP server instance
    """
    global _config, _mcp, _response_enhancer, _concurrency_manager

    if config is None:
        config = Config.from_env()
    
    _config = config
    _response_enhancer = ResponseEnhancer(config)
    _concurrency_manager = ConcurrencyManager(config.max_concurrent_calls)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info(f"Configuration loaded: transport={config.transport}, profile={config.profile}")
    logger.info(f"Concurrency limit: max_concurrent_calls={config.max_concurrent_calls}")
    logger.info(f"Prompt suggestions: enabled={config.enable_suggestions}, "
                f"threshold={config.suggestion_confidence_threshold}, "
                f"max_per_response={config.max_suggestions_per_response}")

    # Create MCP server with configuration
    _mcp = FastMCP(
        "devops-os",
        instructions=(
            "DevOps-OS MCP Server provides tools for generating DevOps automation "
            "artifacts including GitHub Actions workflows, Jenkins pipelines, "
            "Kubernetes manifests, and dev-container configurations."
        ),
    )

    # Register tools on the new server instance
    _register_tools(_mcp)

    return _mcp


def get_config() -> Config:
    """Get the current configuration.

    Returns:
        Current Config instance

    Raises:
        RuntimeError: If server not yet created
    """
    if _config is None:
        raise RuntimeError("Server not yet initialized. Call create_mcp_server() first.")
    return _config


def get_response_enhancer() -> ResponseEnhancer:
    """Get the response enhancer instance.

    Returns:
        ResponseEnhancer instance

    Raises:
        RuntimeError: If server not yet created
    """
    if _response_enhancer is None:
        raise RuntimeError("Server not yet initialized. Call create_mcp_server() first.")
    return _response_enhancer


def get_concurrency_manager() -> ConcurrencyManager:
    """Get the concurrency manager instance.

    Returns:
        ConcurrencyManager instance

    Raises:
        RuntimeError: If server not yet created
    """
    if _concurrency_manager is None:
        raise RuntimeError("Server not yet initialized. Call create_mcp_server() first.")
    return _concurrency_manager


def _register_tools(mcp: FastMCP) -> None:
    """Register all tools on the given FastMCP instance."""
    mcp.tool()(generate_github_actions_workflow)
    mcp.tool()(generate_jenkins_pipeline)
    mcp.tool()(generate_gitlab_ci_pipeline)
    mcp.tool()(generate_k8s_config)
    mcp.tool()(generate_argocd_config)
    mcp.tool()(generate_sre_configs)
    mcp.tool()(scaffold_devcontainer)
    mcp.tool()(generate_unittest_config)


# Initialize MCP server for backward compatibility with direct imports
# This ensures `python -m mcp_server.server` still works
mcp = FastMCP(
    "devops-os",
    instructions=(
        "DevOps-OS MCP Server provides tools for generating DevOps automation "
        "artifacts including GitHub Actions workflows, Jenkins pipelines, "
        "Kubernetes manifests, and dev-container configurations."
    ),
)


# ---------------------------------------------------------------------------
# Tool: generate_github_actions_workflow
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_github_actions_workflow(
    name: str = "my-app",
    workflow_type: str = "complete",
    languages: str = "python",
    kubernetes: bool = False,
    k8s_method: str = "kubectl",
    branches: str = "main",
    matrix: bool = False,
    user_context: str = "",
) -> str:
    """Generate a GitHub Actions CI/CD workflow YAML.

    Creates a complete or basic GitHub Actions workflow for Python, JavaScript,
    Go, Java, or multi-language projects with optional Kubernetes deployment.

    Args:
        name: Application/workflow name (lowercase, alphanumeric + dashes)
        workflow_type: 'basic' or 'complete' (default: 'complete')
        languages: Comma-separated languages (python, javascript, go, java, rust)
        kubernetes: Enable Kubernetes deployment stage (default: False)
        k8s_method: 'kubectl' or 'kustomize' (default: 'kubectl')
        branches: Trigger branch(es) (default: 'main')
        matrix: Enable job matrix for multi-version testing (default: False)
        user_context: Original user prompt/context (optional, used for suggestions)

    Returns:
        GitHub Actions workflow YAML as string, optionally with prompt suggestions
        in JSON format if suggestions are enabled

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs("generate_github_actions_workflow", name=name, languages=languages)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    
    from devops_os.core import scaffold_gha

    with tempfile.TemporaryDirectory() as tmp:
        args = _build_gha_args(
            name=name,
            workflow_type=workflow_type,
            languages=languages,
            kubernetes=kubernetes,
            k8s_method=k8s_method,
            branches=branches,
            matrix=matrix,
            output_dir=tmp,
        )

        env_config = {}
        configs = {
            "languages": scaffold_gha.generate_language_config(args.languages, env_config),
            "kubernetes": scaffold_gha.generate_kubernetes_config(args.kubernetes, args.k8s_method, env_config),
            "cicd": scaffold_gha.generate_cicd_config(env_config),
            "build_tools": scaffold_gha.generate_build_tools_config(env_config),
            "code_analysis": scaffold_gha.generate_code_analysis_config(env_config),
            "devops_tools": scaffold_gha.generate_devops_tools_config(env_config),
        }

        import yaml
        workflow_content = scaffold_gha.generate_workflow(args, {}, configs)
        tool_output = yaml.dump(workflow_content, sort_keys=False, Dumper=_NoAliasDumper)
        
        # Enhance response with prompt suggestions
        try:
            enhancer = get_response_enhancer()
            prompt_for_analysis = user_context or f"{languages} {workflow_type} workflow"
            return enhancer.enhance_response(
                tool_name="generate_github_actions_workflow",
                tool_output=tool_output,
                user_prompt=prompt_for_analysis,
            )
        except RuntimeError:
            # Server not initialized yet (e.g., direct testing), return raw output
            return tool_output


# ---------------------------------------------------------------------------
# Tool: generate_jenkins_pipeline
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_jenkins_pipeline(
    name: str = "my-app",
    pipeline_type: str = "complete",
    languages: str = "python",
    kubernetes: bool = False,
    k8s_method: str = "kubectl",
    parameters: bool = False,
    user_context: str = "",
) -> str:
    """Generate a Jenkins Declarative Pipeline (Jenkinsfile) as a string.

    Creates a Jenkins pipeline for Python, JavaScript, Go, Java, or
    multi-language projects with optional Kubernetes deployment.

    Args:
        name: Pipeline/application name (lowercase, alphanumeric + dashes)
        pipeline_type: 'build', 'test', 'deploy', 'complete', or 'parameterized'
        languages: Comma-separated languages (python, javascript, go, java, rust)
        kubernetes: Include Kubernetes deployment stage (default: False)
        k8s_method: 'kubectl', 'kustomize', 'argocd', or 'flux' (default: 'kubectl')
        parameters: Add runtime parameters to pipeline (default: False)
        user_context: Original user prompt/context (optional, used for suggestions)

    Returns:
        Generated Jenkinsfile content as string, optionally with prompt suggestions
        in JSON format if suggestions are enabled

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs("generate_jenkins_pipeline", name=name, languages=languages)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    from devops_os.core import scaffold_jenkins

    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "Jenkinsfile")
        args = _build_jenkins_args(
            name=name,
            pipeline_type=pipeline_type,
            languages=languages,
            kubernetes=kubernetes,
            k8s_method=k8s_method,
            parameters=parameters,
            output_path=out_path,
        )

        env_config = {}
        configs = {
            "languages": scaffold_jenkins.generate_language_config(args.languages, env_config),
            "kubernetes": scaffold_jenkins.generate_kubernetes_config(args.kubernetes, args.k8s_method, env_config),
            "cicd": scaffold_jenkins.generate_cicd_config(env_config),
            "build_tools": scaffold_jenkins.generate_build_tools_config(env_config),
        }

        pipeline_content = scaffold_jenkins.generate_pipeline(args, configs)
        with open(out_path, "w") as fh:
            fh.write(pipeline_content)
        
        # Enhance response with prompt suggestions
        try:
            enhancer = get_response_enhancer()
            prompt_for_analysis = user_context or f"{languages} {pipeline_type} Jenkins pipeline"
            return enhancer.enhance_response(
                tool_name="generate_jenkins_pipeline",
                tool_output=pipeline_content,
                user_prompt=prompt_for_analysis,
            )
        except RuntimeError:
            # Server not initialized yet (e.g., direct testing), return raw output
            return pipeline_content


# ---------------------------------------------------------------------------
# Tool: generate_k8s_config
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_k8s_config(
    app_name: str = "my-app",
    image: str = "myregistry/my-app:latest",
    replicas: int = 2,
    port: int = 8080,
    namespace: str = "default",
    deployment_method: str = "kubectl",
    expose_service: bool = True,
    user_context: str = "",
) -> str:
    """Generate Kubernetes deployment manifests.

    Creates a Kubernetes Deployment with optional Service for a containerized
    application. Supports kubectl, kustomize, Argo CD, and Flux deployment.
    Includes prompt suggestions for follow-up actions.

    Args:
        app_name: Application name for Kubernetes resources (lowercase, alphanumeric + dashes)
        image: Container image reference (e.g., ghcr.io/org/app:v1.0.0)
        replicas: Number of pod replicas (1-100, default: 2)
        port: Container port to expose (1-65535, default: 8080)
        namespace: Kubernetes namespace (lowercase, alphanumeric + dashes, default: default)
        deployment_method: 'kubectl', 'kustomize', 'argocd', or 'flux'
        expose_service: Create ClusterIP Service (default: True)
        user_context: Optional context for generating prompt suggestions

    Returns:
        Kubernetes YAML manifests as multi-document string

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs(
            "generate_k8s_config",
            app_name=app_name,
            image=image,
            replicas=replicas,
            port=port,
            namespace=namespace,
        )
    except ValidationError as e:
        raise ValueError(str(e)) from e
    labels = {"app": app_name}
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": app_name,
            "namespace": namespace,
            "labels": labels,
        },
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": labels},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "containers": [
                        {
                            "name": app_name,
                            "image": image,
                            "ports": [{"containerPort": port}],
                            "resources": {
                                "requests": {"memory": "64Mi", "cpu": "250m"},
                                "limits": {"memory": "128Mi", "cpu": "500m"},
                            },
                        }
                    ]
                },
            },
        },
    }

    import yaml
    manifests = [yaml.dump(deployment, sort_keys=False)]

    if expose_service:
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": app_name, "namespace": namespace, "labels": labels},
            "spec": {
                "selector": labels,
                "ports": [{"protocol": "TCP", "port": port, "targetPort": port}],
                "type": "ClusterIP",
            },
        }
        manifests.append(yaml.dump(service, sort_keys=False))

    if deployment_method == "kustomize":
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": ["deployment.yaml", "service.yaml"] if expose_service else ["deployment.yaml"],
        }
        manifests.append(
            "# kustomization.yaml\n" + yaml.dump(kustomization, sort_keys=False)
        )

    tool_output = "---\n".join(manifests)
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or f"{deployment_method} deployment for {app_name}"
        return enhancer.enhance_response(
            tool_name="generate_k8s_config",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output


# ---------------------------------------------------------------------------
# Tool: scaffold_devcontainer
# ---------------------------------------------------------------------------

@mcp.tool()
def scaffold_devcontainer(
    languages: str = "python",
    cicd_tools: str = "docker,github_actions",
    kubernetes_tools: str = "k9s,kustomize",
    build_tools: str = "",
    code_analysis_tools: str = "",
    devops_tools: str = "",
    python_version: str = "3.12",
    node_version: str = "22",
    java_version: str = "21",
    go_version: str = "1.25.0",
    ruby_version: str = "3.3",
    rust_version: str = "latest",
    user_context: str = "",
) -> str:
    """Generate a devcontainer.json and devcontainer.env.json configuration.

    Creates a production-ready development container configuration for multiple programming
    languages, CI/CD tools, Kubernetes utilities, build systems, and DevOps automation tools.
    Includes intelligent VS Code extension recommendations and port forwarding setup.

    Args:
        languages: Comma-separated languages (python, java, javascript, node, typescript,
                   go, rust, ruby, csharp, php, kotlin, c, cpp)
        cicd_tools: Comma-separated CI/CD tools (docker, podman, terraform, kubectl, helm,
                    github_actions, jenkins, gitlab)
        kubernetes_tools: Comma-separated K8s tools (k9s, kustomize, argocd_cli, flux,
                          lens, kubeseal, kind, minikube, openshift_cli)
        build_tools: Comma-separated build tools (maven, gradle, make, cmake, ant)
        code_analysis_tools: Comma-separated analysis tools (sonarqube, eslint, pylint,
                             checkstyle, pmd)
        devops_tools: Comma-separated DevOps tools (prometheus, grafana, elk, nexus)
        python_version: Python version (default: 3.12)
        node_version: Node.js version (default: 22)
        java_version: Java JDK version (default: 21)
        go_version: Go version (default: 1.25.0)
        ruby_version: Ruby version (default: 3.3)
        rust_version: Rust version (default: latest)
        user_context: Optional context for generating prompt suggestions

    Returns:
        JSON string with 'devcontainer_json' and 'devcontainer_env_json' keys,
        optionally with prompt suggestions for further customization.

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        if languages:
            validate_tool_inputs("scaffold_devcontainer", languages=languages)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    
    # Use new MCP devcontainer module
    from mcp_server.devcontainer_mcp import generate_devcontainer_config
    
    config = generate_devcontainer_config(
        languages=languages,
        cicd_tools=cicd_tools,
        kubernetes_tools=kubernetes_tools,
        build_tools=build_tools,
        code_analysis_tools=code_analysis_tools,
        devops_tools=devops_tools,
        python_version=python_version,
        java_version=java_version,
        node_version=node_version,
        go_version=go_version,
        ruby_version=ruby_version,
        rust_version=rust_version,
    )

    tool_output = json.dumps(
        {
            "devcontainer_json": json.dumps(config["devcontainer_json"], indent=2),
            "devcontainer_env_json": json.dumps(config["devcontainer_env_json"], indent=2),
        },
        indent=2,
    )
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or (
            f"devcontainer with languages: {languages}, "
            f"CI/CD tools: {cicd_tools}, Kubernetes tools: {kubernetes_tools}"
        )
        return enhancer.enhance_response(
            tool_name="scaffold_devcontainer",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output



# ---------------------------------------------------------------------------
# Tool: generate_gitlab_ci_pipeline
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_gitlab_ci_pipeline(
    name: str = "my-app",
    pipeline_type: str = "complete",
    languages: str = "python",
    kubernetes: bool = False,
    k8s_method: str = "kubectl",
    branches: str = "main",
    user_context: str = "",
) -> str:
    """Generate a GitLab CI pipeline (.gitlab-ci.yml) as a YAML string.

    Creates a GitLab CI/CD pipeline for Python, JavaScript, Go, Java, or
    multi-language projects with optional Kubernetes deployment.
    Includes prompt suggestions for pipeline enhancements.

    Args:
        name: Application name for variable APP_NAME and image tags
        pipeline_type: 'build', 'test', 'deploy', or 'complete'
        languages: Comma-separated languages (python, javascript, go, java, rust)
        kubernetes: Include Kubernetes deployment stage (default: False)
        k8s_method: 'kubectl', 'kustomize', 'argocd', or 'flux' (default: kubectl)
        branches: Comma-separated trigger branches (default: main)
        user_context: Optional context for generating prompt suggestions

    Returns:
        Generated .gitlab-ci.yml content as YAML string

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs("generate_gitlab_ci_pipeline", name=name, languages=languages)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    from devops_os.core import scaffold_gitlab
    import yaml

    args = argparse.Namespace(
        name=name,
        type=pipeline_type,
        languages=languages,
        kubernetes=kubernetes,
        k8s_method=k8s_method,
        branches=branches,
        image="docker:24",
        custom_values=None,
    )

    pipeline = scaffold_gitlab.generate_pipeline(args, {})
    tool_output = yaml.dump(pipeline, sort_keys=False, default_flow_style=False)
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or f"{languages} {pipeline_type} GitLab CI pipeline"
        return enhancer.enhance_response(
            tool_name="generate_gitlab_ci_pipeline",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output


# ---------------------------------------------------------------------------
# Tool: generate_argocd_config
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_argocd_config(
    name: str = "my-app",
    method: str = "argocd",
    repo: str = "https://github.com/myorg/my-app.git",
    revision: str = "HEAD",
    path: str = "k8s",
    namespace: str = "default",
    project: str = "default",
    auto_sync: bool = False,
    rollouts: bool = False,
    allow_any_source_repo: bool = False,
    image: str = "ghcr.io/myorg/my-app",
    user_context: str = "",
) -> str:
    """Generate ArgoCD Application + AppProject CRs, or Flux Kustomization resources.

    Creates GitOps configurations for Argo CD or Flux CD based on Git repositories.
    Includes prompt suggestions for GitOps workflow enhancements.

    Args:
        name: Application name (lowercase, alphanumeric + dashes)
        method: GitOps tool 'argocd' or 'flux' (default: argocd)
        repo: Git repository URL with Kubernetes manifests (not validated as URL)
        revision: Git revision/branch/tag to sync (default: HEAD)
        path: Path in repo to manifests directory (default: k8s)
        namespace: Kubernetes namespace (lowercase, alphanumeric + dashes, default: default)
        project: ArgoCD project name (lowercase, alphanumeric + dashes, default: default)
        auto_sync: Enable ArgoCD automated sync (default: False)
        rollouts: Add Argo Rollouts canary Rollout (default: False)
        allow_any_source_repo: Allow AppProject sourceRepos wildcard (default: False)
        image: Container image for Flux image automation
        user_context: Optional context for generating prompt suggestions

    Returns:
        JSON string with generated YAML documents keyed by filename

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs("generate_argocd_config", name=name, namespace=namespace)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    from devops_os.core import scaffold_argocd
    import yaml as _yaml

    args = argparse.Namespace(
        name=name, method=method, repo=repo, revision=revision, path=path,
        namespace=namespace, project=project, auto_sync=auto_sync,
        rollouts=rollouts, allow_any_source_repo=allow_any_source_repo,
        image=image, output_dir=".", custom_values=None,
        server="https://kubernetes.default.svc",
    )

    docs = {}
    if method == "argocd":
        docs["argocd/application.yaml"] = _yaml.dump(
            scaffold_argocd.generate_argocd_application(args), sort_keys=False)
        docs["argocd/appproject.yaml"] = _yaml.dump(
            scaffold_argocd.generate_argocd_appproject(args), sort_keys=False)
        if rollouts:
            docs["argocd/rollout.yaml"] = _yaml.dump(
                scaffold_argocd.generate_argo_rollout(args), sort_keys=False)
    else:
        docs["flux/git-repository.yaml"] = _yaml.dump(
            scaffold_argocd.generate_flux_git_repository(args), sort_keys=False)
        docs["flux/kustomization.yaml"] = _yaml.dump(
            scaffold_argocd.generate_flux_kustomization(args), sort_keys=False)

    tool_output = json.dumps(docs, indent=2)
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or f"{method} GitOps configuration for {name}"
        return enhancer.enhance_response(
            tool_name="generate_argocd_config",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output


# ---------------------------------------------------------------------------
# Tool: generate_sre_configs
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_sre_configs(
    name: str = "my-app",
    team: str = "platform",
    namespace: str = "default",
    slo_type: str = "all",
    slo_target: float = 99.9,
    latency_threshold: float = 0.5,
    slack_channel: str = "#alerts",
    user_context: str = "",
) -> str:
    """Generate SRE configuration files: Prometheus alerts, Grafana dashboards, and SLOs.

    Creates observability and reliability configurations for a Kubernetes service.
    Includes prompt suggestions for SRE workflow improvements.

    Args:
        name: Service name (lowercase, alphanumeric + dashes)
        team: Owning team for alerts and routing (lowercase, alphanumeric + dashes)
        namespace: Kubernetes namespace (lowercase, alphanumeric + dashes, default: default)
        slo_type: 'availability', 'latency', 'error_rate', or 'all' (default: all)
        slo_target: SLO target percentage, 50.0-99.99 (default: 99.9)
        latency_threshold: Latency SLI threshold in seconds (default: 0.5)
        slack_channel: Slack channel for alert routing (default: #alerts)
        user_context: Optional context for generating prompt suggestions

    Returns:
        JSON string with keys: alert_rules_yaml, grafana_dashboard_json, slo_yaml, alertmanager_config_yaml

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs(
            "generate_sre_configs",
            name=name,
            team=team,
            namespace=namespace,
            slo_target=slo_target,
        )
    except ValidationError as e:
        raise ValueError(str(e)) from e
    from devops_os.core import scaffold_sre
    import yaml as _yaml

    args = argparse.Namespace(
        name=name, team=team, namespace=namespace,
        slo_type=slo_type, slo_target=slo_target,
        latency_threshold=latency_threshold,
        slack_channel=slack_channel, pagerduty_key="",
        output_dir=".",
    )

    tool_output = json.dumps(
        {
            "alert_rules_yaml": _yaml.dump(
                scaffold_sre.generate_alert_rules(args), sort_keys=False),
            "grafana_dashboard_json": json.dumps(
                scaffold_sre.generate_grafana_dashboard(args), indent=2),
            "slo_yaml": _yaml.dump(
                scaffold_sre.generate_slo_manifest(args), sort_keys=False),
            "alertmanager_config_yaml": _yaml.dump(
                scaffold_sre.generate_alertmanager_config(args), sort_keys=False),
        },
        indent=2,
    )
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or f"SRE configuration for {name} with {slo_type} SLO"
        return enhancer.enhance_response(
            tool_name="generate_sre_configs",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output



# ---------------------------------------------------------------------------
# Tool: generate_unittest_config
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_unittest_config(
    name: str = "my-app",
    languages: str = "python",
    framework: str = "",
    coverage: bool = True,
    user_context: str = "",
) -> str:
    """Generate unit testing configuration and sample test files.

    Creates testing setup files for Python (pytest), JavaScript/TypeScript
    (Jest/Mocha/Vitest), and Go (go test). Includes prompt suggestions for test improvements.

    Args:
        name: Project name (lowercase, alphanumeric + dashes)
        languages: Comma-separated languages (python, javascript, typescript, go)
        framework: Testing framework override (empty = auto-select per language)
        coverage: Include coverage configuration (default: True)
        user_context: Optional context for generating prompt suggestions

    Returns:
        JSON string with file names as keys and generated file contents as values

    Raises:
        ValueError: If inputs are invalid
    """
    try:
        validate_tool_inputs("generate_unittest_config", project_name=name, languages=languages)
    except ValidationError as e:
        raise ValueError(str(e)) from e
    from devops_os.core import scaffold_unittest

    result = {}

    lang_list = [l.strip().lower() for l in languages.split(",") if l.strip()]
    fw = framework.strip().lower() if framework else ""

    for lang in lang_list:
        if lang not in scaffold_unittest.SUPPORTED_LANGUAGES:
            continue

        resolved_fw = fw if fw else scaffold_unittest.FRAMEWORK_DEFAULTS.get(lang, "")
        is_ts = lang == "typescript"

        if lang == "python":
            result["pytest.ini"] = scaffold_unittest.generate_pytest_ini(name, coverage)
            result["conftest.py"] = scaffold_unittest.generate_conftest_py(name)
            result["tests/__init__.py"] = scaffold_unittest.generate_python_tests_init()
            result["tests/test_sample.py"] = scaffold_unittest.generate_python_test_sample(name)

        elif lang in ("javascript", "typescript"):
            if resolved_fw not in scaffold_unittest.JS_FRAMEWORKS:
                resolved_fw = "jest"
            if resolved_fw == "jest":
                result["jest.config.js"] = scaffold_unittest.generate_jest_config(name, is_ts, coverage)
            elif resolved_fw == "vitest":
                result["vitest.config.js"] = scaffold_unittest.generate_vitest_config(name, coverage)
            elif resolved_fw == "mocha":
                result[".mocharc.js"] = scaffold_unittest.generate_mocha_rc(name, coverage)
            ext = "ts" if is_ts else "js"
            result[f"tests/sample.test.{ext}"] = scaffold_unittest.generate_js_test_sample(
                name, resolved_fw, is_ts
            )

        elif lang == "go":
            pkg = name.replace("-", "_").lower()
            result[f"{pkg}_test.go"] = scaffold_unittest.generate_go_test_sample(name)
            result["Makefile.test"] = scaffold_unittest.generate_go_makefile(name, coverage)

    tool_output = json.dumps(result, indent=2)
    
    # Enhance response with prompt suggestions
    try:
        enhancer = get_response_enhancer()
        prompt_for_analysis = user_context or f"unit testing configuration for {languages}"
        return enhancer.enhance_response(
            tool_name="generate_unittest_config",
            tool_output=tool_output,
            user_prompt=prompt_for_analysis,
        )
    except RuntimeError:
        # Server not initialized yet, return raw output
        return tool_output


# Register tools on the backward-compatibility instance
_register_tools(mcp)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    try:
        # Load configuration from environment (or use defaults for stdio)
        config = Config.from_env()
        
        # Log startup configuration (redacted)
        logger.log_startup(
            transport=config.transport,
            profile=config.profile,
            port=config.port if config.transport in ("sse", "streamable-http") else None,
        )
        
        # For stdio (local), use the global mcp instance
        if config.transport == "stdio":
            mcp.run(transport="stdio")
        
        # For HTTP transports, create a new instance with auth configuration
        elif config.transport in ("sse", "streamable-http"):
            # Create token verifier based on profile (only for remote)
            token_verifier = None
            if config.profile == "remote":
                try:
                    token_verifier = create_token_verifier(
                        profile=config.profile,
                        jwt_issuer=config.jwt_issuer,
                        jwt_audience=config.jwt_audience,
                        jwt_jwks_url=config.jwt_jwks_url,
                        jwt_algorithms=config.jwt_algorithms,
                    )
                except ValueError as e:
                    logger.error(f"Authentication configuration error: {e}")
                    sys.exit(1)
            
            # Create a new FastMCP instance (auth only if remote profile)
            http_mcp_kwargs = {
                "name": "devops-os",
                "instructions": "DevOps Configuration Generator",
                "host": config.host,
                "port": config.port,
                "streamable_http_path": config.mcp_endpoint,
                "max_request_body_size": config.request_size_bytes,
                "log_level": config.log_level,
            }
            
            # Only add token_verifier if remote profile
            if token_verifier is not None:
                http_mcp_kwargs["token_verifier"] = token_verifier
            
            http_mcp = FastMCP(**http_mcp_kwargs)
            
            # Register all tools on the HTTP instance
            _register_tools(http_mcp)
            
            # Run with the selected transport
            http_mcp.run(
                transport=config.transport,
                mount_path=config.mcp_endpoint,
            )
        
        else:
            raise ValueError(f"Unknown transport: {config.transport}")
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.log_shutdown(reason="keyboard_interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
