#!/usr/bin/env python3
"""
DevOps-OS GitHub Actions Workflow Generator

This script generates GitHub Actions workflow files for CI/CD pipelines
using the DevOps-OS container as the execution environment.

Features:
- Generates workflows for build, test, deploy, or complete CI/CD
- Supports multiple programming languages
- Configurable Kubernetes deployment methods
- Customizable through command-line arguments or environment variables
- Container image configuration options
- Secrets and environment variable management
- Matrix build support for multiple OS/architectures
"""

import os
import sys
import argparse
import json
import yaml
from string import Template
from pathlib import Path

# Default paths
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.getcwd()
ENV_CONFIG_PATH = os.path.join(TEMPLATE_DIR, "devcontainer.env.json")

# Default workflow types
WORKFLOW_TYPES = ["build", "test", "deploy", "complete", "reusable"]

# Environment variable prefixes
ENV_PREFIX = "DEVOPS_OS_GHA_"

def parse_arguments():
    """Parse command line arguments with environment variable fallbacks."""
    parser = argparse.ArgumentParser(description="Generate GitHub Actions workflow files for DevOps-OS")
    parser.add_argument("--name", 
                       help="Workflow name",
                       default=os.environ.get(f"{ENV_PREFIX}NAME", "DevOps-OS"))
    parser.add_argument("--type", choices=WORKFLOW_TYPES, 
                       help="Type of workflow to generate",
                       default=os.environ.get(f"{ENV_PREFIX}TYPE", "complete"))
    parser.add_argument("--languages", 
                       help="Comma-separated list of languages to enable (python,java,javascript,go)",
                       default=os.environ.get(f"{ENV_PREFIX}LANGUAGES", "python,javascript"))
    parser.add_argument("--kubernetes", action="store_true", 
                       help="Include Kubernetes deployment steps",
                       default=os.environ.get(f"{ENV_PREFIX}KUBERNETES", "false").lower() in ("true", "1", "yes"))
    parser.add_argument("--registry", 
                       help="Container registry URL",
                       default=os.environ.get(f"{ENV_PREFIX}REGISTRY", "ghcr.io"))
    parser.add_argument("--k8s-method", choices=["kubectl", "kustomize", "argocd", "flux"],
                       help="Kubernetes deployment method",
                       default=os.environ.get(f"{ENV_PREFIX}K8S_METHOD", "kubectl"))
    parser.add_argument("--output", 
                       help="Output directory for generated workflow files",
                       default=os.environ.get(f"{ENV_PREFIX}OUTPUT", os.path.join(OUTPUT_DIR, ".github/workflows")))
    parser.add_argument("--custom-values", 
                       help="Path to custom values JSON file",
                       default=os.environ.get(f"{ENV_PREFIX}CUSTOM_VALUES"))
    parser.add_argument("--image", 
                       help="DevOps-OS container image to use",
                       default=os.environ.get(f"{ENV_PREFIX}IMAGE", "ghcr.io/yourorg/devops-os:latest"))
    parser.add_argument("--branches", 
                       help="Comma-separated list of branches to trigger workflow",
                       default=os.environ.get(f"{ENV_PREFIX}BRANCHES", "main"))
    parser.add_argument("--matrix", action="store_true",
                       help="Enable matrix builds (multiple OS/architectures)",
                       default=os.environ.get(f"{ENV_PREFIX}MATRIX", "false").lower() in ("true", "1", "yes"))
    parser.add_argument("--env-file", 
                       help="Use DevOps-OS devcontainer.env.json for configuration",
                       default=os.environ.get(f"{ENV_PREFIX}ENV_FILE", ENV_CONFIG_PATH))
    parser.add_argument("--reusable", action="store_true", 
                       help="Generate a reusable workflow that can be called from other workflows",
                       default=os.environ.get(f"{ENV_PREFIX}REUSABLE", "false").lower() in ("true", "1", "yes"))
    
    args = parser.parse_args()
    
    # If type is 'reusable', set reusable flag to True
    if args.type == "reusable":
        args.reusable = True
    
    return args

def load_custom_values(file_path):
    """Load custom values from a JSON file."""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def load_env_config(file_path):
    """Load DevOps-OS environment configuration."""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            # Remove comments that start with // for JSON parsing
            lines = f.readlines()
            cleaned_json = ""
            for line in lines:
                if not line.strip().startswith("//"):
                    cleaned_json += line
            return json.loads(cleaned_json)
    return {}

