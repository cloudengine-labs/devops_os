#!/usr/bin/env python3
"""
DevOps-OS Dev Container Config Generator

Generates devcontainer.json and devcontainer.env.json configuration files
for VS Code Dev Containers.  Supports non-interactive usage via command-line
arguments or environment variables, following the same conventions as the
other DevOps-OS scaffold commands.

Outputs (relative to --output-dir):
  .devcontainer/
  ├── devcontainer.json        VS Code dev container configuration
  └── devcontainer.env.json    Tool / language selection & versions
"""

import os
import argparse
import json
from pathlib import Path

ENV_PREFIX = "DEVOPS_OS_DEVCONTAINER_"

# Canonical lists of supported options
ALL_LANGUAGES = [
    "python", "java", "node", "ruby", "csharp", "php",
    "rust", "typescript", "kotlin", "c", "cpp", "javascript", "go",
]
ALL_CICD = [
    "docker", "podman", "terraform", "kubectl", "helm", "github_actions", "jenkins",
]
ALL_KUBERNETES = [
    "k9s", "kustomize", "argocd_cli", "lens", "kubeseal", "flux",
    "kind", "minikube", "openshift_cli",
]
ALL_BUILD_TOOLS = ["gradle", "maven", "ant", "make", "cmake"]
ALL_CODE_ANALYSIS = ["sonarqube", "checkstyle", "pmd", "eslint", "pylint"]
ALL_DEVOPS_TOOLS = ["nexus", "prometheus", "grafana", "elk", "jenkins"]

