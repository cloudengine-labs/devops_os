---
title: "Kubernetes"
weight: 50
---

# Kubernetes Deployment Configuration

DevOps-OS provides a Kubernetes configuration generator (`k8s-config-generator.py`) that creates YAML manifest files for deploying your applications to Kubernetes clusters.

---

## Basic Usage

```bash
python kubernetes/k8s-config-generator.py --name my-app --image ghcr.io/myorg/my-app:v1
```

Generated files are written to the `./k8s` directory by default.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `app` | Application name |
| `--namespace NS` | `default` | Kubernetes namespace |
| `--image IMAGE` | `docker.io/yourorg/app:latest` | Container image |
| `--port PORT` | `8080` | Port your application listens on |
| `--replicas N` | `1` | Number of pod replicas |
| `--output DIR` | `./k8s` | Output directory for generated files |
| `--containers NAMES` | _(single)_ | Comma-separated container names for multi-container pods |
| `--ingress` | off | Add an Ingress resource |
| `--storage` | off | Add a PersistentVolumeClaim |
| `--kustomize` | off | Add Kustomize base + overlays structure |
| `--environments ENVS` | _(single)_ | Comma-separated environments (e.g. `dev,staging,prod`) |

---

## Examples

### Single container application

```bash
python kubernetes/k8s-config-generator.py \
  --name backend-api \
  --namespace backend \
  --image docker.io/myorg/api:v1.0 \
  --port 3000 \
  --replicas 3
# Output: k8s/deployment.yaml + k8s/service.yaml
```

### With Ingress and persistent storage

```bash
python kubernetes/k8s-config-generator.py \
  --name web-app \
  --ingress \
  --storage
# Output: k8s/deployment.yaml + k8s/service.yaml + k8s/ingress.yaml + k8s/pvc.yaml
```

### Multi-environment with Kustomize

```bash
python kubernetes/k8s-config-generator.py \
  --name my-app \
  --kustomize \
  --environments dev,staging,prod
# Output: k8s/base/ + k8s/overlays/dev/ + k8s/overlays/staging/ + k8s/overlays/prod/
```

---

## Applying Configurations

```bash
# Apply with kubectl
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Apply all files
kubectl apply -f k8s/

# Apply with Kustomize overlay
kubectl apply -k k8s/overlays/dev

# Deploy with ArgoCD (after generating ArgoCD configs)
python -m cli.devopsos scaffold argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --path k8s --namespace production
kubectl apply -f argocd/appproject.yaml
kubectl apply -f argocd/application.yaml
```

---

## Integration with CI/CD Generators

Use the Kubernetes generator alongside the CI/CD generators for a complete pipeline:

```bash
# Generate the K8s manifests
python kubernetes/k8s-config-generator.py --name my-api --replicas 3

# Generate a GitHub Actions workflow that deploys to K8s
python -m cli.devopsos scaffold gha \
  --name my-api \
  --kubernetes \
  --k8s-method kustomize

# Or generate an ArgoCD Application pointing to the k8s/ directory
python -m cli.devopsos scaffold argocd \
  --name my-api \
  --repo https://github.com/myorg/my-api.git \
  --path k8s \
  --auto-sync
```

---

## GitOps Deployment

For GitOps-based deployment, generate ArgoCD or Flux configs that watch the `k8s/` directory in your repository:

```bash
# ArgoCD watches k8s/ directory
python -m cli.devopsos scaffold argocd \
  --name my-app \
  --path k8s \
  --repo https://github.com/myorg/my-app.git

# Flux CD watches k8s/ directory
python -m cli.devopsos scaffold argocd \
  --name my-app \
  --method flux \
  --path k8s \
  --repo https://github.com/myorg/my-app.git
```

Commit the generated `k8s/` directory to your repo — ArgoCD/Flux will automatically apply changes on every push.
