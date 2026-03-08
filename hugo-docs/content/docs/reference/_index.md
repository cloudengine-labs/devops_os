---
title: "CLI Reference"
weight: 80
bookFlatSection: false
---

# CLI Commands Reference

Complete reference for every DevOps-OS CLI command: options, default values, environment variable equivalents, input files, and exact output paths.

---

## Command Overview

| Command | Invocation | Default output |
|---------|-----------|----------------|
| GitHub Actions | `python -m cli.devopsos scaffold gha` | `.github/workflows/<name>-<type>.yml` |
| GitLab CI | `python -m cli.devopsos scaffold gitlab` | `.gitlab-ci.yml` |
| Jenkins | `python -m cli.devopsos scaffold jenkins` | `Jenkinsfile` |
| ArgoCD | `python -m cli.devopsos scaffold argocd` | `argocd/` directory |
| Flux CD | `python -m cli.devopsos scaffold argocd --method flux` | `flux/` directory |
| SRE configs | `python -m cli.devopsos scaffold sre` | `sre/` directory |
| Dev Container | `python -m cli.devopsos scaffold devcontainer` | `.devcontainer/` directory |
| Interactive wizard | `python -m cli.devopsos init` | varies |
| Process-First guide | `python -m cli.devopsos process-first` | stdout (educational content) |

---

## scaffold gha — GitHub Actions