def create_directory_structure(output_dir):
    """Create the necessary directory structure."""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def generate_language_config(languages_str, env_config=None):
    """Generate language configuration JSON."""
    languages = languages_str.split(',')
    
    # Default to env_config if available, otherwise use languages from args
    if env_config and 'languages' in env_config:
        config = env_config['languages']
    else:
        config = {
            "python": "python" in languages,
            "java": "java" in languages,
            "javascript": "javascript" in languages, 
            "go": "go" in languages
        }
    
    return config

def generate_kubernetes_config(k8s_enabled, k8s_method, env_config=None):
    """Generate Kubernetes configuration JSON."""
    # Default to env_config if available
    if env_config and 'kubernetes' in env_config:
        return env_config['kubernetes']
    
    if not k8s_enabled:
        return {"k9s": False, "kustomize": False, "argocd_cli": False, "flux": False}
    
    config = {
        "k9s": True,
        "kustomize": k8s_method == "kustomize",
        "argocd_cli": k8s_method == "argocd",
        "flux": k8s_method == "flux",
        "kind": False,
        "minikube": False
    }
    return config

def generate_cicd_config(env_config=None):
    """Generate CI/CD tools configuration JSON."""
    if env_config and 'cicd' in env_config:
        return env_config['cicd']
    
    return {
        "docker": True,
        "terraform": True,
        "kubectl": True,
        "helm": True,
        "github_actions": True
    }

def generate_build_tools_config(env_config=None):
    """Generate build tools configuration JSON."""
    if env_config and 'build_tools' in env_config:
        return env_config['build_tools']
    
    return {
        "gradle": True,
        "maven": True,
        "ant": False,
        "make": True,
        "cmake": False
    }

def generate_code_analysis_config(env_config=None):
    """Generate code analysis tools configuration JSON."""
    if env_config and 'code_analysis' in env_config:
        return env_config['code_analysis']
    
    return {
        "sonarqube": True,
        "checkstyle": True,
        "pmd": False,
        "eslint": True,
        "pylint": True
    }

def generate_devops_tools_config(env_config=None):
    """Generate DevOps tools configuration JSON."""
    if env_config and 'devops_tools' in env_config:
        return env_config['devops_tools']
    
    return {
        "nexus": False,
        "prometheus": True,
        "grafana": True,
        "elk": True,
        "jenkins": False
    }

def generate_build_workflow(args, values, configs):
    """Generate a build workflow."""
    branches = [b.strip() for b in args.branches.split(',')]
    image = values.get('container_image', args.image)
    
    workflow = {
        "name": f"{args.name} Build",
        "on": {
            "push": {
                "branches": branches
            },
            "pull_request": {
                "branches": branches
            },
            "workflow_dispatch": {}
        },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up build environment",
                        "run": "echo 'Setting up build environment for DevOps-OS'"
                    }
                ]
            }
        }
    }
    
    # Add matrix strategy if enabled
    if args.matrix:
        workflow["jobs"]["build"]["strategy"] = {
            "matrix": {
                "os": ["ubuntu-latest"],
                "arch": ["amd64", "arm64"]
            },
            "fail-fast": False
        }
        workflow["jobs"]["build"]["runs-on"] = "${{ matrix.os }}"
    
    # Add language-specific build steps
    if configs["languages"].get("python", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Install Python dependencies",
            "run": "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build Python package",
            "run": "if [ -f setup.py ]; then pip install -e .; fi"
        })
    
    if configs["languages"].get("java", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Set up Java environment",
            "run": "echo 'Setting up Java environment'"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build with Maven",
            "run": "if [ -f pom.xml ]; then mvn -B package --file pom.xml; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build with Gradle",
            "run": "if [ -f build.gradle ]; then ./gradlew build; fi"
        })
    
    if configs["languages"].get("javascript", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Install Node.js dependencies",
            "run": "if [ -f package.json ]; then npm ci; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build JavaScript/TypeScript",
            "run": "if [ -f package.json ]; then npm run build --if-present; fi"
        })
    
    if configs["languages"].get("go", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build Go application",
            "run": "if [ -f go.mod ]; then go build -v ./...; fi"
        })
    
    # Add code analysis if enabled
    if configs.get("code_analysis", {}).get("sonarqube", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "SonarQube Analysis",
            "run": "echo 'Running SonarQube analysis'"
        })
    
    # Add artifact upload
    artifact_suffix = ""
    if args.matrix:
        artifact_suffix = "-${{ matrix.os }}-${{ matrix.arch }}"
        
    workflow["jobs"]["build"]["steps"].append({
        "name": "Upload build artifacts",
        "uses": "actions/upload-artifact@v3",
        "with": {
            "name": f"build-artifacts{artifact_suffix}",
            "path": values.get("artifact_path", "dist/"),
            "retention-days": 1
        }
    })
    
    return workflow

