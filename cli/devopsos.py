import enum
import sys
import typer
from InquirerPy import inquirer
import json
import os
from pathlib import Path

# Import the refactored main functions from scaffold scripts
import cli.scaffold_cicd as scaffold_cicd
import cli.scaffold_gha as scaffold_gha
import cli.scaffold_jenkins as scaffold_jenkins
import cli.scaffold_gitlab as scaffold_gitlab
import cli.scaffold_argocd as scaffold_argocd
import cli.scaffold_sre as scaffold_sre
import cli.scaffold_devcontainer as scaffold_devcontainer
import cli.process_first as process_first

class ProcessFirstSection(str, enum.Enum):
    """Valid sections for the process-first command."""
    what = "what"
    mapping = "mapping"
    tips = "tips"
    best_practices = "best_practices"
    all = "all"


app = typer.Typer(help="Unified DevOps-OS CLI tool")

@app.command()
def init(
    directory: str = typer.Option(".", "--dir", help="Target directory in which the .devcontainer folder will be created (defaults to the current directory)"),
):
    """Interactive project initializer."""
    typer.echo("Welcome to DevOps-OS Init Wizard!")
    typer.echo("Tools are grouped by Process-First DevOps principles (Systems Thinking).\n")

    # ── Canonical tool lists ──────────────────────────────────────────────
    ALL_LANGUAGES    = ["python", "java", "node", "ruby", "csharp", "php", "rust",
                        "typescript", "kotlin", "c", "cpp", "javascript", "go"]
    ALL_CICD         = ["docker", "podman", "terraform", "kubectl", "helm", "github_actions", "jenkins"]
    ALL_KUBERNETES   = ["k9s", "kustomize", "argocd_cli", "lens", "kubeseal",
                        "flux", "kind", "minikube", "openshift_cli"]
    ALL_BUILD_TOOLS  = ["gradle", "maven", "ant", "make", "cmake"]
    ALL_CODE_ANALYSIS = ["sonarqube", "checkstyle", "pmd", "eslint", "pylint"]
    ALL_DEVOPS_TOOLS  = ["nexus", "prometheus", "grafana", "elk", "jenkins"]

    versions_defaults = {
        "python": "3.11", "java": "17", "node": "20", "go": "1.21", "nexus": "3.50.0",
        "prometheus": "2.45.0", "grafana": "10.0.0", "k9s": "0.29.1", "argocd": "2.8.4",
        "flux": "2.1.2", "kustomize": "5.2.1", "jenkins": "2.440.1"
    }

    # ── Wizard groups aligned with Process-First DevOps principles ────────
    # Each group maps to a DevOps stage in the Systems Thinking value stream.
    wizard_groups = {
        "Languages": {
            "choices": ALL_LANGUAGES,
            "description": "Programming languages for your project",
        },
        "Containerization  [CONTAINER stage]": {
            "choices": ["docker", "podman"],
            "description": "Container runtimes to build, ship, and run application images",
        },
        "Build Tools  [BUILD stage]": {
            "choices": ["gradle", "maven", "ant", "make", "cmake", "nexus"],
            "description": "Tools to compile, package, and store build artifacts",
        },
        "Test & Quality  [TEST stage]": {
            "choices": ["sonarqube", "checkstyle", "pmd", "eslint", "pylint"],
            "description": "Static analysis and quality gates to enforce standards early",
        },
        "Kubernetes  [KUBERNETES stage]": {
            "choices": ["kubectl", "helm", "kustomize", "k9s", "argocd_cli",
                        "flux", "kind", "minikube", "lens", "kubeseal", "openshift_cli"],
            "description": "Kubernetes CLI tools, GitOps engines, and local cluster runtimes",
        },
        "CI/CD & Deploy  [DEPLOY stage]": {
            "choices": ["github_actions", "jenkins", "terraform"],
            "description": "CI/CD pipelines, IaC provisioning, and deployment automation",
        },
        "SRE & Monitoring  [SRE/MONITORING stage]": {
            "choices": ["prometheus", "grafana", "elk"],
            "description": "Observability stack: metrics, dashboards, and centralised logs",
        },
    }

    selected_by_group: dict = {}
    selected_versions: dict = {}

    for group_label, group_info in wizard_groups.items():
        typer.echo(f"\n  📌 {group_info['description']}")
        selected = inquirer.checkbox(
            message=f"Select {group_label}:",
            choices=group_info["choices"],
            instruction="(Space to select, ↑↓ to navigate, Enter to confirm)",
        ).execute()
        selected_by_group[group_label] = selected

    # ── Version prompts ───────────────────────────────────────────────────
    all_selected = {tool for tools in selected_by_group.values() for tool in tools}
    for tool in all_selected:
        vkey = "argocd" if tool == "argocd_cli" else tool
        if vkey in versions_defaults:
            selected_versions[vkey] = inquirer.text(
                message=f"{tool.title()} version:",
                default=versions_defaults[vkey],
            ).execute()

    # ── Map wizard selections back to legacy JSON structure ───────────────
    # Keep the devcontainer.env.json keys identical to scaffold_devcontainer
    # output for backward compatibility.
    def _sel(group): return selected_by_group.get(group, [])

    container_sel = _sel("Containerization  [CONTAINER stage]")
    build_sel     = _sel("Build Tools  [BUILD stage]")
    test_sel      = _sel("Test & Quality  [TEST stage]")
    k8s_sel       = _sel("Kubernetes  [KUBERNETES stage]")
    deploy_sel    = _sel("CI/CD & Deploy  [DEPLOY stage]")
    sre_sel       = _sel("SRE & Monitoring  [SRE/MONITORING stage]")
    lang_sel      = _sel("Languages")

    config = {
        "languages": {opt: opt in lang_sel for opt in ALL_LANGUAGES},
        "cicd": {
            "docker":         "docker"         in container_sel,
            "podman":         "podman"         in container_sel,
            "terraform":      "terraform"      in deploy_sel,
            "kubectl":        "kubectl"        in k8s_sel,
            "helm":           "helm"           in k8s_sel,
            "github_actions": "github_actions" in deploy_sel,
            "jenkins":        "jenkins"        in deploy_sel,
        },
        "kubernetes": {
            "k9s":           "k9s"           in k8s_sel,
            "kustomize":     "kustomize"     in k8s_sel,
            "argocd_cli":    "argocd_cli"    in k8s_sel,
            "lens":          "lens"          in k8s_sel,
            "kubeseal":      "kubeseal"      in k8s_sel,
            "flux":          "flux"          in k8s_sel,
            "kind":          "kind"          in k8s_sel,
            "minikube":      "minikube"      in k8s_sel,
            "openshift_cli": "openshift_cli" in k8s_sel,
        },
        "build_tools": {opt: opt in build_sel for opt in ALL_BUILD_TOOLS},
        "code_analysis": {opt: opt in test_sel for opt in ALL_CODE_ANALYSIS},
        "devops_tools": {
            "nexus":      "nexus"      in build_sel,
            "prometheus": "prometheus" in sre_sel,
            "grafana":    "grafana"    in sre_sel,
            "elk":        "elk"        in sre_sel,
            "jenkins":    "jenkins"    in deploy_sel,
        },
        "versions": selected_versions,
    }

    # Review step: show config and confirm
    typer.echo("\nReview your configuration:")
    typer.echo(json.dumps(config, indent=2))
    if not inquirer.confirm(message="Proceed with this configuration?", default=True).execute():
        typer.echo("Aborted by user.")
        raise typer.Exit(1)

    # Write to .devcontainer/devcontainer.env.json
    devcontainer_dir = Path(directory) / ".devcontainer"
    devcontainer_dir.mkdir(parents=True, exist_ok=True)
    env_json_path = devcontainer_dir / "devcontainer.env.json"
    with open(env_json_path, "w") as f:
        json.dump(config, f, indent=2)
    typer.echo(f"Wrote configuration to {env_json_path}")

    # Offer to generate Dockerfile/devcontainer.json
    if inquirer.confirm(message="Generate Dockerfile and devcontainer.json now?", default=True).execute():
        # Map config to build args for devcontainer.json
        build_args = {}
        # Languages
        lang_map = {
            "python": "INSTALL_PYTHON", "java": "INSTALL_JAVA", "node": "INSTALL_JS",
            "ruby": "INSTALL_RUBY", "csharp": "INSTALL_CSHARP", "php": "INSTALL_PHP",
            "rust": "INSTALL_RUST", "typescript": "INSTALL_TYPESCRIPT",
            "kotlin": "INSTALL_KOTLIN", "c": "INSTALL_C", "cpp": "INSTALL_CPP",
            "javascript": "INSTALL_JAVASCRIPT", "go": "INSTALL_GO"
        }
        for lang, arg in lang_map.items():
            build_args[arg] = str(config["languages"].get(lang, False)).lower()
        # CICD (includes container runtimes docker/podman)
        cicd_map = {
            "docker": "INSTALL_DOCKER", "podman": "INSTALL_PODMAN",
            "terraform": "INSTALL_TERRAFORM",
            "kubectl": "INSTALL_KUBECTL", "helm": "INSTALL_HELM",
            "github_actions": "INSTALL_GITHUB_ACTIONS", "jenkins": "INSTALL_JENKINS"
        }
        for tool, arg in cicd_map.items():
            build_args[arg] = str(config["cicd"].get(tool, False)).lower()
        # Kubernetes
        k8s_map = {
            "k9s": "INSTALL_K9S", "kustomize": "INSTALL_KUSTOMIZE",
            "argocd_cli": "INSTALL_ARGOCD_CLI", "lens": "INSTALL_LENS",
            "kubeseal": "INSTALL_KUBESEAL", "flux": "INSTALL_FLUX",
            "kind": "INSTALL_KIND", "minikube": "INSTALL_MINIKUBE",
            "openshift_cli": "INSTALL_OPENSHIFT_CLI"
        }
        for tool, arg in k8s_map.items():
            build_args[arg] = str(config["kubernetes"].get(tool, False)).lower()
        # Build tools
        build_map = {
            "gradle": "INSTALL_GRADLE", "maven": "INSTALL_MAVEN", "ant": "INSTALL_ANT",
            "make": "INSTALL_MAKE", "cmake": "INSTALL_CMAKE"
        }
        for tool, arg in build_map.items():
            build_args[arg] = str(config["build_tools"].get(tool, False)).lower()
        # Code analysis
        analysis_map = {
            "sonarqube": "INSTALL_SONARQUBE", "checkstyle": "INSTALL_CHECKSTYLE",
            "pmd": "INSTALL_PMD", "eslint": "INSTALL_ESLINT", "pylint": "INSTALL_PYLINT"
        }
        for tool, arg in analysis_map.items():
            build_args[arg] = str(config["code_analysis"].get(tool, False)).lower()
        # DevOps tools
        devops_map = {
            "nexus": "INSTALL_NEXUS", "prometheus": "INSTALL_PROMETHEUS",
            "grafana": "INSTALL_GRAFANA", "elk": "INSTALL_ELK",
            "jenkins": "INSTALL_JENKINS"
        }
        for tool, arg in devops_map.items():
            build_args[arg] = str(config["devops_tools"].get(tool, False)).lower()
        # Versions (only for selected)
        for k, v in config["versions"].items():
            build_args[k.upper() + ("_VERSION" if k not in ["k9s", "argocd", "flux", "kustomize"] else "")] = v
        # Update devcontainer.json
        devcontainer_json_path = devcontainer_dir / "devcontainer.json"
        if devcontainer_json_path.exists():
            with open(devcontainer_json_path) as f:
                devcontainer_json = json.load(f)
        else:
            devcontainer_json = {"build": {"dockerfile": "Dockerfile", "args": {}}}
        devcontainer_json.setdefault("build", {})["args"] = build_args
        with open(devcontainer_json_path, "w") as f:
            json.dump(devcontainer_json, f, indent=2)
        typer.echo(f"Updated {devcontainer_json_path} with build args.")
        # Optionally, update Dockerfile (not strictly needed if it uses build args)
        typer.echo("Dockerfile uses build args; ensure it references the correct ARGs.")

