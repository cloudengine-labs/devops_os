import enum
import sys
import typer
from InquirerPy import inquirer
import json
import os
from pathlib import Path
from typing import Optional

# Import scaffold modules — used as libraries by the unified scaffold sub-commands
import cli.scaffold_cicd as scaffold_cicd
import cli.scaffold_gha as scaffold_gha
import cli.scaffold_jenkins as scaffold_jenkins
import cli.scaffold_gitlab as scaffold_gitlab
import cli.scaffold_argocd as scaffold_argocd
import cli.scaffold_sre as scaffold_sre
import cli.scaffold_devcontainer as scaffold_devcontainer
import cli.scaffold_unittest as scaffold_unittest
import cli.process_first as process_first
from cli import __version__
from cli.devcontainer_templates import (
    ALL_BUILD_TOOLS,
    ALL_CICD,
    ALL_CODE_ANALYSIS,
    ALL_DEVOPS_TOOLS,
    ALL_KUBERNETES,
    ALL_LANGUAGES,
    DEFAULT_VERSIONS,
    write_generated_devcontainer,
)

class ProcessFirstSection(str, enum.Enum):
    """Valid sections for the process-first command."""
    what = "what"
    mapping = "mapping"
    tips = "tips"
    best_practices = "best_practices"
    all = "all"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"devopsos version {__version__}")
        raise typer.Exit()


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the current version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """DevOps-OS: automate your entire DevOps lifecycle.

    \b
    Examples:

      python -m cli.devopsos init                                    # interactive project setup wizard
      python -m cli.devopsos scaffold gha --help                     # GitHub Actions scaffold options
      python -m cli.devopsos scaffold gitlab --type build            # GitLab CI build pipeline
      python -m cli.devopsos scaffold argocd --app-name my-app       # Argo CD application manifest
      python -m cli.devopsos scaffold jenkins --help                 # Jenkins pipeline options
      python -m cli.devopsos scaffold sre --help                     # SRE resources (SLOs, alerts, dashboards)
      python -m cli.devopsos scaffold devcontainer --help            # dev container configuration
      python -m cli.devopsos scaffold cicd --help                    # combined CI/CD scaffold
      python -m cli.devopsos process-first                           # Process-First SDLC overview
      python -m cli.devopsos --version                               # show installed version
    """

# ---------------------------------------------------------------------------
# scaffold sub-app — each scaffold target is a proper Typer subcommand so
# that `devopsos scaffold gha --help` shows all GHA-specific options natively
# instead of requiring the user to know about the underlying module.
# ---------------------------------------------------------------------------

scaffold_app = typer.Typer(
    name="scaffold",
    help="Scaffold CI/CD configs, GitOps manifests, SRE resources, and dev containers.",
    no_args_is_help=True,
)
app.add_typer(scaffold_app, name="scaffold")


def _run_scaffold(module_main, flags: list):
    """Call *module_main()* with the given CLI flag list via sys.argv.

    Each scaffold module uses argparse internally.  We temporarily replace
    sys.argv so argparse sees only the program name and the explicit flags
    we build from the Typer-parsed options, then restore sys.argv afterwards.
    """
    _saved = sys.argv[:]
    sys.argv = sys.argv[:1] + flags
    try:
        module_main()
    finally:
        sys.argv = _saved


def _show_help_if_no_opts(ctx: typer.Context) -> None:
    """Print the command's help text and exit when the user provides no options.

    This gives a friendly usage summary instead of silently running with all
    defaults, which can be confusing.  Flags are detected by looking for any
    ``--`` argument in sys.argv; ``--help`` is always handled by Typer/Click
    before our function body runs, so that path is unaffected.
    """
    if not any(a.startswith("-") for a in sys.argv[1:]):
        typer.echo(ctx.get_help())
        raise typer.Exit()


# ── scaffold gha ────────────────────────────────────────────────────────────