def generate_test_workflow(args, values, configs):
    """Generate a test workflow."""
    branches = [b.strip() for b in args.branches.split(',')]
    image = values.get('container_image', args.image)
    
    workflow = {
        "name": f"{args.name} Test",
        "on": {
            "push": {
                "branches": branches
            },
            "pull_request": {
                "branches": branches
            },
            "workflow_dispatch": {}
        },
        "jobs": {
            "test": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up test environment",
                        "run": "echo 'Setting up test environment for DevOps-OS'"
                    }
                ]
            }
        }
    }
    
    # Add matrix strategy if enabled
    if args.matrix:
        workflow["jobs"]["test"]["strategy"] = {
            "matrix": {
                "os": ["ubuntu-latest"],
                "arch": ["amd64", "arm64"]
            },
            "fail-fast": False
        }
        workflow["jobs"]["test"]["runs-on"] = "${{ matrix.os }}"
    
    # Add language-specific test steps
    if configs["languages"].get("python", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Install Python dependencies",
            "run": "if [ -f requirements.txt ]; then pip install -r requirements.txt pytest pytest-cov; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Python tests",
            "run": "if [ -d tests ]; then python -m pytest --cov=./ --cov-report=xml; fi"
        })
        if configs.get("code_analysis", {}).get("pylint", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run Pylint",
                "run": "if command -v pylint &> /dev/null; then pylint --disable=C0111 **/*.py; fi"
            })
    
    if configs["languages"].get("java", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Set up Java environment",
            "run": "echo 'Setting up Java environment'"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Java tests with Maven",
            "run": "if [ -f pom.xml ]; then mvn -B test --file pom.xml; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Java tests with Gradle",
            "run": "if [ -f build.gradle ]; then ./gradlew test; fi"
        })
        if configs.get("code_analysis", {}).get("checkstyle", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run Checkstyle",
                "run": "if [ -f pom.xml ]; then mvn checkstyle:checkstyle; fi"
            })
    
    if configs["languages"].get("javascript", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Install Node.js dependencies",
            "run": "if [ -f package.json ]; then npm ci; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run JavaScript tests",
            "run": "if [ -f package.json ]; then npm test; fi"
        })
        if configs.get("code_analysis", {}).get("eslint", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run ESLint",
                "run": "if [ -f package.json ] && grep -q eslint package.json; then npm run lint; fi"
            })
    
    if configs["languages"].get("go", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Go tests",
            "run": "if [ -f go.mod ]; then go test -v ./...; fi"
        })
    
    # Add test report
    artifact_suffix = ""
    if args.matrix:
        artifact_suffix = "-${{ matrix.os }}-${{ matrix.arch }}"
        
    workflow["jobs"]["test"]["steps"].append({
        "name": "Upload test results",
        "uses": "actions/upload-artifact@v3",
        "with": {
            "name": f"test-results{artifact_suffix}",
            "path": values.get("test_report_path", "test-reports/"),
            "retention-days": 1
        }
    })
    
    workflow["jobs"]["test"]["steps"].append({
        "name": "Upload coverage reports",
        "uses": "codecov/codecov-action@v3",
        "with": {
            "files": "./coverage.xml,./coverage/lcov.info",
            "fail_ci_if_error": False
        }
    })
    
    return workflow

