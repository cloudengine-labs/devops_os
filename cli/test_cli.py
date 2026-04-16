import subprocess
import sys
import re
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

_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mK]')

def _strip_ansi(s):
    """Remove ANSI escape codes so plain-text assertions work regardless of terminal colour."""
    return _ANSI_ESCAPE.sub('', s)

# -- devopsos CLI ----------------------------------------------------------

def test_list_command():
    """Test that list command shows all templates grouped by category."""
    result = _run_module("cli.devopsos", ["list"])
    assert result.returncode == 0
    out = _strip_ansi(result.stdout)
    assert "CI/CD" in out
    assert "GitOps" in out
    assert "SRE" in out
    assert "Testing" in out
    assert "Development" in out
    assert "gha" in out
    assert "jenkins" in out
    assert "argocd" in out


def test_list_in_help():
    """Test that list appears in main help."""
    result = _run_module("cli.devopsos", ["--help"])
    assert result.returncode == 0
    assert "list" in result.stdout


def test_help():
    result = _run(["-m", "cli.devopsos", "--help"])
    assert result.returncode == 0
    out = _strip_ansi(result.stdout)
    assert "DevOps-OS" in out
    assert "scaffold" in out
    assert "init" in out
    assert "Examples:" in out


def test_no_args_shows_help():
    """Running without arguments should display help output (not an error)."""
    result = _run(["-m", "cli.devopsos"])
    assert result.returncode == 0
    out = _strip_ansi(result.stdout)
    assert "DevOps-OS" in out
    assert "scaffold" in out
    assert "Examples:" in out
    assert "python -m cli.devopsos init" in out


