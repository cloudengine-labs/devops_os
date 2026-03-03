#!/usr/bin/env python3
"""
DevOps-OS SRE Configuration Generator

Generates production-grade SRE configuration files:
  - Prometheus alerting rules
  - Grafana dashboard JSON
  - SLO manifest (SLO definitions for sloth / OpenSLO)
  - PagerDuty / Alertmanager routing config stub

Outputs (default: sre/ directory):
  sre/
  ├── alert-rules.yaml         Prometheus PrometheusRule CR
  ├── grafana-dashboard.json   Grafana dashboard JSON
  ├── slo.yaml                 OpenSLO / Sloth SLO manifest
  └── alertmanager-config.yaml Alertmanager receiver config stub
"""

import os
import argparse
import json
import yaml
from pathlib import Path

ENV_PREFIX = "DEVOPS_OS_SRE_"
SLO_TYPES = ["availability", "latency", "error_rate", "all"]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate SRE configuration files for DevOps-OS")
    parser.add_argument("--name", default=os.environ.get(f"{ENV_PREFIX}NAME", "my-app"),
                        help="Application / service name")
    parser.add_argument("--team", default=os.environ.get(f"{ENV_PREFIX}TEAM", "platform"),
                        help="Owning team (used in labels and routing)")
    parser.add_argument("--namespace", default=os.environ.get(f"{ENV_PREFIX}NAMESPACE", "default"),
                        help="Kubernetes namespace where the app runs")
    parser.add_argument("--slo-type", choices=SLO_TYPES,
                        default=os.environ.get(f"{ENV_PREFIX}SLO_TYPE", "all"),
                        help="Type of SLO to generate")
    parser.add_argument("--slo-target", type=float,
                        default=float(os.environ.get(f"{ENV_PREFIX}SLO_TARGET", "99.9")),
                        help="SLO target percentage (e.g. 99.9)")
    parser.add_argument("--latency-threshold", type=float,
                        default=float(os.environ.get(f"{ENV_PREFIX}LATENCY_THRESHOLD", "0.5")),
                        help="Latency SLI threshold in seconds (default 0.5)")
    parser.add_argument("--pagerduty-key", default=os.environ.get(f"{ENV_PREFIX}PAGERDUTY_KEY", ""),
                        help="PagerDuty integration key (leave empty to skip)")
    parser.add_argument("--slack-channel", default=os.environ.get(f"{ENV_PREFIX}SLACK_CHANNEL", "#alerts"),
                        help="Slack channel for alert routing")
    parser.add_argument("--output-dir", default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", "sre"),
                        help="Output directory for generated SRE configs")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        yaml.dump(data, fh, sort_keys=False, default_flow_style=False)
    return path


def _write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    return path


# ---------------------------------------------------------------------------
# Prometheus Alert Rules
# ---------------------------------------------------------------------------