@scaffold_app.command("gha")
def scaffold_gha_cmd(
    ctx: typer.Context,
    name: str = typer.Option("DevOps-OS", envvar="DEVOPS_OS_GHA_NAME",
                              help="Workflow name"),
    workflow_type: str = typer.Option("complete", "--type", envvar="DEVOPS_OS_GHA_TYPE",
                                      help="Workflow type: build | test | deploy | complete | reusable"),
    languages: str = typer.Option("python,javascript", envvar="DEVOPS_OS_GHA_LANGUAGES",
                                   help="Comma-separated languages: python, java, javascript, go"),
    kubernetes: bool = typer.Option(False, envvar="DEVOPS_OS_GHA_KUBERNETES",
                                    help="Include Kubernetes deployment steps"),
    registry: str = typer.Option("ghcr.io", envvar="DEVOPS_OS_GHA_REGISTRY",
                                  help="Container registry URL"),
    k8s_method: str = typer.Option("kubectl", "--k8s-method", envvar="DEVOPS_OS_GHA_K8S_METHOD",
                                    help="K8s deploy method: kubectl | kustomize | argocd | flux"),
    output: str = typer.Option(".github/workflows", envvar="DEVOPS_OS_GHA_OUTPUT",
                                help="Output directory for generated workflow files"),
    custom_values: Optional[str] = typer.Option(None, "--custom-values",
                                                  envvar="DEVOPS_OS_GHA_CUSTOM_VALUES",
                                                  help="Path to custom values JSON file"),
    image: str = typer.Option("ghcr.io/yourorg/devops-os:latest", envvar="DEVOPS_OS_GHA_IMAGE",
                               help="DevOps-OS container image"),
    branches: str = typer.Option("main", envvar="DEVOPS_OS_GHA_BRANCHES",
                                  help="Comma-separated branches that trigger the workflow"),
    matrix: bool = typer.Option(False, envvar="DEVOPS_OS_GHA_MATRIX",
                                 help="Enable matrix builds (multiple OS/architectures)"),
    env_file: Optional[str] = typer.Option(None, "--env-file", envvar="DEVOPS_OS_GHA_ENV_FILE",
                                            help="Path to devcontainer.env.json for tool selection"),
    reusable: bool = typer.Option(False, envvar="DEVOPS_OS_GHA_REUSABLE",
                                   help="Generate a reusable workflow callable from other workflows"),
):
    """Generate a GitHub Actions workflow YAML file.

    \b
    Examples:
      devopsos scaffold gha --name my-app --languages python,javascript --type complete
      devopsos scaffold gha --name my-app --type deploy --kubernetes --k8s-method argocd
      devopsos scaffold gha --name my-app --matrix
      devopsos scaffold gha --name shared --type reusable
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--type", workflow_type,
        "--languages", languages,
        "--registry", registry,
        "--k8s-method", k8s_method,
        "--output", output,
        "--image", image,
        "--branches", branches,
    ]
    if kubernetes:
        flags.append("--kubernetes")
    if matrix:
        flags.append("--matrix")
    if reusable:
        flags.append("--reusable")
    if custom_values:
        flags += ["--custom-values", custom_values]
    if env_file:
        flags += ["--env-file", env_file]
    _run_scaffold(scaffold_gha.main, flags)


# ── scaffold jenkins ────────────────────────────────────────────────────────

@scaffold_app.command("jenkins")
def scaffold_jenkins_cmd(
    ctx: typer.Context,
    name: str = typer.Option("DevOps-OS", envvar="DEVOPS_OS_JENKINS_NAME",
                              help="Pipeline name"),
    pipeline_type: str = typer.Option("complete", "--type", envvar="DEVOPS_OS_JENKINS_TYPE",
                                       help="Pipeline type: build | test | deploy | complete | parameterized"),
    languages: str = typer.Option("python,javascript", envvar="DEVOPS_OS_JENKINS_LANGUAGES",
                                   help="Comma-separated languages: python, java, javascript, go"),
    kubernetes: bool = typer.Option(False, envvar="DEVOPS_OS_JENKINS_KUBERNETES",
                                    help="Include Kubernetes deployment steps"),
    registry: str = typer.Option("docker.io", envvar="DEVOPS_OS_JENKINS_REGISTRY",
                                  help="Container registry URL"),
    k8s_method: str = typer.Option("kubectl", "--k8s-method", envvar="DEVOPS_OS_JENKINS_K8S_METHOD",
                                    help="K8s deploy method: kubectl | kustomize | argocd | flux"),
    output: str = typer.Option("Jenkinsfile", envvar="DEVOPS_OS_JENKINS_OUTPUT",
                                help="Output file path for the generated Jenkinsfile"),
    custom_values: Optional[str] = typer.Option(None, "--custom-values",
                                                  envvar="DEVOPS_OS_JENKINS_CUSTOM_VALUES",
                                                  help="Path to custom values JSON file"),
    image: str = typer.Option("docker.io/yourorg/devops-os:latest", envvar="DEVOPS_OS_JENKINS_IMAGE",
                               help="DevOps-OS container image"),
    scm: str = typer.Option("git", envvar="DEVOPS_OS_JENKINS_SCM",
                             help="Source control system: git | svn | none"),
    parameters: bool = typer.Option(False, envvar="DEVOPS_OS_JENKINS_PARAMETERS",
                                    help="Generate pipeline with runtime parameters"),
    env_file: Optional[str] = typer.Option(None, "--env-file", envvar="DEVOPS_OS_JENKINS_ENV_FILE",
                                            help="Path to devcontainer.env.json for tool selection"),
):
    """Generate a Jenkins pipeline (Jenkinsfile).

    \b
    Examples:
      devopsos scaffold jenkins --name java-api --languages java --type complete
      devopsos scaffold jenkins --name my-app --languages python --type parameterized
      devopsos scaffold jenkins --name my-app --languages go --kubernetes --k8s-method argocd
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--type", pipeline_type,
        "--languages", languages,
        "--registry", registry,
        "--k8s-method", k8s_method,
        "--output", output,
        "--image", image,
        "--scm", scm,
    ]
    if kubernetes:
        flags.append("--kubernetes")
    if parameters:
        flags.append("--parameters")
    if custom_values:
        flags += ["--custom-values", custom_values]
    if env_file:
        flags += ["--env-file", env_file]
    _run_scaffold(scaffold_jenkins.main, flags)


