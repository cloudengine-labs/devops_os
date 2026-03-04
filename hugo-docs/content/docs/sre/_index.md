---
title: "SRE Configuration"
weight: 40
---

# SRE Configuration Generator

DevOps-OS generates production-grade SRE configuration files for any service with a single command — covering alerting, dashboards, SLOs, and routing.

---

## Quick Start

```bash
# Generate all SRE configs
python -m cli.scaffold_sre --name my-app --team platform
# Output: sre/alert-rules.yaml
#         sre/grafana-dashboard.json
#         sre/slo.yaml
#         sre/alertmanager-config.yaml

# Availability-only SLO with 99.9% target
python -m cli.scaffold_sre --name my-app --slo-type availability --slo-target 99.9

# Latency SLO with 200ms threshold
python -m cli.scaffold_sre --name my-app --slo-type latency --latency-threshold 0.2

# Send critical alerts to PagerDuty
python -m cli.scaffold_sre --name my-app \
       --pagerduty-key YOUR_PD_KEY \
       --slack-channel "#platform-alerts"
```

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `my-app` | Application / service name |
| `--team TEAM` | `platform` | Owning team (used in labels and alert routing) |
| `--namespace NS` | `default` | Kubernetes namespace where the app runs |
| `--slo-type TYPE` | `all` | `availability` \| `latency` \| `error_rate` \| `all` |
| `--slo-target PCT` | `99.9` | SLO target as a percentage (e.g. `99.5`) |
| `--latency-threshold SEC` | `0.5` | Latency SLI threshold in seconds |
| `--pagerduty-key KEY` | _(empty)_ | PagerDuty integration key; omit to skip PD routing |
| `--slack-channel CHANNEL` | `#alerts` | Slack channel for alert routing |
| `--output-dir DIR` | `sre` | Directory where all output files are written |

All options can be set via environment variables prefixed `DEVOPS_OS_SRE_`.

---

## Generated Files

```
sre/
├── alert-rules.yaml         Prometheus PrometheusRule CR
├── grafana-dashboard.json   Grafana dashboard (importable via API or UI)
├── slo.yaml                 Sloth-compatible SLO manifest
└── alertmanager-config.yaml Alertmanager routing config stub
```

---

## alert-rules.yaml

A `PrometheusRule` Custom Resource compatible with **kube-prometheus-stack**.

```bash
kubectl apply -f sre/alert-rules.yaml
```

### Included alert groups

| Group | Alerts |
|-------|--------|
| `<name>.availability` | `HighErrorRate`, `SLOBurnRate` |
| `<name>.latency` | `HighLatency`, `LatencyBudgetBurn` |
| `<name>.infrastructure` | `PodRestartingFrequently`, `DeploymentReplicasMismatch` |

**SLO burn-rate alerts** fire before you exhaust your error budget.

---

## grafana-dashboard.json

A ready-to-import Grafana dashboard with six panels:

| Panel | Metric |
|-------|--------|
| Request Rate (RPS) | `http_requests_total` |
| Error Rate | 5xx ratio |
| p99 Latency | histogram quantile |
| Pod Restarts | `kube_pod_container_status_restarts_total` |
| CPU Usage | `container_cpu_usage_seconds_total` |
| Memory Usage | `container_memory_working_set_bytes` |

### Import the dashboard

```bash
# Via Grafana HTTP API
curl -X POST http://localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d "{\"dashboard\": $(cat sre/grafana-dashboard.json), \"overwrite\": true}"
```

Or use **Grafana → Dashboards → Import → Upload JSON file**.

---

## slo.yaml

A [Sloth](https://sloth.dev)-compatible SLO manifest that Sloth converts into multi-window, multi-burn-rate Prometheus recording rules and alerts:

```bash
sloth generate -i sre/slo.yaml -o sre/slo-rules.yaml
kubectl apply -f sre/slo-rules.yaml
```

---

## alertmanager-config.yaml

An Alertmanager routing configuration that:

1. Routes **all alerts** to your Slack channel
2. Routes **critical alerts** to PagerDuty *(if `--pagerduty-key` is set)*
3. Inhibits duplicate `warning` alerts when a `critical` alert is firing for the same service

### Apply to the cluster (kube-prometheus-stack)

```bash
kubectl create secret generic alertmanager-kube-prometheus-stack-alertmanager \
  --from-file=alertmanager.yaml=sre/alertmanager-config.yaml \
  --namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
```

---

## Prerequisites

Your application must expose Prometheus-compatible metrics:

| Metric | Description |
|--------|-------------|
| `http_requests_total{status}` | Request count, labelled by HTTP status |
| `http_request_duration_seconds_bucket{le}` | Latency histogram |

Auto-instrumentation libraries:

- **Python**: `prometheus-flask-exporter`, `starlette-prometheus`
- **Java**: `micrometer-registry-prometheus`
- **Go**: `prometheus/client_golang`
- **Node.js**: `prom-client`
