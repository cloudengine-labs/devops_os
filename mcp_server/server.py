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
from pathlib import Path
from typing import Any

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP

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
# MCP Server
# ---------------------------------------------------------------------------

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
) -> str:
    """
    Generate a GitHub Actions CI/CD workflow YAML file.

    Args:
        name: Workflow / application name (used in filename and job names).
        workflow_type: One of 'build', 'test', 'deploy', 'complete', 'reusable'.
        languages: Comma-separated list of languages, e.g. 'python,javascript,go,java'.
        kubernetes: Include a Kubernetes deployment stage.
        k8s_method: Kubernetes deployment method — 'kubectl', 'kustomize', 'argocd', or 'flux'.
        branches: Comma-separated list of trigger branches (default 'main').
        matrix: Enable matrix builds across platforms.

    Returns:
        Generated GitHub Actions workflow as a YAML string.
    """
    from cli import scaffold_gha

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
        return yaml.dump(workflow_content, sort_keys=False)


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
) -> str:
    """
    Generate a Jenkins Declarative Pipeline (Jenkinsfile) as a string.

    Args:
        name: Pipeline / application name.
        pipeline_type: One of 'build', 'test', 'deploy', 'complete', 'parameterized'.
        languages: Comma-separated list of languages, e.g. 'python,java'.
        kubernetes: Include a Kubernetes deployment stage.
        k8s_method: Kubernetes deployment method — 'kubectl', 'kustomize', 'argocd', or 'flux'.
        parameters: Add runtime parameters to the pipeline.

    Returns:
        Generated Jenkinsfile content as a string.
    """
    from cli import scaffold_jenkins

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
        # write & read back to normalise line endings
        with open(out_path, "w") as fh:
            fh.write(pipeline_content)
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
) -> str:
    """
    Generate Kubernetes deployment manifests.

    Args:
        app_name: Name of the application / Kubernetes resource.
        image: Container image reference (registry/name:tag).
        replicas: Number of pod replicas.
        port: Container port to expose.
        namespace: Kubernetes namespace to deploy into.
        deployment_method: One of 'kubectl', 'kustomize', 'argocd', 'flux'.
        expose_service: Create a ClusterIP Service alongside the Deployment.

    Returns:
        Kubernetes YAML manifests as a single multi-document string.
    """
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

    return "---\n".join(manifests)


# ---------------------------------------------------------------------------
# Tool: scaffold_devcontainer
# ---------------------------------------------------------------------------