def generate_alert_rules(args):
    """Generate a Prometheus PrometheusRule Custom Resource."""
    name = args.name
    namespace = args.namespace
    team = args.team
    slo = args.slo_target
    error_budget_burn_rate_high = round(14.4 / (1 - slo / 100), 1)
    latency_ms = int(args.latency_threshold * 1000)

    groups = []

    # Availability / error-rate alerts
    if args.slo_type in ("availability", "error_rate", "all"):
        groups.append({
            "name": f"{name}.availability",
            "interval": "30s",
            "rules": [
                {
                    "alert": f"{name.replace('-', '_').title()}HighErrorRate",
                    "expr": (
                        f"rate(http_requests_total{{job=\"{name}\",status=~\"5..\"}}[5m]) / "
                        f"rate(http_requests_total{{job=\"{name}\"}}[5m]) > {round((100 - slo) / 100, 4)}"
                    ),
                    "for": "5m",
                    "labels": {"severity": "critical", "team": team, "slo": "availability"},
                    "annotations": {
                        "summary": f"High error rate on {name}",
                        "description": (
                            f"Error rate for {name} is above {round(100 - slo, 2)}% "
                            f"(SLO target {slo}%). Current value: {{{{ $value | humanizePercentage }}}}"
                        ),
                        "runbook_url": f"https://wiki.example.com/runbooks/{name}/high-error-rate",
                    },
                },
                {
                    "alert": f"{name.replace('-', '_').title()}SLOBurnRate",
                    "expr": (
                        f"(rate(http_requests_total{{job=\"{name}\",status=~\"5..\"}}[1h]) / "
                        f"rate(http_requests_total{{job=\"{name}\"}}[1h])) > "
                        f"{error_budget_burn_rate_high} * {round((100 - slo) / 100, 6)}"
                    ),
                    "for": "2m",
                    "labels": {"severity": "critical", "team": team, "slo": "error-budget"},
                    "annotations": {
                        "summary": f"Error budget burn rate too high for {name}",
                        "description": (
                            f"Error budget for {name} is burning {error_budget_burn_rate_high}x "
                            f"faster than the target rate over the last 1h."
                        ),
                    },
                },
            ],
        })

    # Latency alerts
    if args.slo_type in ("latency", "all"):
        groups.append({
            "name": f"{name}.latency",
            "interval": "30s",
            "rules": [
                {
                    "alert": f"{name.replace('-', '_').title()}HighLatency",
                    "expr": (
                        f"histogram_quantile(0.99, rate(http_request_duration_seconds_bucket"
                        f"{{job=\"{name}\"}}[5m])) > {args.latency_threshold}"
                    ),
                    "for": "5m",
                    "labels": {"severity": "warning", "team": team, "slo": "latency"},
                    "annotations": {
                        "summary": f"High p99 latency on {name}",
                        "description": (
                            f"p99 latency for {name} is above {latency_ms}ms. "
                            f"Current value: {{{{ $value | humanizeDuration }}}}"
                        ),
                        "runbook_url": f"https://wiki.example.com/runbooks/{name}/high-latency",
                    },
                },
                {
                    "alert": f"{name.replace('-', '_').title()}LatencyBudgetBurn",
                    "expr": (
                        f"histogram_quantile(0.99, rate(http_request_duration_seconds_bucket"
                        f"{{job=\"{name}\"}}[1h])) > {args.latency_threshold * 2}"
                    ),
                    "for": "15m",
                    "labels": {"severity": "critical", "team": team, "slo": "latency"},
                    "annotations": {
                        "summary": f"Latency budget burning fast for {name}",
                        "description": (
                            f"p99 latency for {name} has been above "
                            f"{int(args.latency_threshold * 2 * 1000)}ms for 15 minutes."
                        ),
                    },
                },
            ],
        })

    # Infrastructure health
    groups.append({
        "name": f"{name}.infrastructure",
        "rules": [
            {
                "alert": f"{name.replace('-', '_').title()}PodRestartingFrequently",
                "expr": (
                    f"rate(kube_pod_container_status_restarts_total"
                    f"{{namespace=\"{namespace}\",pod=~\"{name}-.*\"}}[15m]) * 60 > 0.1"
                ),
                "for": "5m",
                "labels": {"severity": "warning", "team": team},
                "annotations": {
                    "summary": f"Pod {name} is restarting frequently",
                    "description": "Pod has restarted more than once in the last 15 minutes.",
                },
            },
            {
                "alert": f"{name.replace('-', '_').title()}DeploymentReplicasMismatch",
                "expr": (
                    f"kube_deployment_spec_replicas{{namespace=\"{namespace}\",deployment=\"{name}\"}} "
                    f"!= kube_deployment_status_replicas_available{{namespace=\"{namespace}\",deployment=\"{name}\"}}"
                ),
                "for": "10m",
                "labels": {"severity": "warning", "team": team},
                "annotations": {
                    "summary": f"Deployment {name} does not have the desired number of replicas",
                    "description": "Available replicas don't match desired replicas for 10 minutes.",
                },
            },
        ],
    })

    return {
        "apiVersion": "monitoring.coreos.com/v1",
        "kind": "PrometheusRule",
        "metadata": {
            "name": f"{name}-sre-rules",
            "namespace": namespace,
            "labels": {
                "app": name,
                "team": team,
                "prometheus": "kube-prometheus",
                "role": "alert-rules",
            },
        },
        "spec": {"groups": groups},
    }


