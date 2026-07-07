---
title: "Developer Platform Onboarding: Multi-Language Dev Containers With DevOps-OS"
slug: "developer-platform-onboarding-devcontainer-devops-os"
description: "DevOps-OS scaffolds a fully configured multi-language dev container so every engineer on your team starts from the same reproducible, tool-complete environment."
topic: "developer-experience"
tags: ["DevContainer", "DeveloperExperience", "PlatformEngineering", "DevOpsOS", "Onboarding"]
publishedAt: "2026-08-18"
featured: false
---

# Developer Platform Onboarding: Multi-Language Dev Containers With DevOps-OS

"It works on my machine" is not a culture problem. It is a tooling problem. When developers start a project with different Python versions, missing CLI tools, or mismatched Kubernetes clients, the first day of work becomes a debugging session.

DevOps-OS solves this with a single `devcontainer` scaffold that produces a reproducible, pre-configured development environment for the entire team.

## Generate a dev container

```bash
python -m cli.devopsos scaffold devcontainer \
  --languages python,go \
  --cicd-tools docker,terraform \
  --kubernetes-tools k9s,flux

# Output:
#   .devcontainer/devcontainer.json
#   .devcontainer/devcontainer.env.json
```

Open the folder in VS Code (or any Dev Containers-compatible editor) and click **Reopen in Container**. Every team member gets the same environment — same language versions, same CLI tools, same Kubernetes clients.

## Initialise a new project from scratch

```bash
python -m cli.devopsos init --dir .
```

The `init` command adds `devcontainer.json`, `devcontainer.env.json`, and a Dockerfile to the current directory, then generates CI/CD and GitOps scaffolding interactively based on your answers.

## What gets configured

### Languages

```json
"languages": {
  "python": true,
  "java": true,
  "javascript": true,
  "go": true
}
```

Each enabled language installs the runtime, package manager, linter, and formatter. Versions are pinned in the `versions` block.

### CI/CD and container tools

```json
"cicd": {
  "docker": true,
  "terraform": true,
  "kubectl": true,
  "helm": true,
  "github_actions": true
}
```

### Kubernetes tools

```json
"kubernetes": {
  "k9s": true,
  "kustomize": true,
  "argocd_cli": true,
  "flux": true,
  "kind": true,
  "minikube": true,
  "kubeseal": true
}
```

Every Kubernetes CLI tool the team uses is installed and version-pinned in the container — no more `brew install` archaeology at the start of each sprint.

## Dev-to-CI parity

The `devcontainer.env.json` file is not just for local development. DevOps-OS CI/CD scaffolds read the same file to generate workflows that mirror your local environment:

```bash
python -m cli.devopsos scaffold gha \
  --name my-app \
  --env-file .devcontainer/devcontainer.env.json
```

The CI workflow uses the same language versions and tool set as the container — eliminating the class of bugs that only appear in CI.

## Onboarding checklist for platform teams

| Step | Command |
|------|---------|
| Create dev container | `devopsos scaffold devcontainer --languages python,go` |
| Generate CI/CD pipeline | `devopsos scaffold gha --name my-app --type complete` |
| Add GitOps delivery | `devopsos scaffold argocd --name my-app --repo <url>` |
| Add SRE observability | `devopsos scaffold sre --name my-app --slo-target 99.9` |
| Add hardening policies | `devopsos scaffold hardening --standard cis-k8s --environment production` |

Five commands. A complete platform-engineering baseline — from developer laptop to production observability.

## VS Code extensions included

The generated `devcontainer.json` pre-installs extensions for every enabled language and tool:

- Python (Pylance, Ruff, debugger)
- Go (gopls, dlv)
- Java (Language Support, Debugger)
- Docker, Kubernetes, YAML, Terraform, HashiCorp
- GitLens, GitHub Actions

Engineers open the project and are productive from minute one.