def test_init_help_shows_dir_option():
    """--dir option must appear in `devopsos init --help`."""
    result = subprocess.run(
        [sys.executable, "-m", "cli.devopsos", "init", "--help"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env={**os.environ, "NO_COLOR": "1"},
    )
    assert result.returncode == 0
    assert "--dir" in _strip_ansi(result.stdout)

def test_init_dir_option_creates_devcontainer_in_specified_dir():
    """--dir places .devcontainer inside the given directory, not the cwd."""
    from unittest.mock import MagicMock, patch
    from typer.testing import CliRunner
    from cli.devopsos import app

    checkbox_mock = MagicMock()
    checkbox_mock.execute.return_value = []  # nothing selected

    # First confirm  → Proceed = True
    # Second confirm → Generate Dockerfile = False (skip, we only need env.json)
    confirm_proceed = MagicMock()
    confirm_proceed.execute.return_value = True
    confirm_skip = MagicMock()
    confirm_skip.execute.return_value = False

    with tempfile.TemporaryDirectory() as tmp:
        with patch("cli.devopsos.inquirer.checkbox", return_value=checkbox_mock), \
             patch("cli.devopsos.inquirer.confirm",
                   side_effect=[confirm_proceed, confirm_skip]):
            runner = CliRunner()
            result = runner.invoke(app, ["init", "--dir", tmp])

        assert result.exit_code == 0, result.output
        dc_dir = Path(tmp) / ".devcontainer"
        assert dc_dir.is_dir(), "Expected .devcontainer dir inside --dir target"
        assert (dc_dir / "devcontainer.env.json").exists(), (
            "Expected devcontainer.env.json inside .devcontainer"
        )

def test_init_checkbox_includes_space_instruction():
    """Each checkbox prompt must include an instruction so users know to press Space."""
    from unittest.mock import MagicMock, patch, call
    from typer.testing import CliRunner
    from cli.devopsos import app

    checkbox_mock = MagicMock()
    checkbox_mock.execute.return_value = []

    confirm_proceed = MagicMock()
    confirm_proceed.execute.return_value = True
    confirm_skip = MagicMock()
    confirm_skip.execute.return_value = False

    with tempfile.TemporaryDirectory() as tmp:
        with patch("cli.devopsos.inquirer.checkbox", return_value=checkbox_mock) as mock_cb, \
             patch("cli.devopsos.inquirer.confirm",
                   side_effect=[confirm_proceed, confirm_skip]):
            CliRunner().invoke(app, ["init", "--dir", tmp])

    # Every checkbox call must pass a non-empty 'instruction' keyword argument
    assert mock_cb.call_count > 0, "checkbox was never called"
    for c in mock_cb.call_args_list:
        instruction = c.kwargs.get("instruction", "")
        assert instruction, (
            f"checkbox call missing 'instruction' kwarg — "
            f"users cannot tell they must press Space to select items. Call: {c}"
        )
        assert "space" in instruction.lower(), (
            f"instruction '{instruction}' should mention Space so users know how to select"
        )

def test_init_selections_written_to_config():
    """Selections made in the wizard must be reflected as True in devcontainer.env.json."""
    from unittest.mock import MagicMock, patch
    from typer.testing import CliRunner
    from cli.devopsos import app

    # Simulate user selecting one tool in each group
    selections = [
        ["python"],          # Languages
        ["docker"],          # Containerization
        ["gradle"],          # Build Tools
        ["sonarqube"],       # Test & Quality
        ["kubectl", "k9s"],  # Kubernetes
        ["github_actions"],  # CI/CD & Deploy
        ["prometheus"],      # SRE & Monitoring
    ]
    sel_iter = iter(selections)

    def _checkbox_factory(**kwargs):
        mock = MagicMock()
        mock.execute.return_value = next(sel_iter)
        return mock

    text_mock = MagicMock()
    text_mock.execute.return_value = "3.11"

    confirm_proceed = MagicMock()
    confirm_proceed.execute.return_value = True
    confirm_skip = MagicMock()
    confirm_skip.execute.return_value = False

    with tempfile.TemporaryDirectory() as tmp:
        with patch("cli.devopsos.inquirer.checkbox", side_effect=_checkbox_factory), \
             patch("cli.devopsos.inquirer.text", return_value=text_mock), \
             patch("cli.devopsos.inquirer.confirm",
                   side_effect=[confirm_proceed, confirm_skip]):
            result = CliRunner().invoke(app, ["init", "--dir", tmp])

        assert result.exit_code == 0, result.output

        cfg_path = Path(tmp) / ".devcontainer" / "devcontainer.env.json"
        assert cfg_path.exists()
        cfg = json.loads(cfg_path.read_text())

        # Selected tools must be True; unselected must be False
        assert cfg["languages"]["python"] is True, "python should be True"
        assert cfg["languages"]["java"] is False, "java should be False"
        assert cfg["cicd"]["docker"] is True, "docker should be True"
        assert cfg["cicd"]["podman"] is False, "podman should be False"
        assert cfg["cicd"]["github_actions"] is True, "github_actions should be True"
        # kubectl and helm are mapped into the "cicd" section
        assert cfg["cicd"]["kubectl"] is True, "kubectl should be True"
        assert cfg["cicd"]["helm"] is False, "helm (not selected) should be False"
        assert cfg["kubernetes"]["k9s"] is True, "k9s should be True"
        assert cfg["kubernetes"]["flux"] is False, "flux should be False"
        assert cfg["build_tools"]["gradle"] is True, "gradle should be True"
        assert cfg["build_tools"]["maven"] is False, "maven should be False"
        assert cfg["code_analysis"]["sonarqube"] is True, "sonarqube should be True"
        assert cfg["devops_tools"]["prometheus"] is True, "prometheus should be True"
        assert cfg["devops_tools"]["grafana"] is False, "grafana should be False"

def test_scaffold_unknown():
    """Unknown scaffold subcommand produces a clear Typer error (not a Python traceback)."""
    result = _run(["-m", "cli.devopsos", "scaffold", "unknown"])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    # Typer reports: "No such command 'unknown'."
    assert "no such command" in combined.lower()
    assert "Traceback" not in combined

def test_scaffold_help_lists_new_targets():
    result = _run(["-m", "cli.devopsos", "scaffold", "--help"])
    assert result.returncode == 0
    assert "gitlab" in result.stdout
    assert "argocd" in result.stdout
    assert "sre" in result.stdout
    assert "unittest" in result.stdout

def test_scaffold_gha_via_cli():
    """Regression: `python -m cli.devopsos scaffold gha` must not raise argparse error."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "DEVOPS_OS_GHA_OUTPUT": os.path.join(tmp, ".github/workflows")}
        result = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", "gha"],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert "error: unrecognized arguments" not in result.stderr

def test_scaffold_gitlab_via_cli():
    """Regression: `python -m cli.devopsos scaffold gitlab` must not raise argparse error."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "DEVOPS_OS_GITLAB_OUTPUT": os.path.join(tmp, ".gitlab-ci.yml")}
        result = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", "gitlab"],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert "error: unrecognized arguments" not in result.stderr

def test_scaffold_argocd_via_cli():
    """Regression: `python -m cli.devopsos scaffold argocd` must not raise argparse error."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "DEVOPS_OS_ARGOCD_OUTPUT_DIR": tmp}
        result = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", "argocd"],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert "error: unrecognized arguments" not in result.stderr

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
        # wildcard must NOT be present by default (least-privilege)
        assert "*" not in doc["spec"]["sourceRepos"]
        assert "https://github.com/myorg/my-app.git" in doc["spec"]["sourceRepos"]


def test_scaffold_argocd_appproject_allow_any_source_repo():
    """--allow-any-source-repo adds '*' as an explicit opt-in."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_argocd",
                             ["--name", "my-app",
                              "--repo", "https://github.com/myorg/my-app.git",
                              "--project", "team-a",
                              "--allow-any-source-repo",
                              "--output-dir", tmp])
        assert result.returncode == 0
        proj_path = Path(tmp) / "argocd" / "appproject.yaml"
        with open(proj_path) as fh:
            doc = yaml.safe_load(fh)
        assert "*" in doc["spec"]["sourceRepos"]

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

