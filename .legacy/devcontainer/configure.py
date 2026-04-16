#!/usr/bin/env python3
import json
import os
from copy import deepcopy

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "devcontainer.env.json")
DEVCONTAINER_FILE = os.path.join(os.path.dirname(__file__), "devcontainer.json")

FEATURE_LANGUAGE_KEYS = ["python", "java", "node", "ruby", "php", "rust", "typescript", "javascript", "go"]
FALLBACK_LANGUAGE_KEYS = ["csharp", "kotlin", "c", "cpp"]

DEFAULT_CONFIG = {
    "languages": {
        "python": True,
        "java": True,
        "node": True,
        "ruby": True,
        "csharp": True,
        "php": True,
        "rust": True,
        "typescript": True,
        "kotlin": True,
        "c": True,
        "cpp": True,
        "javascript": True,
        "go": True,
    },
    "cicd": {
        "docker": True,
        "terraform": True,
        "kubectl": True,
        "helm": True,
        "github_actions": True,
        "podman": False,
    },
    "kubernetes": {
        "k9s": True,
        "kustomize": True,
        "argocd_cli": True,
        "lens": False,
        "kubeseal": True,
        "flux": True,
        "kind": True,
        "minikube": True,
        "openshift_cli": False,
    },
    "build_tools": {
        "gradle": True,
        "maven": True,
        "ant": True,
        "make": True,
        "cmake": True,
    },
    "code_analysis": {
        "sonarqube": True,
        "checkstyle": True,
        "pmd": True,
        "eslint": True,
        "pylint": True,
    },
    "devops_tools": {
        "nexus": True,
        "prometheus": True,
        "grafana": True,
        "elk": True,
        "jenkins": False,
    },
    "versions": {
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
    },
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
    "JAVA_VERSION": lambda c: c["versions"].get("java", "21") if c["devops_tools"]["nexus"] else None,
    "TERRAFORM_VERSION": lambda c: "1.14.7" if c["cicd"]["terraform"] else None,
    "HELM_VERSION": lambda c: "4.0.1" if c["cicd"]["helm"] else None,
    "ACTIONS_RUNNER_VERSION": lambda c: "2.330.0" if c["cicd"]["github_actions"] else None,
    "K9S_VERSION": lambda c: c["versions"].get("k9s", "0.50.16") if c["kubernetes"]["k9s"] else None,
    "KUSTOMIZE_VERSION": lambda c: c["versions"].get("kustomize", "5.8.0") if c["kubernetes"]["kustomize"] else None,
    "ARGOCD_VERSION": lambda c: c["versions"].get("argocd", "3.3.6") if c["kubernetes"]["argocd_cli"] else None,
    "FLUX_VERSION": lambda c: c["versions"].get("flux", "2.8.5") if c["kubernetes"]["flux"] else None,
    "KUBESEAL_VERSION": lambda c: "0.33.1" if c["kubernetes"]["kubeseal"] else None,
    "KIND_VERSION": lambda c: "0.31.0" if c["kubernetes"]["kind"] else None,
    "MINIKUBE_VERSION": lambda c: "1.37.0" if c["kubernetes"]["minikube"] else None,
    "SONAR_SCANNER_VERSION": lambda c: "8.0.1.6346" if c["code_analysis"]["sonarqube"] else None,
    "CHECKSTYLE_VERSION": lambda c: "12.1.2" if c["code_analysis"]["checkstyle"] else None,
    "PMD_VERSION": lambda c: "7.18.0" if c["code_analysis"]["pmd"] else None,
    "NEXUS_VERSION": lambda c: c["versions"].get("nexus", "3.91.0") if c["devops_tools"]["nexus"] else None,
    "PROMETHEUS_VERSION": lambda c: c["versions"].get("prometheus", "3.5.1") if c["devops_tools"]["prometheus"] else None,
    "GRAFANA_VERSION": lambda c: c["versions"].get("grafana", "12.4.2") if c["devops_tools"]["grafana"] else None,
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


def deep_merge(defaults, data):
    merged = deepcopy(defaults)
    for key, value in data.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
        config = deep_merge(DEFAULT_CONFIG, json.load(handle))
else:
    config = deepcopy(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")


def unique(values):
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def bool_string(value):
    return str(bool(value)).lower()


def normalize_go_version(version):
    parts = str(version).split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return str(version)


def java_feature_enabled(cfg):
    return (
        cfg["languages"]["java"]
        or cfg["build_tools"]["gradle"]
        or cfg["build_tools"]["maven"]
        or cfg["build_tools"]["ant"]
        or cfg["code_analysis"]["checkstyle"]
        or cfg["code_analysis"]["pmd"]
    )


def node_feature_enabled(cfg):
    return (
        cfg["languages"]["node"]
        or cfg["languages"]["javascript"]
        or cfg["languages"]["typescript"]
        or cfg["code_analysis"]["eslint"]
    )


def build_features(cfg):
    features = {}
    versions = cfg["versions"]

    if cfg["languages"]["python"]:
        features[FEATURE_REFS["python"]] = {
            "version": versions.get("python", "3.12"),
            "installTools": False,
        }

    if java_feature_enabled(cfg):
        features[FEATURE_REFS["java"]] = {
            "version": versions.get("java", "21"),
            "jdkDistro": "ms",
            "installGradle": cfg["build_tools"]["gradle"],
            "installMaven": cfg["build_tools"]["maven"],
            "installAnt": cfg["build_tools"]["ant"],
        }

    if node_feature_enabled(cfg):
        features[FEATURE_REFS["node"]] = {
            "version": versions.get("node", "22"),
            "nodeGypDependencies": True,
        }

    if cfg["languages"]["go"]:
        features[FEATURE_REFS["go"]] = {
            "version": normalize_go_version(versions.get("go", "1.25.0")),
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


def build_args(cfg):
    args = {}
    for name, factory in BUILD_ARG_FACTORIES.items():
        args[name] = bool_string(factory(cfg))

    for name, factory in VERSION_ARG_FACTORIES.items():
        value = factory(cfg)
        if value is not None:
            args[name] = str(value)

    return args


def build_extensions(cfg):
    extensions = []
    langs = cfg["languages"]
    cicd = cfg["cicd"]
    k8s = cfg["kubernetes"]
    build_tools = cfg["build_tools"]
    analysis = cfg["code_analysis"]
    devops = cfg["devops_tools"]

    if langs["python"]:
        extensions.extend([
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.black-formatter",
        ])

    if java_feature_enabled(cfg):
        extensions.extend([
            "vscjava.vscode-java-pack",
            "redhat.java",
            "vscjava.vscode-maven",
            "vscjava.vscode-gradle",
        ])

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
    if cicd["kubectl"] or cicd["helm"]:
        extensions.append("ms-kubernetes-tools.vscode-kubernetes-tools")
    if any(k8s.values()):
        extensions.extend([
            "ms-kubernetes-tools.vscode-kubernetes-tools",
            "mindaro.mindaro",
        ])
    if k8s["argocd_cli"]:
        extensions.append("argoproj.argocd-vscode-extension")
    if k8s["flux"]:
        extensions.append("weaveworks.vscode-gitops-tools")
    if cicd["github_actions"]:
        extensions.append("github.vscode-github-actions")
    if analysis["sonarqube"]:
        extensions.append("SonarSource.sonarlint-vscode")
    if analysis["checkstyle"] and java_feature_enabled(cfg):
        extensions.append("shengchen.vscode-checkstyle")
    if analysis["pmd"] and java_feature_enabled(cfg):
        extensions.append("vscjava.vscode-java-dependency")
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


def build_forward_ports(cfg):
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


features = build_features(config)
devcontainer = {
    "name": "DevOps OS - Multi-Language Development Environment",
    "build": {
        "dockerfile": "Dockerfile",
        "args": build_args(config),
    },
    "features": features,
    "mounts": [
        "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
    ],
    "customizations": {
        "vscode": {
            "extensions": build_extensions(config),
        }
    },
    "postCreateCommand": "bash .devcontainer/bootstrap-toolbox.sh",
}

forward_ports = build_forward_ports(config)
if forward_ports:
    devcontainer["forwardPorts"] = forward_ports

with open(DEVCONTAINER_FILE, "w", encoding="utf-8") as handle:
    json.dump(devcontainer, handle, indent=2)
    handle.write("\n")

print("Created devcontainer.json with configuration for:")
print("\nProgramming Languages:")
for lang, enabled in config["languages"].items():
    print(f"- {lang.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nFeature-installed Languages:")
for lang in FEATURE_LANGUAGE_KEYS:
    print(f"- {lang}: {'Enabled' if config['languages'][lang] else 'Disabled'}")

print("\nFallback-installed Languages:")
for lang in FALLBACK_LANGUAGE_KEYS:
    print(f"- {lang}: {'Enabled' if config['languages'][lang] else 'Disabled'}")

print("\nCI/CD Tools:")
for tool, enabled in config["cicd"].items():
    print(f"- {tool.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nKubernetes Tools:")
for tool, enabled in config["kubernetes"].items():
    print(f"- {tool.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nBuild Tools:")
for tool, enabled in config["build_tools"].items():
    print(f"- {tool.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nCode Analysis Tools:")
for tool, enabled in config["code_analysis"].items():
    print(f"- {tool.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nDevOps Tools:")
for tool, enabled in config["devops_tools"].items():
    print(f"- {tool.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

print("\nForwarded Ports:")
if forward_ports:
    for port in forward_ports:
        print(f"- Port {port}")
else:
    print("- No ports forwarded")

print("\nYour DevOps OS dev container is ready to use!")