# ── scaffold gitlab ─────────────────────────────────────────────────────────

@scaffold_app.command("gitlab")
def scaffold_gitlab_cmd(
    ctx: typer.Context,
    name: str = typer.Option("my-app", envvar="DEVOPS_OS_GITLAB_NAME",
                              help="Application / pipeline name"),
    pipeline_type: str = typer.Option("complete", "--type", envvar="DEVOPS_OS_GITLAB_TYPE",
                                       help="Pipeline type: build | test | deploy | complete"),
    languages: str = typer.Option("python", envvar="DEVOPS_OS_GITLAB_LANGUAGES",
                                   help="Comma-separated languages: python, java, javascript, go"),
    kubernetes: bool = typer.Option(False, envvar="DEVOPS_OS_GITLAB_KUBERNETES",
                                    help="Include Kubernetes deployment stage"),
    k8s_method: str = typer.Option("kubectl", "--k8s-method", envvar="DEVOPS_OS_GITLAB_K8S_METHOD",
                                    help="K8s deploy method: kubectl | kustomize | argocd | flux"),
    output: str = typer.Option(".gitlab-ci.yml", envvar="DEVOPS_OS_GITLAB_OUTPUT",
                                help="Output file path"),
    image: str = typer.Option("docker:24", envvar="DEVOPS_OS_GITLAB_IMAGE",
                               help="Default Docker image for pipeline jobs"),
    branches: str = typer.Option("main", envvar="DEVOPS_OS_GITLAB_BRANCHES",
                                  help="Comma-separated protected branches (used for deploy rules)"),
    kube_namespace: str = typer.Option("", "--kube-namespace", envvar="DEVOPS_OS_GITLAB_KUBE_NAMESPACE",
                                        help="Kubernetes namespace to deploy to"),
    custom_values: Optional[str] = typer.Option(None, "--custom-values",
                                                  help="Path to custom values JSON file"),
):
    """Generate a GitLab CI pipeline (.gitlab-ci.yml).

    \b
    Examples:
      devopsos scaffold gitlab --name flask-api --languages python --type complete
      devopsos scaffold gitlab --name java-api --languages java --type test
      devopsos scaffold gitlab --name my-app --languages python,go --kubernetes --k8s-method argocd
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--type", pipeline_type,
        "--languages", languages,
        "--k8s-method", k8s_method,
        "--output", output,
        "--image", image,
        "--branches", branches,
    ]
    if kubernetes:
        flags.append("--kubernetes")
    if kube_namespace:
        flags += ["--kube-namespace", kube_namespace]
    if custom_values:
        flags += ["--custom-values", custom_values]
    _run_scaffold(scaffold_gitlab.main, flags)


# ── scaffold argocd ─────────────────────────────────────────────────────────

@scaffold_app.command("argocd")
def scaffold_argocd_cmd(
    ctx: typer.Context,
    name: str = typer.Option("my-app", envvar="DEVOPS_OS_ARGOCD_NAME",
                              help="Application name"),
    method: str = typer.Option("argocd", envvar="DEVOPS_OS_ARGOCD_METHOD",
                                help="GitOps tool: argocd | flux"),
    repo: str = typer.Option("https://github.com/myorg/my-app.git", envvar="DEVOPS_OS_ARGOCD_REPO",
                              help="Git repository URL for the application manifests"),
    revision: str = typer.Option("HEAD", envvar="DEVOPS_OS_ARGOCD_REVISION",
                                  help="Git revision / branch / tag to sync"),
    path: str = typer.Option("k8s", envvar="DEVOPS_OS_ARGOCD_PATH",
                              help="Path inside the repository to the manifests"),
    namespace: str = typer.Option("default", envvar="DEVOPS_OS_ARGOCD_NAMESPACE",
                                   help="Kubernetes namespace to deploy into"),
    project: str = typer.Option("default", envvar="DEVOPS_OS_ARGOCD_PROJECT",
                                 help="ArgoCD project name"),
    server: str = typer.Option("https://kubernetes.default.svc", envvar="DEVOPS_OS_ARGOCD_SERVER",
                                help="Destination Kubernetes API server"),
    auto_sync: bool = typer.Option(False, "--auto-sync", envvar="DEVOPS_OS_ARGOCD_AUTO_SYNC",
                                    help="Enable ArgoCD auto-sync policy"),
    rollouts: bool = typer.Option(False, envvar="DEVOPS_OS_ARGOCD_ROLLOUTS",
                                   help="Generate an Argo Rollouts canary strategy"),
    image: str = typer.Option("ghcr.io/myorg/my-app", envvar="DEVOPS_OS_ARGOCD_IMAGE",
                               help="Container image (used in Rollouts / Flux image automation)"),
    output_dir: str = typer.Option(".", "--output-dir", envvar="DEVOPS_OS_ARGOCD_OUTPUT_DIR",
                                    help="Root output directory"),
    allow_any_source_repo: bool = typer.Option(False, "--allow-any-source-repo",
                                                envvar="DEVOPS_OS_ARGOCD_ALLOW_ANY_SOURCE_REPO",
                                                help="Add '*' to AppProject sourceRepos (grants access to any repo)"),
):
    """Generate ArgoCD Application / AppProject manifests or Flux CD configs.

    \b
    Examples:
      devopsos scaffold argocd --name my-app --repo https://github.com/org/repo.git
      devopsos scaffold argocd --name my-app --auto-sync --rollouts
      devopsos scaffold argocd --name my-app --method flux --image ghcr.io/org/app:latest
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--method", method,
        "--repo", repo,
        "--revision", revision,
        "--path", path,
        "--namespace", namespace,
        "--project", project,
        "--server", server,
        "--image", image,
        "--output-dir", output_dir,
    ]
    if auto_sync:
        flags.append("--auto-sync")
    if rollouts:
        flags.append("--rollouts")
    if allow_any_source_repo:
        flags.append("--allow-any-source-repo")
    _run_scaffold(scaffold_argocd.main, flags)


