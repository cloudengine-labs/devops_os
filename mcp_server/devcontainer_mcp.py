"""
DevOps-OS MCP Dev Container Module

Provides MCP tools for generating dev container configurations with support for
multiple programming languages, CI/CD tools, Kubernetes utilities, and automation
frameworks. Designed for seamless AI integration with Claude, ChatGPT, and other
MCP-compatible assistants.

Features:
- Multi-language support (Python, Java, Go, Node.js, Rust, C/C++, Ruby, etc.)
- CI/CD tool integration (Docker, GitHub Actions, Jenkins, GitLab, ArgoCD, Flux)
- Kubernetes tools (kubectl, Helm, K9s, Kustomize, KinD, Minikube)
- Build systems (Maven, Gradle, npm, pip, Go modules, Cargo)
- Code analysis & linting (SonarQube, ESLint, Pylint, Checkstyle)
- DevOps & observability (Prometheus, Grafana, ELK Stack)
- Language-specific version management
- Automated VS Code extension recommendations
- Port forwarding configuration
"""

import json
from typing import Any, Dict, List


# ============================================================================
# Language Configuration Database
# ============================================================================

LANGUAGE_CONFIGS = {
    "python": {
        "extensions": ["ms-python.python", "ms-python.vscode-pylance", "ms-python.black-formatter"],
        "default_version": "3.12",
        "version_env_var": "PYTHON_VERSION",
        "docker_arg": "INSTALL_PYTHON",
    },
    "java": {
        "extensions": ["vscjava.vscode-java-pack", "redhat.java", "vscjava.vscode-maven", "vscjava.vscode-gradle"],
        "default_version": "21",
        "version_env_var": "JAVA_VERSION",
        "docker_arg": "INSTALL_JAVA",
    },
    "go": {
        "extensions": ["golang.go", "golang.go-nightly"],
        "default_version": "1.25.0",
        "version_env_var": "GO_VERSION",
        "docker_arg": "INSTALL_GO",
    },
    "node": {
        "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"],
        "default_version": "22",
        "version_env_var": "NODE_VERSION",
        "docker_arg": "INSTALL_JS",
    },
    "javascript": {
        "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"],
        "default_version": "22",
        "version_env_var": "NODE_VERSION",
        "docker_arg": "INSTALL_JS",
    },
    "typescript": {
        "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode", "ms-vscode.vscode-typescript-next"],
        "default_version": "22",
        "version_env_var": "NODE_VERSION",
        "docker_arg": "INSTALL_TYPESCRIPT",
    },
    "rust": {
        "extensions": ["rust-lang.rust-analyzer", "serayuzgur.crates"],
        "default_version": "latest",
        "version_env_var": "RUST_VERSION",
        "docker_arg": "INSTALL_RUST",
    },
    "ruby": {
        "extensions": ["rebornix.ruby", "ruby-syntax-tree.vscode-syntax-tree"],
        "default_version": "3.3",
        "version_env_var": "RUBY_VERSION",
        "docker_arg": "INSTALL_RUBY",
    },
    "csharp": {
        "extensions": ["ms-dotnettools.csharp", "ms-dotnettools.vscode-dotnet-runtime"],
        "default_version": "8.0",
        "version_env_var": "CSHARP_VERSION",
        "docker_arg": "INSTALL_CSHARP",
    },
    "php": {
        "extensions": ["bmewburn.vscode-intelephense-client", "felixbecker.php-debug"],
        "default_version": "8.3",
        "version_env_var": "PHP_VERSION",
        "docker_arg": "INSTALL_PHP",
    },
    "c": {
        "extensions": ["ms-vscode.cpptools", "ms-vscode.cmake-tools"],
        "default_version": "latest",
        "version_env_var": "C_VERSION",
        "docker_arg": "INSTALL_C",
    },
    "cpp": {
        "extensions": ["ms-vscode.cpptools", "ms-vscode.cmake-tools", "vector-of-bool.cmake-tools"],
        "default_version": "latest",
        "version_env_var": "CPP_VERSION",
        "docker_arg": "INSTALL_CPP",
    },
    "kotlin": {
        "extensions": ["fwcd.kotlin"],
        "default_version": "latest",
        "version_env_var": "KOTLIN_VERSION",
        "docker_arg": "INSTALL_KOTLIN",
    },
}

# ============================================================================
# CI/CD Tools Configuration
# ============================================================================

