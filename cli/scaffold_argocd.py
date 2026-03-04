#!/usr/bin/env python3
"""
DevOps-OS ArgoCD / GitOps Config Generator

Generates ArgoCD Application, AppProject, and supporting Kubernetes resources
for GitOps-based continuous delivery. Also supports generating a Flux
Kustomization when --method flux is selected.

Outputs:
  argocd/                          (default output dir)
  ├── application.yaml             ArgoCD Application CR
  ├── appproject.yaml              ArgoCD AppProject CR
  └── rollout.yaml                 Argo Rollouts (when --rollouts flag used)
  flux/
  ├── kustomization.yaml           Flux Kustomization
  └── image-update-automation.yaml Flux image update automation
"""

import os
import argparse
import json
import yaml
from pathlib import Path

ENV_PREFIX = "DEVOPS_OS_ARGOCD_"
METHODS = ["argocd", "flux"]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate ArgoCD / Flux GitOps configs for DevOps-OS")
    parser.add_argument("--name", default=os.environ.get(f"{ENV_PREFIX}NAME", "my-app"),
                        help="Application name")
    parser.add_argument("--method", choices=METHODS,
                        default=os.environ.get(f"{ENV_PREFIX}METHOD", "argocd"),
                        help="GitOps tool: argocd or flux")
    parser.add_argument("--repo", default=os.environ.get(f"{ENV_PREFIX}REPO", "https://github.com/myorg/my-app.git"),
                        help="Git repository URL for the application manifests")
    parser.add_argument("--revision", default=os.environ.get(f"{ENV_PREFIX}REVISION", "HEAD"),
                        help="Git revision / branch / tag to sync")
    parser.add_argument("--path", default=os.environ.get(f"{ENV_PREFIX}PATH", "k8s"),
                        help="Path inside the repository to the manifests")
    parser.add_argument("--namespace", default=os.environ.get(f"{ENV_PREFIX}NAMESPACE", "default"),
                        help="Kubernetes namespace to deploy into")
    parser.add_argument("--project", default=os.environ.get(f"{ENV_PREFIX}PROJECT", "default"),
                        help="ArgoCD project name")
    parser.add_argument("--server", default=os.environ.get(f"{ENV_PREFIX}SERVER", "https://kubernetes.default.svc"),
                        help="Destination Kubernetes API server")
    parser.add_argument("--auto-sync", action="store_true",
                        default=os.environ.get(f"{ENV_PREFIX}AUTO_SYNC", "false").lower() in ("true", "1", "yes"),
                        help="Enable ArgoCD auto-sync policy")
    parser.add_argument("--rollouts", action="store_true",
                        default=os.environ.get(f"{ENV_PREFIX}ROLLOUTS", "false").lower() in ("true", "1", "yes"),
                        help="Generate an Argo Rollouts canary strategy")
    parser.add_argument("--image", default=os.environ.get(f"{ENV_PREFIX}IMAGE", "ghcr.io/myorg/my-app"),
                        help="Container image (used in Rollouts / Flux image automation)")
    parser.add_argument("--output-dir", default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", "."),
                        help="Root output directory")
    parser.add_argument("--custom-values", default=None,
                        help="Path to custom values JSON file")
    parser.add_argument("--allow-any-source-repo", action="store_true",
                        default=os.environ.get(f"{ENV_PREFIX}ALLOW_ANY_SOURCE_REPO", "false").lower() in ("true", "1", "yes"),
                        help="Add '*' to AppProject sourceRepos (opt-in; grants access to any repo)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_custom_values(file_path):
    if file_path and os.path.exists(file_path):
        with open(file_path) as fh:
            return json.load(fh)
    return {}


def _write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        yaml.dump(data, fh, sort_keys=False, default_flow_style=False)
    return path


# ---------------------------------------------------------------------------
# ArgoCD generators
# ---------------------------------------------------------------------------

def generate_argocd_application(args):
    """Generate an ArgoCD Application Custom Resource."""
    sync_policy = {}
    if args.auto_sync:
        sync_policy = {
            "automated": {"prune": True, "selfHeal": True},
            "syncOptions": ["CreateNamespace=true"],
        }
    else:
        sync_policy = {"syncOptions": ["CreateNamespace=true"]}

    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": args.name,
            "namespace": "argocd",
            "labels": {"app.kubernetes.io/name": args.name},
        },
        "spec": {
            "project": args.project,
            "source": {
                "repoURL": args.repo,
                "targetRevision": args.revision,
                "path": args.path,
            },
            "destination": {
                "server": args.server,
                "namespace": args.namespace,
            },
            "syncPolicy": sync_policy,
        },
    }


def generate_argocd_appproject(args):
    """Generate an ArgoCD AppProject Custom Resource."""
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "AppProject",
        "metadata": {
            "name": args.project,
            "namespace": "argocd",
        },
        "spec": {
            "description": f"Project for {args.name} deployments",
            "sourceRepos": [args.repo, "*"] if getattr(args, "allow_any_source_repo", False) else [args.repo],
            "destinations": [
                {"namespace": args.namespace, "server": args.server},
                {"namespace": "argocd", "server": args.server},
            ],
            "clusterResourceWhitelist": [
                {"group": "*", "kind": "Namespace"},
            ],
            "namespaceResourceWhitelist": [
                {"group": "apps", "kind": "Deployment"},
                {"group": "apps", "kind": "StatefulSet"},
                {"group": "", "kind": "Service"},
                {"group": "", "kind": "ConfigMap"},
                {"group": "", "kind": "Secret"},
                {"group": "networking.k8s.io", "kind": "Ingress"},
            ],
        },
    }