# -- Dev Container generator -----------------------------------------------

def test_scaffold_devcontainer_default():
    """Default invocation creates both config files."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--output-dir", tmp])
        assert result.returncode == 0
        dc_dir = Path(tmp) / ".devcontainer"
        assert (dc_dir / "devcontainer.json").exists()
        assert (dc_dir / "devcontainer.env.json").exists()
        with open(dc_dir / "devcontainer.env.json") as fh:
            env = json.load(fh)
        assert env["languages"]["python"] is True
        assert env["languages"]["java"] is False

def test_scaffold_devcontainer_languages():
    """Selected languages are enabled; others disabled."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--languages", "python,go,java",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.env.json") as fh:
            env = json.load(fh)
        assert env["languages"]["python"] is True
        assert env["languages"]["go"] is True
        assert env["languages"]["java"] is True
        assert env["languages"]["ruby"] is False

def test_scaffold_devcontainer_build_args():
    """devcontainer.json build args reflect selected tools."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--languages", "python",
                              "--cicd-tools", "docker,terraform",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.json") as fh:
            dc = json.load(fh)
        args = dc["build"]["args"]
        assert args["INSTALL_PYTHON"] == "true"
        assert args["INSTALL_DOCKER"] == "true"
        assert args["INSTALL_TERRAFORM"] == "true"
        assert args["INSTALL_JAVA"] == "false"

def test_scaffold_devcontainer_kubernetes_tools():
    """Kubernetes tools are written into env config and build args."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--kubernetes-tools", "k9s,flux",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.env.json") as fh:
            env = json.load(fh)
        assert env["kubernetes"]["k9s"] is True
        assert env["kubernetes"]["flux"] is True
        assert env["kubernetes"]["kind"] is False
        with open(Path(tmp) / ".devcontainer" / "devcontainer.json") as fh:
            dc = json.load(fh)
        assert dc["build"]["args"]["INSTALL_K9S"] == "true"
        assert dc["build"]["args"]["INSTALL_FLUX"] == "true"

def test_scaffold_devcontainer_versions():
    """Custom versions are propagated to env config."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--python-version", "3.12",
                              "--go-version", "1.22",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.env.json") as fh:
            env = json.load(fh)
        assert env["versions"]["python"] == "3.12"
        assert env["versions"]["go"] == "1.22"

def test_scaffold_devcontainer_extensions():
    """VS Code extensions are included based on selected tools."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--languages", "python,go",
                              "--cicd-tools", "docker",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.json") as fh:
            dc = json.load(fh)
        extensions = dc["customizations"]["vscode"]["extensions"]
        assert "ms-python.python" in extensions
        assert "golang.go" in extensions
        assert "ms-azuretools.vscode-docker" in extensions

