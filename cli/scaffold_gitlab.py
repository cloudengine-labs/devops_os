#!/usr/bin/env python3
"""
DevOps-OS GitLab CI Pipeline Generator

Generates a .gitlab-ci.yml file for CI/CD pipelines using the DevOps-OS
container as the execution environment.

Features:
- Generates pipelines for build, test, deploy, or complete CI/CD
- Supports multiple programming languages (Python, Java, JavaScript, Go)
- Configurable Kubernetes deployment methods (kubectl, kustomize, argocd, flux)
- Docker image build and push to GitLab Container Registry
- Environment-based deployment (dev, staging, production)
- Merge request pipelines and branch protection
"""

import os
import sys
import argparse
import json
import yaml
from pathlib import Path

# Environment variable prefix
ENV_PREFIX = "DEVOPS_OS_GITLAB_"

PIPELINE_TYPES = ["build", "test", "deploy", "complete"]
K8S_METHODS = ["kubectl", "kustomize", "argocd", "flux"]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate GitLab CI pipeline files for DevOps-OS")
    parser.add_argument("--name", default=os.environ.get(f"{ENV_PREFIX}NAME", "my-app"),
                        help="Application / pipeline name")
    parser.add_argument("--type", choices=PIPELINE_TYPES,
                        default=os.environ.get(f"{ENV_PREFIX}TYPE", "complete"),
                        help="Type of pipeline to generate")
    parser.add_argument("--languages",
                        default=os.environ.get(f"{ENV_PREFIX}LANGUAGES", "python"),
                        help="Comma-separated list of languages: python,java,javascript,go")
    parser.add_argument("--kubernetes", action="store_true",
                        default=os.environ.get(f"{ENV_PREFIX}KUBERNETES", "false").lower() in ("true", "1", "yes"),
                        help="Include Kubernetes deployment stage")
    parser.add_argument("--k8s-method", choices=K8S_METHODS,
                        default=os.environ.get(f"{ENV_PREFIX}K8S_METHOD", "kubectl"),
                        help="Kubernetes deployment method")
    parser.add_argument("--output", default=os.environ.get(f"{ENV_PREFIX}OUTPUT", ".gitlab-ci.yml"),
                        help="Output file path")
    parser.add_argument("--image", default=os.environ.get(f"{ENV_PREFIX}IMAGE", "docker:24"),
                        help="Default Docker image for pipeline jobs")
    parser.add_argument("--branches", default=os.environ.get(f"{ENV_PREFIX}BRANCHES", "main"),
                        help="Comma-separated protected branches (used for deploy rules)")
    parser.add_argument("--kube-namespace", default=os.environ.get(f"{ENV_PREFIX}KUBE_NAMESPACE", ""),
                        help="Kubernetes namespace to deploy to (omit to let GitLab CI/CD variable take effect)")
    parser.add_argument("--custom-values", default=None,
                        help="Path to custom values JSON file")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_custom_values(file_path):
    if file_path and os.path.exists(file_path):
        with open(file_path) as fh:
            return json.load(fh)
    return {}


def generate_language_config(languages_str):
    languages = [l.strip() for l in languages_str.split(",")]
    return {
        "python": "python" in languages,
        "java": "java" in languages,
        "javascript": "javascript" in languages,
        "go": "go" in languages,
    }


# ---------------------------------------------------------------------------
# Stage builders
# ---------------------------------------------------------------------------

def _global_section(args):
    """Top-level GitLab CI globals."""
    stages = []
    if args.type in ("build", "complete"):
        stages.append("build")
    if args.type in ("test", "complete"):
        stages.append("test")
    if args.type in ("deploy", "complete") and args.kubernetes:
        stages.append("deploy")

    return {
        "stages": stages,
        "variables": {
            "APP_NAME": args.name,
            "IMAGE_TAG": "$CI_COMMIT_SHORT_SHA",
            "REGISTRY": "$CI_REGISTRY",
            "REGISTRY_IMAGE": "$CI_REGISTRY_IMAGE",
        },
    }


