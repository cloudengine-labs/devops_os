# Creating Kubernetes Deployments

This guide covers how to generate and manage Kubernetes deployment configurations using DevOps-OS tooling. The Kubernetes configuration generator helps you create deployment manifests for various application types and deployment strategies.

## Table of Contents

- [Understanding the Kubernetes Configuration Generator](#understanding-the-kubernetes-configuration-generator)
- [Basic Usage](#basic-usage)
- [Configuration Options](#configuration-options)
- [Deployment Types](#deployment-types)
- [Environment Configurations](#environment-configurations)
- [Advanced Features](#advanced-features)
- [Deployment Methods](#deployment-methods)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Understanding the Kubernetes Configuration Generator

The Kubernetes configuration generator (`k8s-config-generator.py`) creates YAML manifest files for deploying your applications to Kubernetes clusters. It generates resources such as Deployments, Services, ConfigMaps, Secrets, and more, tailored to your application needs.

## Basic Usage

To generate basic Kubernetes configurations:

```bash
python k8s-config-generator.py --name my-application
```

This creates a set of YAML files in the `./k8s` directory.

## Configuration Options

### Basic Options

- `--name`: The name of your application (default: "app")
- `--namespace`: The Kubernetes namespace to deploy to (default: "default")
- `--image`: The container image to use (default: "docker.io/yourorg/app:latest")
- `--port`: The port your application listens on (default: "8080")
- `--replicas`: The number of replicas to deploy (default: "1")
- `--output`: Output directory for generated files (default: "./k8s")

### Example with Basic Options

```bash
python k8s-config-generator.py --name backend-api --namespace backend --image docker.io/myorg/api:v1.0 --port 3000 --replicas 3
```

## Deployment Types

The generator supports various deployment types:

### Single Container Application

```bash
python k8s-config-generator.py --name web-app
```

### Multi-container Application

```bash
python k8s-config-generator.py --name backend --containers app,db,cache
```

This creates a deployment with multiple containers in the same pod.

### Microservices

```bash
python k8s-config-generator.py --name platform --services api,auth,frontend,db --service-type microservices
```

This creates separate deployments and services for each microservice.

## Environment Configurations

### Multiple Environments

Generate configurations for different environments:

```bash
python k8s-config-generator.py --name webstore --environments dev,test,staging,prod
```

This creates environment-specific configurations in `./k8s/overlays/{env}`.

### Environment Variables

Configure environment variables for your applications:

```bash
python k8s-config-generator.py --name api --env-vars "DB_HOST=postgres,DB_PORT=5432,API_KEY=secret"
```

### ConfigMaps and Secrets

Generate ConfigMaps and Secrets for configuration:

```bash
python k8s-config-generator.py --name app --config-map config.json --secrets-file secrets.json
```

## Advanced Features

### Resource Requirements

Specify CPU and memory requirements:

```bash
python k8s-config-generator.py --name api --cpu 500m --memory 512Mi --cpu-limit 1000m --memory-limit 1Gi
```

### Health Checks

Configure health checks:

```bash
python k8s-config-generator.py --name service --health-check --liveness-path /health --readiness-path /ready
```

### Persistent Storage

Add persistent storage:

```bash
python k8s-config-generator.py --name db --storage --storage-size 10Gi --storage-class standard
```

### Network Policies

Generate network policies:

```bash
python k8s-config-generator.py --name app --network-policy
```

### Service Mesh

Generate configurations for service mesh integration:

```bash
python k8s-config-generator.py --name api --service-mesh istio
```

## Deployment Methods

### Basic Kubectl

Generate configurations for direct kubectl deployment:

```bash
python k8s-config-generator.py --name app --method kubectl
```

Usage:
```bash
kubectl apply -f ./k8s/deployment.yaml
kubectl apply -f ./k8s/service.yaml
```

### Kustomize

Generate configurations for Kustomize:

```bash
python k8s-config-generator.py --name app --method kustomize --environments dev,prod
```

Usage:
```bash
kubectl apply -k ./k8s/overlays/dev
```

### Helm Chart

Generate a Helm chart:

```bash
python k8s-config-generator.py --name app --method helm
```

Usage:
```bash
helm install my-release ./k8s/helm/app
```

### ArgoCD

Generate configurations for ArgoCD:

```bash
python k8s-config-generator.py --name app --method argocd
```

This creates configurations suitable for ArgoCD application deployment.

### Flux CD

Generate configurations for Flux CD:

```bash
python k8s-config-generator.py --name app --method flux
```

This creates configurations suitable for Flux CD GitOps deployment.

## Examples

### Web Application with Ingress

```bash
python k8s-config-generator.py --name webapp --port 80 --ingress --ingress-host webapp.example.com
```

### Database with Persistent Storage

```bash
python k8s-config-generator.py --name postgres --image postgres:13 --port 5432 --storage --storage-size 20Gi
```

### Microservices Platform

```bash
python k8s-config-generator.py --name platform --services "frontend:80,api:8080,auth:9000,db:5432" --method kustomize --environments dev,prod
```

### Scaling Application

```bash
python k8s-config-generator.py --name api --replicas 3 --autoscaling --min-replicas 2 --max-replicas 10 --cpu-target 70
```

### Secure Application

```bash
python k8s-config-generator.py --name secure-app --tls --network-policy --pod-security-policy
```

## Understanding the Generated Configurations

The generator creates various Kubernetes resource definitions:

### Base Resources

- **Deployment**: Defines how your application should be deployed.
- **Service**: Exposes your application within the cluster.
- **ConfigMap**: Provides configuration data.
- **Secret**: Provides sensitive configuration data.

### Additional Resources

- **Ingress**: Exposes HTTP/HTTPS routes to services.
- **HorizontalPodAutoscaler**: Automatically scales your application.
- **PersistentVolumeClaim**: Provides persistent storage.
- **NetworkPolicy**: Defines network access rules.
- **ServiceAccount**: Provides an identity for your application.

### Directory Structure

```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patches/
    ├── test/
    │   ├── kustomization.yaml
    │   └── patches/
    └── prod/
        ├── kustomization.yaml
        └── patches/
```

## Integration with CI/CD

The Kubernetes configurations can be integrated with your CI/CD pipelines:

### GitHub Actions Integration

```bash
python github-actions-generator-improved.py --kubernetes --k8s-method kustomize
```

### Jenkins Integration

```bash
python jenkins-pipeline-generator-improved.py --kubernetes --k8s-method argocd
```

## Best Practices

1. **Start Simple**: Begin with basic deployments and add complexity as needed.
2. **Use Namespaces**: Isolate your applications in separate namespaces.
3. **Resource Limits**: Always specify resource requests and limits.
4. **Health Checks**: Implement liveness and readiness probes.
5. **Environment Separation**: Use Kustomize or Helm for environment-specific configurations.
6. **Secret Management**: Use Kubernetes Secrets or external secret management tools.
7. **GitOps**: Consider GitOps approaches with tools like ArgoCD or Flux.
8. **Security**: Implement network policies and pod security policies.

## Next Steps

- Learn about [Creating Customized GitHub Actions Templates](./GITHUB-ACTIONS-README.md)
- Learn about [Creating Customized Jenkins Pipeline Templates](./JENKINS-PIPELINE-README.md)
- Explore [Implementing CI/CD Pipelines for Technology Stacks](./CICD-TECH-STACK-README.md)