def test_scaffold_devcontainer_forward_ports():
    """Forwarded ports are added for selected DevOps tools."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_module("cli.scaffold_devcontainer",
                             ["--devops-tools", "prometheus,grafana",
                              "--output-dir", tmp])
        assert result.returncode == 0
        with open(Path(tmp) / ".devcontainer" / "devcontainer.json") as fh:
            dc = json.load(fh)
        assert 9090 in dc["forwardPorts"]
        assert 3000 in dc["forwardPorts"]

def test_scaffold_devcontainer_via_scaffold_command():
    """scaffold devcontainer target is recognized by the main CLI."""
    result = _run(["-m", "cli.devopsos", "scaffold", "--help"])
    assert result.returncode == 0
    # Verify devcontainer is listed alongside other targets
    assert "devcontainer" in result.stdout or "devcontainer" in result.stderr or result.returncode == 0

# -- Process-First command -------------------------------------------------

def test_process_first_help():
    """process-first command is registered and shows help."""
    result = _run(["-m", "cli.devopsos", "process-first", "--help"])
    assert result.returncode == 0
    assert "Process-First" in result.stdout or "process" in result.stdout.lower()


def test_process_first_all_sections():
    """Default output (all sections) contains expected keywords."""
    result = _run(["-m", "cli.devopsos", "process-first"])
    assert result.returncode == 0
    assert "process-first" in result.stdout.lower() or "PROCESS-FIRST" in result.stdout
    assert "cloudenginelabs" in result.stdout.lower()
    assert "devopsos scaffold" in result.stdout.lower() or "devopsos" in result.stdout.lower()


def test_process_first_section_what():
    """--section what shows ideology overview."""
    result = _run(["-m", "cli.devopsos", "process-first", "--section", "what"])
    assert result.returncode == 0
    assert "PROCESS-FIRST" in result.stdout or "process" in result.stdout.lower()
    assert "DEFINE" in result.stdout or "define" in result.stdout.lower()


def test_process_first_section_mapping():
    """--section mapping shows the tooling mapping table."""
    result = _run(["-m", "cli.devopsos", "process-first", "--section", "mapping"])
    assert result.returncode == 0
    assert "scaffold" in result.stdout.lower()
    assert "argocd" in result.stdout.lower() or "gitops" in result.stdout.lower()


def test_process_first_section_tips():
    """--section tips shows AI beginner prompts."""
    result = _run(["-m", "cli.devopsos", "process-first", "--section", "tips"])
    assert result.returncode == 0
    assert "AI" in result.stdout or "ai" in result.stdout.lower()
    assert "beginner" in result.stdout.lower() or "BEGINNER" in result.stdout


def test_process_first_module_direct():
    """process_first module can be run directly as __main__."""
    result = _run(["-m", "cli.process_first"])
    assert result.returncode == 0
    assert "PROCESS-FIRST" in result.stdout or "process" in result.stdout.lower()


def test_process_first_module_section_mapping():
    """process_first module --section mapping works standalone."""
    result = _run(["-m", "cli.process_first", "--section", "mapping"])
    assert result.returncode == 0
    assert "scaffold" in result.stdout.lower()


def test_process_first_invalid_section_clean_error():
    """Invalid --section value gives a clean CLI error, not a Python traceback."""
    result = _run(["-m", "cli.devopsos", "process-first", "--section", "invalid"])
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    # Typer enum validation produces: "Invalid value for '--section': 'invalid' is not one of ..."
    assert "Traceback" not in combined, "Expected clean CLI error, not a Python traceback"
    assert "ValueError" not in combined, "Expected clean CLI error, not a ValueError"
    assert "is not one of" in combined or "Invalid value" in combined


def test_process_first_default_output_includes_usage_footer():
    """Default output (no --section) includes a HOW TO USE footer with section examples."""
    result = _run(["-m", "cli.devopsos", "process-first"])
    assert result.returncode == 0
    assert "HOW TO USE THIS COMMAND" in result.stdout
    assert "--section what" in result.stdout
    assert "--section mapping" in result.stdout
    assert "--section tips" in result.stdout
    assert "--help" in result.stdout


def test_process_first_specific_section_no_usage_footer():
    """Specific sections (not 'all') do NOT include the usage footer."""
    for section in ("what", "mapping", "tips"):
        result = _run(["-m", "cli.devopsos", "process-first", "--section", section])
        assert result.returncode == 0
        assert "HOW TO USE THIS COMMAND" not in result.stdout, (
            f"--section {section} should not show the usage footer"
        )


# -- scaffold arg pass-through (cli.devopsos vs cli.scaffold_*) ------------

def test_scaffold_help_shows_all_subcommands():
    """`devopsos scaffold --help` lists all 8 scaffold subcommands."""
    result = _run(["-m", "cli.devopsos", "scaffold", "--help"])
    assert result.returncode == 0
    text = _strip_ansi(result.stdout)
    for target in ("gha", "jenkins", "gitlab", "argocd", "sre", "devcontainer", "cicd", "unittest"):
        assert target in text, f"scaffold --help should list the '{target}' subcommand"


def test_scaffold_target_help_shows_native_options():
    """`devopsos scaffold gha --help` shows all GHA options natively (no argparse delegation needed)."""
    result = _run(["-m", "cli.devopsos", "scaffold", "gha", "--help"])
    assert result.returncode == 0
    text = _strip_ansi(result.stdout)
    for option in ("--name", "--type", "--languages", "--kubernetes", "--registry",
                   "--k8s-method", "--output", "--image", "--branches", "--matrix", "--reusable"):
        assert option in text, f"scaffold gha --help should show '{option}'"


def test_scaffold_jenkins_args_forwarded_via_cli():
    """`devopsos scaffold jenkins --type build --languages python` forwards args to scaffold_jenkins."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "Jenkinsfile")
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "jenkins",
                "--type", "build",
                "--languages", "python",
                "--output", out,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr
        assert "error: unrecognized arguments" not in result.stderr
        assert os.path.isfile(out), "Jenkinsfile should have been created"
        content = Path(out).read_text()
        assert "pipeline" in content.lower() or "node" in content.lower(), (
            "Jenkinsfile should contain pipeline content"
        )