```bash
python -m cli.devopsos scaffold gha [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GHA_NAME` | `DevOps-OS` | Workflow name |
| `--type TYPE` | `DEVOPS_OS_GHA_TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` \| `reusable` |
| `--languages LANGS` | `DEVOPS_OS_GHA_LANGUAGES` | `python,javascript` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_GHA_KUBERNETES` | `false` | Include Kubernetes steps |
| `--registry URL` | `DEVOPS_OS_GHA_REGISTRY` | `ghcr.io` | Container registry |
| `--k8s-method METHOD` | `DEVOPS_OS_GHA_K8S_METHOD` | `kubectl` | `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output DIR` | `DEVOPS_OS_GHA_OUTPUT` | `.github/workflows` | Output directory |
| `--custom-values FILE` | `DEVOPS_OS_GHA_CUSTOM_VALUES` | _(none)_ | Custom values JSON |
| `--image IMAGE` | `DEVOPS_OS_GHA_IMAGE` | `ghcr.io/yourorg/devops-os:latest` | DevOps-OS image |
| `--branches BRANCHES` | `DEVOPS_OS_GHA_BRANCHES` | `main` | Trigger branches |
| `--matrix` | `DEVOPS_OS_GHA_MATRIX` | `false` | Enable matrix builds |
| `--env-file FILE` | `DEVOPS_OS_GHA_ENV_FILE` | _(cli dir)_ | `devcontainer.env.json` path |
| `--reusable` | `DEVOPS_OS_GHA_REUSABLE` | `false` | Generate reusable workflow |

**Output:** `<output>/<name-hyphenated>-<type>.yml`

---

## scaffold gitlab — GitLab CI

```bash
python -m cli.devopsos scaffold gitlab [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_GITLAB_NAME` | `my-app` | Pipeline name |
| `--type TYPE` | `DEVOPS_OS_GITLAB_TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` |
| `--languages LANGS` | `DEVOPS_OS_GITLAB_LANGUAGES` | `python` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_GITLAB_KUBERNETES` | `false` | Add Kubernetes deploy stage |
| `--k8s-method METHOD` | `DEVOPS_OS_GITLAB_K8S_METHOD` | `kubectl` | Deploy method |
| `--output FILE` | `DEVOPS_OS_GITLAB_OUTPUT` | `.gitlab-ci.yml` | Output file path |
| `--image IMAGE` | `DEVOPS_OS_GITLAB_IMAGE` | `docker:24` | Default pipeline image |
| `--branches BRANCHES` | `DEVOPS_OS_GITLAB_BRANCHES` | `main` | Protected branches |
| `--custom-values FILE` | _(not in env)_ | _(none)_ | Custom values JSON |

**Output:** `<output>` (default: `.gitlab-ci.yml`)

---

## scaffold jenkins — Jenkins

```bash
python -m cli.devopsos scaffold jenkins [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_JENKINS_NAME` | `DevOps-OS` | Pipeline name |
| `--type TYPE` | `DEVOPS_OS_JENKINS_TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` \| `parameterized` |
| `--languages LANGS` | `DEVOPS_OS_JENKINS_LANGUAGES` | `python,javascript` | Comma-separated languages |
| `--kubernetes` | `DEVOPS_OS_JENKINS_KUBERNETES` | `false` | Add Kubernetes stage |
| `--registry URL` | `DEVOPS_OS_JENKINS_REGISTRY` | `docker.io` | Registry URL |
| `--k8s-method METHOD` | `DEVOPS_OS_JENKINS_K8S_METHOD` | `kubectl` | Deploy method |
| `--output FILE` | `DEVOPS_OS_JENKINS_OUTPUT` | `Jenkinsfile` | Output file path |
| `--custom-values FILE` | `DEVOPS_OS_JENKINS_CUSTOM_VALUES` | _(none)_ | Custom values JSON |
| `--image IMAGE` | `DEVOPS_OS_JENKINS_IMAGE` | `docker.io/yourorg/devops-os:latest` | DevOps-OS image |
| `--scm SCM` | `DEVOPS_OS_JENKINS_SCM` | `git` | `git` \| `svn` \| `none` |
| `--parameters` | `DEVOPS_OS_JENKINS_PARAMETERS` | `false` | Add runtime parameters |
| `--env-file FILE` | `DEVOPS_OS_JENKINS_ENV_FILE` | _(cli dir)_ | `devcontainer.env.json` path |

**Output:** `<output>` (default: `Jenkinsfile`)

---

## scaffold argocd — ArgoCD / Flux CD

```bash
python -m cli.devopsos scaffold argocd [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_ARGOCD_NAME` | `my-app` | Application name |
| `--method METHOD` | `DEVOPS_OS_ARGOCD_METHOD` | `argocd` | `argocd` \| `flux` |
| `--repo URL` | `DEVOPS_OS_ARGOCD_REPO` | `https://github.com/myorg/my-app.git` | Git repo URL |
| `--revision REV` | `DEVOPS_OS_ARGOCD_REVISION` | `HEAD` | Branch / tag / SHA |
| `--path PATH` | `DEVOPS_OS_ARGOCD_PATH` | `k8s` | Manifest path in repo |
| `--namespace NS` | `DEVOPS_OS_ARGOCD_NAMESPACE` | `default` | Target namespace |
| `--project PROJECT` | `DEVOPS_OS_ARGOCD_PROJECT` | `default` | ArgoCD project |
| `--server URL` | `DEVOPS_OS_ARGOCD_SERVER` | `https://kubernetes.default.svc` | Destination API server |
| `--auto-sync` | `DEVOPS_OS_ARGOCD_AUTO_SYNC` | `false` | Enable automated sync |
| `--rollouts` | `DEVOPS_OS_ARGOCD_ROLLOUTS` | `false` | Add Argo Rollouts canary |
| `--image IMAGE` | `DEVOPS_OS_ARGOCD_IMAGE` | `ghcr.io/myorg/my-app` | Container image |
| `--output-dir DIR` | `DEVOPS_OS_ARGOCD_OUTPUT_DIR` | `.` | Root output directory |
| `--allow-any-source-repo` | `DEVOPS_OS_ARGOCD_ALLOW_ANY_SOURCE_REPO` | `false` | Allow `*` in AppProject sourceRepos |

**Output (ArgoCD):** `<output-dir>/argocd/application.yaml` + `appproject.yaml` + optional `rollout.yaml`  
**Output (Flux):** `<output-dir>/flux/git-repository.yaml` + `kustomization.yaml` + `image-update-automation.yaml`

---

## scaffold sre — SRE Configuration

```bash
python -m cli.devopsos scaffold sre [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--name NAME` | `DEVOPS_OS_SRE_NAME` | `my-app` | Service name |
| `--team TEAM` | `DEVOPS_OS_SRE_TEAM` | `platform` | Owning team |
| `--namespace NS` | `DEVOPS_OS_SRE_NAMESPACE` | `default` | Kubernetes namespace |
| `--slo-type TYPE` | `DEVOPS_OS_SRE_SLO_TYPE` | `all` | `availability` \| `latency` \| `error_rate` \| `all` |
| `--slo-target PCT` | `DEVOPS_OS_SRE_SLO_TARGET` | `99.9` | SLO target percentage |
| `--latency-threshold SEC` | `DEVOPS_OS_SRE_LATENCY_THRESHOLD` | `0.5` | Latency SLI threshold (seconds) |
| `--pagerduty-key KEY` | `DEVOPS_OS_SRE_PAGERDUTY_KEY` | _(empty)_ | PagerDuty integration key |
| `--slack-channel CHANNEL` | `DEVOPS_OS_SRE_SLACK_CHANNEL` | `#alerts` | Slack channel |
| `--output-dir DIR` | `DEVOPS_OS_SRE_OUTPUT_DIR` | `sre` | Output directory |

**Output:** `<output-dir>/alert-rules.yaml` + `grafana-dashboard.json` + `slo.yaml` + `alertmanager-config.yaml`

---

## scaffold devcontainer — Dev Container

```bash
python -m cli.devopsos scaffold devcontainer [options]
```

| Option | Env var | Default | Description |
|--------|---------|---------|-------------|
| `--languages LANGS` | `DEVOPS_OS_DEVCONTAINER_LANGUAGES` | `python` | Languages to enable |
| `--cicd-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_CICD_TOOLS` | `docker,github_actions` | CI/CD tools |
| `--kubernetes-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_KUBERNETES_TOOLS` | _(none)_ | Kubernetes tools |
| `--build-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_BUILD_TOOLS` | _(none)_ | Build tools |
| `--code-analysis TOOLS` | `DEVOPS_OS_DEVCONTAINER_CODE_ANALYSIS` | _(none)_ | Code analysis tools |
| `--devops-tools TOOLS` | `DEVOPS_OS_DEVCONTAINER_DEVOPS_TOOLS` | _(none)_ | DevOps tools |
| `--python-version VER` | `DEVOPS_OS_DEVCONTAINER_PYTHON_VERSION` | `3.11` | Python version |
| `--java-version VER` | `DEVOPS_OS_DEVCONTAINER_JAVA_VERSION` | `17` | Java JDK version |
| `--node-version VER` | `DEVOPS_OS_DEVCONTAINER_NODE_VERSION` | `20` | Node.js version |
| `--go-version VER` | `DEVOPS_OS_DEVCONTAINER_GO_VERSION` | `1.21` | Go version |
| `--output-dir DIR` | `DEVOPS_OS_DEVCONTAINER_OUTPUT_DIR` | `.` | Root directory |

**Output:** `<output-dir>/.devcontainer/devcontainer.json` + `devcontainer.env.json`

---

## devopsos — Unified CLI

```bash
python -m cli.devopsos COMMAND [options]
```

| Command | Description |
|---------|-------------|
| `init` | Interactive wizard (select languages, tools, generate dev container) |
| `scaffold <target>` | Non-interactive generator — all targets with native options (see below) |
| `process-first` | Learn the Process-First SDLC philosophy and how it maps to DevOps-OS tooling |

### Scaffold targets

```bash
python -m cli.devopsos scaffold gha          # GitHub Actions
python -m cli.devopsos scaffold gitlab       # GitLab CI
python -m cli.devopsos scaffold jenkins      # Jenkins
python -m cli.devopsos scaffold argocd       # ArgoCD / Flux
python -m cli.devopsos scaffold sre          # SRE configs
python -m cli.devopsos scaffold devcontainer # Dev container
```

### process-first command

Prints the Process-First SDLC philosophy to stdout. Accepts an optional `--section` flag to display a focused sub-section.

```bash
# Full overview (all sections, default)
python -m cli.devopsos process-first

# Core principles only
python -m cli.devopsos process-first --section what

# Principle → DevOps-OS tooling mapping table
python -m cli.devopsos process-first --section mapping

# AI prompts and book recommendations for beginners
python -m cli.devopsos process-first --section tips

# Run the standalone module (same output)
python -m cli.process_first --section mapping
```

| Option | Default | Description |
|--------|---------|-------------|
| `--section SECTION` | `all` | Section to display: `what` \| `mapping` \| `tips` \| `all` |

---

## Input File Formats

### devcontainer.env.json (used by `--env-file`)

```json
{
  "languages": { "python": true, "java": false, "javascript": true, "go": false },
  "cicd": { "docker": true, "terraform": false, "kubectl": true, "helm": true },
  "kubernetes": { "k9s": false, "kustomize": true, "argocd_cli": false, "flux": false },
  "build_tools": { "gradle": false, "maven": true, "ant": false, "make": true },
  "code_analysis": { "sonarqube": false, "eslint": true, "pylint": true },
  "devops_tools": { "nexus": false, "prometheus": false, "grafana": false },
  "versions": { "python": "3.11", "java": "17", "node": "20", "go": "1.21" }
}
```

### custom-values.json (used by `--custom-values`)

```json
{
  "build": { "cache": true, "timeout_minutes": 30 },
  "test": { "coverage": true, "junit_reports": true, "parallel": 4 },
  "deploy": { "environments": ["dev", "staging", "prod"], "approval_required": true },
  "credentials": { "docker": "docker-registry-credentials", "kubernetes": "kubeconfig" },
  "matrix": { "os": ["ubuntu-latest", "windows-latest"], "architecture": ["x86_64", "arm64"] }
}
```