def generate_argo_rollout(args):
    """Generate an Argo Rollouts canary Rollout resource."""
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Rollout",
        "metadata": {"name": args.name, "namespace": args.namespace},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": args.name}},
            "template": {
                "metadata": {"labels": {"app": args.name}},
                "spec": {
                    "containers": [
                        {
                            "name": args.name,
                            "image": f"{args.image}:stable",
                            "ports": [{"containerPort": 8080}],
                        }
                    ]
                },
            },
            "strategy": {
                "canary": {
                    "steps": [
                        {"setWeight": 10},
                        {"pause": {"duration": "1m"}},
                        {"setWeight": 30},
                        {"pause": {"duration": "2m"}},
                        {"setWeight": 60},
                        {"pause": {"duration": "2m"}},
                        {"setWeight": 100},
                    ]
                }
            },
        },
    }


# ---------------------------------------------------------------------------
# Flux generators
# ---------------------------------------------------------------------------

def generate_flux_kustomization(args):
    """Generate a Flux CD Kustomization resource."""
    return {
        "apiVersion": "kustomize.toolkit.fluxcd.io/v1",
        "kind": "Kustomization",
        "metadata": {"name": args.name, "namespace": "flux-system"},
        "spec": {
            "interval": "10m",
            "retryInterval": "1m",
            "timeout": "5m",
            "prune": True,
            "sourceRef": {"kind": "GitRepository", "name": args.name},
            "path": f"./{args.path}",
            "targetNamespace": args.namespace,
            "healthChecks": [
                {"apiVersion": "apps/v1", "kind": "Deployment", "name": args.name, "namespace": args.namespace}
            ],
        },
    }


def generate_flux_git_repository(args):
    """Generate a Flux CD GitRepository source."""
    return {
        "apiVersion": "source.toolkit.fluxcd.io/v1",
        "kind": "GitRepository",
        "metadata": {"name": args.name, "namespace": "flux-system"},
        "spec": {
            "interval": "1m",
            "url": args.repo,
            "ref": {"branch": args.revision if args.revision != "HEAD" else "main"},
        },
    }


def generate_flux_image_automation(args):
    """Generate Flux image update automation resources."""
    image_repo = {
        "apiVersion": "image.toolkit.fluxcd.io/v1beta2",
        "kind": "ImageRepository",
        "metadata": {"name": args.name, "namespace": "flux-system"},
        "spec": {"image": args.image, "interval": "5m"},
    }
    image_policy = {
        "apiVersion": "image.toolkit.fluxcd.io/v1beta2",
        "kind": "ImagePolicy",
        "metadata": {"name": args.name, "namespace": "flux-system"},
        "spec": {
            "imageRepositoryRef": {"name": args.name},
            "policy": {"semver": {"range": ">=1.0.0"}},
        },
    }
    image_update = {
        "apiVersion": "image.toolkit.fluxcd.io/v1beta1",
        "kind": "ImageUpdateAutomation",
        "metadata": {"name": args.name, "namespace": "flux-system"},
        "spec": {
            "interval": "30m",
            "sourceRef": {"kind": "GitRepository", "name": args.name},
            "git": {
                "checkout": {"ref": {"branch": "main"}},
                "commit": {
                    "author": {"email": "fluxcdbot@users.noreply.github.com", "name": "FluxBot"},
                    "messageTemplate": f"chore: update {args.name} image to {{{{.AutomationObject}}}}",
                },
                "push": {"branch": "main"},
            },
            "update": {"path": f"./{args.path}", "strategy": "Setters"},
        },
    }
    return image_repo, image_policy, image_update


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    custom_values = load_custom_values(args.custom_values)  # noqa: F841
    output_root = Path(args.output_dir)
    generated = []

    if args.method == "argocd":
        out_dir = output_root / "argocd"

        app = generate_argocd_application(args)
        path = _write_yaml(out_dir / "application.yaml", app)
        generated.append(str(path))

        project = generate_argocd_appproject(args)
        path = _write_yaml(out_dir / "appproject.yaml", project)
        generated.append(str(path))

        if args.rollouts:
            rollout = generate_argo_rollout(args)
            path = _write_yaml(out_dir / "rollout.yaml", rollout)
            generated.append(str(path))

    else:  # flux
        out_dir = output_root / "flux"

        git_repo = generate_flux_git_repository(args)
        path = _write_yaml(out_dir / "git-repository.yaml", git_repo)
        generated.append(str(path))

        kustomization = generate_flux_kustomization(args)
        path = _write_yaml(out_dir / "kustomization.yaml", kustomization)
        generated.append(str(path))

        image_repo, image_policy, image_update = generate_flux_image_automation(args)
        path = _write_yaml(out_dir / "image-update-automation.yaml",
                           [image_repo, image_policy, image_update])
        generated.append(str(path))

    print(f"GitOps configs generated ({args.method}):")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