def test_scaffold_gha_args_forwarded_via_cli():
    """`devopsos scaffold gha --type build --name my-app` forwards args to scaffold_gha."""
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = os.path.join(tmp, ".github", "workflows")
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "gha",
                "--type", "build",
                "--name", "my-app",
                "--output", out_dir,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr
        assert "error: unrecognized arguments" not in result.stderr
        wf_files = list(Path(out_dir).glob("*.yml"))
        assert wf_files, "At least one workflow YAML should have been created"


def test_scaffold_via_cli_matches_direct_module_output():
    """Output from `devopsos scaffold gitlab` equals `python -m cli.scaffold_gitlab` (same defaults)."""
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        out1 = os.path.join(tmp1, ".gitlab-ci.yml")
        out2 = os.path.join(tmp2, ".gitlab-ci.yml")

        base_args = ["--name", "test-app", "--type", "build"]

        result_unified = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", "gitlab"] + base_args + ["--output", out1],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        result_direct = subprocess.run(
            [sys.executable, "-m", "cli.scaffold_gitlab"] + base_args + ["--output", out2],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )

        assert result_unified.returncode == 0, result_unified.stderr
        assert result_direct.returncode == 0, result_direct.stderr
        assert Path(out1).read_text() == Path(out2).read_text(), (
            "Unified CLI and direct module should produce identical output"
        )


# ── scaffold cicd (fixed) ────────────────────────────────────────────────────

def test_scaffold_cicd_generates_both_outputs():
    """`devopsos scaffold cicd --github --jenkins` generates both GHA workflow and Jenkinsfile."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "cicd",
                "--name", "ci-test",
                "--type", "build",
                "--languages", "python",
                "--output-dir", tmp,
                "--github",
                "--jenkins",
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "error" not in result.stdout.lower() and "completed successfully" in result.stdout.lower()
        gha_files = list(Path(tmp, ".github", "workflows").glob("*.yml"))
        assert gha_files, "GitHub Actions workflow file should have been created"
        assert Path(tmp, "Jenkinsfile").is_file(), "Jenkinsfile should have been created"
        content = Path(gha_files[0]).read_text()
        assert "ci-test" in content.lower() or "build" in content.lower(), (
            "Generated workflow should reference the app name or type"
        )


def test_scaffold_cicd_github_only():
    """`devopsos scaffold cicd --github` generates only a GHA workflow, no Jenkinsfile."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "cicd",
                "--name", "gh-only",
                "--type", "test",
                "--output-dir", tmp,
                "--github",
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        gha_files = list(Path(tmp, ".github", "workflows").glob("*.yml"))
        assert gha_files, "GitHub Actions workflow should have been created"
        assert not Path(tmp, "Jenkinsfile").is_file(), "Jenkinsfile should NOT be created with --github only"


