#!/usr/bin/env python3
import json
import os

# Path to the configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'devcontainer.env.json')
DEVCONTAINER_FILE = os.path.join(os.path.dirname(__file__), 'devcontainer.json')

# Default configuration
default_config = {
    "languages": {
        "python": True,
        "java": True,
        "javascript": True,
        "go": True
    },
    "cicd": {
        "docker": True,
        "terraform": True,
        "kubectl": True,
        "helm": True,
        "github_actions": True
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
        "openshift_cli": False
    },
    "build_tools": {
        "gradle": True,
        "maven": True,
        "ant": True,
        "make": True,
        "cmake": True
    },
    "code_analysis": {
        "sonarqube": True,
        "checkstyle": True,
        "pmd": True,
        "eslint": True,
        "pylint": True
    },
    "devops_tools": {
        "nexus": True,
        "prometheus": True,
        "grafana": True,
        "elk": True,
        "jenkins": False
    },
    "versions": {
        "python": "3.11",
        "java": "17",
        "node": "20",
        "go": "1.21",
        "nexus": "3.50.0",
        "prometheus": "2.45.0",
        "grafana": "10.0.0",
        "k9s": "0.29.1",
        "argocd": "2.8.4",
        "flux": "2.1.2",
        "kustomize": "5.2.1"
    }
}

# Read configuration file if it exists, otherwise use defaults
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = default_config
    # Write default config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_config, f, indent=2)

# Create the devcontainer.json content
devcontainer = {
    "name": "DevOps OS - Multi-Language Development Environment",
    "build": {
        "dockerfile": "Dockerfile",
        "args": {
            # Language versions
            "PYTHON_VERSION": config["versions"]["python"],
            "JAVA_VERSION": config["versions"]["java"],
            "NODE_VERSION": config["versions"]["node"],
            "GO_VERSION": config["versions"]["go"],
            
            # Languages
            "INSTALL_PYTHON": str(config["languages"]["python"]).lower(),
            "INSTALL_JAVA": str(config["languages"]["java"]).lower(),
            "INSTALL_JS": str(config["languages"]["javascript"]).lower(),
            "INSTALL_GO": str(config["languages"]["go"]).lower(),
            
            # CI/CD tools
            "INSTALL_DOCKER": str(config["cicd"]["docker"]).lower(),
            "INSTALL_TERRAFORM": str(config["cicd"]["terraform"]).lower(),
            "INSTALL_KUBECTL": str(config["cicd"]["kubectl"]).lower(),
            "INSTALL_HELM": str(config["cicd"]["helm"]).lower(),
            "INSTALL_GITHUB_ACTIONS": str(config["cicd"]["github_actions"]).lower(),
            
            # Kubernetes tools
            "INSTALL_K9S": str(config["kubernetes"]["k9s"]).lower(),
            "K9S_VERSION": config["versions"].get("k9s", "0.29.1"),
            "INSTALL_KUSTOMIZE": str(config["kubernetes"]["kustomize"]).lower(),
            "KUSTOMIZE_VERSION": config["versions"].get("kustomize", "5.2.1"),
            "INSTALL_ARGOCD_CLI": str(config["kubernetes"]["argocd_cli"]).lower(),
            "ARGOCD_VERSION": config["versions"].get("argocd", "2.8.4"),
            "INSTALL_LENS": str(config["kubernetes"]["lens"]).lower(),
            "INSTALL_KUBESEAL": str(config["kubernetes"]["kubeseal"]).lower(),
            "INSTALL_FLUX": str(config["kubernetes"]["flux"]).lower(),
            "FLUX_VERSION": config["versions"].get("flux", "2.1.2"),
            "INSTALL_KIND": str(config["kubernetes"]["kind"]).lower(),
            "INSTALL_MINIKUBE": str(config["kubernetes"]["minikube"]).lower(),
            "INSTALL_OPENSHIFT_CLI": str(config["kubernetes"]["openshift_cli"]).lower(),
            
            # Build tools
            "INSTALL_GRADLE": str(config["build_tools"]["gradle"]).lower(),
            "INSTALL_MAVEN": str(config["build_tools"]["maven"]).lower(),
            "INSTALL_ANT": str(config["build_tools"]["ant"]).lower(),
            "INSTALL_MAKE": str(config["build_tools"]["make"]).lower(),
            "INSTALL_CMAKE": str(config["build_tools"]["cmake"]).lower(),
            
            # Code analysis
            "INSTALL_SONARQUBE": str(config["code_analysis"]["sonarqube"]).lower(),
            "INSTALL_CHECKSTYLE": str(config["code_analysis"]["checkstyle"]).lower(),
            "INSTALL_PMD": str(config["code_analysis"]["pmd"]).lower(),
            "INSTALL_ESLINT": str(config["code_analysis"]["eslint"]).lower(),
            "INSTALL_PYLINT": str(config["code_analysis"]["pylint"]).lower(),
            
            # DevOps tools
            "INSTALL_NEXUS": str(config["devops_tools"]["nexus"]).lower(),
            "NEXUS_VERSION": config["versions"].get("nexus", "3.50.0"),
            "INSTALL_PROMETHEUS": str(config["devops_tools"]["prometheus"]).lower(),
            "PROMETHEUS_VERSION": config["versions"].get("prometheus", "2.45.0"),
            "INSTALL_GRAFANA": str(config["devops_tools"]["grafana"]).lower(),
            "GRAFANA_VERSION": config["versions"].get("grafana", "10.0.0"),
            "INSTALL_ELK": str(config["devops_tools"]["elk"]).lower(),
            "INSTALL_JENKINS": str(config["devops_tools"]["jenkins"]).lower()
        }
    },
    "mounts": [
        "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
    ],
    "customizations": {
        "vscode": {
            "extensions": []
        }
    },
    "forwardPorts": []
}

