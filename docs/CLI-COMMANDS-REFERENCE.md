# DevOps-OS CLI Commands Reference

This page is the single source of truth for every DevOps-OS CLI command.
For each command you will find the **complete option table**, the **input files** it reads, and the **exact output files / directories** it writes.

All scaffold commands are available through the **unified `devopsos` CLI** — one entry point for everything.

---

## Table of Contents

- [Installation](#installation)
- [Command Overview](#command-overview)
- [devopsos scaffold gha — GitHub Actions Generator](#devopsos-scaffold-gha--github-actions-generator)
- [devopsos scaffold gitlab — GitLab CI Generator](#devopsos-scaffold-gitlab--gitlab-ci-generator)
- [devopsos scaffold jenkins — Jenkins Pipeline Generator](#devopsos-scaffold-jenkins--jenkins-pipeline-generator)
- [devopsos scaffold argocd — ArgoCD / Flux CD Generator](#devopsos-scaffold-argocd--argocd--flux-cd-generator)
- [devopsos scaffold sre — SRE Config Generator](#devopsos-scaffold-sre--sre-config-generator)
- [devopsos scaffold devcontainer — Dev Container Generator](#devopsos-scaffold-devcontainer--dev-container-generator)
- [devopsos scaffold cicd — Combined CI/CD Generator](#devopsos-scaffold-cicd--combined-cicd-generator)
- [devopsos init — Interactive Wizard](#devopsos-init--interactive-wizard)
- [devopsos process-first — Process-First Philosophy](#devopsos-process-first--process-first-philosophy)
- [Environment Variable Reference](#environment-variable-reference)
- [Input File Formats](#input-file-formats)

---

## Installation

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scriptsctivate
pip install -r cli/requirements.txt
```

---

## Command Overview

All commands are accessed through the unified `devopsos` CLI:

```bash
python -m cli.devopsos --help
python -m cli.devopsos scaffold --help         # list all scaffold targets
python -m cli.devopsos scaffold gha --help     # GHA-specific options
```

| Command | Invocation | Output location |
|---------|-----------|-----------------|
| GitHub Actions | `python -m cli.devopsos scaffold gha` | `.github/workflows/<name>-<type>.yml` |
| GitLab CI | `python -m cli.devopsos scaffold gitlab` | `.gitlab-ci.yml` |
| Jenkins | `python -m cli.devopsos scaffold jenkins` | `Jenkinsfile` |
| ArgoCD | `python -m cli.devopsos scaffold argocd` | `argocd/` directory |
| Flux CD | `python -m cli.devopsos scaffold argocd --method flux` | `flux/` directory |
| SRE configs | `python -m cli.devopsos scaffold sre` | `sre/` directory |
| Dev Container | `python -m cli.devopsos scaffold devcontainer` | `.devcontainer/` directory |
| Interactive wizard | `python -m cli.devopsos init` | varies (see below) |
| Process-First | `python -m cli.devopsos process-first` | stdout (educational content) |

All generators also accept environment variables as an alternative to flags —
see [Environment Variable Reference](#environment-variable-reference).

---

## devopsos scaffold gha — GitHub Actions Generator

Generates a GitHub Actions workflow YAML file.

### Invocation

```bash
python -m cli.devopsos scaffold gha [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GHA_NAME` | `DevOps-OS` | Workflow name |
| `--type TYPE` | `DEVOPS_OS_GHA_TYPE` | `complete` | Workflow type: `build` \| `test` \| `deploy` \| `complete` \| `reusable` |
| `--languages LANGS` | `DEVOPS_OS_GHA_LANGUAGES` | `python,javascript` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_GHA_KUBERNETES` | `false` | Include Kubernetes deployment steps |
| `--registry URL` | `DEVOPS_OS_GHA_REGISTRY` | `ghcr.io` | Container registry URL |
| `--k8s-method METHOD` | `DEVOPS_OS_GHA_K8S_METHOD` | `kubectl` | K8s deploy method: `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output DIR` | `DEVOPS_OS_GHA_OUTPUT` | `.github/workflows` | Output directory |
| `--custom-values FILE` | `DEVOPS_OS_GHA_CUSTOM_VALUES` | _(none)_ | Path to a custom values JSON file |
| `--image IMAGE` | `DEVOPS_OS_GHA_IMAGE` | `ghcr.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--branches BRANCHES` | `DEVOPS_OS_GHA_BRANCHES` | `main` | Comma-separated branches that trigger the workflow |
| `--matrix` | `DEVOPS_OS_GHA_MATRIX` | `false` | Enable matrix builds across OS/architectures |
| `--env-file FILE` | `DEVOPS_OS_GHA_ENV_FILE` | _(none)_ | Path to `devcontainer.env.json` for tool selection |
| `--reusable` | `DEVOPS_OS_GHA_REUSABLE` | `false` | Generate a reusable workflow |

### Output files

| File | Description |
|------|-------------|
| `<output>/<name>-<type>.yml` | Generated GitHub Actions workflow (YAML) |

### Examples

```bash
python -m cli.devopsos scaffold gha --name my-app --languages python,javascript --type complete
python -m cli.devopsos scaffold gha --name my-app --type deploy --kubernetes --k8s-method argocd
python -m cli.devopsos scaffold gha --name my-app --matrix
python -m cli.devopsos scaffold gha --name shared --type reusable
```

---

## devopsos scaffold gitlab — GitLab CI Generator

Generates a `.gitlab-ci.yml` pipeline file.

### Invocation

```bash
python -m cli.devopsos scaffold gitlab [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GITLAB_NAME` | `my-app` | Application / pipeline name |
| `--type TYPE` | `DEVOPS_OS_GITLAB_TYPE` | `complete` | Pipeline type: `build` \| `test` \| `deploy` \| `complete` |
| `--languages LANGS` | `DEVOPS_OS_GITLAB_LANGUAGES` | `python` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_GITLAB_KUBERNETES` | `false` | Add a Kubernetes deploy stage |
| `--k8s-method METHOD` | `DEVOPS_OS_GITLAB_K8S_METHOD` | `kubectl` | K8s method: `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output FILE` | `DEVOPS_OS_GITLAB_OUTPUT` | `.gitlab-ci.yml` | Output file path |
| `--image IMAGE` | `DEVOPS_OS_GITLAB_IMAGE` | `docker:24` | Default Docker image for pipeline jobs |
| `--branches BRANCHES` | `DEVOPS_OS_GITLAB_BRANCHES` | `main` | Comma-separated protected branches |
| `--kube-namespace NS` | `DEVOPS_OS_GITLAB_KUBE_NAMESPACE` | _(empty)_ | Kubernetes namespace |
| `--custom-values FILE` | _(not in env)_ | _(none)_ | Path to a custom values JSON file |

### Examples

```bash
python -m cli.devopsos scaffold gitlab --name flask-api --languages python --type complete
python -m cli.devopsos scaffold gitlab --name java-api --languages java --type test
python -m cli.devopsos scaffold gitlab --name my-app --languages python,go --kubernetes --k8s-method argocd
```

---

## devopsos scaffold jenkins — Jenkins Pipeline Generator

Generates a `Jenkinsfile` (declarative pipeline).

### Invocation

```bash
python -m cli.devopsos scaffold jenkins [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_JENKINS_NAME` | `DevOps-OS` | Pipeline name |
| `--type TYPE` | `DEVOPS_OS_JENKINS_TYPE` | `complete` | Pipeline type: `build` \| `test` \| `deploy` \| `complete` \| `parameterized` |
| `--languages LANGS` | `DEVOPS_OS_JENKINS_LANGUAGES` | `python,javascript` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_JENKINS_KUBERNETES` | `false` | Add Kubernetes deploy stage |
| `--registry URL` | `DEVOPS_OS_JENKINS_REGISTRY` | `docker.io` | Container registry URL |
| `--k8s-method METHOD` | `DEVOPS_OS_JENKINS_K8S_METHOD` | `kubectl` | K8s method |
| `--output FILE` | `DEVOPS_OS_JENKINS_OUTPUT` | `Jenkinsfile` | Output file path |
| `--custom-values FILE` | `DEVOPS_OS_JENKINS_CUSTOM_VALUES` | _(none)_ | Path to a custom values JSON file |
| `--image IMAGE` | `DEVOPS_OS_JENKINS_IMAGE` | `docker.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--scm SCM` | `DEVOPS_OS_JENKINS_SCM` | `git` | Source control: `git` \| `svn` \| `none` |
| `--parameters` | `DEVOPS_OS_JENKINS_PARAMETERS` | `false` | Add runtime parameters |
| `--env-file FILE` | `DEVOPS_OS_JENKINS_ENV_FILE` | _(none)_ | Path to `devcontainer.env.json` |

### Examples

```bash
python -m cli.devopsos scaffold jenkins --name java-api --languages java --type complete
python -m cli.devopsos scaffold jenkins --name my-app --languages python --type parameterized
python -m cli.devopsos scaffold jenkins --name my-app --languages go --kubernetes --k8s-method kustomize
```

---

## devopsos scaffold argocd — ArgoCD / Flux CD Generator

Generates GitOps configuration files for ArgoCD or Flux CD.

### Invocation

```bash
python -m cli.devopsos scaffold argocd [options]
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
| `--auto-sync` | `DEVOPS_OS_ARGOCD_AUTO_SYNC` | `false` | Enable automated sync |
| `--rollouts` | `DEVOPS_OS_ARGOCD_ROLLOUTS` | `false` | Add Argo Rollouts canary strategy |
| `--image IMAGE` | `DEVOPS_OS_ARGOCD_IMAGE` | `ghcr.io/myorg/my-app` | Container image |
| `--output-dir DIR` | `DEVOPS_OS_ARGOCD_OUTPUT_DIR` | `.` | Root directory for all output files |
| `--allow-any-source-repo` | `DEVOPS_OS_ARGOCD_ALLOW_ANY_SOURCE_REPO` | `false` | Add `*` to AppProject `sourceRepos` |

### Output files

**ArgoCD mode** (`--method argocd`): `argocd/application.yaml`, `argocd/appproject.yaml`, `argocd/rollout.yaml` (with `--rollouts`)

**Flux CD mode** (`--method flux`): `flux/git-repository.yaml`, `flux/kustomization.yaml`, `flux/image-update-automation.yaml`

### Examples

```bash
python -m cli.devopsos scaffold argocd --name my-app --repo https://github.com/myorg/my-app.git
python -m cli.devopsos scaffold argocd --name my-app --auto-sync --rollouts
python -m cli.devopsos scaffold argocd --name my-app --method flux --image ghcr.io/myorg/my-app
```

---

## devopsos scaffold sre — SRE Config Generator

Generates Prometheus alert rules, Grafana dashboard, SLO manifest, and Alertmanager config.

### Invocation

```bash
python -m cli.devopsos scaffold sre [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_SRE_NAME` | `my-app` | Application / service name |
| `--team TEAM` | `DEVOPS_OS_SRE_TEAM` | `platform` | Owning team |
| `--namespace NS` | `DEVOPS_OS_SRE_NAMESPACE` | `default` | Kubernetes namespace |
| `--slo-type TYPE` | `DEVOPS_OS_SRE_SLO_TYPE` | `all` | SLO type: `availability` \| `latency` \| `error_rate` \| `all` |
| `--slo-target PCT` | `DEVOPS_OS_SRE_SLO_TARGET` | `99.9` | SLO target percentage |
| `--latency-threshold SEC` | `DEVOPS_OS_SRE_LATENCY_THRESHOLD` | `0.5` | Latency threshold in seconds |
| `--pagerduty-key KEY` | `DEVOPS_OS_SRE_PAGERDUTY_KEY` | _(empty)_ | PagerDuty integration key |
| `--slack-channel CHANNEL` | `DEVOPS_OS_SRE_SLACK_CHANNEL` | `#alerts` | Slack channel |
| `--output-dir DIR` | `DEVOPS_OS_SRE_OUTPUT_DIR` | `sre` | Output directory |

### Output files

`sre/alert-rules.yaml`, `sre/grafana-dashboard.json`, `sre/slo.yaml`, `sre/alertmanager-config.yaml`

### Examples

```bash
python -m cli.devopsos scaffold sre --name my-app --team platform
python -m cli.devopsos scaffold sre --name my-app --slo-type availability --slo-target 99.9
python -m cli.devopsos scaffold sre --name my-api --slo-type latency --latency-threshold 0.2
```

---

## devopsos scaffold devcontainer — Dev Container Generator

Generates VS Code Dev Container configuration files.

### Invocation

```bash
python -m cli.devopsos scaffold devcontainer [options]
```

### Options

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--languages LANGS` | `DEVOPS_OS_DEVCONTAINER_LANGUAGES` | `python` | Comma-separated languages |
| `--cicd-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_CICD_TOOLS` | `docker,github_actions` | Comma-separated CI/CD tools |
| `--kubernetes-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_KUBERNETES_TOOLS` | _(none)_ | Comma-separated K8s tools |
| `--build-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_BUILD_TOOLS` | _(none)_ | Comma-separated build tools |
| `--code-analysis TOOLS` | `DEVOPS_OS_DEVCONTAINER_CODE_ANALYSIS` | _(none)_ | Comma-separated analysis tools |
| `--devops-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_DEVOPS_TOOLS` | _(none)_ | Comma-separated DevOps tools |
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
| `--output-dir DIR` | `DEVOPS_OS_DEVCONTAINER_OUTPUT_DIR` | `.` | Root output directory |

### Output files

`.devcontainer/devcontainer.json` and `.devcontainer/devcontainer.env.json`

### Examples

```bash
python -m cli.devopsos scaffold devcontainer --languages python,go --cicd-tools docker,kubectl,helm
python -m cli.devopsos scaffold devcontainer --kubernetes-tools kubectl,helm,argocd_cli
python -m cli.devopsos scaffold devcontainer --languages go --go-version 1.22 --output-dir myproject
```

---

## devopsos scaffold cicd — Combined CI/CD Generator

Generates both a GitHub Actions workflow and a Jenkins pipeline in one step.

### Invocation

```bash
python -m cli.devopsos scaffold cicd [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `DevOps-OS` | Pipeline name |
| `--type TYPE` | `complete` | Pipeline type: `build` \| `test` \| `deploy` \| `complete` |
| `--languages LANGS` | `python,javascript` | Comma-separated languages |
| `--kubernetes` | `false` | Include Kubernetes deployment steps |
| `--k8s-method METHOD` | `kubectl` | K8s deploy method |
| `--output-dir DIR` | `.` | Output directory |
| `--registry URL` | `docker.io` | Container registry URL |
| `--matrix` | `false` | Enable matrix builds for GitHub Actions |
| `--parameters` | `false` | Enable parameterized builds for Jenkins |
| `--github` | `false` | Generate GitHub Actions workflow only |
| `--jenkins` | `false` | Generate Jenkins pipeline only |
| `--all` | `false` | Generate both (default when neither is given) |

### Examples

```bash
python -m cli.devopsos scaffold cicd --name my-app --type complete --languages python
python -m cli.devopsos scaffold cicd --name my-app --github
python -m cli.devopsos scaffold cicd --name my-app --jenkins --type build
```

---

## devopsos init — Interactive Wizard

Prompts you to select languages, CI/CD tools, Kubernetes tools, build tools, code analysis tools, and DevOps tools. Then writes a dev container config.

### Invocation

```bash
python -m cli.devopsos init [--dir DIRECTORY]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dir DIR` | `.` | Directory in which to create the `.devcontainer/` folder |

### Output files

`.devcontainer/devcontainer.env.json` and `.devcontainer/devcontainer.json`

---

## devopsos process-first — Process-First Philosophy

Prints educational content about the **Process-First** SDLC philosophy and shows how each principle maps to DevOps-OS tooling.

### Invocation

```bash
python -m cli.devopsos process-first [--section SECTION]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--section SECTION` | `all` | Section to display: `what` \| `mapping` \| `tips` \| `best_practices` \| `all` |

### Examples

```bash
python -m cli.devopsos process-first
python -m cli.devopsos process-first --section what
python -m cli.devopsos process-first --section mapping
python -m cli.devopsos process-first --section tips
```

---

## Environment Variable Reference

Every flag for every command has a corresponding environment variable. The prefix varies by command:

| Command | Env var prefix | Example |
|---------|---------------|---------|
| `scaffold gha` | `DEVOPS_OS_GHA_` | `DEVOPS_OS_GHA_TYPE=complete` |
| `scaffold gitlab` | `DEVOPS_OS_GITLAB_` | `DEVOPS_OS_GITLAB_LANGUAGES=python,go` |
| `scaffold jenkins` | `DEVOPS_OS_JENKINS_` | `DEVOPS_OS_JENKINS_KUBERNETES=true` |
| `scaffold argocd` | `DEVOPS_OS_ARGOCD_` | `DEVOPS_OS_ARGOCD_AUTO_SYNC=true` |
| `scaffold sre` | `DEVOPS_OS_SRE_` | `DEVOPS_OS_SRE_SLO_TARGET=99.5` |
| `scaffold devcontainer` | `DEVOPS_OS_DEVCONTAINER_` | `DEVOPS_OS_DEVCONTAINER_LANGUAGES=python,go` |

Environment variables are looked up at startup and used as default values when the corresponding flag is not supplied. Explicit flags always take precedence over environment variables.

**CI/CD usage example** (no interactive prompts needed):

```bash
export DEVOPS_OS_GHA_NAME="my-service"
export DEVOPS_OS_GHA_TYPE="complete"
export DEVOPS_OS_GHA_LANGUAGES="python,go"
export DEVOPS_OS_GHA_KUBERNETES="true"
export DEVOPS_OS_GHA_K8S_METHOD="argocd"
python -m cli.devopsos scaffold gha
# Output: .github/workflows/my-service-complete.yml
```

---

## Input File Formats

### devcontainer.env.json

Used by `scaffold gha` (`--env-file`) and `scaffold jenkins` (`--env-file`) to align CI/CD tooling with the local dev container.

> **Tip:** Generate this file automatically with `python -m cli.devopsos scaffold devcontainer`, then pass it to other generators with `--env-file .devcontainer/devcontainer.env.json`.

### custom-values.json

Accepted by `scaffold gha`, `scaffold jenkins`, and `scaffold gitlab` via `--custom-values` to override any generated default value.

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
