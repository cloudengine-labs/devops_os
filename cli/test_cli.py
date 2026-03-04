import subprocess
import sys
import tempfile
import os
import yaml
import json
from pathlib import Path

# -- helpers ---------------------------------------------------------------
def _run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True,
                          cwd=os.path.dirname(os.path.dirname(__file__)))

def _run_module(module, extra_args=None):
    args = ["-m", module] + (extra_args or [])
    return _run(args)

# -- devopsos CLI ----------------------------------------------------------

def test_help():
    result = _run(["-m", "cli.devopsos", "--help"])
    assert "Unified DevOps-OS CLI tool" in result.stdout

def test_scaffold_unknown():
    result = _run(["-m", "cli.devopsos", "scaffold", "unknown"])
    assert "Unknown scaffold target" in result.stdout

def test_scaffold_help_lists_new_targets():
    result = _run(["-m", "cli.devopsos", "scaffold", "--help"])
    assert result.returncode == 0
    assert "gitlab" in result.stdout
    assert "argocd" in result.stdout
    assert "sre" in result.stdout

# -- GitLab CI generator ---------------------------------------------------

def test_scaffold_gitlab_build():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, ".gitlab-ci.yml")
        result = _run_module("cli.scaffold_gitlab",
                             ["--name", "test-app", "--type", "build",
                              "--languages", "python", "--output", out])
        assert result.returncode == 0
        assert os.path.exists(out)
        with open(out) as fh:
            data = yaml.safe_load(fh)
        assert "build" in (data.get("stages") or [])
        assert "build" in data

def test_scaffold_gitlab_complete_with_k8s():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, ".gitlab-ci.yml")
        result = _run_module("cli.scaffold_gitlab",
                             ["--name", "api", "--type", "complete",
                              "--languages", "python,go",
                              "--kubernetes", "--k8s-method", "kubectl",
                              "--output", out])
        assert result.returncode == 0
        with open(out) as fh:
            data = yaml.safe_load(fh)
        assert "deploy" in (data.get("stages") or [])

def test_scaffold_gitlab_test_java():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, ".gitlab-ci.yml")
        result = _run_module("cli.scaffold_gitlab",
                             ["--name", "java-svc", "--type", "test",
                              "--languages", "java", "--output", out])
        assert result.returncode == 0
        with open(out) as fh:
            data = yaml.safe_load(fh)
        assert "test:java" in data

# -- ArgoCD / Flux generator -----------------------------------------------

def test_scaffold_argocd_application():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_argocd",
                             ["--name", "my-app",
                              "--repo", "https://github.com/myorg/my-app.git",
                              "--output-dir", tmp])
        assert result.returncode == 0
        app_path = Path(tmp) / "argocd" / "application.yaml"
        assert app_path.exists()
        with open(app_path) as fh:
            doc = yaml.safe_load(fh)
        assert doc["kind"] == "Application"
        assert doc["metadata"]["name"] == "my-app"

def test_scaffold_argocd_appproject():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_argocd",
                             ["--name", "my-app",
                              "--repo", "https://github.com/myorg/my-app.git",
                              "--project", "team-a",
                              "--output-dir", tmp])
        assert result.returncode == 0
        proj_path = Path(tmp) / "argocd" / "appproject.yaml"
        assert proj_path.exists()
        with open(proj_path) as fh:
            doc = yaml.safe_load(fh)
        assert doc["kind"] == "AppProject"
        assert doc["metadata"]["name"] == "team-a"

def test_scaffold_argocd_with_rollouts():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_argocd",
                             ["--name", "my-app",
                              "--repo", "https://github.com/myorg/my-app.git",
                              "--rollouts", "--output-dir", tmp])
        assert result.returncode == 0
        rollout_path = Path(tmp) / "argocd" / "rollout.yaml"
        assert rollout_path.exists()
        with open(rollout_path) as fh:
            doc = yaml.safe_load(fh)
        assert doc["kind"] == "Rollout"

def test_scaffold_argocd_flux():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_argocd",
                             ["--name", "my-app", "--method", "flux",
                              "--repo", "https://github.com/myorg/my-app.git",
                              "--output-dir", tmp])
        assert result.returncode == 0
        kust_path = Path(tmp) / "flux" / "kustomization.yaml"
        assert kust_path.exists()
        with open(kust_path) as fh:
            doc = yaml.safe_load(fh)
        assert doc["kind"] == "Kustomization"

# -- SRE generator ---------------------------------------------------------

def test_scaffold_sre_all_outputs_exist():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_sre",
                             ["--name", "my-svc", "--team", "platform",
                              "--output-dir", tmp])
        assert result.returncode == 0
        assert (Path(tmp) / "alert-rules.yaml").exists()
        assert (Path(tmp) / "grafana-dashboard.json").exists()
        assert (Path(tmp) / "slo.yaml").exists()
        assert (Path(tmp) / "alertmanager-config.yaml").exists()

def test_scaffold_sre_alert_rules_structure():
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_sre",
                             ["--name", "api-svc", "--slo-type", "availability",
                              "--slo-target", "99.5", "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / "alert-rules.yaml") as fh:
            doc = yaml.safe_load(fh)
        assert doc["kind"] == "PrometheusRule"
        assert len(doc["spec"]["groups"]) > 0

def test_scaffold_sre_grafana_dashboard_panels():
    with tempfile.TemporaryDirectory() as tmp:
        _run_module("cli.scaffold_sre",
                    ["--name", "web-app", "--output-dir", tmp])
        with open(Path(tmp) / "grafana-dashboard.json") as fh:
            dash = json.load(fh)
        assert "panels" in dash
        assert len(dash["panels"]) > 0
        assert "web-app" in dash.get("title", "").lower()

def test_scaffold_sre_slo_latency():
    with tempfile.TemporaryDirectory() as tmp:
        _run_module("cli.scaffold_sre",
                    ["--name", "latency-svc", "--slo-type", "latency",
                     "--slo-target", "99.9", "--latency-threshold", "0.2",
                     "--output-dir", tmp])
        with open(Path(tmp) / "slo.yaml") as fh:
            doc = yaml.safe_load(fh)
        assert doc["service"] == "latency-svc"
        slo_names = [s["name"] for s in doc["slos"]]
        assert "latency" in slo_names
