---
title: "GitOps — ArgoCD & Flux CD"
weight: 30
---

# GitOps Configuration Generator

DevOps-OS generates production-ready GitOps configuration files for both **ArgoCD** and **Flux CD** in a single command.

---

## Quick Start

```bash
# ArgoCD Application + AppProject
python -m cli.devopsos scaffold argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --namespace production
# Output: argocd/application.yaml + argocd/appproject.yaml

# Flux CD (GitRepository + Kustomization + Image Automation)
python -m cli.devopsos scaffold argocd \
  --name my-app --method flux \
  --repo https://github.com/myorg/my-app.git \
  --image ghcr.io/myorg/my-app
# Output: flux/git-repository.yaml + flux/kustomization.yaml + flux/image-update-automation.yaml
```

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `my-app` | Application name |
| `--method METHOD` | `argocd` | GitOps tool: `argocd` \| `flux` |
| `--repo URL` | `https://github.com/myorg/my-app.git` | Git repository URL |
| `--revision REV` | `HEAD` | Branch / tag / commit to sync |
| `--path PATH` | `k8s` | Path inside the repository to manifests |
| `--namespace NS` | `default` | Target Kubernetes namespace |
| `--project PROJECT` | `default` | ArgoCD project name |
| `--server URL` | `https://kubernetes.default.svc` | Destination Kubernetes API server |
| `--auto-sync` | off | Enable automated sync (prune + self-heal) |
| `--rollouts` | off | Add an Argo Rollouts canary strategy resource |
| `--image IMAGE` | `ghcr.io/myorg/my-app` | Container image (for Rollouts / Flux image automation) |
| `--output-dir DIR` | `.` | Root directory for all output files |
| `--allow-any-source-repo` | off | Allow `*` in AppProject sourceRepos (use with caution) |

All options can be set via environment variables prefixed `DEVOPS_OS_ARGOCD_`.

---

## ArgoCD Output Files

```
argocd/
├── application.yaml    ArgoCD Application CR
├── appproject.yaml     ArgoCD AppProject CR
└── rollout.yaml        Argo Rollouts Rollout (only with --rollouts)
```

### application.yaml

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/my-app.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
```

### appproject.yaml

Restricts which repositories and namespaces the application can target (principle of least privilege).

### rollout.yaml (`--rollouts`)

Generates an Argo Rollouts **canary strategy** that gradually shifts traffic:
```
10% → 1 min wait → 30% → 2 min wait → 60% → 2 min wait → 100%
```

---

## Flux CD Output Files

```
flux/
├── git-repository.yaml           Flux GitRepository source
├── kustomization.yaml            Flux Kustomization
└── image-update-automation.yaml  ImageRepository + ImagePolicy + ImageUpdateAutomation
```

The image update automation configures Flux to watch the container registry and automatically open a commit/PR when a new semver-compatible image is pushed.

---

## Examples

### ArgoCD with automated sync and canary rollout

```bash
python -m cli.devopsos scaffold argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --auto-sync --rollouts
# Output: argocd/application.yaml
#         argocd/appproject.yaml
#         argocd/rollout.yaml
```

### ArgoCD in a custom output directory

```bash
python -m cli.devopsos scaffold argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --namespace production \
  --output-dir gitops
# Output: gitops/argocd/application.yaml
#         gitops/argocd/appproject.yaml
```

### Flux CD with image automation

```bash
python -m cli.devopsos scaffold argocd \
  --name my-app --method flux \
  --repo https://github.com/myorg/my-app.git \
  --image ghcr.io/myorg/my-app \
  --output-dir gitops
# Output: gitops/flux/git-repository.yaml
#         gitops/flux/kustomization.yaml
#         gitops/flux/image-update-automation.yaml
```

---

## Applying the Generated Configs

### ArgoCD

```bash
# Apply AppProject first (it constrains the Application)
kubectl apply -f argocd/appproject.yaml
kubectl apply -f argocd/application.yaml

# Watch sync status
argocd app get my-app
argocd app sync my-app
```

### Flux CD

```bash
# Bootstrap Flux (first time only)
flux bootstrap github \
  --owner=myorg \
  --repository=my-app \
  --branch=main \
  --path=flux

# Apply generated resources
kubectl apply -f flux/git-repository.yaml
kubectl apply -f flux/kustomization.yaml
kubectl apply -f flux/image-update-automation.yaml

# Watch reconciliation
flux get kustomizations
flux logs --follow
```
