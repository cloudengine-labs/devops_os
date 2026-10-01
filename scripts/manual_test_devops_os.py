#!/usr/bin/env python3
"""Manual smoke test runner for DevOps-OS MCP server.

This script exercises the MCP server tool functions without touching repo-tracked files.
It is intended as a fast local confidence check, not a replacement for the full pytest suite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mcp_server.server import (
    generate_github_actions_workflow,
    generate_jenkins_pipeline,
    generate_k8s_config,
    scaffold_devcontainer,
    generate_gitlab_ci_pipeline,
    generate_argocd_config,
    generate_sre_configs,
    generate_unittest_config,
)


def _ok(message: str) -> None:
    print(f"PASS  {message}")


def _fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def run_mcp_smoke() -> None:
    """Run smoke tests against the MCP server."""
    gha = generate_github_actions_workflow(name="manual-app", workflow_type="complete", languages="python,go")
    _assert("manual-app" in gha, "MCP GHA output missing app name")
    _ok("MCP generate_github_actions_workflow")

    jenkins = generate_jenkins_pipeline(name="manual-app", pipeline_type="complete", languages="java")
    _assert("pipeline" in jenkins.lower(), "MCP Jenkins output looks invalid")
    _ok("MCP generate_jenkins_pipeline")

    k8s = generate_k8s_config(app_name="manual-app", image="ghcr.io/example/manual-app:latest")
    _assert("Deployment" in k8s, "MCP Kubernetes output missing Deployment")
    _ok("MCP generate_k8s_config")

    devcontainer = json.loads(scaffold_devcontainer(languages="python,go", cicd_tools="docker,github_actions"))
    _assert("devcontainer_json" in devcontainer, "MCP scaffold_devcontainer missing devcontainer_json")
    _assert("devcontainer_env_json" in devcontainer, "MCP scaffold_devcontainer missing devcontainer_env_json")
    _ok("MCP scaffold_devcontainer")

    gitlab = generate_gitlab_ci_pipeline(name="manual-app", pipeline_type="complete", languages="python")
    _assert("stages:" in gitlab, "MCP GitLab output looks invalid")
    _ok("MCP generate_gitlab_ci_pipeline")

    argocd = json.loads(
        generate_argocd_config(
            name="manual-app",
            repo="https://github.com/example/manual-app.git",
            auto_sync=True,
            rollouts=True,
            allow_any_source_repo=True,
        )
    )
    _assert("argocd/application.yaml" in argocd, "MCP ArgoCD output missing application")
    _assert("argocd/appproject.yaml" in argocd, "MCP ArgoCD output missing AppProject")
    _ok("MCP generate_argocd_config")

    sre = json.loads(generate_sre_configs(name="manual-app", team="platform"))
    _assert("alert_rules_yaml" in sre, "MCP SRE output missing alert rules")
    _assert("grafana_dashboard_json" in sre, "MCP SRE output missing dashboard")
    _ok("MCP generate_sre_configs")

    unittest_cfg = json.loads(generate_unittest_config(name="manual-app", languages="python,javascript,go"))
    _assert("pytest.ini" in unittest_cfg, "MCP unittest output missing pytest.ini")
    _assert("tests/sample.test.js" in unittest_cfg, "MCP unittest output missing JS sample")
    _ok("MCP generate_unittest_config")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DevOps-OS MCP server smoke tests.")
    parser.add_argument(
        "--skip-mcp",
        action="store_true",
        help="Skip MCP smoke tests when mcp_server dependencies are not installed locally.",
    )
    args = parser.parse_args()

    if args.skip_mcp:
        print("SKIP  MCP smoke tests")
    else:
        run_mcp_smoke()

    print("All manual smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
