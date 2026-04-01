# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.6] - 2026-04-01

### Changed
- Automated patch release — version bump to 0.4.6.

---

## [0.4.5] - 2026-03-21

### Changed
- Automated patch release — version bump to 0.4.5.

---

## [0.4.4] - 2026-03-21

### Changed
- Automated patch release — version bump to 0.4.4.

---

## [0.4.3] - 2026-03-21

### Changed
- Automated patch release — version bump to 0.4.3.

---

## [0.4.2] - 2026-03-18

### Fixed
- **`scaffold sre` empty `slos: []` when `--slo-type error_rate`** — `generate_slo_manifest()` in
  `cli/scaffold_sre.py` had no branch for the `error_rate` SLO type, leaving `slo.yaml` with an
  empty `slos: []` list. Sloth/OpenSLO tooling therefore received no SLO objectives. A dedicated
  `error_rate` SLO entry (with matching SLI queries and alerting config) is now generated when
  `--slo-type error_rate` is specified.

---

## [0.4.1] - 2026-03-17

### Changed
- Automated patch release — version bump to 0.4.1.

---

## [0.4.0] - 2026-03-15

### Added
- **`scaffold unittest` subcommand** — new `devopsos scaffold unittest` command that generates
  unit testing configuration files and sample test stubs for multiple tech stacks:
  - **Python** → `pytest.ini` (with pytest-cov options), `conftest.py` with shared fixtures,
    `tests/__init__.py`, and `tests/test_sample.py` with parametrized examples.
  - **JavaScript** → Jest (`jest.config.js`), Vitest (`vitest.config.js`), or Mocha (`.mocharc.js`)
    configuration plus a matching `tests/sample.test.js`.
  - **TypeScript** → same as JavaScript with TypeScript-specific Jest transform (`ts-jest`)
    and `tests/sample.test.ts`.
  - **Go** → table-driven `<name>_test.go` sample and `Makefile.test` with `test`, `test-race`,
    `test-cov`, and `lint` targets.
  - Coverage configuration is included by default and can be disabled with `--no-coverage`.
  - Supports comma-separated `--languages` to scaffold multiple stacks at once.
- **`generate_unittest_config` MCP tool** — exposes the new unit-test scaffold as an MCP tool
  so AI assistants can generate test configurations via conversation.
- **`cli/scaffold_unittest.py`** — the scaffold library backing the new command.
- **`docs/CLI-COMMANDS-REFERENCE.md`** — new section documenting all `unittest` options,
  output files, and examples.

---

## [0.3.0] - 2026-03-10

### Fixed
- **`scaffold gitlab` empty stages when `--type deploy` without `--kubernetes`** — `scaffold_gitlab.py`
  `_global_section()` previously excluded the `deploy` stage from the stages list whenever the
  `--kubernetes` flag was absent, producing an invalid pipeline. The condition is now corrected so
  that `--type deploy` always adds the `deploy` stage regardless of the Kubernetes flag.
- **Missing deploy job when `--type deploy` without `--kubernetes`** — `_deploy_job()` previously
  returned an empty dict when `kubernetes=False`, leaving the pipeline with a declared `deploy` stage
  but no corresponding job. A generic deploy stub (with branch-based rules) is now returned instead,
  giving users a ready-to-customise deployment step out of the box.

### Added
- **GitHub star count badge in README** — the project README now displays a live GitHub Stars badge
  alongside the existing license and version badges.

---

## [0.2.0] - 2026-03-08

### Fixed
- **`scaffold cicd` broken subprocess calls** — `scaffold_cicd.py` previously invoked
  `github-actions-generator-improved.py` and `jenkins-pipeline-generator-improved.py` via
  `subprocess.run`, which no longer exist. Both generators are now called directly via the
  `scaffold_gha` and `scaffold_jenkins` modules (same `_run_module_main` pattern used by all
  other scaffold subcommands).