# Mapping from option name → Dockerfile build-arg name
LANG_ARG_MAP = {
    "python": "INSTALL_PYTHON", "java": "INSTALL_JAVA",
    "node": "INSTALL_JS", "ruby": "INSTALL_RUBY",
    "csharp": "INSTALL_CSHARP", "php": "INSTALL_PHP",
    "rust": "INSTALL_RUST", "typescript": "INSTALL_TYPESCRIPT",
    "kotlin": "INSTALL_KOTLIN", "c": "INSTALL_C",
    "cpp": "INSTALL_CPP", "javascript": "INSTALL_JAVASCRIPT",
    "go": "INSTALL_GO",
}
CICD_ARG_MAP = {
    "docker": "INSTALL_DOCKER", "podman": "INSTALL_PODMAN",
    "terraform": "INSTALL_TERRAFORM",
    "kubectl": "INSTALL_KUBECTL", "helm": "INSTALL_HELM",
    "github_actions": "INSTALL_GITHUB_ACTIONS", "jenkins": "INSTALL_JENKINS",
}
K8S_ARG_MAP = {
    "k9s": "INSTALL_K9S", "kustomize": "INSTALL_KUSTOMIZE",
    "argocd_cli": "INSTALL_ARGOCD_CLI", "lens": "INSTALL_LENS",
    "kubeseal": "INSTALL_KUBESEAL", "flux": "INSTALL_FLUX",
    "kind": "INSTALL_KIND", "minikube": "INSTALL_MINIKUBE",
    "openshift_cli": "INSTALL_OPENSHIFT_CLI",
}
BUILD_ARG_MAP = {
    "gradle": "INSTALL_GRADLE", "maven": "INSTALL_MAVEN",
    "ant": "INSTALL_ANT", "make": "INSTALL_MAKE", "cmake": "INSTALL_CMAKE",
}
ANALYSIS_ARG_MAP = {
    "sonarqube": "INSTALL_SONARQUBE", "checkstyle": "INSTALL_CHECKSTYLE",
    "pmd": "INSTALL_PMD", "eslint": "INSTALL_ESLINT", "pylint": "INSTALL_PYLINT",
}
DEVOPS_ARG_MAP = {
    "nexus": "INSTALL_NEXUS", "prometheus": "INSTALL_PROMETHEUS",
    "grafana": "INSTALL_GRAFANA", "elk": "INSTALL_ELK",
    "jenkins": "INSTALL_JENKINS",
}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    """Parse command line arguments with environment variable fallbacks."""
    parser = argparse.ArgumentParser(
        description="Generate VS Code Dev Container configuration for DevOps-OS",
    )
    parser.add_argument(
        "--languages",
        default=os.environ.get(f"{ENV_PREFIX}LANGUAGES", "python"),
        help="Comma-separated languages to enable (default: python)",
    )
    parser.add_argument(
        "--cicd-tools",
        default=os.environ.get(f"{ENV_PREFIX}CICD_TOOLS", "docker,github_actions"),
        help="Comma-separated CI/CD tools (default: docker,github_actions)",
    )
    parser.add_argument(
        "--kubernetes-tools",
        default=os.environ.get(f"{ENV_PREFIX}KUBERNETES_TOOLS", ""),
        help="Comma-separated Kubernetes tools (default: none)",
    )
    parser.add_argument(
        "--build-tools",
        default=os.environ.get(f"{ENV_PREFIX}BUILD_TOOLS", ""),
        help="Comma-separated build tools (default: none)",
    )
    parser.add_argument(
        "--code-analysis",
        default=os.environ.get(f"{ENV_PREFIX}CODE_ANALYSIS", ""),
        help="Comma-separated code analysis tools (default: none)",
    )
    parser.add_argument(
        "--devops-tools",
        default=os.environ.get(f"{ENV_PREFIX}DEVOPS_TOOLS", ""),
        help="Comma-separated DevOps tools (default: none)",
    )
    # Version overrides
    parser.add_argument("--python-version",
                        default=os.environ.get(f"{ENV_PREFIX}PYTHON_VERSION", "3.11"),
                        help="Python version (default: 3.11)")
    parser.add_argument("--java-version",
                        default=os.environ.get(f"{ENV_PREFIX}JAVA_VERSION", "17"),
                        help="Java JDK version (default: 17)")
    parser.add_argument("--node-version",
                        default=os.environ.get(f"{ENV_PREFIX}NODE_VERSION", "20"),
                        help="Node.js version (default: 20)")
    parser.add_argument("--go-version",
                        default=os.environ.get(f"{ENV_PREFIX}GO_VERSION", "1.21"),
                        help="Go version (default: 1.21)")
    parser.add_argument("--k9s-version",
                        default=os.environ.get(f"{ENV_PREFIX}K9S_VERSION", "0.29.1"),
                        help="K9s version (default: 0.29.1)")
    parser.add_argument("--argocd-version",
                        default=os.environ.get(f"{ENV_PREFIX}ARGOCD_VERSION", "2.8.4"),
                        help="ArgoCD version (default: 2.8.4)")
    parser.add_argument("--flux-version",
                        default=os.environ.get(f"{ENV_PREFIX}FLUX_VERSION", "2.1.2"),
                        help="Flux version (default: 2.1.2)")
    parser.add_argument("--kustomize-version",
                        default=os.environ.get(f"{ENV_PREFIX}KUSTOMIZE_VERSION", "5.2.1"),
                        help="Kustomize version (default: 5.2.1)")
    parser.add_argument("--nexus-version",
                        default=os.environ.get(f"{ENV_PREFIX}NEXUS_VERSION", "3.50.0"),
                        help="Nexus version (default: 3.50.0)")
    parser.add_argument("--prometheus-version",
                        default=os.environ.get(f"{ENV_PREFIX}PROMETHEUS_VERSION", "2.45.0"),
                        help="Prometheus version (default: 2.45.0)")
    parser.add_argument("--grafana-version",
                        default=os.environ.get(f"{ENV_PREFIX}GRAFANA_VERSION", "10.0.0"),
                        help="Grafana version (default: 10.0.0)")
    parser.add_argument(
        "--output-dir",
        default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", "."),
        help="Root output directory (files written to <output-dir>/.devcontainer/)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split(csv_string):
    """Split a comma-separated string into a deduplicated list of tokens."""
    return [t.strip() for t in csv_string.split(",") if t.strip()]


def _bool_flag(value):
    return str(value).lower()


# ---------------------------------------------------------------------------
# Config generators
# ---------------------------------------------------------------------------

def generate_devcontainer_env_json(args):
    """Build the devcontainer.env.json configuration dict."""
    langs = _split(args.languages)
    cicd = _split(args.cicd_tools)
    k8s = _split(args.kubernetes_tools)
    build = _split(args.build_tools)
    analysis = _split(args.code_analysis)
    devops = _split(args.devops_tools)

    versions = {
        "python": args.python_version,
        "java": args.java_version,
        "node": args.node_version,
        "go": args.go_version,
    }
    # Only include tool versions when the corresponding tool is selected
    if "k9s" in k8s:
        versions["k9s"] = args.k9s_version
    if "argocd_cli" in k8s:
        versions["argocd"] = args.argocd_version
    if "flux" in k8s:
        versions["flux"] = args.flux_version
    if "kustomize" in k8s:
        versions["kustomize"] = args.kustomize_version
    if "nexus" in devops:
        versions["nexus"] = args.nexus_version
    if "prometheus" in devops:
        versions["prometheus"] = args.prometheus_version
    if "grafana" in devops:
        versions["grafana"] = args.grafana_version

    return {
        "languages": {lang: lang in langs for lang in ALL_LANGUAGES},
        "cicd": {tool: tool in cicd for tool in ALL_CICD},
        "kubernetes": {tool: tool in k8s for tool in ALL_KUBERNETES},
        "build_tools": {tool: tool in build for tool in ALL_BUILD_TOOLS},
        "code_analysis": {tool: tool in analysis for tool in ALL_CODE_ANALYSIS},
        "devops_tools": {tool: tool in devops for tool in ALL_DEVOPS_TOOLS},
        "versions": versions,
    }


def generate_devcontainer_json(env_config):
    """Build the devcontainer.json dict from a resolved env config."""
    langs = env_config["languages"]
    cicd = env_config["cicd"]
    k8s = env_config["kubernetes"]
    build = env_config["build_tools"]
    analysis = env_config["code_analysis"]
    devops = env_config["devops_tools"]
    versions = env_config["versions"]

    # -- build args --------------------------------------------------------
    build_args = {}
    for opt, arg in LANG_ARG_MAP.items():
        build_args[arg] = _bool_flag(langs.get(opt, False))
    for opt, arg in CICD_ARG_MAP.items():
        build_args[arg] = _bool_flag(cicd.get(opt, False))
    for opt, arg in K8S_ARG_MAP.items():
        build_args[arg] = _bool_flag(k8s.get(opt, False))
    for opt, arg in BUILD_ARG_MAP.items():
        build_args[arg] = _bool_flag(build.get(opt, False))
    for opt, arg in ANALYSIS_ARG_MAP.items():
        build_args[arg] = _bool_flag(analysis.get(opt, False))
    for opt, arg in DEVOPS_ARG_MAP.items():
        build_args[arg] = _bool_flag(devops.get(opt, False))

    # Version build args
    if langs.get("python"):
        build_args["PYTHON_VERSION"] = versions.get("python", "3.11")
    if langs.get("java"):
        build_args["JAVA_VERSION"] = versions.get("java", "17")
    if langs.get("node"):
        build_args["NODE_VERSION"] = versions.get("node", "20")
    if langs.get("go"):
        build_args["GO_VERSION"] = versions.get("go", "1.21")
    if k8s.get("k9s"):
        build_args["K9S_VERSION"] = versions.get("k9s", "0.29.1")
    if k8s.get("argocd_cli"):
        build_args["ARGOCD_VERSION"] = versions.get("argocd", "2.8.4")
    if k8s.get("flux"):
        build_args["FLUX_VERSION"] = versions.get("flux", "2.1.2")
    if k8s.get("kustomize"):
        build_args["KUSTOMIZE_VERSION"] = versions.get("kustomize", "5.2.1")
    if devops.get("nexus"):
        build_args["NEXUS_VERSION"] = versions.get("nexus", "3.50.0")
    if devops.get("prometheus"):
        build_args["PROMETHEUS_VERSION"] = versions.get("prometheus", "2.45.0")
    if devops.get("grafana"):
        build_args["GRAFANA_VERSION"] = versions.get("grafana", "10.0.0")

    # -- extensions --------------------------------------------------------
    extensions = []
    if langs.get("python"):
        extensions += ["ms-python.python", "ms-python.vscode-pylance", "ms-python.black-formatter"]
    if langs.get("java"):
        extensions += ["vscjava.vscode-java-pack", "redhat.java", "vscjava.vscode-maven", "vscjava.vscode-gradle"]
    if langs.get("javascript") or langs.get("node"):
        extensions += ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode", "ms-vscode.vscode-typescript-next"]
    if langs.get("go"):
        extensions.append("golang.go")
    if cicd.get("docker") or cicd.get("podman"):
        extensions.append("ms-azuretools.vscode-docker")  # Docker extension also works with Podman
    if cicd.get("terraform"):
        extensions.append("hashicorp.terraform")
    if cicd.get("kubectl") or cicd.get("helm"):
        extensions.append("ms-kubernetes-tools.vscode-kubernetes-tools")
    if any(k8s.values()):
        if "ms-kubernetes-tools.vscode-kubernetes-tools" not in extensions:
            extensions.append("ms-kubernetes-tools.vscode-kubernetes-tools")
        extensions.append("mindaro.mindaro")
    if k8s.get("argocd_cli"):
        extensions.append("argoproj.argocd-vscode-extension")
    if k8s.get("flux"):
        extensions.append("weaveworks.vscode-gitops-tools")
    if cicd.get("github_actions"):
        extensions.append("github.vscode-github-actions")
    if analysis.get("sonarqube"):
        extensions.append("SonarSource.sonarlint-vscode")
    if analysis.get("pylint") and langs.get("python"):
        extensions.append("ms-python.pylint")
    if devops.get("jenkins"):
        extensions.append("secanis.jenkinsfile-support")
    # General-purpose extensions
    extensions += [
        "github.copilot", "github.copilot-chat",
        "ms-vsliveshare.vsliveshare",
        "streetsidesoftware.code-spell-checker",
        "eamodio.gitlens",
    ]

    # -- forwarded ports ---------------------------------------------------
    forward_ports = []
    if devops.get("nexus"):
        forward_ports.append(8081)
    if devops.get("prometheus"):
        forward_ports.append(9090)
    if devops.get("grafana"):
        forward_ports.append(3000)
    if devops.get("elk"):
        forward_ports.extend([9200, 9300, 5601])
    if devops.get("jenkins"):
        forward_ports.append(8080)

    devcontainer = {
        "name": "DevOps OS - Multi-Language Development Environment",
        "build": {"dockerfile": "Dockerfile", "args": build_args},
        "mounts": ["source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"],
        "customizations": {"vscode": {"extensions": extensions}},
    }
    if forward_ports:
        devcontainer["forwardPorts"] = forward_ports
    if any(k8s.values()):
        devcontainer["postCreateCommand"] = (
            "chmod +x /workspaces/.devcontainer/k8s-config-generator.py "
            "&& ln -sf /workspaces/.devcontainer/k8s-config-generator.py "
            "/usr/local/bin/k8s-config-generator"
        )

    return devcontainer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    output_root = Path(args.output_dir) / ".devcontainer"
    output_root.mkdir(parents=True, exist_ok=True)

    env_config = generate_devcontainer_env_json(args)
    env_json_path = output_root / "devcontainer.env.json"
    with open(env_json_path, "w") as fh:
        json.dump(env_config, fh, indent=2)

    devcontainer = generate_devcontainer_json(env_config)
    dc_json_path = output_root / "devcontainer.json"
    with open(dc_json_path, "w") as fh:
        json.dump(devcontainer, fh, indent=2)

    print("Dev container configuration generated:")
    print(f"  {env_json_path}")
    print(f"  {dc_json_path}")


if __name__ == "__main__":
    main()