@app.command()
def scaffold(
    target: str = typer.Argument(..., help="What to scaffold: cicd | gha | gitlab | jenkins | argocd | sre | devcontainer"),
    tool: str = typer.Option(None, help="Tool type (e.g., github, jenkins, argo, flux)"),
):
    """Scaffold CI/CD or K8s resources."""
    # Each scaffold module uses argparse internally and calls parse_args() which
    # reads sys.argv.  When invoked via `python -m cli.devopsos scaffold <target>`
    # sys.argv still contains the parent CLI tokens (e.g. ['devopsos.py', 'scaffold',
    # 'gha']).  Temporarily strip those extra tokens so argparse inside each
    # scaffold module only sees the program name and falls back to env-var / default
    # values, then restore sys.argv afterwards.
    _saved_argv = sys.argv[:]
    sys.argv = sys.argv[:1]
    try:
        if target == "cicd":
            scaffold_cicd.main()
        elif target == "gha":
            scaffold_gha.main()
        elif target == "gitlab":
            scaffold_gitlab.main()
        elif target == "jenkins":
            scaffold_jenkins.main()
        elif target == "argocd":
            scaffold_argocd.main()
        elif target == "sre":
            scaffold_sre.main()
        elif target == "devcontainer":
            scaffold_devcontainer.main()
        else:
            typer.echo("Unknown scaffold target.")
    finally:
        sys.argv = _saved_argv