# ── scaffold sre ────────────────────────────────────────────────────────────

@scaffold_app.command("sre")
def scaffold_sre_cmd(
    ctx: typer.Context,
    name: str = typer.Option("my-app", envvar="DEVOPS_OS_SRE_NAME",
                              help="Application / service name"),
    team: str = typer.Option("platform", envvar="DEVOPS_OS_SRE_TEAM",
                              help="Owning team (used in labels and routing)"),
    namespace: str = typer.Option("default", envvar="DEVOPS_OS_SRE_NAMESPACE",
                                   help="Kubernetes namespace where the app runs"),
    slo_type: str = typer.Option("all", "--slo-type", envvar="DEVOPS_OS_SRE_SLO_TYPE",
                                  help="SLO type: availability | latency | error_rate | all"),
    slo_target: float = typer.Option(99.9, "--slo-target", envvar="DEVOPS_OS_SRE_SLO_TARGET",
                                     help="SLO target percentage (e.g. 99.9)"),
    latency_threshold: float = typer.Option(0.5, "--latency-threshold",
                                             envvar="DEVOPS_OS_SRE_LATENCY_THRESHOLD",
                                             help="Latency SLI threshold in seconds (default 0.5)"),
    pagerduty_key: str = typer.Option("", "--pagerduty-key", envvar="DEVOPS_OS_SRE_PAGERDUTY_KEY",
                                       help="PagerDuty integration key (leave empty to skip)"),
    slack_channel: str = typer.Option("#alerts", "--slack-channel", envvar="DEVOPS_OS_SRE_SLACK_CHANNEL",
                                       help="Slack channel for alert routing"),
    output_dir: str = typer.Option("sre", "--output-dir", envvar="DEVOPS_OS_SRE_OUTPUT_DIR",
                                    help="Output directory for generated SRE configs"),
):
    """Generate SRE configs: Prometheus alert rules, Grafana dashboard, SLO manifest, Alertmanager config.

    \b
    Output files (default: sre/ directory):
      sre/alert-rules.yaml         Prometheus PrometheusRule CR
      sre/grafana-dashboard.json   Grafana dashboard JSON
      sre/slo.yaml                 OpenSLO / Sloth SLO manifest
      sre/alertmanager-config.yaml Alertmanager receiver config stub

    \b
    Examples:
      devopsos scaffold sre --name my-app --team platform
      devopsos scaffold sre --name my-app --slo-type availability --slo-target 99.9
      devopsos scaffold sre --name my-api --slo-type latency --latency-threshold 0.2
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--team", team,
        "--namespace", namespace,
        "--slo-type", slo_type,
        "--slo-target", str(slo_target),
        "--latency-threshold", str(latency_threshold),
        "--slack-channel", slack_channel,
        "--output-dir", output_dir,
    ]
    if pagerduty_key:
        flags += ["--pagerduty-key", pagerduty_key]
    _run_scaffold(scaffold_sre.main, flags)


# ── scaffold devcontainer ───────────────────────────────────────────────────

@scaffold_app.command("devcontainer")
def scaffold_devcontainer_cmd(
    ctx: typer.Context,
    languages: str = typer.Option("python", envvar="DEVOPS_OS_DEVCONTAINER_LANGUAGES",
                                   help="Comma-separated languages to enable (default: python)"),
    cicd_tools: str = typer.Option("docker,github_actions", "--cicd-tools",
                                    envvar="DEVOPS_OS_DEVCONTAINER_CICD_TOOLS",
                                    help="Comma-separated CI/CD tools (default: docker,github_actions)"),
    kubernetes_tools: str = typer.Option("", "--kubernetes-tools",
                                          envvar="DEVOPS_OS_DEVCONTAINER_KUBERNETES_TOOLS",
                                          help="Comma-separated Kubernetes tools (default: none)"),
    build_tools: str = typer.Option("", "--build-tools", envvar="DEVOPS_OS_DEVCONTAINER_BUILD_TOOLS",
                                     help="Comma-separated build tools (default: none)"),
    code_analysis: str = typer.Option("", "--code-analysis",
                                       envvar="DEVOPS_OS_DEVCONTAINER_CODE_ANALYSIS",
                                       help="Comma-separated code analysis tools (default: none)"),
    devops_tools: str = typer.Option("", "--devops-tools", envvar="DEVOPS_OS_DEVCONTAINER_DEVOPS_TOOLS",
                                      help="Comma-separated DevOps tools (default: none)"),
    python_version: str = typer.Option("3.12", "--python-version",
                                        envvar="DEVOPS_OS_DEVCONTAINER_PYTHON_VERSION",
                                        help="Python version (default: 3.12)"),
    java_version: str = typer.Option("21", "--java-version",
                                      envvar="DEVOPS_OS_DEVCONTAINER_JAVA_VERSION",
                                      help="Java JDK version (default: 21)"),
    node_version: str = typer.Option("22", "--node-version",
                                      envvar="DEVOPS_OS_DEVCONTAINER_NODE_VERSION",
                                      help="Node.js version (default: 22)"),
    go_version: str = typer.Option("1.25.0", "--go-version", envvar="DEVOPS_OS_DEVCONTAINER_GO_VERSION",
                                    help="Go version (default: 1.25.0)"),
    k9s_version: str = typer.Option("0.50.16", "--k9s-version",
                                     envvar="DEVOPS_OS_DEVCONTAINER_K9S_VERSION",
                                     help="K9s version (default: 0.50.16)"),
    argocd_version: str = typer.Option("3.3.6", "--argocd-version",
                                        envvar="DEVOPS_OS_DEVCONTAINER_ARGOCD_VERSION",
                                        help="ArgoCD version (default: 3.3.6)"),
    flux_version: str = typer.Option("2.8.5", "--flux-version",
                                      envvar="DEVOPS_OS_DEVCONTAINER_FLUX_VERSION",
                                      help="Flux version (default: 2.8.5)"),
    kustomize_version: str = typer.Option("5.8.0", "--kustomize-version",
                                           envvar="DEVOPS_OS_DEVCONTAINER_KUSTOMIZE_VERSION",
                                           help="Kustomize version (default: 5.8.0)"),
    nexus_version: str = typer.Option("3.91.0", "--nexus-version",
                                       envvar="DEVOPS_OS_DEVCONTAINER_NEXUS_VERSION",
                                       help="Nexus version (default: 3.91.0)"),
    prometheus_version: str = typer.Option("3.5.1", "--prometheus-version",
                                            envvar="DEVOPS_OS_DEVCONTAINER_PROMETHEUS_VERSION",
                                            help="Prometheus version (default: 3.5.1)"),
    grafana_version: str = typer.Option("12.4.2", "--grafana-version",
                                         envvar="DEVOPS_OS_DEVCONTAINER_GRAFANA_VERSION",
                                         help="Grafana version (default: 12.4.2)"),
    output_dir: str = typer.Option(".", "--output-dir", envvar="DEVOPS_OS_DEVCONTAINER_OUTPUT_DIR",
                                    help="Root output directory (files written to <output-dir>/.devcontainer/)"),
):
    """Generate a VS Code Dev Container configuration (.devcontainer/).

    \b
    Output files (relative to --output-dir):
      .devcontainer/devcontainer.json      VS Code dev container configuration
      .devcontainer/devcontainer.env.json  Tool / language selection & versions

    \b
    Examples:
      devopsos scaffold devcontainer --languages python,java --cicd-tools docker,github_actions
      devopsos scaffold devcontainer --kubernetes-tools kubectl,helm,argocd_cli
      devopsos scaffold devcontainer --languages go --go-version 1.25.0 --output-dir myproject
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--languages", languages,
        "--cicd-tools", cicd_tools,
        "--kubernetes-tools", kubernetes_tools,
        "--build-tools", build_tools,
        "--code-analysis", code_analysis,
        "--devops-tools", devops_tools,
        "--python-version", python_version,
        "--java-version", java_version,
        "--node-version", node_version,
        "--go-version", go_version,
        "--k9s-version", k9s_version,
        "--argocd-version", argocd_version,
        "--flux-version", flux_version,
        "--kustomize-version", kustomize_version,
        "--nexus-version", nexus_version,
        "--prometheus-version", prometheus_version,
        "--grafana-version", grafana_version,
        "--output-dir", output_dir,
    ]
    _run_scaffold(scaffold_devcontainer.main, flags)


