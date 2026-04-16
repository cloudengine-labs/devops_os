#!/usr/bin/env python3
"""
DevOps-OS onboarding POC orchestration for the Chennai FOSS demo.

This module analyzes a local Git repository, detects the primary language,
reuses the existing DevOps-OS scaffold generators, and writes a compact JSON
summary that can be consumed by a static dashboard page.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from cli import scaffold_argocd, scaffold_devcontainer, scaffold_gha, scaffold_sre, scaffold_unittest


ENV_PREFIX = "DEVOPS_OS_ONBOARD_"

LANGUAGE_EXTENSIONS = {
    "go": {".go"},
    "python": {".py"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "java": {".java"},
}

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".github",
    ".devcontainer",
    "argocd",
    "flux",
    "sre",
    "unittest",
}

DEVCONTAINER_LANGS = {"go", "python", "javascript", "typescript", "java"}
UNITTEST_LANGS = {"go", "python", "javascript", "typescript"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a repo and scaffold a Chennai FOSS onboarding demo output."
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get(f"{ENV_PREFIX}REPO", "."),
        help="Local git repository path to analyze and scaffold.",
    )
    parser.add_argument(
        "--repo-url",
        default=os.environ.get(f"{ENV_PREFIX}REPO_URL", ""),
        help="Optional repository URL shown in the dashboard.",
    )
    parser.add_argument(
        "--name",
        default=os.environ.get(f"{ENV_PREFIX}NAME", "demo-app"),
        help="Application name used in generated templates.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", ""),
        help="Output directory for generated assets. Defaults to the repo path.",
    )
    parser.add_argument(
        "--enable-ci",
        dest="enable_ci",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}ENABLE_CI", "true").lower() in ("1", "true", "yes"),
        help="Generate GitHub Actions CI assets.",
    )
    parser.add_argument("--disable-ci", dest="enable_ci", action="store_false")
    parser.add_argument(
        "--enable-unittest",
        dest="enable_unittest",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}ENABLE_UNITTEST", "true").lower()
        in ("1", "true", "yes"),
        help="Generate unit test scaffold assets.",
    )
    parser.add_argument("--disable-unittest", dest="enable_unittest", action="store_false")
    parser.add_argument(
        "--enable-container",
        dest="enable_container",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}ENABLE_CONTAINER", "true").lower()
        in ("1", "true", "yes"),
        help="Generate container/devcontainer assets.",
    )
    parser.add_argument("--disable-container", dest="enable_container", action="store_false")
    parser.add_argument(
        "--enable-cd",
        dest="enable_cd",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}ENABLE_CD", "false").lower() in ("1", "true", "yes"),
        help="Generate ArgoCD GitOps assets.",
    )
    parser.add_argument("--disable-cd", dest="enable_cd", action="store_false")
    parser.add_argument(
        "--enable-sre",
        dest="enable_sre",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}ENABLE_SRE", "false").lower() in ("1", "true", "yes"),
        help="Generate SRE/monitoring assets.",
    )
    parser.add_argument("--disable-sre", dest="enable_sre", action="store_false")
    return parser.parse_args()


def _run_module_main(module_main, flags: list[str]) -> None:
    saved = sys.argv[:]
    sys.argv = sys.argv[:1] + flags
    try:
        module_main()
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise RuntimeError(f"Generator exited with code {exc.code}: {' '.join(flags)}") from exc
    finally:
        sys.argv = saved


def _git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _relative_to_output(output_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(output_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _safe_read_preview(path: Path, limit: int = 220) -> str:
    try:
        content = path.read_text()
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="replace")
    return content[:limit].strip()


def _find_first_file(path: Path) -> Path:
    if path.is_file():
        return path
    for candidate in sorted(path.rglob("*")):
        if candidate.is_file():
            return candidate
    return path


def detect_primary_language(repo_path: Path) -> tuple[str, dict[str, int]]:
    counts: Counter[str] = Counter()
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file_name in files:
            extension = Path(file_name).suffix.lower()
            for language, extensions in LANGUAGE_EXTENSIONS.items():
                if extension in extensions:
                    counts[language] += 1
    if not counts:
        return "unknown", {}
    primary_language = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return primary_language, dict(counts)


def analyze_repository(repo_path: Path, repo_url: str = "") -> dict[str, Any]:
    branch = _git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    commit = _git(repo_path, "rev-parse", "--short", "HEAD")
    if repo_url:
        detected_url = repo_url
    else:
        try:
            detected_url = _git(repo_path, "config", "--get", "remote.origin.url")
        except RuntimeError:
            detected_url = ""
    primary_language, language_counts = detect_primary_language(repo_path)
    recommended = {
        "ci": True,
        "unittest": primary_language in UNITTEST_LANGS,
        "container": primary_language in DEVCONTAINER_LANGS,
        "cd": False,
        "sre": False,
    }
    return {
        "repo_path": str(repo_path.resolve()),
        "repo_url": detected_url,
        "branch": branch,
        "commit": commit,
        "primary_language": primary_language,
        "language_counts": language_counts,
        "recommended_templates": recommended,
    }


def _workflow_filename(name: str) -> str:
    return f"{name.lower().replace(' ', '-')}-complete.yml"


def generate_onboarding_assets(
    repo_path: Path,
    output_dir: Path,
    name: str,
    repo_url: str,
    enable_ci: bool,
    enable_unittest: bool,
    enable_container: bool,
    enable_cd: bool,
    enable_sre: bool,
) -> dict[str, Any]:
    analysis = analyze_repository(repo_path, repo_url=repo_url)
    language = analysis["primary_language"]
    languages_for_scaffold = language if language != "unknown" else "python"

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_records: list[dict[str, str]] = []

    if enable_ci:
        gha_flags = [
            "--name",
            name,
            "--languages",
            languages_for_scaffold,
            "--type",
            "complete",
            "--output",
            str(output_dir / ".github" / "workflows"),
        ]
        if enable_cd:
            gha_flags += ["--kubernetes", "--k8s-method", "argocd"]
        _run_module_main(scaffold_gha.main, gha_flags)
        workflow_path = output_dir / ".github" / "workflows" / _workflow_filename(name)
        artifact_records.append(
            {
                "key": "ci",
                "label": "GitHub Actions workflow",
                "path": _relative_to_output(output_dir, workflow_path),
                "preview": _safe_read_preview(workflow_path),
            }
        )

    if enable_unittest:
        _run_module_main(
            scaffold_unittest.main,
            [
                "--name",
                name,
                "--languages",
                languages_for_scaffold,
                "--output-dir",
                str(output_dir / "unittest"),
            ],
        )
        unit_target = output_dir / "unittest"
        artifact_records.append(
            {
                "key": "unittest",
                "label": "Unit test scaffold",
                "path": _relative_to_output(output_dir, unit_target),
                "preview": _safe_read_preview(_find_first_file(unit_target)),
            }
        )

    if enable_container:
        devops_tools = []
        if enable_sre:
            devops_tools = ["prometheus", "grafana"]
        kubernetes_tools = ["kubectl", "helm"]
        if enable_cd:
            kubernetes_tools.extend(["argocd_cli", "flux"])
        _run_module_main(
            scaffold_devcontainer.main,
            [
                "--languages",
                languages_for_scaffold,
                "--cicd-tools",
                "docker,github_actions",
                "--kubernetes-tools",
                ",".join(kubernetes_tools),
                "--devops-tools",
                ",".join(devops_tools),
                "--output-dir",
                str(output_dir),
            ],
        )
        devcontainer_path = output_dir / ".devcontainer" / "devcontainer.json"
        artifact_records.append(
            {
                "key": "container",
                "label": "Dev container / container baseline",
                "path": _relative_to_output(output_dir, devcontainer_path),
                "preview": _safe_read_preview(devcontainer_path),
            }
        )

    if enable_cd:
        _run_module_main(
            scaffold_argocd.main,
            [
                "--name",
                name,
                "--repo",
                analysis["repo_url"] or "https://github.com/cloudengine-labs/devops_os.git",
                "--path",
                "k8s",
                "--auto-sync",
                "--output-dir",
                str(output_dir),
            ],
        )
        argocd_path = output_dir / "argocd" / "application.yaml"
        artifact_records.append(
            {
                "key": "cd",
                "label": "ArgoCD deployment template",
                "path": _relative_to_output(output_dir, argocd_path),
                "preview": _safe_read_preview(argocd_path),
            }
        )

    if enable_sre:
        _run_module_main(
            scaffold_sre.main,
            [
                "--name",
                name,
                "--team",
                "platform",
                "--slo-target",
                "99.9",
                "--output-dir",
                str(output_dir / "sre"),
            ],
        )
        sre_path = output_dir / "sre" / "grafana-dashboard.json"
        artifact_records.append(
            {
                "key": "sre",
                "label": "SRE dashboard template",
                "path": _relative_to_output(output_dir, sre_path),
                "preview": _safe_read_preview(sre_path),
            }
        )

    stages = [
        {"key": "connected", "label": "Repo connected", "state": "done"},
        {"key": "analysed", "label": "Branch / commit detected", "state": "done"},
        {"key": "language", "label": f"Language detected: {analysis['primary_language']}", "state": "done"},
        {"key": "ci", "label": "CI scaffolded", "state": "done" if enable_ci else "skipped"},
        {
            "key": "unittest",
            "label": "Unit tests scaffolded",
            "state": "done" if enable_unittest else "skipped",
        },
        {
            "key": "container",
            "label": "Containerization scaffolded",
            "state": "done" if enable_container else "skipped",
        },
        {"key": "cd", "label": "CD scaffolded", "state": "done" if enable_cd else "skipped"},
        {"key": "sre", "label": "SRE scaffolded", "state": "done" if enable_sre else "skipped"},
        {"key": "review", "label": "Ready for review", "state": "done"},
    ]

    summary = {
        "demo": {
            "title": "Chennai FOSS IDP Onboarding POC",
            "app_name": name,
            "status_model": [
                "Connected",
                "Analysed",
                "Templates selected",
                "Generated",
                "Ready for review",
                "Optional deploy enabled",
                "Optional observability enabled",
            ],
            "todo": {
                "jira": [
                    "Create onboarding tasks automatically",
                    "Link generated assets to epics or stories",
                    "Sync dashboard stage updates back to Jira",
                ],
                "cloud": [
                    "Add cloud target selection during onboarding",
                    "Generate cloud-specific deployment overlays",
                    "Show environment and rollout status in the dashboard",
                ],
            },
        },
        "repo": analysis,
        "selected_templates": {
            "ci": enable_ci,
            "unittest": enable_unittest,
            "container": enable_container,
            "cd": enable_cd,
            "sre": enable_sre,
        },
        "stages": stages,
        "artifacts": artifact_records,
        "generated_output_dir": str(output_dir.resolve()),
    }

    summary_path = output_dir / "onboarding-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    args = parse_arguments()
    repo_path = Path(args.repo).resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        raise SystemExit(f"Repository path does not exist or is not a directory: {repo_path}")

    output_dir = Path(args.output_dir).resolve() if args.output_dir else repo_path
    summary = generate_onboarding_assets(
        repo_path=repo_path,
        output_dir=output_dir,
        name=args.name,
        repo_url=args.repo_url,
        enable_ci=args.enable_ci,
        enable_unittest=args.enable_unittest,
        enable_container=args.enable_container,
        enable_cd=args.enable_cd,
        enable_sre=args.enable_sre,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