def generate_deploy_workflow(args, values, configs):
    """Generate a deployment workflow."""
    branches = [b.strip() for b in args.branches.split(',')]
    image = values.get('container_image', args.image)
    
    workflow = {
        "name": f"{args.name} Deploy",
        "on": {
            "push": {
                "branches": branches
            },
            "workflow_dispatch": {
                "inputs": {
                    "environment": {
                        "description": "Environment to deploy to",
                        "required": True,
                        "default": "dev",
                        "type": "choice",
                        "options": ["dev", "test", "staging", "prod"]
                    }
                }
            }
        },
        "jobs": {
            "deploy": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up deployment environment",
                        "run": "echo 'Setting up deployment environment for DevOps-OS'"
                    },
                    {
                        "name": "Build and Push Docker Image",
                        "if": "github.ref == 'refs/heads/main'",
                        "run": "\n".join([
                            "echo \"${{ secrets.REGISTRY_TOKEN }}\" | docker login " + args.registry + " -u ${{ github.actor }} --password-stdin",
                            "docker build -t " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest .",
                            "docker push " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest"
                        ])
                    }
                ]
            }
        }
    }
    
    # Add Kubernetes deployment steps if enabled
    if args.kubernetes:
        if args.k8s_method == "kubectl":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy to Kubernetes",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "mkdir -p $HOME/.kube",
                    "echo \"${{ secrets.KUBECONFIG }}\" > $HOME/.kube/config",
                    "chmod 600 $HOME/.kube/config",
                    "kubectl apply -f ./k8s/deployment.yaml",
                    "kubectl apply -f ./k8s/service.yaml",
                    "kubectl rollout status deployment/my-app"
                ])
            })
        elif args.k8s_method == "kustomize":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy to Kubernetes with Kustomize",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "mkdir -p $HOME/.kube",
                    "echo \"${{ secrets.KUBECONFIG }}\" > $HOME/.kube/config",
                    "chmod 600 $HOME/.kube/config",
                    "kubectl apply -k ./k8s/overlays/${ENVIRONMENT}",
                    "kubectl rollout status deployment/my-app"
                ]),
                "env": {
                    "ENVIRONMENT": "${{ github.event.inputs.environment || 'dev' }}"
                }
            })
        elif args.k8s_method == "argocd":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy with ArgoCD",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure",
                    "argocd app sync my-application",
                    "argocd app wait my-application --health"
                ]),
                "env": {
                    "ARGOCD_SERVER": "${{ secrets.ARGOCD_SERVER }}",
                    "ARGOCD_USERNAME": "${{ secrets.ARGOCD_USERNAME }}",
                    "ARGOCD_PASSWORD": "${{ secrets.ARGOCD_PASSWORD }}"
                }
            })
        elif args.k8s_method == "flux":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy with Flux",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "flux reconcile source git flux-system",
                    "flux reconcile kustomization flux-system"
                ])
            })
    
    return workflow

