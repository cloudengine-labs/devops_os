# Kubernetes Cluster Connection and Configuration in DevOps-OS

This guide explains how to use the Kubernetes tools and capabilities available in your DevOps-OS development container.

## Available Kubernetes Tools

Your DevOps-OS container includes the following Kubernetes tools (when enabled in the configuration):

- **kubectl**: The Kubernetes command-line tool
- **Helm**: The Kubernetes package manager
- **K9s**: A terminal UI to interact with your Kubernetes clusters
- **Kustomize**: Kubernetes configuration customization tool
- **ArgoCD CLI**: Command-line interface for Argo CD
- **Kubeseal**: Client-side tool for Sealed Secrets
- **Flux CLI**: Command-line interface for GitOps with Flux
- **KinD**: Kubernetes in Docker - for creating local Kubernetes clusters
- **Minikube**: Run Kubernetes locally
- **OpenShift CLI**: Command-line interface for OpenShift (optional)

## Kubernetes Configuration Generator

The DevOps-OS container includes a Kubernetes configuration generator that helps you create deployment manifests for various methods:

```bash
# Basic usage - creates a simple kubectl deployment
k8s-config-generator --app-name my-app --environment dev

# Generate Kustomize configuration
k8s-config-generator --app-name my-app --environment prod --method kustomize

# Generate ArgoCD configuration
k8s-config-generator --app-name my-app --environment staging --method argocd

# Generate Flux configuration
k8s-config-generator --app-name my-app --environment test --method flux --registry ghcr.io/myorg --image-tag v1.0.0

# Use custom values from a JSON file
k8s-config-generator --app-name my-app --environment dev --custom-values my-values.json
```

The generator creates a standardized directory structure for Kubernetes manifests based on best practices for each deployment method.

## Connecting to a Kubernetes Cluster

### 1. Using kubeconfig files

The container is configured to use Kubernetes configuration from your host machine. Your `~/.kube` directory is shared with the container, allowing you to access your existing cluster configurations.

To check your available clusters:

```bash
kubectl config get-contexts
```

To switch between contexts:

```bash
kubectl config use-context <context-name>
```

### 2. Creating a local development cluster

You can create a local Kubernetes cluster for development using either KinD or Minikube:

#### Using KinD (Kubernetes in Docker)

```bash
# Create a cluster
kind create cluster --name devops-os-cluster

# Verify it's working
kubectl cluster-info --context kind-devops-os-cluster

# Delete the cluster when done
kind delete cluster --name devops-os-cluster
```

#### Using Minikube

```bash
# Start minikube
minikube start

# Verify it's working
kubectl get nodes

# Stop minikube when done
minikube stop
```

## Using K9s UI for Cluster Management

K9s provides a terminal UI for managing your Kubernetes clusters:

```bash
# Start K9s
k9s
```

Navigate using keyboard shortcuts (press `?` for help).

## GitOps with ArgoCD and Flux

### Using ArgoCD

```bash
# Login to ArgoCD server
argocd login <argocd-server>

# Create an application
argocd app create <app-name> \
  --repo <git-repo-url> \
  --path <path-in-repo> \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace <namespace>

# Sync an application
argocd app sync <app-name>
```

### Using Flux

```bash
# Bootstrap flux on a cluster
flux bootstrap github \
  --owner=<github-username> \
  --repository=<repository-name> \
  --path=clusters/my-cluster

# Create a GitRepository source
flux create source git <source-name> \
  --url=<git-repo-url> \
  --branch=main \
  --interval=1m

# Create a Kustomization to deploy resources
flux create kustomization <name> \
  --source=<source-name> \
  --path="./kustomize" \
  --prune=true \
  --interval=10m
```

## Using Helm for Package Management

```bash
# Add a Helm repository
helm repo add <repo-name> <repo-url>
helm repo update

# Search for charts
helm search repo <keyword>

# Install a chart
helm install <release-name> <repo-name>/<chart-name> -n <namespace>

# List installed releases
helm list --all-namespaces
```

## Using Kustomize for Configuration Management

```bash
# Create a kustomization.yaml file
cat > kustomization.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
namespace: my-app
EOF

# Build and apply the kustomization
kubectl apply -k .
```

## Using Sealed Secrets with Kubeseal

```bash
# Create a sealed secret
kubectl create secret generic mysecret \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml | \
  kubeseal --controller-name=sealed-secrets \
  --format yaml > sealed-secret.yaml

# Apply the sealed secret
kubectl apply -f sealed-secret.yaml
```

## Best Practices for Kubernetes in CI/CD

When integrating Kubernetes with your CI/CD pipelines:

1. **Use namespaces for isolation**: Create separate namespaces for different environments or applications
2. **Implement GitOps workflows**: Use Flux or ArgoCD for GitOps-based deployments
3. **Secure secrets**: Use Sealed Secrets or external secret management solutions
4. **Use Helm or Kustomize**: Package your applications with Helm or use Kustomize for customization
5. **Implement progressive delivery**: Use tools like Argo Rollouts or Flagger for progressive delivery

## Configuring the DevOps-OS Container for Kubernetes

You can customize which Kubernetes tools are included in your container by editing the `.devcontainer/devcontainer.env.json` file:

```json
{
  "kubernetes": {
    "k9s": true,
    "kustomize": true,
    "argocd_cli": true,
    "lens": false,
    "kubeseal": true,
    "flux": true,
    "kind": true,
    "minikube": true,
    "openshift_cli": false
  },
  "versions": {
    "k9s": "0.29.1",
    "argocd": "2.8.4",
    "flux": "2.1.2",
    "kustomize": "5.2.1"
  }
}
```

After modifying the configuration, run the configure script to update your container:

```bash
cd .devcontainer
python configure.py
```

Then rebuild your container to apply the changes.