# ---------------------------------------------------------------------------
# Grafana Dashboard
# ---------------------------------------------------------------------------

def generate_grafana_dashboard(args):
    """Generate a minimal but functional Grafana dashboard JSON."""
    name = args.name
    title = f"{name.title()} SRE Dashboard"

    def panel(pid, title, expr, panel_type="timeseries", gridx=0, gridy=0, w=12, h=8, unit=""):
        p = {
            "id": pid,
            "type": panel_type,
            "title": title,
            "gridPos": {"x": gridx, "y": gridy, "w": w, "h": h},
            "targets": [{"expr": expr, "legendFormat": "{{job}}", "refId": "A"}],
            "options": {},
        }
        if unit:
            p["fieldConfig"] = {"defaults": {"unit": unit}, "overrides": []}
        return p

    panels = [
        panel(1, "Request Rate (RPS)",
              f"rate(http_requests_total{{job=\"{name}\"}}[5m])",
              gridx=0, gridy=0, unit="reqps"),
        panel(2, "Error Rate",
              f"rate(http_requests_total{{job=\"{name}\",status=~\"5..\"}}[5m]) / rate(http_requests_total{{job=\"{name}\"}}[5m])",
              gridx=12, gridy=0, unit="percentunit"),
        panel(3, "p50 / p95 / p99 Latency",
              f"histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{{job=\"{name}\"}}[5m]))",
              gridx=0, gridy=8, unit="s"),
        panel(4, "Pod Restarts",
              f"rate(kube_pod_container_status_restarts_total{{pod=~\"{name}-.*\"}}[15m]) * 60",
              gridx=12, gridy=8, unit="short"),
        panel(5, "CPU Usage",
              f"rate(container_cpu_usage_seconds_total{{pod=~\"{name}-.*\"}}[5m])",
              gridx=0, gridy=16, w=12, h=8, unit="cores"),
        panel(6, "Memory Usage",
              f"container_memory_working_set_bytes{{pod=~\"{name}-.*\"}}",
              gridx=12, gridy=16, w=12, h=8, unit="bytes"),
        {
            "id": 7,
            "type": "stat",
            "title": f"SLO Target ({args.slo_target}%)",
            "gridPos": {"x": 0, "y": 24, "w": 6, "h": 4},
            "targets": [{
                "expr": (
                    f"1 - (rate(http_requests_total{{job=\"{name}\",status=~\"5..\"}}[30d]) / "
                    f"rate(http_requests_total{{job=\"{name}\"}}[30d]))"
                ),
                "refId": "A",
                "legendFormat": "Availability",
            }],
            "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "orientation": "auto"},
            "fieldConfig": {
                "defaults": {
                    "unit": "percentunit",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": None},
                            {"color": "yellow", "value": args.slo_target / 100 - 0.001},
                            {"color": "green", "value": args.slo_target / 100},
                        ],
                    },
                },
                "overrides": [],
            },
        },
    ]

    return {
        "__inputs": [{"name": "DS_PROMETHEUS", "label": "Prometheus", "type": "datasource", "pluginId": "prometheus"}],
        "__requires": [{"type": "grafana", "id": "grafana", "name": "Grafana", "version": "10.0.0"}],
        "id": None,
        "uid": f"{name[:8]}-sre",
        "title": title,
        "tags": ["sre", "slo", name, args.team],
        "timezone": "browser",
        "schemaVersion": 38,
        "version": 1,
        "refresh": "30s",
        "time": {"from": "now-3h", "to": "now"},
        "panels": panels,
    }


# ---------------------------------------------------------------------------
# SLO Manifest (OpenSLO / Sloth compatible)
# ---------------------------------------------------------------------------