def generate_complete_workflow(args, values, configs):
    """Generate a complete CI/CD workflow."""
    branches = [b.strip() for b in args.branches.split(',')]
    image = values.get('container_image', args.image)
    
    workflow = {
        "name": f"{args.name} CI/CD",
        "on": {
            "push": {
                "branches": branches
            },
            "pull_request": {
                "branches": branches
            },
            "workflow_dispatch": {
                "inputs": {
                    "environment": {
                        "description": "Environment to deploy to",
                        "required": True,
                        "default": "dev",
                        "type": "choice",
                        "options": ["dev", "test", "staging", "prod"]
                    }
                }
            }
        },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up build environment",
                        "run": "echo 'Setting up build environment for DevOps-OS'"
                    }
                ]
            },
            "test": {
                "needs": ["build"],
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up test environment",
                        "run": "echo 'Setting up test environment for DevOps-OS'"
                    }
                ]
            },
            "deploy": {
                "needs": ["test"],
                "if": "github.ref == 'refs/heads/main'",
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up deployment environment",
                        "run": "echo 'Setting up deployment environment for DevOps-OS'"
                    }
                ]
            }
        }
    }
    
    # Add matrix strategy if enabled
    if args.matrix:
        for job in ["build", "test", "deploy"]:
            workflow["jobs"][job]["strategy"] = {
                "matrix": {
                    "os": ["ubuntu-latest"],
                    "arch": ["amd64", "arm64"]
                },
                "fail-fast": False
            }
            workflow["jobs"][job]["runs-on"] = "${{ matrix.os }}"
    
    # Add language-specific build steps
    if configs["languages"].get("python", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Install Python dependencies",
            "run": "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build Python package",
            "run": "if [ -f setup.py ]; then pip install -e .; elif [ -f pyproject.toml ]; then pip install -e .; fi"
        })
    
    if configs["languages"].get("java", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Set up Java environment",
            "run": "echo 'Setting up Java environment'"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build with Maven",
            "run": "if [ -f pom.xml ]; then mvn -B package --file pom.xml; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build with Gradle",
            "run": "if [ -f build.gradle ]; then ./gradlew build; fi"
        })
    
    if configs["languages"].get("javascript", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Install Node.js dependencies",
            "run": "if [ -f package.json ]; then npm ci; fi"
        })
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build JavaScript/TypeScript",
            "run": "if [ -f package.json ]; then npm run build --if-present; fi"
        })
    
    if configs["languages"].get("go", False):
        workflow["jobs"]["build"]["steps"].append({
            "name": "Build Go application",
            "run": "if [ -f go.mod ]; then go build -v ./...; fi"
        })
    
    # Add artifact upload for build
    artifact_suffix = ""
    if args.matrix:
        artifact_suffix = "-${{ matrix.os }}-${{ matrix.arch }}"
        
    workflow["jobs"]["build"]["steps"].append({
        "name": "Upload build artifacts",
        "uses": "actions/upload-artifact@v3",
        "with": {
            "name": f"build-artifacts{artifact_suffix}",
            "path": values.get("artifact_path", "dist/"),
            "retention-days": 1
        }
    })
    
    # Add language-specific test steps
    if configs["languages"].get("python", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Install Python dependencies",
            "run": "if [ -f requirements.txt ]; then pip install -r requirements.txt pytest pytest-cov; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Python tests",
            "run": "if [ -d tests ]; then python -m pytest --cov=./ --cov-report=xml; fi"
        })
        if configs.get("code_analysis", {}).get("pylint", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run Pylint",
                "run": "if command -v pylint &> /dev/null; then pylint --disable=C0111 **/*.py; fi"
            })
    
    if configs["languages"].get("java", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Set up Java environment",
            "run": "echo 'Setting up Java environment'"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Java tests with Maven",
            "run": "if [ -f pom.xml ]; then mvn -B test --file pom.xml; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Java tests with Gradle",
            "run": "if [ -f build.gradle ]; then ./gradlew test; fi"
        })
        if configs.get("code_analysis", {}).get("checkstyle", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run Checkstyle",
                "run": "if [ -f pom.xml ]; then mvn checkstyle:checkstyle; fi"
            })
    
    if configs["languages"].get("javascript", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Install Node.js dependencies",
            "run": "if [ -f package.json ]; then npm ci; fi"
        })
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run JavaScript tests",
            "run": "if [ -f package.json ]; then npm test; fi"
        })
        if configs.get("code_analysis", {}).get("eslint", False):
            workflow["jobs"]["test"]["steps"].append({
                "name": "Run ESLint",
                "run": "if [ -f package.json ] && grep -q eslint package.json; then npm run lint; fi"
            })
    
    if configs["languages"].get("go", False):
        workflow["jobs"]["test"]["steps"].append({
            "name": "Run Go tests",
            "run": "if [ -f go.mod ]; then go test -v ./...; fi"
        })
    
    # Add test report
    workflow["jobs"]["test"]["steps"].append({
        "name": "Upload test results",
        "uses": "actions/upload-artifact@v3",
        "with": {
            "name": f"test-results{artifact_suffix}",
            "path": values.get("test_report_path", "test-reports/"),
            "retention-days": 1
        }
    })
    
    workflow["jobs"]["test"]["steps"].append({
        "name": "Upload coverage reports",
        "uses": "codecov/codecov-action@v3",
        "with": {
            "files": "./coverage.xml,./coverage/lcov.info",
            "fail_ci_if_error": False
        }
    })
    
    # Add deployment steps
    workflow["jobs"]["deploy"]["steps"].append({
        "name": "Build and Push Docker Image",
        "if": "github.ref == 'refs/heads/main'",
        "run": "\n".join([
            "echo \"${{ secrets.REGISTRY_TOKEN }}\" | docker login " + args.registry + " -u ${{ github.actor }} --password-stdin",
            "docker build -t " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest .",
            "docker push " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest"
        ])
    })
    
    # Add Kubernetes deployment steps if enabled
    if args.kubernetes:
        if args.k8s_method == "kubectl":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy to Kubernetes",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "mkdir -p $HOME/.kube",
                    "echo \"${{ secrets.KUBECONFIG }}\" > $HOME/.kube/config",
                    "chmod 600 $HOME/.kube/config",
                    "kubectl apply -f ./k8s/deployment.yaml",
                    "kubectl apply -f ./k8s/service.yaml",
                    "kubectl rollout status deployment/my-app"
                ])
            })
        elif args.k8s_method == "kustomize":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy to Kubernetes with Kustomize",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "mkdir -p $HOME/.kube",
                    "echo \"${{ secrets.KUBECONFIG }}\" > $HOME/.kube/config",
                    "chmod 600 $HOME/.kube/config",
                    "kubectl apply -k ./k8s/overlays/${ENVIRONMENT}",
                    "kubectl rollout status deployment/my-app"
                ]),
                "env": {
                    "ENVIRONMENT": "${{ github.event.inputs.environment || 'dev' }}"
                }
            })
        elif args.k8s_method == "argocd":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy with ArgoCD",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure",
                    "argocd app sync my-application",
                    "argocd app wait my-application --health"
                ]),
                "env": {
                    "ARGOCD_SERVER": "${{ secrets.ARGOCD_SERVER }}",
                    "ARGOCD_USERNAME": "${{ secrets.ARGOCD_USERNAME }}",
                    "ARGOCD_PASSWORD": "${{ secrets.ARGOCD_PASSWORD }}"
                }
            })
        elif args.k8s_method == "flux":
            workflow["jobs"]["deploy"]["steps"].append({
                "name": "Deploy with Flux",
                "if": "github.ref == 'refs/heads/main'",
                "run": "\n".join([
                    "flux reconcile source git flux-system",
                    "flux reconcile kustomization flux-system"
                ])
            })
    
    return workflow

