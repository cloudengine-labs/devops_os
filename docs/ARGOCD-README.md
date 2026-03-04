# ArgoCD & Flux CD Configuration Generator

DevOps-OS can generate production-ready GitOps configuration files for both
**ArgoCD** and **Flux CD** in a single command.

## Quick Start

```bash
# ArgoCD Application + AppProject
python -m cli.scaffold_argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --namespace production

# ArgoCD with canary rollout (Argo Rollouts)
python -m cli.scaffold_argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --rollouts \
  --auto-sync

# Flux CD Kustomization + GitRepository + Image Automation
python -m cli.scaffold_argocd \
  --name my-app \
  --method flux \
  --repo https://github.com/myorg/my-app.git \
  --image ghcr.io/myorg/my-app
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `my-app` | Application name |
| `--method` | `argocd` | GitOps tool: `argocd` or `flux` |
| `--repo` | `https://github.com/myorg/my-app.git` | Git repository URL |
| `--revision` | `HEAD` | Branch / tag / commit to sync |
| `--path` | `k8s` | Path inside repo to manifests |
| `--namespace` | `default` | Target Kubernetes namespace |
| `--project` | `default` | ArgoCD project name |
| `--server` | `https://kubernetes.default.svc` | Destination API server |
| `--auto-sync` | off | Enable automated sync (prune + self-heal) |
| `--rollouts` | off | Add an Argo Rollouts canary resource |
| `--image` | `ghcr.io/myorg/my-app` | Image for Flux image automation |
| `--output-dir` | `.` | Root directory for output files |
| `--allow-any-source-repo` | off | Add `*` to AppProject `sourceRepos` (grants access to any repo — use with caution) |

All options can also be set via environment variables prefixed with `DEVOPS_OS_ARGOCD_`
(e.g. `DEVOPS_OS_ARGOCD_AUTO_SYNC=true`).

## ArgoCD Output Files

```
argocd/
├── application.yaml    ArgoCD Application CR
├── appproject.yaml     ArgoCD AppProject CR
└── rollout.yaml        Argo Rollouts Rollout (--rollouts only)
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

Restricts which repositories and namespaces the application can target, following
the principle of least privilege.

### rollout.yaml (--rollouts)

Generates an Argo Rollouts **canary strategy** that gradually shifts traffic:

```
10% → 1 min wait → 30% → 2 min wait → 60% → 2 min wait → 100%
```

## Flux CD Output Files

```
flux/
├── git-repository.yaml           Flux GitRepository source
├── kustomization.yaml            Flux Kustomization
└── image-update-automation.yaml  ImageRepository + ImagePolicy + ImageUpdateAutomation
```

The image update automation configures Flux to watch the container registry and
automatically open a commit / PR when a new semver-compatible image is pushed.

## Applying the Configs

### ArgoCD

```bash
# Apply to your cluster (ArgoCD namespace must exist)
kubectl apply -f argocd/appproject.yaml
kubectl apply -f argocd/application.yaml

# Watch sync status
argocd app get my-app
argocd app sync my-app
```

### Flux CD

```bash
# Bootstrap Flux (first time only)
flux bootstrap github --owner=myorg --repository=my-app --branch=main --path=flux

# Apply generated resources
kubectl apply -f flux/git-repository.yaml
kubectl apply -f flux/kustomization.yaml
kubectl apply -f flux/image-update-automation.yaml

# Watch reconciliation
flux get kustomizations
flux logs --follow
```

## Related Guides

- [Getting Started](GETTING-STARTED.md)
- [Kubernetes Deployment](KUBERNETES-DEPLOYMENT-README.md)
- [GitLab CI Generator](GITLAB-CI-README.md)
- [SRE Configuration](SRE-CONFIGURATION-README.md)