@mcp.tool()
def scaffold_devcontainer(
    languages: str = "python",
    cicd_tools: str = "docker,github_actions",
    kubernetes_tools: str = "k9s,kustomize",
    python_version: str = "3.11",
    node_version: str = "20",
    java_version: str = "17",
    go_version: str = "1.21",
) -> str:
    """
    Generate a devcontainer.json and devcontainer.env.json configuration.

    Args:
        languages: Comma-separated list of languages to install
                   (python, java, javascript, typescript, go, rust, csharp,
                    php, kotlin, c, cpp, ruby).
        cicd_tools: Comma-separated list of CI/CD tools
                    (docker, terraform, kubectl, helm, github_actions, jenkins).
        kubernetes_tools: Comma-separated list of Kubernetes tools
                          (k9s, kustomize, argocd_cli, lens, kubeseal, flux,
                           kind, minikube, openshift_cli).
        python_version: Python version (default '3.11').
        node_version: Node.js version (default '20').
        java_version: Java JDK version (default '17').
        go_version: Go version (default '1.21').

    Returns:
        A JSON string with two keys: 'devcontainer_json' and 'devcontainer_env_json'.
    """
    lang_list = [l.strip() for l in languages.split(",") if l.strip()]
    cicd_list = [t.strip() for t in cicd_tools.split(",") if t.strip()]
    k8s_list = [t.strip() for t in kubernetes_tools.split(",") if t.strip()]

    all_languages = ["python", "java", "javascript", "go", "rust", "csharp", "php",
                     "typescript", "kotlin", "c", "cpp", "ruby"]
    all_cicd = ["docker", "terraform", "kubectl", "helm", "github_actions", "jenkins"]
    all_k8s = ["k9s", "kustomize", "argocd_cli", "lens", "kubeseal", "flux",
               "kind", "minikube", "openshift_cli"]

    env_json: dict[str, Any] = {
        "languages": {lang: lang in lang_list for lang in all_languages},
        "cicd": {tool: tool in cicd_list for tool in all_cicd},
        "kubernetes": {tool: tool in k8s_list for tool in all_k8s},
        "versions": {
            "python": python_version,
            "java": java_version,
            "node": node_version,
            "go": go_version,
        },
    }

    extensions = [
        "ms-python.python",
        "ms-azuretools.vscode-docker",
        "redhat.vscode-yaml",
    ]
    if "java" in lang_list:
        extensions += ["redhat.java", "vscjava.vscode-java-debug"]
    if "javascript" in lang_list or "typescript" in lang_list:
        extensions.append("dbaeumer.vscode-eslint")
    if "go" in lang_list:
        extensions.append("golang.go")
    if "terraform" in cicd_list:
        extensions.append("hashicorp.terraform")
    if k8s_list:
        extensions.append("ms-kubernetes-tools.vscode-kubernetes-tools")

    devcontainer_json = {
        "name": "DevOps-OS",
        "build": {
            "dockerfile": "Dockerfile",
            "context": ".",
            "args": {
                f"INSTALL_{lang.upper()}": str(lang in lang_list).lower()
                for lang in all_languages
            },
        },
        "runArgs": ["--init", "--privileged"],
        "overrideCommand": False,
        "customizations": {"vscode": {"extensions": extensions}},
        "mounts": [
            "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
        ],
        "postCreateCommand": "python3 .devcontainer/configure.py",
    }

    return json.dumps(
        {
            "devcontainer_json": json.dumps(devcontainer_json, indent=2),
            "devcontainer_env_json": json.dumps(env_json, indent=2),
        },
        indent=2,
    )



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
) -> str:
    """
    Generate a GitLab CI pipeline (.gitlab-ci.yml) as a YAML string.

    Args:
        name: Application name (used in variable APP_NAME and image tags).
        pipeline_type: One of 'build', 'test', 'deploy', 'complete'.
        languages: Comma-separated list of languages, e.g. 'python,javascript,go,java'.
        kubernetes: Include a Kubernetes deployment stage.
        k8s_method: Kubernetes deployment method — 'kubectl', 'kustomize', 'argocd', or 'flux'.
        branches: Comma-separated list of branches that trigger deploy jobs.

    Returns:
        Generated .gitlab-ci.yml content as a YAML string.
    """
    from cli import scaffold_gitlab
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
    return yaml.dump(pipeline, sort_keys=False, default_flow_style=False)


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
    image: str = "ghcr.io/myorg/my-app",
) -> str:
    """
    Generate ArgoCD Application + AppProject CRs, or Flux Kustomization resources.

    Args:
        name: Application name.
        method: GitOps tool — 'argocd' or 'flux'.
        repo: Git repository URL containing the Kubernetes manifests.
        revision: Git revision / branch / tag to sync (default 'HEAD').
        path: Path inside the repo to the manifests directory.
        namespace: Kubernetes namespace to deploy into.
        project: ArgoCD project name.
        auto_sync: Enable ArgoCD automated sync (prune + self-heal).
        rollouts: Add an Argo Rollouts canary Rollout resource.
        image: Container image for Flux image automation.

    Returns:
        JSON string with generated YAML documents keyed by filename.
    """
    from cli import scaffold_argocd
    import yaml as _yaml

    args = argparse.Namespace(
        name=name, method=method, repo=repo, revision=revision, path=path,
        namespace=namespace, project=project, auto_sync=auto_sync,
        rollouts=rollouts, image=image, output_dir=".", custom_values=None,
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

    return json.dumps(docs, indent=2)


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
) -> str:
    """
    Generate SRE configuration files: Prometheus alert rules, Grafana dashboard,
    SLO manifest, and Alertmanager routing config.

    Args:
        name: Application / service name.
        team: Owning team (used in alert labels and routing).
        namespace: Kubernetes namespace where the app runs.
        slo_type: Which SLOs to generate — 'availability', 'latency', 'error_rate', or 'all'.
        slo_target: SLO target percentage, e.g. 99.9.
        latency_threshold: Latency SLI threshold in seconds (default 0.5).
        slack_channel: Slack channel for alert routing.

    Returns:
        JSON string with keys 'alert_rules_yaml', 'grafana_dashboard_json',
        'slo_yaml', 'alertmanager_config_yaml'.
    """
    from cli import scaffold_sre
    import yaml as _yaml

    args = argparse.Namespace(
        name=name, team=team, namespace=namespace,
        slo_type=slo_type, slo_target=slo_target,
        latency_threshold=latency_threshold,
        slack_channel=slack_channel, pagerduty_key="",
        output_dir=".",
    )

    return json.dumps(
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
