#!/usr/bin/env python3
"""
DevOps-OS Helm Chart Generator

Generates a production-ready Helm chart scaffold for Kubernetes deployments.
Creates a complete chart structure with Chart.yaml, values.yaml, and essential
templates for deployment, service, and RBAC resources.

Outputs:
  chart/                          (default output dir)
  ├── Chart.yaml                  Chart metadata
  ├── values.yaml                 Default values
  ├── .helmignore                 Helm ignore patterns
  ├── README.md                   Chart documentation
  └── templates/
      ├── deployment.yaml         Kubernetes Deployment
      ├── service.yaml            Kubernetes Service
      ├── configmap.yaml          ConfigMap for configuration
      ├── _helpers.tpl            Helm template helpers
      └── NOTES.txt               Post-deployment notes
"""

import os
import argparse
import re
import yaml
from pathlib import Path

ENV_PREFIX = "DEVOPS_OS_HELM_"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_helm_chart_name(name):
    """Validate that name is a valid Helm chart name (lowercase alphanumeric and hyphens)."""
    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
        raise ValueError(
            f"Invalid chart name: '{name}'. Chart names must start and end with a lowercase letter or digit, "
            "and contain only lowercase letters, digits, and hyphens."
        )
    return name


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Helm chart for DevOps-OS")
    parser.add_argument("--name", default=os.environ.get(f"{ENV_PREFIX}NAME", "my-app"),
                        help="Application name")
    parser.add_argument("--description", default=os.environ.get(f"{ENV_PREFIX}DESCRIPTION", "A Helm chart for Kubernetes"),
                        help="Chart description")
    parser.add_argument("--chart-version", default=os.environ.get(f"{ENV_PREFIX}CHART_VERSION", "0.1.0"),
                        help="Chart version")
    parser.add_argument("--app-version", default=os.environ.get(f"{ENV_PREFIX}APP_VERSION", "1.0.0"),
                        help="Application version")
    parser.add_argument("--namespace", default=os.environ.get(f"{ENV_PREFIX}NAMESPACE", "default"),
                        help="Kubernetes namespace to deploy into")
    parser.add_argument("--image", default=os.environ.get(f"{ENV_PREFIX}IMAGE", "ghcr.io/myorg/my-app"),
                        help="Container image URL")
    parser.add_argument("--image-tag", default=os.environ.get(f"{ENV_PREFIX}IMAGE_TAG", "latest"),
                        help="Container image tag")
    parser.add_argument("--replicas", type=int, default=int(os.environ.get(f"{ENV_PREFIX}REPLICAS", "1")),
                        help="Number of replicas")
    parser.add_argument("--port", type=int, default=int(os.environ.get(f"{ENV_PREFIX}PORT", "8080")),
                        help="Container port")
    parser.add_argument("--service-type", default=os.environ.get(f"{ENV_PREFIX}SERVICE_TYPE", "ClusterIP"),
                        help="Kubernetes Service type (ClusterIP, NodePort, LoadBalancer)")
    parser.add_argument("--author", default=os.environ.get(f"{ENV_PREFIX}AUTHOR", ""),
                        help="Chart author (optional)")
    parser.add_argument("--author-email", default=os.environ.get(f"{ENV_PREFIX}AUTHOR_EMAIL", ""),
                        help="Chart author email (optional)")
    parser.add_argument("--repo-url", default=os.environ.get(f"{ENV_PREFIX}REPO_URL", ""),
                        help="Repository URL for home and sources (optional)")
    parser.add_argument("--output-dir", default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", "."),
                        help="Root output directory")
    args = parser.parse_args()
    # Validate chart name
    try:
        args.name = _validate_helm_chart_name(args.name)
    except ValueError as e:
        parser.error(str(e))
    return args


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_file(path, content):
    """Write content to a file, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    return path


def _write_yaml(path, data):
    """Write YAML content to a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        yaml.dump(data, fh, sort_keys=False, default_flow_style=False)
    return path


# ---------------------------------------------------------------------------
# Helm Chart generators
# ---------------------------------------------------------------------------

