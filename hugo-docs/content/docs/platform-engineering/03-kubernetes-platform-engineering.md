---
title: "Kubernetes-Based Platform Engineering"
description: "Container-native CI/CD architectures, GitOps design patterns, and Kubernetes-native observability."
weight: 25
---

# Kubernetes-Based Platform Engineering

Kubernetes has become the standard execution environment for cloud-native applications. Platform engineering in a Kubernetes context means designing self-service capabilities that leverage Kubernetes' declarative model, GitOps principles, and cloud-native observability.

## Kubernetes as a Platform Foundation

Kubernetes provides the infrastructure layer, but platform engineering adds the operational and developer-facing layers on top.

```
┌─────────────────────────────────────────────────────────┐
│ Developer Productivity Layer (IDP)                       │
│ - Self-service templates, AI-assisted generation         │
│ - Guided deployment workflows                           │
│ - Cost visibility and performance dashboards            │
├─────────────────────────────────────────────────────────┤
│ Platform Orchestration Layer                            │
│ - ArgoCD/Flux (GitOps), Kyverno (Policy), Istio (Mesh) │
│ - Tekton/ArgoWorkflows (in-cluster pipelines)          │
│ - Prometheus, Grafana, Jaeger (observability)          │
├─────────────────────────────────────────────────────────┤
│ Kubernetes Infrastructure Layer                         │
│ - Deployments, Services, Ingress, RBAC                 │
│ - StatefulSets, DaemonSets for stateful workloads       │
│ - Network Policies, Pod Security Standards             │
│ - Storage: PersistentVolumes, StorageClasses           │
└─────────────────────────────────────────────────────────┘
```

## Container-Native CI/CD Architecture

### **Traditional CI/CD**: External Pipeline → Kubernetes Deploy

```
GitHub / GitLab / GitHub Enterprise
    ↓
GitHub Actions / GitLab CI / Jenkins Runner (external VM)
    ↓
Build, test, push image
    ↓
Deploy to Kubernetes (kubectl apply)
```

**Issues**:
- Pipeline infrastructure separate from workload infrastructure
- Different scalability models and failure domains
- Complex credential management (external pipeline needs K8s access)

### **Kubernetes-Native CI/CD**: In-Cluster Pipeline → Kubernetes Deploy

```
Git Commit
    ↓
Tekton / ArgoWorkflows (runs in cluster)
    ↓
Build container, run tests (within cluster)
    ↓
Push to registry
    ↓
GitOps (ArgoCD / Flux) applies to cluster
    ↓
Application runs on Kubernetes
```

**Advantages**:
- Single execution environment (cluster is both build and runtime platform)
- Native Kubernetes access (no credential bootstrapping needed)
- Horizontal scalability (pipeline pods scale like regular workloads)
- Observability built-in (logs, metrics, traces in same cluster)

## Tekton: Kubernetes-Native CI/CD

Tekton is Kubernetes-native CI/CD. Instead of imperative scripts, Tekton uses declarative Kubernetes CRDs (Custom Resource Definitions).

### Example: Tekton Task (Reusable Unit of Work)

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-and-push-image
spec:
  params:
  - name: imageUrl
    description: URL of image repository
  - name: imageTag
    description: Tag for the image (e.g., v1.0)
  steps:
  - name: build
    image: kaniko/executor:latest
    args:
    - --destination=$(params.imageUrl):$(params.imageTag)
    - --dockerfile=Dockerfile
  - name: scan-vulnerabilities
    image: aquasec/trivy:latest
    args:
    - image
    - --severity HIGH,CRITICAL
    - $(params.imageUrl):$(params.imageTag)
```

### Example: Tekton Pipeline (Composition of Tasks)

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: deploy-python-service
spec:
  params:
  - name: app-name
  - name: image-url
  tasks:
  - name: clone-repo
    taskRef:
      name: git-clone
  - name: run-tests
    runAfter: [clone-repo]
    taskRef:
      name: pytest
  - name: build-image
    runAfter: [run-tests]
    taskRef:
      name: build-and-push-image
    params:
    - name: imageUrl
      value: $(params.image-url)
  - name: deploy-to-staging
    runAfter: [build-image]
    taskRef:
      name: kubectl-apply
    params:
    - name: namespace
      value: staging
  - name: run-smoke-tests
    runAfter: [deploy-to-staging]
    taskRef:
      name: smoke-tests
    params:
    - name: namespace
      value: staging
```