def generate_slo_manifest(args):
    """Generate a Sloth-compatible SLO manifest."""
    name = args.name
    slos = []

    if args.slo_type in ("availability", "all"):
        slos.append({
            "name": "availability",
            "description": f"{name} availability SLO — {args.slo_target}% of requests succeed",
            "objective": args.slo_target,
            "sli": {
                "events": {
                    "error_query": f"rate(http_requests_total{{job=\"{name}\",status=~\"(5..)\"}}[{{{{.window}}}}])",
                    "total_query": f"rate(http_requests_total{{job=\"{name}\"}}[{{{{.window}}}}])",
                }
            },
            "alerting": {
                "name": f"{name.title()}AvailabilitySLO",
                "labels": {"team": args.team},
                "annotations": {
                    "runbook": f"https://wiki.example.com/runbooks/{name}/availability",
                },
                "page_alert": {"labels": {"severity": "critical"}},
                "ticket_alert": {"labels": {"severity": "warning"}},
            },
        })

    if args.slo_type in ("latency", "all"):
        slos.append({
            "name": "latency",
            "description": (
                f"{name} latency SLO — {args.slo_target}% of requests complete "
                f"within {int(args.latency_threshold * 1000)}ms"
            ),
            "objective": args.slo_target,
            "sli": {
                "events": {
                    "error_query": (
                        f"rate(http_request_duration_seconds_bucket{{job=\"{name}\","
                        f"le=\"{args.latency_threshold}\"}}[{{{{.window}}}}])"
                    ),
                    "total_query": f"rate(http_request_duration_seconds_count{{job=\"{name}\"}}[{{{{.window}}}}])",
                }
            },
            "alerting": {
                "name": f"{name.title()}LatencySLO",
                "labels": {"team": args.team},
                "page_alert": {"labels": {"severity": "critical"}},
                "ticket_alert": {"labels": {"severity": "warning"}},
            },
        })

    return {
        "version": "prometheus/v1",
        "service": name,
        "labels": {"owner": args.team, "repo": f"https://github.com/myorg/{name}"},
        "slos": slos,
    }


# ---------------------------------------------------------------------------
# Alertmanager Config Stub
# ---------------------------------------------------------------------------

def generate_alertmanager_config(args):
    """Generate an Alertmanager routing config stub."""
    receivers = [
        {
            "name": f"{args.team}-slack",
            "slack_configs": [
                {
                    "api_url": "$SLACK_WEBHOOK_URL",
                    "channel": args.slack_channel,
                    "send_resolved": True,
                    "title": "{{ .GroupLabels.alertname }}",
                    "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                }
            ],
        }
    ]

    if args.pagerduty_key:
        receivers.append({
            "name": f"{args.team}-pagerduty",
            "pagerduty_configs": [
                {
                    "integration_key": args.pagerduty_key,
                    "severity": "{{ .CommonLabels.severity }}",
                }
            ],
        })

    route = {
        "group_by": ["alertname", "team"],
        "group_wait": "30s",
        "group_interval": "5m",
        "repeat_interval": "4h",
        "receiver": f"{args.team}-slack",
        "routes": [
            {
                "match": {"severity": "critical"},
                "receiver": f"{args.team}-pagerduty" if args.pagerduty_key else f"{args.team}-slack",
                "continue": True,
            },
            {
                "match": {"team": args.team},
                "receiver": f"{args.team}-slack",
            },
        ],
    }

    return {
        "global": {
            "resolve_timeout": "5m",
            "slack_api_url": "$SLACK_WEBHOOK_URL",
        },
        "route": route,
        "receivers": receivers,
        "inhibit_rules": [
            {
                "source_match": {"severity": "critical"},
                "target_match": {"severity": "warning"},
                "equal": ["alertname", "team"],
            }
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    generated = []

    alert_rules = generate_alert_rules(args)
    path = _write_yaml(output_dir / "alert-rules.yaml", alert_rules)
    generated.append(str(path))

    dashboard = generate_grafana_dashboard(args)
    path = _write_json(output_dir / "grafana-dashboard.json", dashboard)
    generated.append(str(path))

    slo = generate_slo_manifest(args)
    path = _write_yaml(output_dir / "slo.yaml", slo)
    generated.append(str(path))

    am_config = generate_alertmanager_config(args)
    path = _write_yaml(output_dir / "alertmanager-config.yaml", am_config)
    generated.append(str(path))

    print("SRE configs generated:")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