def generate_chart_yaml(args):
    """Generate Chart.yaml with chart metadata."""
    chart = {
        "apiVersion": "v2",
        "name": args.name,
        "description": args.description,
        "type": "application",
        "version": args.chart_version,
        "appVersion": args.app_version,
        "keywords": ["kubernetes", "helm", "application"],
    }
    
    # Add optional maintainer information if provided
    if args.author or args.author_email:
        maintainer = {"name": args.author}
        if args.author_email:
            maintainer["email"] = args.author_email
        chart["maintainers"] = [maintainer]
    
    # Add optional repository URLs if provided
    if args.repo_url:
        chart["home"] = args.repo_url
        chart["sources"] = [args.repo_url]
    
    return chart


def generate_values_yaml(args):
    """Generate values.yaml with default configuration values."""
    return {
        "replicaCount": args.replicas,
        "image": {
            "repository": args.image,
            "pullPolicy": "IfNotPresent",
            "tag": args.image_tag
        },
        "imagePullSecrets": [],
        "nameOverride": "",
        "fullnameOverride": "",
        "serviceAccount": {
            "create": True,
            "annotations": {},
            "name": ""
        },
        "podAnnotations": {},
        "podSecurityContext": {},
        "securityContext": {},
        "service": {
            "type": args.service_type,
            "port": 80,
            "targetPort": args.port,
            "annotations": {}
        },
        "ingress": {
            "enabled": False,
            "className": "nginx",
            "annotations": {},
            "hosts": [
                {
                    "host": f"{args.name}.example.com",
                    "paths": [
                        {
                            "path": "/",
                            "pathType": "Prefix"
                        }
                    ]
                }
            ],
            "tls": []
        },
        "resources": {
            "limits": {
                "cpu": "500m",
                "memory": "512Mi"
            },
            "requests": {
                "cpu": "100m",
                "memory": "128Mi"
            }
        },
        "autoscaling": {
            "enabled": False,
            "minReplicas": 1,
            "maxReplicas": 10,
            "targetCPUUtilizationPercentage": 80
        },
        "nodeSelector": {},
        "affinity": {},
        "tolerations": [],
        "env": [],
        "configMap": {
            "enabled": False,
            "data": {}
        }
    }


def generate_deployment_template(args):
    """Generate templates/deployment.yaml template."""
    chart_name = args.name
    deployment = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  {{{{- end }}}}
  selector:
    matchLabels:
      {{{{- include "{chart_name}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      {{{{- with .Values.podAnnotations }}}}
      annotations:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      labels:
        {{{{- include "{chart_name}.selectorLabels" . | nindent 8 }}}}
    spec:
      {{{{- with .Values.imagePullSecrets }}}}
      imagePullSecrets:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      serviceAccountName: {{{{ include "{chart_name}.serviceAccountName" . }}}}
      securityContext:
        {{{{- toYaml .Values.podSecurityContext | nindent 8 }}}}
      containers:
      - name: {chart_name}
        securityContext:
          {{{{- toYaml .Values.securityContext | nindent 12 }}}}
        image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
        imagePullPolicy: {{{{ .Values.image.pullPolicy }}}}
        ports:
        - name: http
          containerPort: {{{{ .Values.service.targetPort }}}}
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          {{{{- toYaml .Values.resources | nindent 12 }}}}
        {{{{- if .Values.configMap.enabled }}}}
        envFrom:
        - configMapRef:
            name: {{{{ include "{chart_name}.fullname" . }}}}
        {{{{- end }}}}
        {{{{- with .Values.env }}}}
        env:
          {{{{- toYaml . | nindent 12 }}}}
        {{{{- end }}}}
      {{{{- with .Values.nodeSelector }}}}
      nodeSelector:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.affinity }}}}
      affinity:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.tolerations }}}}
      tolerations:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
"""
    return deployment


def generate_service_template(args):
    """Generate templates/service.yaml template."""
    chart_name = args.name
    service = f"""apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  type: {{{{ .Values.service.type }}}}
  ports:
    - port: {{{{ .Values.service.port }}}}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{{{- include "{chart_name}.selectorLabels" . | nindent 4 }}}}