**Advantages**:
- Declarative (Git-friendly, version-controlled)
- Reusable tasks (library of common operations)
- Native Kubernetes (runs as pods, scales horizontally)
- Native observability (logs available via kubectl)

## GitOps: Git as Single Source of Truth

### **GitOps Principles**

1. **Declarative**: System state defined in Git (not imperative commands)
2. **Versioned & Immutable**: All changes tracked in Git with history
3. **Automatically Reconciled**: Operator pulls from Git and applies changes
4. **Observed**: Real-time status visible (alerts on drift)

### ArgoCD Example

**Git Repo Contains**:
```
gitops-repo/
├── apps/
│   ├── production/
│   │   ├── payment-service-deployment.yaml
│   │   ├── payment-service-service.yaml
│   │   └── payment-service-configmap.yaml
│   └── staging/
│       ├── payment-service-deployment.yaml
│       └── ...
└── infrastructure/
    ├── namespaces.yaml
    └── network-policies.yaml
```

**ArgoCD Application**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service-prod
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/gitops-repo
    targetRevision: main
    path: apps/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Remove resources deleted from Git
      selfHeal: true   # Auto-sync on drift detection
    syncOptions:
    - CreateNamespace=true
```

**Result**:
- Commit changes to Git
- ArgoCD detects change within 3 minutes
- Cluster automatically reconciles to Git state
- Full audit trail in Git

### Flux CD Alternative

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: GitRepository
metadata:
  name: payment-service
spec:
  interval: 1m
  url: https://github.com/myorg/gitops-repo
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: payment-service-prod
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: payment-service
  path: ./apps/production
  prune: true
  wait: true
```

---

## Progressive Delivery: Canary & Blue-Green

### **Canary Deployment** (Gradual rollout)

```
┌──────────────────────────────────────────────────────┐
│ Kubernetes Service with 2 pods                        │
├──────────────────────────────────────────────────────┤
│ Pod 1: v1.0 (stable) ──── 95% traffic               │
│ Pod 2: v1.1 (canary) ──── 5% traffic                │
│                                                      │
│ If v1.1 metrics look good:                          │
│ → shift 10% traffic → 25% → 50% → 100%              │
│                                                      │
│ If v1.1 errors detected:                            │
│ → automatic rollback to v1.0                        │
└──────────────────────────────────────────────────────┘
```

**Flagger Example**:
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: payment-service
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5           # Max 5% error increase
    maxWeight: 50          # Cap canary at 50% traffic
    stepWeight: 10         # Increase by 10% every minute
  metrics:
  - name: request-success-rate
    thresholdRange:
      min: 99
  - name: request-duration
    thresholdRange:
      max: 500             # p99 latency < 500ms
  webhooks:
  - name: smoke-tests
    url: http://flagger-loadtester/
    timeout: 5s
```

### **Blue-Green Deployment** (Complete switch)

```
┌──────────────────────────────────────────────────────┐
│ BLUE (v1.0 - active)                                 │
│ Pod 1, Pod 2, Pod 3 ──── 100% traffic               │
└──────────────────────────────────────────────────────┘

                [Run smoke tests]

┌──────────────────────────────────────────────────────┐
│ GREEN (v1.1 - ready)                                 │
│ Pod A, Pod B, Pod C ──── 0% traffic                 │
└──────────────────────────────────────────────────────┘

                [Tests pass]

                [Switch Service → GREEN]

┌──────────────────────────────────────────────────────┐
│ BLUE (v1.0 - standby)                                │
│ Pod 1, Pod 2, Pod 3 ──── 0% traffic                 │
└──────────────────────────────────────────────────────┘

                [If issues detected: switch back]
```

---

## Cluster Configuration Templates

### **Namespace Template** (Isolation, resource quotas)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: payment-service-prod
  labels:
    team: payments
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: payment-service-quota
  namespace: payment-service-prod
spec:
  hard:
    requests.cpu: "100"      # Max 100 CPUs reserved
    requests.memory: "200Gi" # Max 200GB reserved
    pods: "500"              # Max 500 pods
---
apiVersion: v1
kind: LimitRange
metadata:
  name: payment-service-limits
  namespace: payment-service-prod
spec:
  limits:
  - max:
      cpu: "4"               # Single pod max 4 CPUs
      memory: "8Gi"          # Single pod max 8GB
    min:
      cpu: "50m"             # Single pod min 50m CPU
      memory: "64Mi"         # Single pod min 64MB
    type: Container
```