### Added
- **Graceful help exit for all scaffold subcommands** — invoking any of the 7 scaffold
  subcommands (`gha`, `jenkins`, `gitlab`, `argocd`, `sre`, `devcontainer`, `cicd`) with no
  options now prints the command's full help text (including usage summary and examples) and
  exits cleanly with code 0, instead of silently running with defaults.
- **`--version` / `-V` flag** — `devopsos --version` (or `devopsos -V`) prints the current
  version string and exits. Version is sourced from the new `cli/__version__.py` single source
  of truth.
- **`cli/__version__.py`** — single source of truth for the package version (`0.2.0`).
- **`CHANGELOG.md`** — this file, tracking all notable changes.

---

## [0.1.0] - 2025-03-08

### Added

#### CLI (`cli/`)
- **`devopsos` unified CLI** – single entry-point (`python -m cli.devopsos`) built with [Typer](https://typer.tiangolo.com/).
- **`devopsos init`** – interactive wizard that scaffolds a `.devcontainer/devcontainer.json` tailored to the languages, CI/CD tools, and DevOps utilities you select.
- **`devopsos scaffold gha`** – generates a multi-stage GitHub Actions workflow (lint → build → test → deploy).
- **`devopsos scaffold jenkins`** – generates a `Jenkinsfile` with declarative pipeline stages.
- **`devopsos scaffold gitlab`** – generates a `.gitlab-ci.yml` with Docker, Kubernetes, and deploy stages.
- **`devopsos scaffold argocd`** – generates ArgoCD `Application` and `AppProject` manifests for GitOps deployments.
- **`devopsos scaffold sre`** – generates Prometheus alert rules, Grafana dashboard JSON, and SLO manifests.
- **`devopsos scaffold devcontainer`** – standalone devcontainer scaffolder with full tool-version control.
- **`devopsos scaffold cicd`** – meta-scaffolder that runs both GHA and Jenkins generation in one step.
- **`devopsos process-first`** – prints Process-First DevOps principles (Systems Thinking sections: what, mapping, tips, best-practices).
- **`--version` / `-V` flag** – prints the current `devopsos` version and exits.

#### MCP Server (`mcp_server/`)
- FastMCP-based server exposing every scaffold function as a native AI tool for Claude / ChatGPT plugins.
- Tools: `generate_github_actions`, `generate_jenkins_pipeline`, `generate_gitlab_ci`, `generate_argocd_config`, `generate_sre_config`, `generate_devcontainer`, `generate_cicd_pipeline`.

#### Documentation & Examples
- `README.md` – full project overview with quick-start, use-case table, and architecture diagram.
- `README-USECASE-EXAMPLES.md` – end-to-end worked examples for every scaffold command.
- `README-INDEX.md` – top-level navigation index for all documentation.
- `CONTRIBUTING.md` – contribution guide with coding conventions and PR checklist.
- `docs/` – extended Hugo-compatible documentation site sources.
- `feature-announcements/` – HTML/Markdown feature-announcement pages.
- `skills/` – reusable prompt-skill definitions for AI assistants.
- `go-project/` – example Go micro-service wired to the DevOps-OS scaffold outputs.
- `kubernetes/` – sample Kubernetes manifests referenced by the ArgoCD scaffold.
- `scripts/examples/` – shell-script quick-start examples.

#### Development Environment
- `.devcontainer/devcontainer.json` – ready-to-use GitHub Codespaces / VS Code dev-container with all Python, Docker, and Kubernetes tooling pre-installed.
- `.github/workflows/ci.yml` – full CI pipeline (lint, unit tests, integration tests).
- `.github/workflows/sanity.yml` – lightweight sanity-check workflow for PRs.
- `.github/workflows/pages.yml` – GitHub Pages deployment workflow for the Hugo docs site.

[0.3.0]: https://github.com/cloudengine-labs/devops_os/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/cloudengine-labs/devops_os/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cloudengine-labs/devops_os/releases/tag/v0.1.0