CICD_TOOLS = {
    "docker": {
        "extensions": ["ms-azuretools.vscode-docker"],
        "ports": [],
        "docker_arg": "INSTALL_DOCKER",
    },
    "podman": {
        "extensions": ["ms-azuretools.vscode-docker"],  # Docker extension also works with Podman
        "ports": [],
        "docker_arg": "INSTALL_PODMAN",
    },
    "github_actions": {
        "extensions": ["github.vscode-github-actions"],
        "ports": [],
        "docker_arg": "INSTALL_GITHUB_ACTIONS",
    },
    "jenkins": {
        "extensions": ["secanis.jenkinsfile-support"],
        "ports": [8080],
        "docker_arg": "INSTALL_JENKINS",
    },
    "gitlab": {
        "extensions": ["gitlab.gitlab-workflow"],
        "ports": [],
        "docker_arg": "INSTALL_GITLAB",
    },
    "terraform": {
        "extensions": ["hashicorp.terraform"],
        "ports": [],
        "docker_arg": "INSTALL_TERRAFORM",
    },
    "kubectl": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_KUBECTL",
    },
    "helm": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_HELM",
    },
}

# ============================================================================
# Kubernetes Tools Configuration
# ============================================================================

KUBERNETES_TOOLS = {
    "k9s": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_K9S",
        "version_env_var": "K9S_VERSION",
        "default_version": "0.50.16",
    },
    "kustomize": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_KUSTOMIZE",
        "version_env_var": "KUSTOMIZE_VERSION",
        "default_version": "5.8.0",
    },
    "argocd_cli": {
        "extensions": ["argoproj.argocd-vscode-extension"],
        "ports": [],
        "docker_arg": "INSTALL_ARGOCD_CLI",
        "version_env_var": "ARGOCD_VERSION",
        "default_version": "3.3.6",
    },
    "flux": {
        "extensions": ["weaveworks.vscode-gitops-tools"],
        "ports": [],
        "docker_arg": "INSTALL_FLUX",
        "version_env_var": "FLUX_VERSION",
        "default_version": "2.8.5",
    },
    "lens": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_LENS",
    },
    "kubeseal": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_KUBESEAL",
    },
    "kind": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_KIND",
    },
    "minikube": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_MINIKUBE",
    },
    "openshift_cli": {
        "extensions": ["ms-kubernetes-tools.vscode-kubernetes-tools"],
        "ports": [],
        "docker_arg": "INSTALL_OPENSHIFT_CLI",
    },
}

# ============================================================================
# Build Tools Configuration
# ============================================================================

BUILD_TOOLS = {
    "maven": {
        "extensions": ["vscjava.vscode-maven"],
        "docker_arg": "INSTALL_MAVEN",
    },
    "gradle": {
        "extensions": ["vscjava.vscode-gradle"],
        "docker_arg": "INSTALL_GRADLE",
    },
    "make": {
        "extensions": [],
        "docker_arg": "INSTALL_MAKE",
    },
    "cmake": {
        "extensions": ["ms-vscode.cmake-tools"],
        "docker_arg": "INSTALL_CMAKE",
    },
    "ant": {
        "extensions": [],
        "docker_arg": "INSTALL_ANT",
    },
}

# ============================================================================
# Code Analysis Tools Configuration
# ============================================================================

CODE_ANALYSIS_TOOLS = {
    "sonarqube": {
        "extensions": ["SonarSource.sonarlint-vscode"],
        "docker_arg": "INSTALL_SONARQUBE",
    },
    "eslint": {
        "extensions": ["dbaeumer.vscode-eslint"],
        "docker_arg": "INSTALL_ESLINT",
    },
    "pylint": {
        "extensions": ["ms-python.pylint"],
        "docker_arg": "INSTALL_PYLINT",
    },
    "checkstyle": {
        "extensions": [],
        "docker_arg": "INSTALL_CHECKSTYLE",
    },
    "pmd": {
        "extensions": [],
        "docker_arg": "INSTALL_PMD",
    },
}

# ============================================================================
# DevOps & Observability Tools Configuration
# ============================================================================

DEVOPS_TOOLS = {
    "prometheus": {
        "extensions": [],
        "ports": [9090],
        "docker_arg": "INSTALL_PROMETHEUS",
        "version_env_var": "PROMETHEUS_VERSION",
        "default_version": "3.5.1",
    },
    "grafana": {
        "extensions": [],
        "ports": [3000],
        "docker_arg": "INSTALL_GRAFANA",
        "version_env_var": "GRAFANA_VERSION",
        "default_version": "12.4.2",
    },
    "elk": {
        "extensions": [],
        "ports": [9200, 9300, 5601],
        "docker_arg": "INSTALL_ELK",
    },
    "nexus": {
        "extensions": [],
        "ports": [8081],
        "docker_arg": "INSTALL_NEXUS",
        "version_env_var": "NEXUS_VERSION",
        "default_version": "3.91.0",
    },
}

# ============================================================================
# Core MCP Functions
# ============================================================================