# ── scaffold cicd ───────────────────────────────────────────────────────────

@scaffold_app.command("cicd")
def scaffold_cicd_cmd(
    ctx: typer.Context,
    name: str = typer.Option("DevOps-OS", help="CI/CD pipeline name"),
    cicd_type: str = typer.Option("complete", "--type",
                                   help="Pipeline type: build | test | deploy | complete"),
    languages: str = typer.Option("python,javascript",
                                   help="Comma-separated languages"),
    kubernetes: bool = typer.Option(False, help="Include Kubernetes deployment steps"),
    k8s_method: str = typer.Option("kubectl", "--k8s-method",
                                    help="K8s deploy method: kubectl | kustomize | argocd | flux"),
    output_dir: str = typer.Option(".", "--output-dir", help="Output directory"),
    registry: str = typer.Option("docker.io", help="Container registry URL"),
    image: str = typer.Option("docker.io/yourorg/devops-os:latest", help="DevOps-OS container image"),
    custom_values: Optional[str] = typer.Option(None, "--custom-values",
                                                  help="Path to custom values JSON file"),
    matrix: bool = typer.Option(False, help="Enable matrix builds for GitHub Actions"),
    parameters: bool = typer.Option(False, help="Enable parameterized builds for Jenkins"),
    github: bool = typer.Option(False, help="Generate GitHub Actions workflow only"),
    jenkins: bool = typer.Option(False, help="Generate Jenkins pipeline only"),
    all_targets: bool = typer.Option(False, "--all",
                                      help="Generate both GitHub Actions and Jenkins (default if neither --github nor --jenkins)"),
):
    """Generate both GitHub Actions and Jenkins pipelines in one step.

    \b
    When neither --github nor --jenkins is given, both are generated (equivalent to --all).

    \b
    Examples:
      devopsos scaffold cicd --name my-app --type complete --languages python
      devopsos scaffold cicd --name my-app --github
      devopsos scaffold cicd --name my-app --jenkins --type build
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--type", cicd_type,
        "--languages", languages,
        "--k8s-method", k8s_method,
        "--output-dir", output_dir,
        "--registry", registry,
        "--image", image,
    ]
    if kubernetes:
        flags.append("--kubernetes")
    if matrix:
        flags.append("--matrix")
    if parameters:
        flags.append("--parameters")
    if github:
        flags.append("--github")
    if jenkins:
        flags.append("--jenkins")
    if all_targets:
        flags.append("--all")
    if custom_values:
        flags += ["--custom-values", custom_values]
    _run_scaffold(scaffold_cicd.main, flags)


# ── scaffold unittest ────────────────────────────────────────────────────────

@scaffold_app.command("unittest")
def scaffold_unittest_cmd(
    ctx: typer.Context,
    name: str = typer.Option("my-app", envvar="DEVOPS_OS_UNITTEST_NAME",
                              help="Project / application name"),
    languages: str = typer.Option("python", envvar="DEVOPS_OS_UNITTEST_LANGUAGES",
                                   help=(
                                       "Comma-separated languages to generate tests for: "
                                       "python, javascript, typescript, go"
                                   )),
    framework: str = typer.Option("", envvar="DEVOPS_OS_UNITTEST_FRAMEWORK",
                                   help=(
                                       "Testing framework override (auto-selected by default). "
                                       "JS/TS: jest | mocha | vitest. Python: pytest. Go: go-test."
                                   )),
    coverage: bool = typer.Option(True, envvar="DEVOPS_OS_UNITTEST_COVERAGE",
                                   help="Include coverage configuration (default: true)"),
    output_dir: str = typer.Option("unittest", "--output-dir",
                                    envvar="DEVOPS_OS_UNITTEST_OUTPUT_DIR",
                                    help="Root output directory for generated files"),
):
    """Generate unit testing configuration and sample test files.

    \b
    Supported languages and their default frameworks:
      python       → pytest + pytest-cov
      javascript   → Jest (override with --framework mocha | vitest)
      typescript   → Jest (override with --framework mocha | vitest)
      go           → go test

    \b
    Output files (default: unittest/ directory):
      unittest/pytest.ini              Python pytest configuration
      unittest/conftest.py             Python shared fixtures
      unittest/tests/__init__.py       Python test-package marker
      unittest/tests/test_sample.py    Python sample unit tests
      unittest/jest.config.js          JavaScript/TypeScript Jest config
      unittest/vitest.config.js        JavaScript/TypeScript Vitest config
      unittest/.mocharc.js             JavaScript/TypeScript Mocha config
      unittest/tests/sample.test.js    JavaScript/TypeScript sample tests
      unittest/<name>_test.go          Go sample unit test file
      unittest/Makefile.test           Go Makefile test targets

    \b
    Examples:
      devopsos scaffold unittest --name my-app --languages python
      devopsos scaffold unittest --name my-app --languages javascript --framework jest
      devopsos scaffold unittest --name my-app --languages typescript --framework vitest
      devopsos scaffold unittest --name my-api --languages go
      devopsos scaffold unittest --name my-app --languages python,javascript,go
    """
    _show_help_if_no_opts(ctx)
    flags = [
        "--name", name,
        "--languages", languages,
        "--output-dir", output_dir,
    ]
    if framework:
        flags += ["--framework", framework]
    if not coverage:
        # coverage defaults to True; only pass flag when False
        flags.append("--no-coverage")
    _run_scaffold(scaffold_unittest.main, flags)


@app.command()
def init(
    directory: str = typer.Option(".", "--dir", help="Target directory in which the .devcontainer folder will be created (defaults to the current directory)"),
):
    """Interactive project initializer."""
    typer.echo("Welcome to DevOps-OS Init Wizard!")
    typer.echo("Tools are grouped by Process-First DevOps principles (Systems Thinking).\n")

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
        if vkey in DEFAULT_VERSIONS:
            selected_versions[vkey] = inquirer.text(
                message=f"{tool.title()} version:",
                default=DEFAULT_VERSIONS[vkey],
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

    target_root = Path(directory)
    devcontainer_dir = target_root / ".devcontainer"
    if devcontainer_dir.exists():
        typer.echo(
            f"Existing {devcontainer_dir} detected. Preserving it and skipping devcontainer generation."
        )
        typer.echo("Remove or rename the existing .devcontainer/ directory if you want init to generate a new one.")
        raise typer.Exit(0)

    written = write_generated_devcontainer(devcontainer_dir, config)
    typer.echo(f"Wrote configuration to {written['env']}")
    typer.echo(f"Wrote Dockerfile to {written['dockerfile']}")
    typer.echo(f"Wrote devcontainer.json to {written['json']}")


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