"""
    return service


def generate_configmap_template(args):
    """Generate templates/configmap.yaml template."""
    chart_name = args.name
    configmap = f"""{{{{- if .Values.configMap.enabled }}}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
data:
  {{{{- with .Values.configMap.data }}}}
  {{{{- toYaml . | nindent 2 }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
    return configmap


def generate_helpers_template(args):
    """Generate templates/_helpers.tpl template."""
    helpers = '''{{/*
Expand the name of the chart.
*/}}
{{- define "''' + args.name + '''.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "''' + args.name + '''.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "''' + args.name + '''.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "''' + args.name + '''.labels" -}}
helm.sh/chart: {{ include "''' + args.name + '''.chart" . }}
{{ include "''' + args.name + '''.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "''' + args.name + '''.selectorLabels" -}}
app.kubernetes.io/name: {{ include "''' + args.name + '''.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "''' + args.name + '''.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "''' + args.name + '''.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
'''
    return helpers


def generate_notes_template(args):
    """Generate templates/NOTES.txt template."""
    notes = f"""1. Get the application URL by running these commands:
{{{{- if contains "NodePort" .Values.service.type }}}}
  export NODE_PORT=$(kubectl get --namespace {{{{ .Release.Namespace }}}} -o jsonpath="{{{{.spec.ports[0].nodePort}}}}" services {{{{ include "{args.name}.fullname" . }}}})
  export NODE_IP=$(kubectl get nodes --namespace {{{{ .Release.Namespace }}}} -o jsonpath="{{{{.items[0].status.addresses[0].address}}}}")
  echo http://$NODE_IP:$NODE_PORT
{{{{- else if contains "LoadBalancer" .Values.service.type }}}}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  You can watch the status by running 'kubectl get --namespace {{{{ .Release.Namespace }}}} svc -w {{{{ include "{args.name}.fullname" . }}}}'
  export SERVICE_IP=$(kubectl get svc --namespace {{{{ .Release.Namespace }}}} {{{{ include "{args.name}.fullname" . }}}} --template "{{{{ range (index .status.loadBalancer.ingress 0) }}}}{{{{.}}}}{{{{ end }}}}")
  echo http://$SERVICE_IP:{{{{ .Values.service.port }}}}
{{{{- else if contains "ClusterIP" .Values.service.type }}}}
  export POD_NAME=$(kubectl get pods --namespace {{{{ .Release.Namespace }}}} -l "app.kubernetes.io/name={args.name},app.kubernetes.io/instance={{{{ .Release.Name }}}}" -o jsonpath="{{{{.items[0].metadata.name}}}}")
  export CONTAINER_PORT=$(kubectl get pod --namespace {{{{ .Release.Namespace }}}} $POD_NAME -o jsonpath="{{{{.spec.containers[0].ports[0].containerPort}}}}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace {{{{ .Release.Namespace }}}} port-forward $POD_NAME 8080:$CONTAINER_PORT
{{{{- end }}}}

2. Check the deployment status by running:
  kubectl get deployment -n {{{{ .Release.Namespace }}}} {{{{ include "{args.name}.fullname" . }}}}

3. View logs with:
  kubectl logs -n {{{{ .Release.Namespace }}}} -l "app.kubernetes.io/name={args.name},app.kubernetes.io/instance={{{{ .Release.Name }}}}"
"""
    return notes


def generate_helmignore():
    """Generate .helmignore file."""
    return """# Patterns to ignore when building packages.
# This supports shell glob patterns, relative paths, and negated patterns
# as per .gitignore syntax: https://git-scm.com/docs/gitignore

# Remove build artifacts from the local charts repository context before charting
.DS_Store
.git/
.gitignore
.bzr/
.bzrignore
.hg/
.hgignore
.svn/
*.swp
*.swo
*~
.idea/
*.iml
.vscode/
*.vscode
.env

# Common dependency patterns to ignore
node_modules/
vendor/
.venv/
env/
venv/

# Test files
test/
tests/
*_test.py
*_test.go
*.test

# Temporary files
*.tmp
*.bak
*.backup
*.orig

# Documentation build files
docs/_build/
site/
"""


def generate_readme(args):
    """Generate README.md for the chart."""
    readme = f"""# {args.name} Helm Chart

A Helm chart for deploying {args.name} on Kubernetes.

## Prerequisites

- Kubernetes 1.18+
- Helm 3+

## Installation

### Add the repository (optional)
```bash
helm repo add myrepo https://charts.example.com
helm repo update
```

### Install the chart

```bash
helm install {args.name} ./chart \\
  --namespace {args.namespace} \\
  --create-namespace
```

### Install with custom values

```bash
helm install {args.name} ./chart \\
  --namespace {args.namespace} \\
  --create-namespace \\
  -f values.yaml
```

## Uninstall

```bash
helm uninstall {args.name} -n {args.namespace}
```

## Configuration

The following table lists the configurable parameters of the {args.name} chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `{args.replicas}` |
| `image.repository` | Container image repository | `{args.image}` |
| `image.tag` | Container image tag | `{args.image_tag}` |
| `image.pullPolicy` | Container image pull policy | `IfNotPresent` |
| `service.type` | Kubernetes Service type | `{args.service_type}` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `{args.port}` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `ingress.enabled` | Enable Ingress | `false` |

## Usage Examples

### Deploy with specific replicas

```bash
helm install {args.name} ./chart --set replicaCount=3
```

### Deploy with custom image

```bash
helm install {args.name} ./chart \\
  --set image.repository=myregistry.azurecr.io/myapp \\
  --set image.tag=v1.2.3
```

### Enable autoscaling

```bash
helm install {args.name} ./chart \\
  --set autoscaling.enabled=true \\
  --set autoscaling.minReplicas=2 \\
  --set autoscaling.maxReplicas=10
```

### Enable Ingress

```bash
helm install {args.name} ./chart \\
  --set ingress.enabled=true \\
  --set ingress.hosts[0].host={args.name}.example.com
```

## Advanced Configuration

### Add environment variables

Create a `custom-values.yaml`:

```yaml
env:
  - name: LOG_LEVEL
    value: "debug"
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: url
```

```bash
helm install {args.name} ./chart -f custom-values.yaml
```

### Enable ConfigMap

Create a `custom-values.yaml`:

```yaml
configMap:
  enabled: true
  data:
    app.properties: |
      key1=value1
      key2=value2
```

```bash
helm install {args.name} ./chart -f custom-values.yaml
```

## Upgrade

```bash
helm upgrade {args.name} ./chart -f values.yaml
```

## Rollback

```bash
helm rollback {args.name}
```

## Troubleshooting

### Check deployment status

```bash
kubectl get deployment -n {args.namespace} {args.name}
kubectl describe deployment -n {args.namespace} {args.name}
```

### View logs

```bash
kubectl logs -n {args.namespace} -l app.kubernetes.io/name={args.name}
```

### Check service

```bash
kubectl get svc -n {args.namespace} {args.name}
kubectl describe svc -n {args.namespace} {args.name}
```

## Contributing

Please report issues and contribute to the development of this chart.

## License

MIT

---

Generated with DevOps-OS - Automate your entire DevOps lifecycle
"""
    return readme


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    output_root = Path(args.output_dir)
    chart_dir = output_root / "chart"
    templates_dir = chart_dir / "templates"
    
    generated = []
    
    # Generate Chart.yaml
    chart_yaml = generate_chart_yaml(args)
    path = _write_yaml(chart_dir / "Chart.yaml", chart_yaml)
    generated.append(str(path))
    
    # Generate values.yaml
    values_yaml = generate_values_yaml(args)
    path = _write_yaml(chart_dir / "values.yaml", values_yaml)
    generated.append(str(path))
    
    # Generate templates
    deployment_template = generate_deployment_template(args)
    path = _write_file(templates_dir / "deployment.yaml", deployment_template)
    generated.append(str(path))
    
    service_template = generate_service_template(args)
    path = _write_file(templates_dir / "service.yaml", service_template)
    generated.append(str(path))
    
    configmap_template = generate_configmap_template(args)
    path = _write_file(templates_dir / "configmap.yaml", configmap_template)
    generated.append(str(path))
    
    helpers_template = generate_helpers_template(args)
    path = _write_file(templates_dir / "_helpers.tpl", helpers_template)
    generated.append(str(path))
    
    notes_template = generate_notes_template(args)
    path = _write_file(templates_dir / "NOTES.txt", notes_template)
    generated.append(str(path))
    
    # Generate .helmignore
    helmignore = generate_helmignore()
    path = _write_file(chart_dir / ".helmignore", helmignore)
    generated.append(str(path))
    
    # Generate README.md
    readme = generate_readme(args)
    path = _write_file(chart_dir / "README.md", readme)
    generated.append(str(path))
    
    print(f"Helm chart generated in {chart_dir}:")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