def _build_job(args, lang_config):
    """Docker build + push job."""
    script = [
        "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY",
        "docker build -t $REGISTRY_IMAGE:$IMAGE_TAG .",
        "docker push $REGISTRY_IMAGE:$IMAGE_TAG",
        "docker tag $REGISTRY_IMAGE:$IMAGE_TAG $REGISTRY_IMAGE:latest",
        "docker push $REGISTRY_IMAGE:latest",
    ]

    # Language-specific compile/package steps before Docker build
    pre = []
    if lang_config["python"]:
        pre += [
            "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi",
            "if [ -f setup.py ] || [ -f pyproject.toml ]; then pip install -e .; fi",
        ]
    if lang_config["java"]:
        pre += [
            "if [ -f pom.xml ]; then mvn -B package -DskipTests --file pom.xml; fi",
            "if [ -f build.gradle ]; then ./gradlew assemble; fi",
        ]
    if lang_config["javascript"]:
        pre += [
            "if [ -f package.json ]; then npm ci && npm run build --if-present; fi",
        ]
    if lang_config["go"]:
        pre += [
            "if [ -f go.mod ]; then go build -v ./...; fi",
        ]

    image = getattr(args, "image", "docker:24")
    if isinstance(image, str) and image.startswith("docker:"):
        dind_service = f"{image}-dind"
    else:
        dind_service = "docker:24-dind"

    return {
        "build": {
            "stage": "build",
            "image": image,
            "services": [dind_service],
            "variables": {"DOCKER_TLS_CERTDIR": "/certs"},
            "script": pre + script,
            "rules": [{"if": "$CI_COMMIT_BRANCH", "when": "always"}],
        }
    }


