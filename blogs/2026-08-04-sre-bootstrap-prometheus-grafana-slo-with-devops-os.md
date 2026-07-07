---
title: "SRE Bootstrap: Prometheus, Grafana, and SLOs in Minutes With DevOps-OS"
slug: "sre-bootstrap-prometheus-grafana-slo-with-devops-os"
description: "DevOps-OS generates a complete SRE observability stack — Prometheus alert rules, Grafana dashboard, and SLO manifest — from one scaffold command."
topic: "sre-observability"
tags: ["SRE", "Prometheus", "Grafana", "SLO", "Observability", "DevOpsOS"]
publishedAt: "2026-08-04"
featured: false
---

# SRE Bootstrap: Prometheus, Grafana, and SLOs in Minutes With DevOps-OS

One of the most expensive parts of launching a new service is wiring up observability from scratch — defining alert thresholds, building a Grafana dashboard, and expressing SLOs in a format your toolchain understands. DevOps-OS does it in one command.

## The command

```bash
python -m cli.devopsos scaffold sre \
  --name payment-service \
  --team platform \
  --slo-target 99.9

# Output: sre/ directory containing:
#   sre/prometheus-rules.yaml
#   sre/grafana-dashboard.json
#   sre/slo.yaml
```

Three files, one command. Let's look at what each one does.

## Prometheus alert rules

`sre/prometheus-rules.yaml` is a Kubernetes `PrometheusRule` CRD that defines:

- **Latency alerts** — fires when p99 response time exceeds threshold
- **Error rate alerts** — fires when HTTP 5xx rate exceeds budget
- **Availability alerts** — fires when the SLO burn rate is too high
- **Saturation alerts** — CPU and memory pressure warnings

All alerts are pre-labelled with `team`, `service`, and `severity` so they route cleanly to your on-call tool.

## Grafana dashboard

`sre/grafana-dashboard.json` is an importable Grafana dashboard JSON with panels covering the four golden signals:

| Signal | What it tracks |
|--------|---------------|
| **Rate** | Requests per second |
| **Errors** | HTTP error rate (4xx and 5xx) |
| **Duration** | Request latency percentiles (p50, p95, p99) |
| **Saturation** | CPU and memory utilisation |

Import it directly via the Grafana UI or the Grafana API.

## SLO manifest

`sre/slo.yaml` is a [Sloth](https://github.com/slok/sloth)-compatible SLO manifest. It encodes:

- The SLO target (e.g. 99.9% availability)
- The SLI definition (ratio of successful requests)
- Multi-window burn rate alerting (short window catches fast burns, long window catches slow burns)

```bash
# Generate with a custom SLO target
python -m cli.devopsos scaffold sre --name my-api --slo-target 99.5

# Generate with an error-rate SLO type
python -m cli.devopsos scaffold sre --name my-api --slo-type error_rate
```

## Process-First SRE

The Process-First philosophy applied to SRE means: **define your SLOs before your first production deployment, not after your first incident.**

DevOps-OS makes that easy. You define the target (`--slo-target 99.9`) and the scaffold encodes it into Prometheus and Grafana artefacts that start measuring from day one.

Key principles:

- **Alert on symptoms, not causes** — burn rate alerts fire on SLO burn, not raw CPU spikes
- **Error budgets** give teams a data-driven way to balance reliability with feature velocity
- **Golden signals** (Rate, Errors, Duration, Saturation) ensure dashboards answer real operational questions

## Integrate with your pipeline

Add SRE config generation to your DevOps-OS pipeline setup:

```bash
# Generate CI/CD + SRE together for a new service
python -m cli.devopsos scaffold gha --name my-api --languages python --type complete
python -m cli.devopsos scaffold sre --name my-api --team backend --slo-target 99.9
```

Commit both the CI/CD workflow and the SRE configs to your repository. The workflow deploys your service; the SRE configs monitor it from the first request.

## Options reference

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | required | Service name |
| `--team` | `platform` | Owning team label on alerts |
| `--slo-target` | `99.9` | Availability SLO target as a percentage |
| `--slo-type` | `availability` | `availability` or `error_rate` |
| `--output` | `./sre/` | Output directory |
