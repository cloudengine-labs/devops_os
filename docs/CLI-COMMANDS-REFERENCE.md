# DevOps-OS CLI Commands Reference

This page is the single source of truth for every DevOps-OS CLI command.
For each command you will find the **complete option table**, the **input files** it reads, and the **exact output files / directories** it writes.

---

## Table of Contents

- [Installation](#installation)
- [Command Overview](#command-overview)
- [scaffold_gha — GitHub Actions Generator](#scaffold_gha--github-actions-generator)
- [scaffold_gitlab — GitLab CI Generator](#scaffold_gitlab--gitlab-ci-generator)
- [scaffold_jenkins — Jenkins Pipeline Generator](#scaffold_jenkins--jenkins-pipeline-generator)
- [scaffold_argocd — ArgoCD / Flux CD Generator](#scaffold_argocd--argocd--flux-cd-generator)
- [scaffold_sre — SRE Config Generator](#scaffold_sre--sre-config-generator)
- [scaffold_devcontainer — Dev Container Generator](#scaffold_devcontainer--dev-container-generator)
- [devopsos — Unified CLI](#devopsos--unified-cli)
- [process-first — Process-First Philosophy](#process-first--process-first-philosophy)
- [Environment Variable Reference](#environment-variable-reference)
- [Input File Formats](#input-file-formats)

---

## Installation

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r cli/requirements.txt
```

---

## Command Overview

| Command | Invocation | Output location |
|---------|-----------|-----------------|
| GitHub Actions | `python -m cli.scaffold_gha` | `.github/workflows/<name>-<type>.yml` |
| GitLab CI | `python -m cli.scaffold_gitlab` | `.gitlab-ci.yml` |
| Jenkins | `python -m cli.scaffold_jenkins` | `Jenkinsfile` |
| ArgoCD | `python -m cli.scaffold_argocd` | `argocd/` directory |
| Flux CD | `python -m cli.scaffold_argocd --method flux` | `flux/` directory |
| SRE configs | `python -m cli.scaffold_sre` | `sre/` directory |
| Dev Container | `python -m cli.scaffold_devcontainer` | `.devcontainer/` directory |
| Interactive wizard | `python -m cli.devopsos` | varies (see below) |
| Process-First | `python -m cli.devopsos process-first` | stdout (educational content) |

All generators also accept environment variables as an alternative to flags —
see [Environment Variable Reference](#environment-variable-reference).

---

## scaffold_gha — GitHub Actions Generator

Generates a GitHub Actions workflow YAML file.

### Invocation

```bash
python -m cli.scaffold_gha [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GHA_NAME` | `DevOps-OS` | Workflow name |
| `--type TYPE` | `DEVOPS_OS_GHA_TYPE` | `complete` | Workflow type: `build` \| `test` \| `deploy` \| `complete` \| `reusable` |
| `--languages LANGS` | `DEVOPS_OS_GHA_LANGUAGES` | `python,javascript` | Comma-separated languages: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | `DEVOPS_OS_GHA_KUBERNETES` | `false` | Include Kubernetes deployment steps |
| `--registry URL` | `DEVOPS_OS_GHA_REGISTRY` | `ghcr.io` | Container registry URL |
| `--k8s-method METHOD` | `DEVOPS_OS_GHA_K8S_METHOD` | `kubectl` | K8s deploy method: `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output DIR` | `DEVOPS_OS_GHA_OUTPUT` | `.github/workflows` | Output directory |
| `--custom-values FILE` | `DEVOPS_OS_GHA_CUSTOM_VALUES` | _(none)_ | Path to a custom values JSON file |
| `--image IMAGE` | `DEVOPS_OS_GHA_IMAGE` | `ghcr.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--branches BRANCHES` | `DEVOPS_OS_GHA_BRANCHES` | `main` | Comma-separated branches that trigger the workflow |
| `--matrix` | `DEVOPS_OS_GHA_MATRIX` | `false` | Enable matrix builds across OS/architectures |
| `--env-file FILE` | `DEVOPS_OS_GHA_ENV_FILE` | _(cli dir)_ | Path to `devcontainer.env.json` for tool selection |
| `--reusable` | `DEVOPS_OS_GHA_REUSABLE` | `false` | Generate a reusable workflow (also set by `--type reusable`) |

### Input files (optional)

| File | Flag | Purpose |
|------|------|---------|
| `devcontainer.env.json` | `--env-file` | Pre-loads language and tool selection from your dev container config |
| `custom-values.json` | `--custom-values` | Overrides any generated value (build timeouts, matrix config, etc.) |

### Output files

| File | Condition | Description |
|------|-----------|-------------|
| `<output>/<name>-<type>.yml` | always | Generated GitHub Actions workflow (YAML) |

**Default output path:**

```
.github/workflows/devops-os-complete.yml
```

The filename is built as `<name-lowercased-and-hyphenated>-<type>.yml`.  
Example: `--name "My App" --type build` → `.github/workflows/my-app-build.yml`

### Examples

```bash
# Complete CI/CD pipeline for Python + JavaScript, written to default location
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete
# Output: .github/workflows/my-app-complete.yml

# Deploy pipeline with Kubernetes via ArgoCD
python -m cli.scaffold_gha --name my-app --type deploy --kubernetes --k8s-method argocd
# Output: .github/workflows/my-app-deploy.yml

# Matrix build written to a custom directory
python -m cli.scaffold_gha --name my-app --matrix --output /tmp/workflows
# Output: /tmp/workflows/my-app-complete.yml

# Reusable workflow
python -m cli.scaffold_gha --name shared --type reusable
# Output: .github/workflows/shared-reusable.yml
```

---

## scaffold_gitlab — GitLab CI Generator

Generates a `.gitlab-ci.yml` pipeline file.

### Invocation

```bash
python -m cli.scaffold_gitlab [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GITLAB_NAME` | `my-app` | Application / pipeline name |
| `--type TYPE` | `DEVOPS_OS_GITLAB_TYPE` | `complete` | Pipeline type: `build` \| `test` \| `deploy` \| `complete` |
| `--languages LANGS` | `DEVOPS_OS_GITLAB_LANGUAGES` | `python` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | `DEVOPS_OS_GITLAB_KUBERNETES` | `false` | Add a Kubernetes deploy stage |
| `--k8s-method METHOD` | `DEVOPS_OS_GITLAB_K8S_METHOD` | `kubectl` | K8s method: `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output FILE` | `DEVOPS_OS_GITLAB_OUTPUT` | `.gitlab-ci.yml` | Output file path |
| `--image IMAGE` | `DEVOPS_OS_GITLAB_IMAGE` | `docker:24` | Default Docker image for pipeline jobs |
| `--branches BRANCHES` | `DEVOPS_OS_GITLAB_BRANCHES` | `main` | Comma-separated protected branches (used for deploy rules) |
| `--kube-namespace NS` | `DEVOPS_OS_GITLAB_KUBE_NAMESPACE` | _(empty)_ | Kubernetes namespace; empty means use `$KUBE_NAMESPACE` GitLab variable |
| `--custom-values FILE` | _(not in env)_ | _(none)_ | Path to a custom values JSON file |

### Input files (optional)

| File | Flag | Purpose |
|------|------|---------|
| `custom-values.json` | `--custom-values` | Overrides any generated value |

### Output files

| File | Condition | Description |
|------|-----------|-------------|
| `<output>` | always | Generated GitLab CI pipeline (YAML) |

**Default output path:**

```
.gitlab-ci.yml
```

Use `--output path/to/my-pipeline.yml` to write to a different location.

### Examples

```bash
# Complete Python pipeline (default output)
python -m cli.scaffold_gitlab --name flask-api --languages python --type complete
# Output: .gitlab-ci.yml

# Java build + test, written to a sub-directory
python -m cli.scaffold_gitlab --name java-api --languages java --type test \
       --output ci/gitlab-ci.yml
# Output: ci/gitlab-ci.yml

# Complete pipeline with ArgoCD deploy on main and production branches
python -m cli.scaffold_gitlab --name my-app --languages python,go \
       --kubernetes --k8s-method argocd --branches main,production
# Output: .gitlab-ci.yml
```

---

## scaffold_jenkins — Jenkins Pipeline Generator

Generates a `Jenkinsfile` (declarative pipeline).

### Invocation

```bash
python -m cli.scaffold_jenkins [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_JENKINS_NAME` | `DevOps-OS` | Pipeline name |
| `--type TYPE` | `DEVOPS_OS_JENKINS_TYPE` | `complete` | Pipeline type: `build` \| `test` \| `deploy` \| `complete` \| `parameterized` |
| `--languages LANGS` | `DEVOPS_OS_JENKINS_LANGUAGES` | `python,javascript` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | `DEVOPS_OS_JENKINS_KUBERNETES` | `false` | Add Kubernetes deploy stage |
| `--registry URL` | `DEVOPS_OS_JENKINS_REGISTRY` | `docker.io` | Container registry URL |
| `--k8s-method METHOD` | `DEVOPS_OS_JENKINS_K8S_METHOD` | `kubectl` | K8s method: `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output FILE` | `DEVOPS_OS_JENKINS_OUTPUT` | `Jenkinsfile` | Output file path |
| `--custom-values FILE` | `DEVOPS_OS_JENKINS_CUSTOM_VALUES` | _(none)_ | Path to a custom values JSON file |
| `--image IMAGE` | `DEVOPS_OS_JENKINS_IMAGE` | `docker.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--scm SCM` | `DEVOPS_OS_JENKINS_SCM` | `git` | Source control: `git` \| `svn` \| `none` |
| `--parameters` | `DEVOPS_OS_JENKINS_PARAMETERS` | `false` | Add runtime parameters (auto-enabled for `--type parameterized`) |
| `--env-file FILE` | `DEVOPS_OS_JENKINS_ENV_FILE` | _(cli dir)_ | Path to `devcontainer.env.json` |

### Input files (optional)

| File | Flag | Purpose |
|------|------|---------|
| `devcontainer.env.json` | `--env-file` | Pre-loads language and tool selection |
| `custom-values.json` | `--custom-values` | Overrides generated defaults (credentials IDs, timeouts, etc.) |

### Output files

| File | Condition | Description |
|------|-----------|-------------|
| `<output>` | always | Generated Jenkinsfile (Groovy declarative pipeline) |

**Default output path:**

```
Jenkinsfile
```

Use `--output path/to/Jenkinsfile` to write to a different location.

### Examples

```bash
# Complete Java pipeline with default output
python -m cli.scaffold_jenkins --name java-api --languages java --type complete
# Output: Jenkinsfile

# Parameterized pipeline for Python
python -m cli.scaffold_jenkins --name my-app --languages python --type parameterized
# Output: Jenkinsfile

# Pipeline with Kubernetes deploy, written to a sub-directory
python -m cli.scaffold_jenkins --name my-app --languages go \
       --kubernetes --k8s-method kustomize --output pipelines/Jenkinsfile
# Output: pipelines/Jenkinsfile
```

---

## scaffold_argocd — ArgoCD / Flux CD Generator

Generates GitOps configuration files for ArgoCD (Application, AppProject, optional Rollout) or Flux CD (GitRepository, Kustomization, image automation).

### Invocation

```bash
python -m cli.scaffold_argocd [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_ARGOCD_NAME` | `my-app` | Application name |
| `--method METHOD` | `DEVOPS_OS_ARGOCD_METHOD` | `argocd` | GitOps tool: `argocd` \| `flux` |
| `--repo URL` | `DEVOPS_OS_ARGOCD_REPO` | `https://github.com/myorg/my-app.git` | Git repository URL |
| `--revision REV` | `DEVOPS_OS_ARGOCD_REVISION` | `HEAD` | Git branch, tag, or commit SHA |
| `--path PATH` | `DEVOPS_OS_ARGOCD_PATH` | `k8s` | Path inside the repository to manifests |
| `--namespace NS` | `DEVOPS_OS_ARGOCD_NAMESPACE` | `default` | Target Kubernetes namespace |
| `--project PROJECT` | `DEVOPS_OS_ARGOCD_PROJECT` | `default` | ArgoCD project name |
| `--server URL` | `DEVOPS_OS_ARGOCD_SERVER` | `https://kubernetes.default.svc` | Destination Kubernetes API server |
| `--auto-sync` | `DEVOPS_OS_ARGOCD_AUTO_SYNC` | `false` | Enable automated sync (prune + self-heal) |
| `--rollouts` | `DEVOPS_OS_ARGOCD_ROLLOUTS` | `false` | Add an Argo Rollouts canary strategy resource |
| `--image IMAGE` | `DEVOPS_OS_ARGOCD_IMAGE` | `ghcr.io/myorg/my-app` | Container image (used in Rollouts / Flux image automation) |
| `--output-dir DIR` | `DEVOPS_OS_ARGOCD_OUTPUT_DIR` | `.` | Root directory for all output files |
| `--allow-any-source-repo` | `DEVOPS_OS_ARGOCD_ALLOW_ANY_SOURCE_REPO` | `false` | Add `*` to AppProject `sourceRepos` (opt-in; grants access to any repo) |

### Input files

This command does not read any input files. All configuration is provided via flags or environment variables.

### Output files — ArgoCD mode (`--method argocd`)

All files are written under `<output-dir>/argocd/`:

| File | Condition | Description |
|------|-----------|-------------|
| `argocd/application.yaml` | always | ArgoCD `Application` Custom Resource |
| `argocd/appproject.yaml` | always | ArgoCD `AppProject` Custom Resource |
| `argocd/rollout.yaml` | only with `--rollouts` | Argo Rollouts canary `Rollout` resource |

**Default output paths (with `--output-dir .`):**

```
argocd/
├── application.yaml
├── appproject.yaml
└── rollout.yaml        ← only when --rollouts is set
```

### Output files — Flux CD mode (`--method flux`)

All files are written under `<output-dir>/flux/`:

| File | Condition | Description |
|------|-----------|-------------|
| `flux/git-repository.yaml` | always | Flux `GitRepository` source |
| `flux/kustomization.yaml` | always | Flux `Kustomization` resource |
| `flux/image-update-automation.yaml` | always | `ImageRepository` + `ImagePolicy` + `ImageUpdateAutomation` resources (multi-doc YAML) |

**Default output paths (with `--output-dir .`):**

```
flux/
├── git-repository.yaml
├── kustomization.yaml
└── image-update-automation.yaml
```

### Examples

```bash
# ArgoCD Application + AppProject in a custom directory
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --namespace production \
       --output-dir gitops
# Output: gitops/argocd/application.yaml
#         gitops/argocd/appproject.yaml

# ArgoCD with automated sync and canary rollout
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --auto-sync --rollouts
# Output: argocd/application.yaml
#         argocd/appproject.yaml
#         argocd/rollout.yaml

# Flux CD with image automation
python -m cli.scaffold_argocd --name my-app --method flux \
       --repo https://github.com/myorg/my-app.git \
       --image ghcr.io/myorg/my-app \
       --output-dir gitops
# Output: gitops/flux/git-repository.yaml
#         gitops/flux/kustomization.yaml
#         gitops/flux/image-update-automation.yaml
```

---

## scaffold_sre — SRE Config Generator

Generates production-grade SRE configuration files: Prometheus alert rules, Grafana dashboard, SLO manifest, and Alertmanager routing config.

### Invocation

```bash
python -m cli.scaffold_sre [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_SRE_NAME` | `my-app` | Application / service name |
| `--team TEAM` | `DEVOPS_OS_SRE_TEAM` | `platform` | Owning team (used in labels and alert routing) |
| `--namespace NS` | `DEVOPS_OS_SRE_NAMESPACE` | `default` | Kubernetes namespace where the app runs |
| `--slo-type TYPE` | `DEVOPS_OS_SRE_SLO_TYPE` | `all` | SLO type: `availability` \| `latency` \| `error_rate` \| `all` |
| `--slo-target PCT` | `DEVOPS_OS_SRE_SLO_TARGET` | `99.9` | SLO target as a percentage (e.g. `99.5`) |
| `--latency-threshold SEC` | `DEVOPS_OS_SRE_LATENCY_THRESHOLD` | `0.5` | Latency SLI threshold in seconds |
| `--pagerduty-key KEY` | `DEVOPS_OS_SRE_PAGERDUTY_KEY` | _(empty)_ | PagerDuty integration key; omit to skip PagerDuty routing |
| `--slack-channel CHANNEL` | `DEVOPS_OS_SRE_SLACK_CHANNEL` | `#alerts` | Slack channel for alert routing |
| `--output-dir DIR` | `DEVOPS_OS_SRE_OUTPUT_DIR` | `sre` | Directory where all output files are written |

### Input files

This command does not read any input files. All configuration is provided via flags or environment variables.

### Output files

All files are written to `<output-dir>/`:

| File | Condition | Description |
|------|-----------|-------------|
| `alert-rules.yaml` | always | Prometheus `PrometheusRule` Custom Resource with availability, latency, and infrastructure alert groups |
| `grafana-dashboard.json` | always | Importable Grafana dashboard JSON with six metric panels |
| `slo.yaml` | always | [Sloth](https://sloth.dev)-compatible SLO manifest |
| `alertmanager-config.yaml` | always | Alertmanager routing config stub (Slack + optional PagerDuty) |

**Default output paths (with `--output-dir sre`):**

```
sre/
├── alert-rules.yaml
├── grafana-dashboard.json
├── slo.yaml
└── alertmanager-config.yaml
```

### Examples

```bash
# All SRE configs with defaults
python -m cli.scaffold_sre --name my-app --team platform
# Output: sre/alert-rules.yaml
#         sre/grafana-dashboard.json
#         sre/slo.yaml
#         sre/alertmanager-config.yaml

# Availability-only SLO, written to a custom directory
python -m cli.scaffold_sre --name my-app --slo-type availability \
       --slo-target 99.9 --output-dir monitoring
# Output: monitoring/alert-rules.yaml  (etc.)

# Latency SLO with 200ms threshold and PagerDuty alerting
python -m cli.scaffold_sre --name my-api --slo-type latency \
       --latency-threshold 0.2 \
       --pagerduty-key YOUR_PD_KEY \
       --slack-channel "#platform-alerts"
# Output: sre/alert-rules.yaml  (etc.)
```

---

## scaffold_devcontainer — Dev Container Generator

Generates VS Code Dev Container configuration files.

### Invocation

```bash
python -m cli.scaffold_devcontainer [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--languages LANGS` | `DEVOPS_OS_DEVCONTAINER_LANGUAGES` | `python` | Comma-separated languages: `python`, `java`, `node`, `ruby`, `csharp`, `php`, `rust`, `typescript`, `kotlin`, `c`, `cpp`, `javascript`, `go` |
| `--cicd-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_CICD_TOOLS` | `docker,github_actions` | Comma-separated CI/CD tools: `docker`, `terraform`, `kubectl`, `helm`, `github_actions`, `jenkins` |
| `--kubernetes-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_KUBERNETES_TOOLS` | _(none)_ | Comma-separated K8s tools: `k9s`, `kustomize`, `argocd_cli`, `lens`, `kubeseal`, `flux`, `kind`, `minikube`, `openshift_cli` |
| `--build-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_BUILD_TOOLS` | _(none)_ | Comma-separated build tools: `gradle`, `maven`, `ant`, `make`, `cmake` |
| `--code-analysis TOOLS` | `DEVOPS_OS_DEVCONTAINER_CODE_ANALYSIS` | _(none)_ | Comma-separated analysis tools: `sonarqube`, `checkstyle`, `pmd`, `eslint`, `pylint` |
| `--devops-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_DEVOPS_TOOLS` | _(none)_ | Comma-separated DevOps tools: `nexus`, `prometheus`, `grafana`, `elk`, `jenkins` |
| `--python-version VER` | `DEVOPS_OS_DEVCONTAINER_PYTHON_VERSION` | `3.11` | Python version |
| `--java-version VER` | `DEVOPS_OS_DEVCONTAINER_JAVA_VERSION` | `17` | Java JDK version |
| `--node-version VER` | `DEVOPS_OS_DEVCONTAINER_NODE_VERSION` | `20` | Node.js version |
| `--go-version VER` | `DEVOPS_OS_DEVCONTAINER_GO_VERSION` | `1.21` | Go version |
| `--k9s-version VER` | `DEVOPS_OS_DEVCONTAINER_K9S_VERSION` | `0.29.1` | K9s version |
| `--argocd-version VER` | `DEVOPS_OS_DEVCONTAINER_ARGOCD_VERSION` | `2.8.4` | ArgoCD CLI version |
| `--flux-version VER` | `DEVOPS_OS_DEVCONTAINER_FLUX_VERSION` | `2.1.2` | Flux version |
| `--kustomize-version VER` | `DEVOPS_OS_DEVCONTAINER_KUSTOMIZE_VERSION` | `5.2.1` | Kustomize version |
| `--nexus-version VER` | `DEVOPS_OS_DEVCONTAINER_NEXUS_VERSION` | `3.50.0` | Nexus version |
| `--prometheus-version VER` | `DEVOPS_OS_DEVCONTAINER_PROMETHEUS_VERSION` | `2.45.0` | Prometheus version |
| `--grafana-version VER` | `DEVOPS_OS_DEVCONTAINER_GRAFANA_VERSION` | `10.0.0` | Grafana version |
| `--output-dir DIR` | `DEVOPS_OS_DEVCONTAINER_OUTPUT_DIR` | `.` | Root output directory; files are always written to `<output-dir>/.devcontainer/` |

### Input files

This command does not read any input files. All configuration is provided via flags or environment variables.

### Output files

Both files are always written to `<output-dir>/.devcontainer/`:

| File | Description |
|------|-------------|
| `.devcontainer/devcontainer.json` | VS Code dev container configuration (build args, extensions, forwarded ports) |
| `.devcontainer/devcontainer.env.json` | Tool / language selection used by the Dockerfile and other generators |

**Default output paths (with `--output-dir .`):**

```
.devcontainer/
├── devcontainer.json
└── devcontainer.env.json
```

> **Tip:** The generated `devcontainer.env.json` can be fed into the GitHub Actions and Jenkins generators via their `--env-file` option to ensure your CI/CD environment mirrors your local dev container.

### Examples

```bash
# Python + Go project with Docker and kubectl
python -m cli.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,kubectl,helm \
  --python-version 3.12 \
  --go-version 1.22
# Output: .devcontainer/devcontainer.json
#         .devcontainer/devcontainer.env.json

# Full-stack project with Kubernetes tools, written to a custom directory
python -m cli.scaffold_devcontainer \
  --languages python,java,javascript \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,argocd_cli,flux \
  --devops-tools prometheus,grafana \
  --output-dir /path/to/myproject
# Output: /path/to/myproject/.devcontainer/devcontainer.json
#         /path/to/myproject/.devcontainer/devcontainer.env.json
```

---

## devopsos — Unified CLI

The `devopsos` CLI wraps all generators and provides an interactive wizard.

### Invocation

```bash
python -m cli.devopsos COMMAND [options]
```

### Commands

| Command | Description |
|---------|-------------|
| `init` | Interactive wizard to select tools/languages and optionally generate dev container files |
| `scaffold TARGET` | Non-interactive generator (delegates to the corresponding `scaffold_*` module) |
| `process-first` | Display the Process-First SDLC philosophy, tooling map, and beginner learning tips |

### `devopsos init`

Prompts you to select languages, CI/CD tools, Kubernetes tools, build tools, code analysis tools, and DevOps tools. Then writes a dev container config.

**Output files:**

| File | Description |
|------|-------------|
| `.devcontainer/devcontainer.env.json` | Tool / language selection |
| `.devcontainer/devcontainer.json` | Dev container build configuration (created / updated when you confirm the generation prompt) |

### `devopsos scaffold TARGET`

Delegates to the individual `scaffold_*` modules. Accepts the same environment variables as each module (no interactive prompts).

| Target | Module | Output |
|--------|--------|--------|
| `gha` | `scaffold_gha` | `.github/workflows/<name>-<type>.yml` |
| `gitlab` | `scaffold_gitlab` | `.gitlab-ci.yml` |
| `jenkins` | `scaffold_jenkins` | `Jenkinsfile` |
| `argocd` | `scaffold_argocd` | `argocd/` or `flux/` directory |
| `sre` | `scaffold_sre` | `sre/` directory |
| `devcontainer` | `scaffold_devcontainer` | `.devcontainer/` directory |

```bash
# Examples
python -m cli.devopsos scaffold gha        # uses DEVOPS_OS_GHA_* env vars
python -m cli.devopsos scaffold gitlab     # uses DEVOPS_OS_GITLAB_* env vars
python -m cli.devopsos scaffold argocd     # uses DEVOPS_OS_ARGOCD_* env vars
python -m cli.devopsos scaffold sre        # uses DEVOPS_OS_SRE_* env vars
python -m cli.devopsos scaffold devcontainer
```

### `devopsos process-first`

Prints educational content about the **Process-First** SDLC philosophy used by [cloudenginelabs.io](https://cloudenginelabs.io) and shows exactly how each principle maps to DevOps-OS tooling.

| Option | Default | Description |
|--------|---------|-------------|
| `--section SECTION` | `all` | Section to display: `what` \| `mapping` \| `tips` \| `all` |

| Section | Content |
|---------|---------|
| `what` | What Process-First is and its 5 core principles |
| `mapping` | Table mapping each principle to a specific `devopsos scaffold` command |
| `tips` | AI prompts and book recommendations for DevOps beginners |
| `all` *(default)* | All sections in order |

```bash
# Full overview (all sections)
python -m cli.devopsos process-first

# Ideology & core principles only
python -m cli.devopsos process-first --section what

# Principle → DevOps-OS tooling map
python -m cli.devopsos process-first --section mapping

# AI learning tips for beginners
python -m cli.devopsos process-first --section tips

# Run the module directly (same output)
python -m cli.process_first
python -m cli.process_first --section mapping
```

**When to use this command:**

- **Onboarding new engineers** — run `process-first` before introducing any other `scaffold` command so they understand *why* before *how*.
- **Team workshops** — show the `--section mapping` table to demonstrate which DevOps-OS tool encodes which SDLC process.
- **Self-study** — the `--section tips` output contains copy-paste AI prompts that let any beginner explore CI/CD, GitOps, and SRE concepts in depth.

---

## process-first — Process-First Philosophy

The `process-first` command is also available as a standalone module.

### Invocation

```bash
python -m cli.process_first [--section SECTION]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--section SECTION` | `all` | Which section to display: `what` \| `mapping` \| `tips` \| `all` |

### Output

Prints formatted text to **stdout** — no files are created.

| Section | What it covers |
|---------|---------------|
| `what` | The Process-First philosophy: define before build, standardise before scale, automate the repeatable, observe and iterate, culture over tooling |
| `mapping` | A table mapping each of the 5 principles to the corresponding `devopsos scaffold` sub-command |
| `tips` | Ready-to-paste AI prompts (Claude / ChatGPT / Gemini) for deepening DevOps knowledge, plus book recommendations |
| `all` | All three sections combined (default) |

---

## Environment Variable Reference

Every flag for every command has a corresponding environment variable. The prefix varies by command:

| Command | Env var prefix | Example |
|---------|---------------|---------|
| `scaffold_gha` | `DEVOPS_OS_GHA_` | `DEVOPS_OS_GHA_TYPE=complete` |
| `scaffold_gitlab` | `DEVOPS_OS_GITLAB_` | `DEVOPS_OS_GITLAB_LANGUAGES=python,go` |
| `scaffold_jenkins` | `DEVOPS_OS_JENKINS_` | `DEVOPS_OS_JENKINS_KUBERNETES=true` |
| `scaffold_argocd` | `DEVOPS_OS_ARGOCD_` | `DEVOPS_OS_ARGOCD_AUTO_SYNC=true` |
| `scaffold_sre` | `DEVOPS_OS_SRE_` | `DEVOPS_OS_SRE_SLO_TARGET=99.5` |
| `scaffold_devcontainer` | `DEVOPS_OS_DEVCONTAINER_` | `DEVOPS_OS_DEVCONTAINER_LANGUAGES=python,go` |

Environment variables are looked up at startup and used as default values when the corresponding flag is not supplied. Explicit flags always take precedence over environment variables.

**CI/CD usage example** (no interactive prompts needed):

```bash
export DEVOPS_OS_GHA_NAME="my-service"
export DEVOPS_OS_GHA_TYPE="complete"
export DEVOPS_OS_GHA_LANGUAGES="python,go"
export DEVOPS_OS_GHA_KUBERNETES="true"
export DEVOPS_OS_GHA_K8S_METHOD="argocd"
python -m cli.scaffold_gha
# Output: .github/workflows/my-service-complete.yml
```

---

## Input File Formats

### devcontainer.env.json

Used by `scaffold_gha` (`--env-file`) and `scaffold_jenkins` (`--env-file`) to align CI/CD tooling with the local dev container.

```json
{
  "languages": {
    "python": true,
    "java": false,
    "javascript": true,
    "go": false
  },
  "cicd": {
    "docker": true,
    "terraform": false,
    "kubectl": true,
    "helm": true,
    "github_actions": true,
    "jenkins": false
  },
  "kubernetes": {
    "k9s": false,
    "kustomize": true,
    "argocd_cli": false,
    "flux": false,
    "kind": false,
    "minikube": false,
    "openshift_cli": false
  },
  "build_tools": { "gradle": false, "maven": true, "ant": false, "make": true, "cmake": false },
  "code_analysis": { "sonarqube": false, "checkstyle": false, "pmd": false, "eslint": true, "pylint": true },
  "devops_tools": { "nexus": false, "prometheus": false, "grafana": false, "elk": false, "jenkins": false },
  "versions": {
    "python": "3.11",
    "java": "17",
    "node": "20",
    "go": "1.21"
  }
}
```

> **Tip:** Generate this file automatically with `python -m cli.scaffold_devcontainer`, then pass it to other generators with `--env-file .devcontainer/devcontainer.env.json`.

### custom-values.json

Accepted by `scaffold_gha`, `scaffold_jenkins`, and `scaffold_gitlab` via `--custom-values`.

```json
{
  "build": {
    "cache": true,
    "timeout_minutes": 30,
    "artifact_paths": ["dist/**", "build/**"]
  },
  "test": {
    "coverage": true,
    "junit_reports": true,
    "parallel": 4,
    "timeout_minutes": 20
  },
  "deploy": {
    "environments": ["dev", "staging", "prod"],
    "approval_required": true,
    "rollback_enabled": true
  },
  "credentials": {
    "docker": "docker-registry-credentials",
    "kubernetes": "k8s-kubeconfig",
    "git": "git-credentials",
    "argocd": "argocd-token"
  },
  "matrix": {
    "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
    "architecture": ["x86_64", "arm64"]
  }
}
```

---

## Related Documentation

| Topic | Document |
|-------|---------|
| Getting started (first pipeline in 5 min) | [GETTING-STARTED.md](GETTING-STARTED.md) |
| Process-First philosophy & tooling map | [PROCESS-FIRST.md](PROCESS-FIRST.md) |
| GitHub Actions deep dive | [GITHUB-ACTIONS-README.md](GITHUB-ACTIONS-README.md) |
| GitLab CI deep dive | [GITLAB-CI-README.md](GITLAB-CI-README.md) |
| Jenkins deep dive | [JENKINS-PIPELINE-README.md](JENKINS-PIPELINE-README.md) |
| ArgoCD / Flux deep dive | [ARGOCD-README.md](ARGOCD-README.md) |
| SRE configuration deep dive | [SRE-CONFIGURATION-README.md](SRE-CONFIGURATION-README.md) |
| MCP server (AI integration) | [../mcp_server/README.md](../mcp_server/README.md) |