@app.command("process-first")
def process_first_cmd(
    section: ProcessFirstSection = typer.Option(
        ProcessFirstSection.all,
        help=(
            "Section to display:\n\n"
            "  'what'           — What Process-First is, 5 core principles + thought leaders\n\n"
            "  'mapping'        — How each principle maps to a devopsos scaffold command\n\n"
            "  'tips'           — AI prompts and book recommendations for DevOps beginners\n\n"
            "  'best_practices' — Best practices by stage (build/test/iac/deploy/sre/monitoring/security)\n\n"
            "  'all'            — All sections combined (default)"
        ),
        show_choices=True,
    ),
):
    """Learn about the Process-First SDLC philosophy and how it maps to DevOps-OS tooling.

    \b
    Quick invocation guide:

      python -m cli.devopsos process-first                           # full overview
      python -m cli.devopsos process-first --section what            # core principles + thought leaders
      python -m cli.devopsos process-first --section mapping         # tool mapping table
      python -m cli.devopsos process-first --section tips            # AI prompts for beginners
      python -m cli.devopsos process-first --section best_practices  # best practices by stage

    You can also run the module directly:

      python -m cli.process_first
      python -m cli.process_first --section best_practices
    """
    process_first.display(section.value)


if __name__ == "__main__":
    app()