### **RBAC Template** (Fine-grained access control)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payment-service
  namespace: payment-service-prod
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payment-service
  namespace: payment-service-prod
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["payment-service-config"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["payment-service-secrets"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]  # Read-only pod access
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payment-service
  namespace: payment-service-prod
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payment-service
subjects:
- kind: ServiceAccount
  name: payment-service
  namespace: payment-service-prod
```

### **Network Policy Template** (Microsegmentation)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payment-service-ingress
  namespace: payment-service-prod
spec:
  podSelector:
    matchLabels:
      app: payment-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx  # Only from ingress controller
    - podSelector:
        matchLabels:
          app: api-gateway     # Or from API gateway pods
    ports:
    - protocol: TCP
      port: 8080
---
# Deny egress to internet, allow only internal
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payment-service-egress
  namespace: payment-service-prod
spec:
  podSelector:
    matchLabels:
      app: payment-service
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}  # Allow to all namespaces
    ports:
    - protocol: TCP
      port: 443  # Only HTTPS
```

---

## Kubernetes Observability

### **Prometheus ServiceMonitor Template**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: payment-service
  namespace: payment-service-prod
spec:
  selector:
    matchLabels:
      app: payment-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### **Grafana Dashboard Template**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-service-dashboard
  namespace: monitoring
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Payment Service",
        "panels": [
          {
            "title": "Request Rate (req/s)",
            "targets": [{"expr": "rate(http_requests_total[5m])"}]
          },
          {
            "title": "Error Rate (%)",
            "targets": [{"expr": "100 * rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m])"}]
          },
          {
            "title": "P95 Latency (ms)",
            "targets": [{"expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"}]
          }
        ]
      }
    }
```

### **SLO Manifest Template**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: payment-service-slo
  namespace: payment-service-prod
spec:
  groups:
  - name: payment-service-slo
    interval: 30s
    rules:
    - alert: PaymentServiceSLOViolation
      expr: |
        (
          rate(http_requests_total{job="payment-service",status=~"5.."}[5m]) /
          rate(http_requests_total{job="payment-service"}[5m])
        ) > 0.001  # 99.9% availability = max 0.1% error rate
      for: 5m
      labels:
        severity: critical
        slo: "99.9"
      annotations:
        summary: "Payment service SLO violated"
```

---

## Multi-Cluster Deployment Patterns

### **Active-Active** (Multiple clusters serve traffic)

```
┌─────────────────────────────────────────────┐
│ Global Load Balancer (AWS Route53, GCP LB)  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌──────────────┐   │
│  │ Cluster 1    │      │ Cluster 2    │   │
│  │ (us-east)    │      │ (eu-west)    │   │
│  │ 50% traffic  │      │ 50% traffic  │   │
│  └──────────────┘      └──────────────┘   │
│                                             │
│  Both clusters actively serving traffic    │
│  Failover is automatic at DNS level        │
└─────────────────────────────────────────────┘
```

### **Active-Passive** (Standby cluster)

```
┌─────────────────────────────────────────────┐
│ Load Balancer with Health Checks            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐                          │
│  │ Cluster 1    │                          │
│  │ (Primary)    │                          │
│  │ 100% traffic │                          │
│  └──────────────┘                          │
│                                             │
│  ┌──────────────┐                          │
│  │ Cluster 2    │                          │
│  │ (Standby)    │                          │
│  │ 0% traffic   │                          │
│  └──────────────┘                          │
│                                             │
│  If Cluster 1 health check fails:          │
│  → Traffic switches to Cluster 2           │
└─────────────────────────────────────────────┘
```

---

## Next Steps

- **Ready for cloud deployment?** → [Cloud-Based Platform](04-cloud-based-platform.md)
- **Want to see how this fits together?** → [Reference Architecture](06-reference-architecture.md)
- **Looking for examples?** → [Case Studies](07-case-studies.md)