def generate_reusable_workflow(args, values, configs):
    """Generate a reusable workflow that can be called from other workflows."""
    image = values.get('container_image', args.image)
    
    workflow = {
        "name": f"{args.name} Reusable Workflow",
        "on": {
            "workflow_call": {
                "inputs": {
                    "environment": {
                        "description": "Environment to deploy to",
                        "required": False,
                        "default": "dev",
                        "type": "string"
                    },
                    "languages": {
                        "description": "JSON string of languages to enable",
                        "required": False,
                        "default": json.dumps(configs["languages"]),
                        "type": "string"
                    },
                    "kubernetes_deploy": {
                        "description": "Whether to deploy to Kubernetes",
                        "required": False,
                        "default": args.kubernetes,
                        "type": "boolean"
                    },
                    "k8s_method": {
                        "description": "Kubernetes deployment method",
                        "required": False,
                        "default": args.k8s_method,
                        "type": "string"
                    }
                },
                "secrets": {
                    "registry_token": {
                        "description": "Token for container registry",
                        "required": False
                    },
                    "kubeconfig": {
                        "description": "Kubernetes configuration",
                        "required": False
                    }
                }
            }
        },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up build environment",
                        "run": "echo 'Setting up build environment for DevOps-OS'"
                    }
                ]
            },
            "test": {
                "needs": ["build"],
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up test environment",
                        "run": "echo 'Setting up test environment for DevOps-OS'"
                    }
                ]
            },
            "deploy": {
                "needs": ["test"],
                "if": "github.ref == 'refs/heads/main'",
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": image,
                    "options": "--user root"
                },
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up deployment environment",
                        "run": "echo 'Setting up deployment environment for DevOps-OS'"
                    },
                    {
                        "name": "Parse input configurations",
                        "id": "config",
                        "run": "\n".join([
                            "echo \"languages=${{ inputs.languages }}\" >> $GITHUB_OUTPUT",
                            "echo \"k8s_deploy=${{ inputs.kubernetes_deploy }}\" >> $GITHUB_OUTPUT",
                            "echo \"k8s_method=${{ inputs.k8s_method }}\" >> $GITHUB_OUTPUT",
                            "echo \"env=${{ inputs.environment }}\" >> $GITHUB_OUTPUT"
                        ])
                    },
                    {
                        "name": "Build and Push Docker Image",
                        "if": "github.ref == 'refs/heads/main'",
                        "run": "\n".join([
                            "echo \"${{ secrets.registry_token }}\" | docker login " + args.registry + " -u ${{ github.actor }} --password-stdin",
                            "docker build -t " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest .",
                            "docker push " + args.registry + "/${{ github.repository_owner }}/${{ github.event.repository.name }}:latest"
                        ])
                    }
                ]
            }
        }
    }
    
    # Add matrix strategy if enabled
    if args.matrix:
        for job in ["build", "test", "deploy"]:
            workflow["jobs"][job]["strategy"] = {
                "matrix": {
                    "os": ["ubuntu-latest"],
                    "arch": ["amd64", "arm64"]
                },
                "fail-fast": False
            }
            workflow["jobs"][job]["runs-on"] = "${{ matrix.os }}"
    
    # Add conditional Kubernetes deployment steps
    workflow["jobs"]["deploy"]["steps"].append({
        "name": "Deploy to Kubernetes",
        "if": "github.ref == 'refs/heads/main' && steps.config.outputs.k8s_deploy == 'true'",
        "run": "\n".join([
            "mkdir -p $HOME/.kube",
            "echo \"${{ secrets.kubeconfig }}\" > $HOME/.kube/config",
            "chmod 600 $HOME/.kube/config",
            "if [[ \"${{ steps.config.outputs.k8s_method }}\" == \"kubectl\" ]]; then",
            "  kubectl apply -f ./k8s/deployment.yaml",
            "  kubectl apply -f ./k8s/service.yaml",
            "  kubectl rollout status deployment/my-app",
            "elif [[ \"${{ steps.config.outputs.k8s_method }}\" == \"kustomize\" ]]; then",
            "  kubectl apply -k ./k8s/overlays/${{ steps.config.outputs.env }}",
            "  kubectl rollout status deployment/my-app",
            "elif [[ \"${{ steps.config.outputs.k8s_method }}\" == \"argocd\" ]]; then",
            "  argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure",
            "  argocd app sync my-application",
            "  argocd app wait my-application --health",
            "elif [[ \"${{ steps.config.outputs.k8s_method }}\" == \"flux\" ]]; then",
            "  flux reconcile source git flux-system",
            "  flux reconcile kustomization flux-system",
            "fi"
        ])
    })
    
    return workflow