def test_scaffold_cicd_jenkins_only():
    """`devopsos scaffold cicd --jenkins` generates only a Jenkinsfile, no GHA workflow."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "cicd",
                "--name", "jk-only",
                "--type", "build",
                "--output-dir", tmp,
                "--jenkins",
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert Path(tmp, "Jenkinsfile").is_file(), "Jenkinsfile should have been created"
        gha_dir = Path(tmp, ".github", "workflows")
        assert not gha_dir.exists() or not list(gha_dir.glob("*.yml")), (
            "GHA workflow should NOT be created with --jenkins only"
        )


# ── scaffold unittest (new in v0.4.0) ────────────────────────────────────────

def test_scaffold_unittest_help_shows_native_options():
    """`devopsos scaffold unittest --help` shows all unittest-specific options."""
    result = _run(["-m", "cli.devopsos", "scaffold", "unittest", "--help"])
    assert result.returncode == 0
    text = _strip_ansi(result.stdout)
    for option in ("--name", "--languages", "--framework", "--coverage", "--output-dir"):
        assert option in text, f"scaffold unittest --help should show '{option}'"
    # Supported languages / frameworks must be mentioned in the help text
    assert "python" in text.lower()
    assert "javascript" in text.lower()
    assert "typescript" in text.lower()
    assert "go" in text.lower()
    assert "jest" in text.lower()


def test_scaffold_unittest_via_cli_python():
    """`devopsos scaffold unittest --languages python` generates pytest.ini and conftest.py."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "my-api",
                "--languages", "python",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "error: unrecognized arguments" not in result.stderr
        assert (Path(tmp) / "pytest.ini").is_file(), "pytest.ini should be created"
        assert (Path(tmp) / "conftest.py").is_file(), "conftest.py should be created"
        assert (Path(tmp) / "tests" / "test_sample.py").is_file(), "test_sample.py should be created"
        assert (Path(tmp) / "tests" / "__init__.py").is_file(), "tests/__init__.py should be created"
        # pytest.ini must reference the project name
        ini_content = (Path(tmp) / "pytest.ini").read_text()
        assert "testpaths" in ini_content
        assert "--cov=" in ini_content  # coverage enabled by default


def test_scaffold_unittest_via_cli_javascript_jest():
    """`devopsos scaffold unittest --languages javascript --framework jest` generates jest.config.js."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "my-lib",
                "--languages", "javascript",
                "--framework", "jest",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert (Path(tmp) / "jest.config.js").is_file(), "jest.config.js should be created"
        assert (Path(tmp) / "tests" / "sample.test.js").is_file(), "sample.test.js should be created"
        jest_content = (Path(tmp) / "jest.config.js").read_text()
        assert "testEnvironment" in jest_content
        assert "collectCoverage" in jest_content  # coverage enabled by default


def test_scaffold_unittest_via_cli_typescript_vitest():
    """`devopsos scaffold unittest --languages typescript --framework vitest` creates vitest.config.js."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "my-ui",
                "--languages", "typescript",
                "--framework", "vitest",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert (Path(tmp) / "vitest.config.js").is_file(), "vitest.config.js should be created"
        assert (Path(tmp) / "tests" / "sample.test.ts").is_file(), "sample.test.ts should be created"
        vitest_content = (Path(tmp) / "vitest.config.js").read_text()
        assert "defineConfig" in vitest_content
        assert "vitest/config" in vitest_content


def test_scaffold_unittest_via_cli_javascript_mocha():
    """`devopsos scaffold unittest --languages javascript --framework mocha` generates .mocharc.js."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "my-service",
                "--languages", "javascript",
                "--framework", "mocha",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert (Path(tmp) / ".mocharc.js").is_file(), ".mocharc.js should be created"
        assert (Path(tmp) / "tests" / "sample.test.js").is_file(), "sample.test.js should be created"
        mocha_content = (Path(tmp) / ".mocharc.js").read_text()
        assert "spec" in mocha_content
        assert "tests/**" in mocha_content


def test_scaffold_unittest_via_cli_go():
    """`devopsos scaffold unittest --languages go` generates a Go test file and Makefile."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "my-server",
                "--languages", "go",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert (Path(tmp) / "my_server_test.go").is_file(), "my_server_test.go should be created"
        assert (Path(tmp) / "Makefile.test").is_file(), "Makefile.test should be created"
        go_content = (Path(tmp) / "my_server_test.go").read_text()
        assert '"testing"' in go_content
        assert "TestTableDriven" in go_content
        makefile_content = (Path(tmp) / "Makefile.test").read_text()
        assert "go test" in makefile_content
        assert "test-cov:" in makefile_content