def parse_comma_separated(value: str) -> List[str]:
    """Parse comma-separated string into list of tokens."""
    if not value:
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


def get_recommended_extensions(
    languages: List[str],
    cicd_tools: List[str],
    kubernetes_tools: List[str],
    build_tools: List[str],
    code_analysis_tools: List[str],
    devops_tools: List[str],
) -> List[str]:
    """Generate list of recommended VS Code extensions."""
    extensions = set()

    # Language extensions
    for lang in languages:
        if lang in LANGUAGE_CONFIGS:
            extensions.update(LANGUAGE_CONFIGS[lang]["extensions"])

    # CI/CD tool extensions
    for tool in cicd_tools:
        if tool in CICD_TOOLS:
            extensions.update(CICD_TOOLS[tool]["extensions"])

    # Kubernetes tool extensions
    for tool in kubernetes_tools:
        if tool in KUBERNETES_TOOLS:
            extensions.update(KUBERNETES_TOOLS[tool]["extensions"])

    # Build tool extensions
    for tool in build_tools:
        if tool in BUILD_TOOLS:
            extensions.update(BUILD_TOOLS[tool]["extensions"])

    # Code analysis tool extensions
    for tool in code_analysis_tools:
        if tool in CODE_ANALYSIS_TOOLS:
            extensions.update(CODE_ANALYSIS_TOOLS[tool]["extensions"])

    # DevOps tool extensions
    for tool in devops_tools:
        if tool in DEVOPS_TOOLS:
            extensions.update(DEVOPS_TOOLS[tool]["extensions"])

    # Add general-purpose extensions
    general_extensions = [
        "github.copilot",
        "github.copilot-chat",
        "ms-vsliveshare.vsliveshare",
        "streetsidesoftware.code-spell-checker",
        "eamodio.gitlens",
        "ms-vscode.remote-explorer",
        "ms-vscode-remote.remote-containers",
    ]
    extensions.update(general_extensions)

    return sorted(list(extensions))


def get_forwarded_ports(
    cicd_tools: List[str],
    kubernetes_tools: List[str],
    devops_tools: List[str],
) -> List[int]:
    """Generate list of ports to forward in devcontainer."""
    ports = set()

    for tool in cicd_tools:
        if tool in CICD_TOOLS:
            ports.update(CICD_TOOLS[tool]["ports"])

    for tool in kubernetes_tools:
        if tool in KUBERNETES_TOOLS:
            ports.update(KUBERNETES_TOOLS[tool]["ports"])

    for tool in devops_tools:
        if tool in DEVOPS_TOOLS:
            ports.update(DEVOPS_TOOLS[tool]["ports"])

    return sorted(list(ports))


def get_docker_build_args(
    languages: List[str],
    cicd_tools: List[str],
    kubernetes_tools: List[str],
    build_tools: List[str],
    code_analysis_tools: List[str],
    devops_tools: List[str],
    language_versions: Dict[str, str],
) -> Dict[str, str]:
    """Generate Docker build arguments."""
    build_args = {}

    # Language build args and versions
    for lang in languages:
        if lang in LANGUAGE_CONFIGS:
            build_args[LANGUAGE_CONFIGS[lang]["docker_arg"]] = "true"
            version_key = LANGUAGE_CONFIGS[lang]["version_env_var"]
            default_version = LANGUAGE_CONFIGS[lang]["default_version"]
            build_args[version_key] = language_versions.get(lang, default_version)

    # CI/CD tool build args
    for tool in cicd_tools:
        if tool in CICD_TOOLS:
            build_args[CICD_TOOLS[tool]["docker_arg"]] = "true"

    # Kubernetes tool build args
    for tool in kubernetes_tools:
        if tool in KUBERNETES_TOOLS:
            build_args[KUBERNETES_TOOLS[tool]["docker_arg"]] = "true"
            if "version_env_var" in KUBERNETES_TOOLS[tool]:
                version_key = KUBERNETES_TOOLS[tool]["version_env_var"]
                default_version = KUBERNETES_TOOLS[tool]["default_version"]
                build_args[version_key] = language_versions.get(tool, default_version)

    # Build tools build args
    for tool in build_tools:
        if tool in BUILD_TOOLS:
            build_args[BUILD_TOOLS[tool]["docker_arg"]] = "true"

    # Code analysis tools build args
    for tool in code_analysis_tools:
        if tool in CODE_ANALYSIS_TOOLS:
            build_args[CODE_ANALYSIS_TOOLS[tool]["docker_arg"]] = "true"

    # DevOps tools build args
    for tool in devops_tools:
        if tool in DEVOPS_TOOLS:
            build_args[DEVOPS_TOOLS[tool]["docker_arg"]] = "true"
            if "version_env_var" in DEVOPS_TOOLS[tool]:
                version_key = DEVOPS_TOOLS[tool]["version_env_var"]
                default_version = DEVOPS_TOOLS[tool]["default_version"]
                build_args[version_key] = language_versions.get(tool, default_version)

    return build_args