def _test_job(lang_config):
    """Language-specific test jobs."""
    jobs = {}

    if lang_config["python"]:
        jobs["test:python"] = {
            "stage": "test",
            "image": "python:3.11-slim",
            "script": [
                "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi",
                "pip install pytest pytest-cov",
                "if [ -d tests ] || [ -d test ]; then python -m pytest --cov=./ --cov-report=xml -v; fi",
            ],
            "coverage": r"/TOTAL.*\s+(\d+%)$/",
            "artifacts": {
                "reports": {"coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}},
                "when": "always",
            },
            "rules": [{"if": "$CI_COMMIT_BRANCH", "when": "always"},
                      {"if": "$CI_MERGE_REQUEST_ID", "when": "always"}],
        }

    if lang_config["java"]:
        jobs["test:java"] = {
            "stage": "test",
            "image": "maven:3.9-eclipse-temurin-17",
            "script": [
                "if [ -f pom.xml ]; then mvn -B test --file pom.xml; fi",
                "if [ -f build.gradle ]; then ./gradlew test; fi",
            ],
            "artifacts": {
                "reports": {"junit": ["**/target/surefire-reports/*.xml", "**/build/test-results/**/*.xml"]},
                "when": "always",
            },
            "rules": [{"if": "$CI_COMMIT_BRANCH", "when": "always"},
                      {"if": "$CI_MERGE_REQUEST_ID", "when": "always"}],
        }

    if lang_config["javascript"]:
        jobs["test:javascript"] = {
            "stage": "test",
            "image": "node:20-slim",
            "script": [
                "if [ -f package.json ]; then npm ci && npm test -- --ci; fi",
            ],
            "artifacts": {
                "reports": {"junit": ["junit.xml", "test-results/junit.xml"]},
                "when": "always",
            },
            "rules": [{"if": "$CI_COMMIT_BRANCH", "when": "always"},
                      {"if": "$CI_MERGE_REQUEST_ID", "when": "always"}],
        }

    if lang_config["go"]:
        jobs["test:go"] = {
            "stage": "test",
            "image": "golang:1.21",
            "script": [
                "if [ -f go.mod ]; then go test -v -coverprofile=coverage.out ./...; fi",
                "if [ -f coverage.out ]; then go tool cover -func=coverage.out; fi",
            ],
            "rules": [{"if": "$CI_COMMIT_BRANCH", "when": "always"},
                      {"if": "$CI_MERGE_REQUEST_ID", "when": "always"}],
        }

    return jobs


def _deploy_job(args):
    """Kubernetes deploy job."""
    if not args.kubernetes:
        return {}

    protected_branches = [b.strip() for b in args.branches.split(",")]

    if args.k8s_method == "kubectl":
        script = [
            "kubectl config use-context $KUBE_CONTEXT",
            "kubectl set image deployment/$APP_NAME $APP_NAME=$REGISTRY_IMAGE:$IMAGE_TAG --namespace=$KUBE_NAMESPACE",
            "kubectl rollout status deployment/$APP_NAME --namespace=$KUBE_NAMESPACE",
        ]
    elif args.k8s_method == "kustomize":
        script = [
            "kustomize edit set image $REGISTRY_IMAGE=$REGISTRY_IMAGE:$IMAGE_TAG",
            "kustomize build . | kubectl apply -f - --namespace=$KUBE_NAMESPACE",
            "kubectl rollout status deployment/$APP_NAME --namespace=$KUBE_NAMESPACE",
        ]
    elif args.k8s_method == "argocd":
        script = [
            "argocd login $ARGOCD_SERVER --auth-token $ARGOCD_TOKEN --insecure",
            f"argocd app set {args.name} --helm-set image.tag=$IMAGE_TAG",
            f"argocd app sync {args.name} --force",
            f"argocd app wait {args.name} --health --timeout 120",
        ]
    else:  # flux
        script = [
            "flux reconcile image repository $APP_NAME",
            "flux reconcile kustomization $APP_NAME",
        ]

    rules = [
        {"if": f"$CI_COMMIT_BRANCH == \"{b}\"", "when": "manual" if b != protected_branches[0] else "on_success"}
        for b in protected_branches
    ]

    # Select a method-appropriate image so that the required CLI is present.
    deploy_image = {
        "kubectl":    "bitnami/kubectl:1.29",
        "kustomize":  "bitnami/kubectl:1.29",   # kubectl 1.14+ ships kustomize built-in
        "argocd":     "argoproj/argocd:v2.11.0",
        "flux":       "fluxcd/flux-cli:v2.3.0",
    }.get(args.k8s_method, "bitnami/kubectl:1.29")

    job: dict = {
        "stage": "deploy",
        "image": deploy_image,
        "environment": {"name": "$CI_COMMIT_BRANCH", "url": "https://$APP_NAME.$KUBE_NAMESPACE.example.com"},
        "script": script,
        "rules": rules,
    }
    # Only pin KUBE_NAMESPACE in the job when the user provided one at generation time.
    # If omitted, the value set in GitLab CI/CD Variables takes effect.
    kube_namespace = getattr(args, "kube_namespace", "")
    if kube_namespace:
        job["variables"] = {"KUBE_NAMESPACE": kube_namespace}
    return {"deploy:kubernetes": job}


# ---------------------------------------------------------------------------
# Pipeline assemblers
# ---------------------------------------------------------------------------

def generate_pipeline(args, custom_values):
    lang_config = generate_language_config(args.languages)
    pipeline = _global_section(args)

    if args.type in ("build", "complete"):
        pipeline.update(_build_job(args, lang_config))

    if args.type in ("test", "complete"):
        pipeline.update(_test_job(lang_config))

    if args.type in ("deploy", "complete") and args.kubernetes:
        pipeline.update(_deploy_job(args))

    pipeline.update(custom_values)
    return pipeline


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    custom_values = load_custom_values(args.custom_values)
    pipeline = generate_pipeline(args, custom_values)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as fh:
        yaml.dump(pipeline, fh, sort_keys=False, default_flow_style=False)

    print(f"GitLab CI pipeline generated: {output_path}")
    print(f"Type: {args.type}")
    print(f"Languages: {args.languages}")
    if args.kubernetes:
        print(f"Kubernetes deployment method: {args.k8s_method}")


if __name__ == "__main__":
    main()
