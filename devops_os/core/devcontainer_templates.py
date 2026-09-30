#!/usr/bin/env python3
"""Template-backed devcontainer generation helpers used by ``devopsos init`` only.

This module intentionally supports the `init` flow and should not be used to
change the public contract of `scaffold devcontainer`, which remains on its
legacy generator path for backward compatibility.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "devcontainer"

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

DEFAULT_VERSIONS = {
    "python": "3.12",
    "java": "21",
    "node": "22",
    "go": "1.25.0",
    "nexus": "3.91.0",
    "prometheus": "3.5.1",
    "grafana": "12.4.2",
    "k9s": "0.50.16",
    "argocd": "3.3.6",
    "flux": "2.8.5",
    "kustomize": "5.8.0",
    "jenkins": "2.440.1",
}

FEATURE_REFS = {
    "python": "ghcr.io/devcontainers/features/python:1",
    "java": "ghcr.io/devcontainers/features/java:1",
    "node": "ghcr.io/devcontainers/features/node:1",
    "go": "ghcr.io/devcontainers/features/go:1",
    "ruby": "ghcr.io/devcontainers/features/ruby:1",
    "php": "ghcr.io/devcontainers/features/php:1",
    "rust": "ghcr.io/devcontainers/features/rust:1",
}

BUILD_ARG_FACTORIES = {
    "INSTALL_CSHARP": lambda c: c["languages"]["csharp"],
    "INSTALL_KOTLIN": lambda c: c["languages"]["kotlin"],
    "INSTALL_C": lambda c: c["languages"]["c"],
    "INSTALL_CPP": lambda c: c["languages"]["cpp"],
    "INSTALL_DOCKER": lambda c: c["cicd"]["docker"],
    "INSTALL_PODMAN": lambda c: c["cicd"].get("podman", False),
    "INSTALL_TERRAFORM": lambda c: c["cicd"]["terraform"],
    "INSTALL_KUBECTL": lambda c: c["cicd"]["kubectl"],
    "INSTALL_HELM": lambda c: c["cicd"]["helm"],
    "INSTALL_GITHUB_ACTIONS": lambda c: c["cicd"]["github_actions"],
    "INSTALL_K9S": lambda c: c["kubernetes"]["k9s"],
    "INSTALL_KUSTOMIZE": lambda c: c["kubernetes"]["kustomize"],
    "INSTALL_ARGOCD_CLI": lambda c: c["kubernetes"]["argocd_cli"],
    "INSTALL_LENS": lambda c: c["kubernetes"]["lens"],
    "INSTALL_KUBESEAL": lambda c: c["kubernetes"]["kubeseal"],
    "INSTALL_FLUX": lambda c: c["kubernetes"]["flux"],
    "INSTALL_KIND": lambda c: c["kubernetes"]["kind"],
    "INSTALL_MINIKUBE": lambda c: c["kubernetes"]["minikube"],
    "INSTALL_OPENSHIFT_CLI": lambda c: c["kubernetes"]["openshift_cli"],
    "INSTALL_MAKE": lambda c: c["build_tools"]["make"],
    "INSTALL_CMAKE": lambda c: c["build_tools"]["cmake"],
    "INSTALL_SONARQUBE": lambda c: c["code_analysis"]["sonarqube"],
    "INSTALL_CHECKSTYLE": lambda c: c["code_analysis"]["checkstyle"],
    "INSTALL_PMD": lambda c: c["code_analysis"]["pmd"],
    "INSTALL_NEXUS": lambda c: c["devops_tools"]["nexus"],
    "INSTALL_PROMETHEUS": lambda c: c["devops_tools"]["prometheus"],
    "INSTALL_GRAFANA": lambda c: c["devops_tools"]["grafana"],
    "INSTALL_ELK": lambda c: c["devops_tools"]["elk"],
    "INSTALL_JENKINS": lambda c: c["devops_tools"]["jenkins"],
}

VERSION_ARG_FACTORIES = {
    "JAVA_VERSION": lambda c: c["versions"].get("java", DEFAULT_VERSIONS["java"]) if java_feature_enabled(c) or c["devops_tools"]["nexus"] else None,
    "TERRAFORM_VERSION": lambda c: "1.14.7" if c["cicd"]["terraform"] else None,
    "HELM_VERSION": lambda c: "4.0.1" if c["cicd"]["helm"] else None,
    "ACTIONS_RUNNER_VERSION": lambda c: "2.330.0" if c["cicd"]["github_actions"] else None,
    "K9S_VERSION": lambda c: c["versions"].get("k9s", DEFAULT_VERSIONS["k9s"]) if c["kubernetes"]["k9s"] else None,
    "KUSTOMIZE_VERSION": lambda c: c["versions"].get("kustomize", DEFAULT_VERSIONS["kustomize"]) if c["kubernetes"]["kustomize"] else None,
    "ARGOCD_VERSION": lambda c: c["versions"].get("argocd", DEFAULT_VERSIONS["argocd"]) if c["kubernetes"]["argocd_cli"] else None,
    "FLUX_VERSION": lambda c: c["versions"].get("flux", DEFAULT_VERSIONS["flux"]) if c["kubernetes"]["flux"] else None,
    "KUBESEAL_VERSION": lambda c: "0.33.1" if c["kubernetes"]["kubeseal"] else None,
    "KIND_VERSION": lambda c: "0.31.0" if c["kubernetes"]["kind"] else None,
    "MINIKUBE_VERSION": lambda c: "1.37.0" if c["kubernetes"]["minikube"] else None,
    "SONAR_SCANNER_VERSION": lambda c: "8.0.1.6346" if c["code_analysis"]["sonarqube"] else None,
    "CHECKSTYLE_VERSION": lambda c: "12.1.2" if c["code_analysis"]["checkstyle"] else None,
    "PMD_VERSION": lambda c: "7.18.0" if c["code_analysis"]["pmd"] else None,
    "NEXUS_VERSION": lambda c: c["versions"].get("nexus", DEFAULT_VERSIONS["nexus"]) if c["devops_tools"]["nexus"] else None,
    "PROMETHEUS_VERSION": lambda c: c["versions"].get("prometheus", DEFAULT_VERSIONS["prometheus"]) if c["devops_tools"]["prometheus"] else None,
    "GRAFANA_VERSION": lambda c: c["versions"].get("grafana", DEFAULT_VERSIONS["grafana"]) if c["devops_tools"]["grafana"] else None,
}


def split_csv(csv_string: str) -> list[str]:
    return [token.strip() for token in csv_string.split(",") if token.strip()]


def bool_string(value: Any) -> str:
    return str(bool(value)).lower()


def normalize_go_version(version: str) -> str:
    parts = str(version).split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return str(version)


def unique(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def java_feature_enabled(cfg: dict[str, Any]) -> bool:
    return (
        cfg["languages"]["java"]
        or cfg["build_tools"]["gradle"]
        or cfg["build_tools"]["maven"]
        or cfg["build_tools"]["ant"]
        or cfg["code_analysis"]["checkstyle"]
        or cfg["code_analysis"]["pmd"]
    )


def node_feature_enabled(cfg: dict[str, Any]) -> bool:
    return (
        cfg["languages"]["node"]
        or cfg["languages"]["javascript"]
        or cfg["languages"]["typescript"]
        or cfg["code_analysis"]["eslint"]
    )


def build_env_config(
    *,
    languages: list[str],
    cicd_tools: list[str],
    kubernetes_tools: list[str],
    build_tools: list[str],
    code_analysis: list[str],
    devops_tools: list[str],
    versions: dict[str, str],
) -> dict[str, Any]:
    resolved_versions = {}
    for key in ("python", "java", "node", "go"):
        resolved_versions[key] = versions.get(key, DEFAULT_VERSIONS[key])

    optional_version_keys = {
        "k9s": kubernetes_tools,
        "argocd": kubernetes_tools,
        "flux": kubernetes_tools,
        "kustomize": kubernetes_tools,
        "nexus": devops_tools,
        "prometheus": devops_tools,
        "grafana": devops_tools,
        "jenkins": devops_tools,
    }
    selection_names = {
        "k9s": "k9s",
        "argocd": "argocd_cli",
        "flux": "flux",
        "kustomize": "kustomize",
        "nexus": "nexus",
        "prometheus": "prometheus",
        "grafana": "grafana",
        "jenkins": "jenkins",
    }
    for key, selected_list in optional_version_keys.items():
        if selection_names[key] in selected_list:
            resolved_versions[key] = versions.get(key, DEFAULT_VERSIONS[key])

    return {
        "languages": {lang: lang in languages for lang in ALL_LANGUAGES},
        "cicd": {tool: tool in cicd_tools for tool in ALL_CICD},
        "kubernetes": {tool: tool in kubernetes_tools for tool in ALL_KUBERNETES},
        "build_tools": {tool: tool in build_tools for tool in ALL_BUILD_TOOLS},
        "code_analysis": {tool: tool in code_analysis for tool in ALL_CODE_ANALYSIS},
        "devops_tools": {tool: tool in devops_tools for tool in ALL_DEVOPS_TOOLS},
        "versions": resolved_versions,
    }


def build_features(cfg: dict[str, Any]) -> dict[str, Any]:
    versions = cfg["versions"]
    features: dict[str, Any] = {}

    if cfg["languages"]["python"]:
        features[FEATURE_REFS["python"]] = {
            "version": versions.get("python", DEFAULT_VERSIONS["python"]),
            "installTools": False,
        }
    if java_feature_enabled(cfg):
        features[FEATURE_REFS["java"]] = {
            "version": versions.get("java", DEFAULT_VERSIONS["java"]),
            "jdkDistro": "ms",
            "installGradle": cfg["build_tools"]["gradle"],
            "installMaven": cfg["build_tools"]["maven"],
            "installAnt": cfg["build_tools"]["ant"],
        }
    if node_feature_enabled(cfg):
        features[FEATURE_REFS["node"]] = {
            "version": versions.get("node", DEFAULT_VERSIONS["node"]),
            "nodeGypDependencies": True,
        }
    if cfg["languages"]["go"]:
        features[FEATURE_REFS["go"]] = {
            "version": normalize_go_version(versions.get("go", DEFAULT_VERSIONS["go"])),
        }
    if cfg["languages"]["ruby"]:
        features[FEATURE_REFS["ruby"]] = {}
    if cfg["languages"]["php"]:
        features[FEATURE_REFS["php"]] = {"installComposer": True}
    if cfg["languages"]["rust"]:
        features[FEATURE_REFS["rust"]] = {
            "profile": "minimal",
            "components": "rust-analyzer,rust-src,rustfmt,clippy",
        }

    return features


def build_args(cfg: dict[str, Any]) -> dict[str, str]:
    args: dict[str, str] = {}
    for name, factory in BUILD_ARG_FACTORIES.items():
        args[name] = bool_string(factory(cfg))

    for name, factory in VERSION_ARG_FACTORIES.items():
        value = factory(cfg)
        if value is not None:
            args[name] = str(value)

    return args


def build_extensions(cfg: dict[str, Any]) -> list[str]:
    langs = cfg["languages"]
    cicd = cfg["cicd"]
    k8s = cfg["kubernetes"]
    build_tools = cfg["build_tools"]
    analysis = cfg["code_analysis"]
    devops = cfg["devops_tools"]
    extensions: list[str] = []

    if langs["python"]:
        extensions.extend([
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.black-formatter",
        ])
        if analysis["pylint"]:
            extensions.append("ms-python.pylint")

    if java_feature_enabled(cfg):
        extensions.extend([
            "vscjava.vscode-java-pack",
            "redhat.java",
            "vscjava.vscode-maven",
            "vscjava.vscode-gradle",
        ])
        if analysis["checkstyle"]:
            extensions.append("shengchen.vscode-checkstyle")
        if analysis["pmd"]:
            extensions.append("vscjava.vscode-java-dependency")

    if node_feature_enabled(cfg):
        extensions.extend([
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "ms-vscode.vscode-typescript-next",
        ])

    if langs["go"]:
        extensions.append("golang.go")
    if langs["ruby"]:
        extensions.append("Shopify.ruby-lsp")
    if langs["php"]:
        extensions.extend([
            "bmewburn.vscode-intelephense-client",
            "xdebug.php-debug",
        ])
    if langs["rust"]:
        extensions.extend([
            "rust-lang.rust-analyzer",
            "tamasfe.even-better-toml",
        ])
    if langs["csharp"]:
        extensions.extend([
            "ms-dotnettools.csharp",
            "ms-dotnettools.csdevkit",
        ])
    if langs["c"] or langs["cpp"]:
        extensions.append("ms-vscode.cpptools")
    if langs["kotlin"]:
        extensions.append("fwcd.kotlin")

    if cicd["docker"] or cicd.get("podman", False):
        extensions.append("ms-azuretools.vscode-docker")
    if cicd["terraform"]:
        extensions.append("hashicorp.terraform")
    if cicd["kubectl"] or cicd["helm"] or any(k8s.values()):
        extensions.append("ms-kubernetes-tools.vscode-kubernetes-tools")
    if any(k8s.values()):
        extensions.append("mindaro.mindaro")
    if k8s["argocd_cli"]:
        extensions.append("argoproj.argocd-vscode-extension")
    if k8s["flux"]:
        extensions.append("weaveworks.vscode-gitops-tools")
    if cicd["github_actions"]:
        extensions.append("github.vscode-github-actions")
    if analysis["sonarqube"]:
        extensions.append("SonarSource.sonarlint-vscode")
    if devops["jenkins"]:
        extensions.append("secanis.jenkinsfile-support")

    extensions.extend([
        "github.copilot",
        "github.copilot-chat",
        "ms-vsliveshare.vsliveshare",
        "streetsidesoftware.code-spell-checker",
        "eamodio.gitlens",
    ])

    return unique(extensions)


def build_forward_ports(cfg: dict[str, Any]) -> list[int]:
    ports = []
    if cfg["devops_tools"]["nexus"]:
        ports.append(8081)
    if cfg["devops_tools"]["prometheus"]:
        ports.append(9090)
    if cfg["devops_tools"]["grafana"]:
        ports.append(3000)
    if cfg["devops_tools"]["elk"]:
        ports.extend([9200, 9300, 5601])
    if cfg["devops_tools"]["jenkins"]:
        ports.append(8080)
    return ports


def build_post_create_command(cfg: dict[str, Any]) -> str:
    commands = ["set -euo pipefail"]

    if cfg["languages"]["python"]:
        commands.append(
            "if command -v python3 >/dev/null 2>&1; then "
            "sudo python3 -m pip install --no-cache-dir --upgrade pip && "
            "sudo python3 -m pip install --no-cache-dir pytest black flake8 mypy pipenv tox coverage pytest-cov pylint; "
            "fi"
        )

    if node_feature_enabled(cfg):
        commands.append(
            "if command -v npm >/dev/null 2>&1; then "
            "sudo npm install -g typescript jest prettier eslint; "
            "fi"
        )

    if cfg["languages"]["go"]:
        commands.append(
            "if command -v go >/dev/null 2>&1; then "
            "GO_BIN=\"$(go env GOPATH 2>/dev/null)/bin/golangci-lint\"; "
            "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && "
            "if [ -f \"${GO_BIN}\" ]; then sudo install -m 0755 \"${GO_BIN}\" /usr/local/bin/golangci-lint; fi; "
            "fi"
        )

    if cfg["cicd"]["kubectl"] or cfg["cicd"]["helm"] or any(cfg["kubernetes"].values()):
        commands.append(
            "if [ -f ./kubernetes/k8s-config-generator.py ]; then "
            "sudo chmod +x ./kubernetes/k8s-config-generator.py && "
            "sudo ln -sf \"$(pwd)/kubernetes/k8s-config-generator.py\" /usr/local/bin/k8s-config-generator; "
            "fi"
        )

    commands.append("printf 'Devcontainer bootstrap complete.\\n'")
    return "bash -lc " + json.dumps("; ".join(commands))


def build_devcontainer_json(cfg: dict[str, Any]) -> dict[str, Any]:
    devcontainer = {
        "name": "DevOps OS - Multi-Language Development Environment",
        "build": {
            "dockerfile": "Dockerfile",
            "args": build_args(cfg),
        },
        "features": build_features(cfg),
        "mounts": [
            "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind",
        ],
        "customizations": {
            "vscode": {
                "extensions": build_extensions(cfg),
            }
        },
        "postCreateCommand": build_post_create_command(cfg),
    }
    forward_ports = build_forward_ports(cfg)
    if forward_ports:
        devcontainer["forwardPorts"] = forward_ports
    return devcontainer


def _load_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8")


def _json_fragment(value: Any, indent_prefix: int) -> str:
    text = json.dumps(value, indent=2)
    if "\n" not in text:
        return text
    lines = text.splitlines()
    return lines[0] + "\n" + "\n".join((" " * indent_prefix) + line for line in lines[1:])


def render_env_json(cfg: dict[str, Any]) -> str:
    template = _load_template("devcontainer.env.json.tpl")
    replacements = {
        "__LANGUAGES__": _json_fragment(cfg["languages"], 2),
        "__CICD__": _json_fragment(cfg["cicd"], 2),
        "__KUBERNETES__": _json_fragment(cfg["kubernetes"], 2),
        "__BUILD_TOOLS__": _json_fragment(cfg["build_tools"], 2),
        "__CODE_ANALYSIS__": _json_fragment(cfg["code_analysis"], 2),
        "__DEVOPS_TOOLS__": _json_fragment(cfg["devops_tools"], 2),
        "__VERSIONS__": _json_fragment(cfg["versions"], 2),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return template


def render_devcontainer_json(cfg: dict[str, Any]) -> str:
    devcontainer = build_devcontainer_json(cfg)
    template = _load_template("devcontainer.json.tpl")
    forward_ports_block = ""
    if "forwardPorts" in devcontainer:
        forward_ports_block = ",\n  \"forwardPorts\": " + _json_fragment(devcontainer["forwardPorts"], 2)
    replacements = {
        "__BUILD_ARGS__": _json_fragment(devcontainer["build"]["args"], 4),
        "__FEATURES__": _json_fragment(devcontainer["features"], 2),
        "__EXTENSIONS__": _json_fragment(devcontainer["customizations"]["vscode"]["extensions"], 6),
        "__FORWARD_PORTS_BLOCK__": forward_ports_block,
        "__POST_CREATE_COMMAND__": json.dumps(devcontainer["postCreateCommand"]),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return template


def render_dockerfile() -> str:
    return _load_template("Dockerfile.tpl")


def write_generated_devcontainer(output_root: Path, cfg: dict[str, Any]) -> dict[str, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    files = {
        "env": output_root / "devcontainer.env.json",
        "json": output_root / "devcontainer.json",
        "dockerfile": output_root / "Dockerfile",
    }
    files["env"].write_text(render_env_json(cfg), encoding="utf-8")
    files["json"].write_text(render_devcontainer_json(cfg), encoding="utf-8")
    files["dockerfile"].write_text(render_dockerfile(), encoding="utf-8")
    return files