def generate_devcontainer_config(
    languages: str = "python",
    cicd_tools: str = "docker,github_actions",
    kubernetes_tools: str = "k9s,kustomize",
    build_tools: str = "",
    code_analysis_tools: str = "",
    devops_tools: str = "",
    python_version: str = "3.12",
    java_version: str = "21",
    node_version: str = "22",
    go_version: str = "1.25.0",
    ruby_version: str = "3.3",
    rust_version: str = "latest",
) -> Dict[str, Any]:
    """
    Generate a complete devcontainer configuration.

    Returns a dict with 'devcontainer_json' and 'devcontainer_env_json' keys,
    suitable for writing to .devcontainer/ files.
    """
    # Parse inputs
    langs = parse_comma_separated(languages)
    cicd = parse_comma_separated(cicd_tools)
    k8s = parse_comma_separated(kubernetes_tools)
    build = parse_comma_separated(build_tools)
    analysis = parse_comma_separated(code_analysis_tools)
    devops = parse_comma_separated(devops_tools)

    # Language versions mapping
    language_versions = {
        "python": python_version,
        "java": java_version,
        "node": node_version,
        "javascript": node_version,
        "typescript": node_version,
        "go": go_version,
        "ruby": ruby_version,
        "rust": rust_version,
    }

    # Generate extensions list
    extensions = get_recommended_extensions(langs, cicd, k8s, build, analysis, devops)

    # Generate forwarded ports
    ports = get_forwarded_ports(cicd, k8s, devops)

    # Generate Docker build args
    build_args = get_docker_build_args(langs, cicd, k8s, build, analysis, devops, language_versions)

    # Build devcontainer.json
    devcontainer_json = {
        "name": "DevOps OS - Multi-Language Development Environment",
        "build": {
            "dockerfile": "Dockerfile",
            "args": build_args,
        },
        "mounts": ["source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"],
        "customizations": {
            "vscode": {
                "extensions": extensions,
            },
        },
    }

    if ports:
        devcontainer_json["forwardPorts"] = ports

    if any(k8s):
        devcontainer_json["postCreateCommand"] = (
            "chmod +x /workspaces/.devcontainer/k8s-config-generator.py "
            "&& ln -sf /workspaces/.devcontainer/k8s-config-generator.py "
            "/usr/local/bin/k8s-config-generator"
        )

    # Build devcontainer.env.json
    all_languages = list(LANGUAGE_CONFIGS.keys())
    all_cicd = list(CICD_TOOLS.keys())
    all_kubernetes = list(KUBERNETES_TOOLS.keys())
    all_build = list(BUILD_TOOLS.keys())
    all_analysis = list(CODE_ANALYSIS_TOOLS.keys())
    all_devops = list(DEVOPS_TOOLS.keys())

    devcontainer_env_json = {
        "languages": {lang: lang in langs for lang in all_languages},
        "cicd": {tool: tool in cicd for tool in all_cicd},
        "kubernetes": {tool: tool in k8s for tool in all_kubernetes},
        "build_tools": {tool: tool in build for tool in all_build},
        "code_analysis": {tool: tool in analysis for tool in all_analysis},
        "devops_tools": {tool: tool in devops for tool in all_devops},
        "versions": language_versions,
    }

    return {
        "devcontainer_json": devcontainer_json,
        "devcontainer_env_json": devcontainer_env_json,
    }


def get_language_recommendations(languages: str = "") -> Dict[str, Any]:
    """Get detailed recommendations for selected languages."""
    langs = parse_comma_separated(languages)
    recommendations = {}

    for lang in langs:
        if lang in LANGUAGE_CONFIGS:
            config = LANGUAGE_CONFIGS[lang]
            recommendations[lang] = {
                "extensions": config["extensions"],
                "default_version": config["default_version"],
                "docker_arg": config["docker_arg"],
            }

    return recommendations


def get_available_tools() -> Dict[str, Any]:
    """Get all available tools and their configurations."""
    return {
        "languages": list(LANGUAGE_CONFIGS.keys()),
        "cicd_tools": list(CICD_TOOLS.keys()),
        "kubernetes_tools": list(KUBERNETES_TOOLS.keys()),
        "build_tools": list(BUILD_TOOLS.keys()),
        "code_analysis_tools": list(CODE_ANALYSIS_TOOLS.keys()),
        "devops_tools": list(DEVOPS_TOOLS.keys()),
    }