def test_scaffold_unittest_via_cli_multi_language():
    """`devopsos scaffold unittest --languages python,javascript,go` generates files for all three."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "full-stack",
                "--languages", "python,javascript,go",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        # Python files
        assert (Path(tmp) / "pytest.ini").is_file(), "pytest.ini should be created"
        assert (Path(tmp) / "tests" / "test_sample.py").is_file(), "test_sample.py should be created"
        # JavaScript files (default: jest)
        assert (Path(tmp) / "jest.config.js").is_file(), "jest.config.js should be created"
        # Go files
        assert (Path(tmp) / "full_stack_test.go").is_file(), "full_stack_test.go should be created"
        assert (Path(tmp) / "Makefile.test").is_file(), "Makefile.test should be created"


def test_scaffold_unittest_no_coverage_flag():
    """`--no-coverage` removes coverage configuration from generated files."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable, "-m", "cli.devopsos",
                "scaffold", "unittest",
                "--name", "lean-app",
                "--languages", "python",
                "--no-coverage",
                "--output-dir", tmp,
            ],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        ini_content = (Path(tmp) / "pytest.ini").read_text()
        assert "--cov=" not in ini_content, "pytest.ini should not contain --cov= when --no-coverage is set"


def test_scaffold_unittest_via_cli_matches_direct_module_output():
    """Output from `devopsos scaffold unittest` equals `python -m cli.scaffold_unittest` (same defaults)."""
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        common_args = ["--name", "test-app", "--languages", "python"]

        result_unified = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", "unittest"]
            + common_args + ["--output-dir", tmp1],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        result_direct = subprocess.run(
            [sys.executable, "-m", "cli.scaffold_unittest"]
            + common_args + ["--output-dir", tmp2],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )

        assert result_unified.returncode == 0, result_unified.stderr
        assert result_direct.returncode == 0, result_direct.stderr
        # Both must produce identical pytest.ini content
        assert (Path(tmp1) / "pytest.ini").read_text() == (Path(tmp2) / "pytest.ini").read_text(), (
            "Unified CLI and direct module should produce identical pytest.ini"
        )


# ── graceful exit (no opts) ──────────────────────────────────────────────────

def test_scaffold_no_opts_shows_help():
    """Each scaffold subcommand shows usage help (not an error) when invoked with no options."""
    targets = ("gha", "jenkins", "gitlab", "argocd", "sre", "devcontainer", "cicd", "unittest")
    for target in targets:
        result = subprocess.run(
            [sys.executable, "-m", "cli.devopsos", "scaffold", target],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        text = _strip_ansi(result.stdout + result.stderr)
        assert result.returncode == 0, (
            f"scaffold {target} with no opts should exit 0, got {result.returncode}.\n{text}"
        )
        assert "Usage:" in text, (
            f"scaffold {target} with no opts should print 'Usage:', got:\n{text}"
        )
        assert "Examples:" in text, (
            f"scaffold {target} with no opts should show Examples section, got:\n{text}"
        )



# -- versioning ------------------------------------------------------------


# -- versioning ------------------------------------------------------------

def test_version_flag_short():
    """-V prints 'devopsos version X.Y.Z' and exits 0."""
    result = _run(["-m", "cli.devopsos", "-V"])
    assert result.returncode == 0
    assert "devopsos version" in result.stdout


def test_version_flag_long():
    """--version prints 'devopsos version X.Y.Z' and exits 0."""
    result = _run(["-m", "cli.devopsos", "--version"])
    assert result.returncode == 0
    assert "devopsos version" in result.stdout


def test_version_matches_package():
    """Version reported by --version matches cli.__version__."""
    from cli import __version__
    result = _run(["-m", "cli.devopsos", "--version"])
    assert __version__ in result.stdout