def generate_workflow(args, values, configs):
    """Generate the requested workflow type."""
    if args.type == "build":
        return generate_build_workflow(args, values, configs)
    elif args.type == "test":
        return generate_test_workflow(args, values, configs)
    elif args.type == "deploy":
        return generate_deploy_workflow(args, values, configs)
    elif args.type == "complete":
        return generate_complete_workflow(args, values, configs)
    elif args.type == "reusable" or args.reusable:
        return generate_reusable_workflow(args, values, configs)
    else:
        print(f"Error: Unknown workflow type '{args.type}'")
        sys.exit(1)

def main():
    """Main function."""
    args = parse_arguments()
    output_dir = create_directory_structure(args.output)
    custom_values = load_custom_values(args.custom_values)
    env_config = load_env_config(args.env_file)
    
    # Generate configuration objects
    configs = {
        "languages": generate_language_config(args.languages, env_config),
        "kubernetes": generate_kubernetes_config(args.kubernetes, args.k8s_method, env_config),
        "cicd": generate_cicd_config(env_config),
        "build_tools": generate_build_tools_config(env_config),
        "code_analysis": generate_code_analysis_config(env_config),
        "devops_tools": generate_devops_tools_config(env_config)
    }
    
    # Generate workflow filename
    filename = f"{args.name.lower().replace(' ', '-')}-{args.type}.yml"
    filepath = os.path.join(output_dir, filename)
    
    # Generate workflow content
    workflow_content = generate_workflow(args, custom_values, configs)
    
    # Convert workflow to YAML
    yaml_content = yaml.dump(workflow_content, sort_keys=False)
    
    # Write to file
    with open(filepath, 'w') as f:
        f.write(yaml_content)
    
    print(f"GitHub Actions workflow generated: {filepath}")
    print(f"Type: {args.type}")
    print(f"Languages: {args.languages}")
    if args.kubernetes:
        print(f"Kubernetes deployment method: {args.k8s_method}")

if __name__ == "__main__":
    main()