# Add language-specific extensions
if config["languages"]["python"]:
    devcontainer["customizations"]["vscode"]["extensions"].extend([
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter"
    ])

if config["languages"]["java"]:
    devcontainer["customizations"]["vscode"]["extensions"].extend([
        "vscjava.vscode-java-pack",
        "redhat.java",
        "vscjava.vscode-maven",
        "vscjava.vscode-gradle"
    ])

if config["languages"]["javascript"]:
    devcontainer["customizations"]["vscode"]["extensions"].extend([
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next"
    ])

if config["languages"]["go"]:
    devcontainer["customizations"]["vscode"]["extensions"].extend([
        "golang.go"
    ])

# Add CI/CD extensions
if config["cicd"]["docker"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("ms-azuretools.vscode-docker")

if config["cicd"]["terraform"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("hashicorp.terraform")

if config["cicd"]["kubectl"] or config["cicd"]["helm"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("ms-kubernetes-tools.vscode-kubernetes-tools")

# Add Kubernetes extensions
if any(config["kubernetes"].values()):
    devcontainer["customizations"]["vscode"]["extensions"].extend([
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "mindaro.mindaro",  # Bridge to Kubernetes
    ])
    
    # Add Kubernetes templates to postCreateCommand
    devcontainer["postCreateCommand"] = "chmod +x /workspaces/.devcontainer/k8s-config-generator.py && ln -sf /workspaces/.devcontainer/k8s-config-generator.py /usr/local/bin/k8s-config-generator"
    
if config["kubernetes"]["argocd_cli"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("argoproj.argocd-vscode-extension") 

if config["kubernetes"]["flux"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("weaveworks.vscode-gitops-tools")

if config["cicd"]["github_actions"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("github.vscode-github-actions")

# Add code analysis tools extensions
if config["code_analysis"]["sonarqube"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("SonarSource.sonarlint-vscode")

if config["code_analysis"]["checkstyle"] and config["languages"]["java"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("shengchen.vscode-checkstyle")

if config["code_analysis"]["pmd"] and config["languages"]["java"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("vscjava.vscode-java-dependency")

if config["code_analysis"]["eslint"] and config["languages"]["javascript"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("dbaeumer.vscode-eslint")

if config["code_analysis"]["pylint"] and config["languages"]["python"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("ms-python.pylint")

# Add DevOps tools extensions
if config["devops_tools"]["jenkins"]:
    devcontainer["customizations"]["vscode"]["extensions"].append("secanis.jenkinsfile-support")

# Forward ports for DevOps tools
if config["devops_tools"]["nexus"]:
    devcontainer["forwardPorts"].append(8081)  # Nexus port

if config["devops_tools"]["prometheus"]:
    devcontainer["forwardPorts"].append(9090)  # Prometheus port

if config["devops_tools"]["grafana"]:
    devcontainer["forwardPorts"].append(3000)  # Grafana port

if config["devops_tools"]["elk"]:
    devcontainer["forwardPorts"].extend([9200, 9300, 5601])  # Elasticsearch and Kibana ports

if config["devops_tools"]["jenkins"]:
    devcontainer["forwardPorts"].append(8080)  # Jenkins port

# Add general useful extensions
devcontainer["customizations"]["vscode"]["extensions"].extend([
    "github.copilot",
    "github.copilot-chat",
    "ms-vsliveshare.vsliveshare",
    "streetsidesoftware.code-spell-checker",
    "eamodio.gitlens"
])

# Write the devcontainer.json file
with open(DEVCONTAINER_FILE, 'w') as f:
    json.dump(devcontainer, f, indent=2)

print(f"Created devcontainer.json with configuration for:")
print("\nProgramming Languages:")
for lang, enabled in config["languages"].items():
    print(f"- {lang.capitalize()}: {'Enabled' if enabled else 'Disabled'}")

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
if devcontainer["forwardPorts"]:
    for port in devcontainer["forwardPorts"]:
        print(f"- Port {port}")
else:
    print("- No ports forwarded")

print("\nYour DevOps OS dev container is ready to use!")
