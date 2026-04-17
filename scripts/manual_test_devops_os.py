#!/usr/bin/env python3
"""Manual smoke test runner for DevOps-OS.

This script exercises the public CLI generators plus the MCP tool functions
without touching repo-tracked files. It is intended as a fast local confidence
check, not a replacement for the full pytest suite.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typer.testing import CliRunner

from cli.devopsos import app



def _ok(message: str) -> None:
    print(f"PASS  {message}")


def _fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(REPO_ROOT)
    )
    result = subprocess.run(
        [sys.executable, "-m", "cli.devopsos", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        details = result.stdout + "\n" + result.stderr
        _fail(f"`python -m cli.devopsos {' '.join(args)}` failed\n{details}")
    return result


def _assert_exists(path: Path) -> None:
    _assert(path.exists(), f"Expected path to exist: {path}")


def run_cli_smoke(workdir: Path) -> None:
    _run_cli(
        "scaffold",
        "gha",
        "--name",
        "manual-app",
        "--type",
        "complete",
        "--languages",
        "python,go",
        "--kubernetes",
        "--k8s-method",
        "argocd",
        cwd=workdir,
    )
    workflow = workdir / ".github" / "workflows" / "manual-app-complete.yml"
    _assert_exists(workflow)
    _assert("name:" in workflow.read_text(encoding="utf-8"), "Generated GHA workflow looks invalid")
    _ok("CLI scaffold gha")

    _run_cli(
        "scaffold",
        "jenkins",
        "--name",
        "manual-app",
        "--type",
        "complete",
        "--languages",
        "java",
        "--output",
        str(workdir / "jenkins" / "Jenkinsfile"),
        cwd=workdir,
    )
    jenkinsfile = workdir / "jenkins" / "Jenkinsfile"
    _assert_exists(jenkinsfile)
    _assert("pipeline" in jenkinsfile.read_text(encoding="utf-8").lower(), "Generated Jenkinsfile looks invalid")
    _ok("CLI scaffold jenkins")

    _run_cli(
        "scaffold",
        "gitlab",
        "--name",
        "manual-app",
        "--type",
        "complete",
        "--languages",
        "python,go",
        "--kubernetes",
        "--k8s-method",
        "flux",
        cwd=workdir,
    )
    gitlab = workdir / ".gitlab-ci.yml"
    _assert_exists(gitlab)
    _assert("stages:" in gitlab.read_text(encoding="utf-8"), "Generated GitLab CI file looks invalid")
    _ok("CLI scaffold gitlab")

    _run_cli(
        "scaffold",
        "argocd",
        "--name",
        "manual-app",
        "--repo",
        "https://github.com/example/manual-app.git",
        "--rollouts",
        cwd=workdir,
    )
    app_yaml = workdir / "argocd" / "application.yaml"
    project_yaml = workdir / "argocd" / "appproject.yaml"
    rollout_yaml = workdir / "argocd" / "rollout.yaml"
    _assert_exists(app_yaml)
    _assert_exists(project_yaml)
    _assert_exists(rollout_yaml)
    _ok("CLI scaffold argocd")

    _run_cli(
        "scaffold",
        "sre",
        "--name",
        "manual-app",
        "--team",
        "platform",
        cwd=workdir,
    )
    _assert_exists(workdir / "sre" / "alert-rules.yaml")
    _assert_exists(workdir / "sre" / "grafana-dashboard.json")
    _assert_exists(workdir / "sre" / "slo.yaml")
    _ok("CLI scaffold sre")

    _run_cli(
        "scaffold",
        "devcontainer",
        "--languages",
        "python,go",
        "--cicd-tools",
        "docker,terraform,kubectl,helm",
        "--kubernetes-tools",
        "k9s,flux",
        cwd=workdir,
    )
    devcontainer_dir = workdir / ".devcontainer"
    _assert_exists(devcontainer_dir / "devcontainer.json")
    _assert_exists(devcontainer_dir / "devcontainer.env.json")
    _assert(not (devcontainer_dir / "Dockerfile").exists(), "Legacy scaffold should not generate Dockerfile")
    _ok("CLI scaffold devcontainer")

    _run_cli(
        "scaffold",
        "unittest",
        "--name",
        "manual-app",
        "--languages",
        "python,javascript,go",
        cwd=workdir,
    )
    unittest_dir = workdir / "unittest"
    _assert_exists(unittest_dir / "pytest.ini")
    _assert_exists(unittest_dir / "tests" / "test_sample.py")
    _assert_exists(unittest_dir / "tests" / "sample.test.js")
    _assert_exists(unittest_dir / "manual_app_test.go")
    _ok("CLI scaffold unittest")

    cicd_dir = workdir / "combined-cicd"
    cicd_dir.mkdir()
    _run_cli(
        "scaffold",
        "cicd",
        "--name",
        "manual-app",
        "--type",
        "build",
        "--languages",
        "python",
        "--github",
        "--jenkins",
        "--output-dir",
        str(cicd_dir),
        cwd=workdir,
    )
    _assert_exists(cicd_dir / ".github" / "workflows" / "manual-app-build.yml")
    _assert_exists(cicd_dir / "Jenkinsfile")
    _ok("CLI scaffold cicd")

    result = _run_cli("process-first", "--section", "what", cwd=workdir)
    _assert("Process-First" in result.stdout, "process-first output looks incomplete")
    _ok("CLI process-first")


def run_init_smoke() -> None:
    checkbox_selections = iter(
        [
            ["python", "go"],
            ["docker"],
            ["gradle"],
            ["sonarqube"],
            ["kubectl", "k9s"],
            ["github_actions", "terraform"],
            ["prometheus"],
        ]
    )

    def checkbox_factory(**_: object) -> MagicMock:
        mock = MagicMock()
        mock.execute.return_value = next(checkbox_selections)
        return mock

    text_mock = MagicMock()
    text_mock.execute.return_value = "3.12"
    confirm_mock = MagicMock()
    confirm_mock.execute.return_value = True

    with tempfile.TemporaryDirectory(prefix="devopsos-init-") as tmpdir:
        with patch("cli.devopsos.inquirer.checkbox", side_effect=checkbox_factory), patch(
            "cli.devopsos.inquirer.text", return_value=text_mock
        ), patch("cli.devopsos.inquirer.confirm", return_value=confirm_mock):
            result = CliRunner().invoke(app, ["init", "--dir", tmpdir])

        if result.exit_code != 0:
            _fail(f"`devopsos init` smoke test failed\n{result.output}")

        devcontainer_dir = Path(tmpdir) / ".devcontainer"
        _assert_exists(devcontainer_dir / "Dockerfile")
        _assert_exists(devcontainer_dir / "devcontainer.json")
        _assert_exists(devcontainer_dir / "devcontainer.env.json")

        generated = json.loads((devcontainer_dir / "devcontainer.json").read_text(encoding="utf-8"))
        _assert("features" in generated, "`init` should generate hybrid devcontainer.json with features")
        _assert("build" in generated, "`init` should generate build config")
        _ok("CLI init")


def run_mcp_smoke() -> None:
    try:
        from mcp_server.server import (
            generate_argocd_config,
            generate_github_actions_workflow,
            generate_gitlab_ci_pipeline,
            generate_jenkins_pipeline,
            generate_k8s_config,
            generate_sre_configs,
            generate_unittest_config,
            scaffold_devcontainer,
        )
    except ModuleNotFoundError as exc:
        _fail(
            "MCP smoke tests require mcp_server dependencies. "
            "Install `pip install -r mcp_server/requirements.txt` "
            f"or rerun with --skip-mcp. Missing module: {exc.name}"
        )

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
    parser = argparse.ArgumentParser(description="Run DevOps-OS manual smoke tests.")
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary CLI output directory and print its path.",
    )
    parser.add_argument(
        "--skip-mcp",
        action="store_true",
        help="Skip MCP smoke tests when mcp_server dependencies are not installed locally.",
    )
    args = parser.parse_args()

    tempdir = Path(tempfile.mkdtemp(prefix="devopsos-manual-smoke-"))
    print(f"Using temp directory: {tempdir}")

    try:
        run_cli_smoke(tempdir)
        run_init_smoke()
        if args.skip_mcp:
            print("SKIP  MCP smoke tests")
        else:
            run_mcp_smoke()
    finally:
        if args.keep_temp:
            print(f"Kept temp directory: {tempdir}")
        else:
            shutil.rmtree(tempdir, ignore_errors=True)

    print("All manual smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
