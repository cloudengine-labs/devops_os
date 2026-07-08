---
title: "Introducing DevOps-OS: AI-Assisted DevOps Automation From a Single CLI"
slug: "introducing-devops-os-ai-assisted-devops-automation"
description: "DevOps-OS scaffolds production-ready CI/CD pipelines, Kubernetes configs, and SRE dashboards in seconds — from one CLI command or an AI chat prompt."
topic: "devops-automation"
tags: ["DevOpsOS", "DevOpsAutomation", "CICD", "PlatformEngineering", "OpenSource"]
publishedAt: "2026-07-07"
featured: true
---

# Introducing DevOps-OS: AI-Assisted DevOps Automation From a Single CLI

Every DevOps team spends the first weeks of a new project doing the same thing: wiring together CI/CD pipelines, Kubernetes manifests, monitoring dashboards, and local development environments. The tooling differs — GitHub Actions, Jenkins, ArgoCD, Prometheus — but the boilerplate is always recognisable.

**DevOps-OS exists to eliminate that boilerplate entirely.**

## What is DevOps-OS?

DevOps-OS is an open-source DevOps automation platform built by [CloudEngine Labs](https://cloudenginelabs.io). It scaffolds production-ready configuration artefacts — CI/CD pipelines, Kubernetes manifests, SRE observability configs, infrastructure hardening baselines, and developer environments — in seconds, from a single CLI command or an AI chat prompt.

```bash
# Install
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
pip install -r cli/requirements.txt

# Generate a complete GitHub Actions CI/CD pipeline for a Python app
python -m cli.devopsos scaffold gha --name my-api --languages python --type complete
# Output: .github/workflows/my-api-complete.yml
```

That one command produces a fully wired, multi-stage workflow: lint, test, build, Docker push, and Kubernetes deploy.

## The full scaffold surface

| Command | What it generates |
|---------|-------------------|
| `scaffold gha` | GitHub Actions workflows (build / test / deploy / complete / reusable) |
| `scaffold gitlab` | GitLab CI/CD pipeline (`.gitlab-ci.yml`) |
| `scaffold jenkins` | Jenkinsfile (Declarative Pipeline) |
| `scaffold argocd` | ArgoCD Application + AppProject, or Flux CD Kustomization |
| `scaffold sre` | Prometheus alert rules, Grafana dashboard, SLO manifest |
| `scaffold hardening` | Kyverno policies, InSpec profiles, Checkov checks |
| `scaffold devcontainer` | `devcontainer.json` for multi-language dev environments |
| `scaffold unittest` | pytest, Jest, Vitest, Mocha, or Go test configs |

## Use it with AI

DevOps-OS ships with a built-in **MCP (Model Context Protocol) server** that exposes every scaffold tool as a native skill for Claude, ChatGPT, or any MCP-compatible AI assistant.

```bash
python -m mcp_server.server
```

Ask your AI assistant: *"Generate a Jenkins pipeline for a Java Spring Boot app with Kubernetes deployment via Kustomize."* It calls DevOps-OS under the hood and hands you a production-ready `Jenkinsfile`.

## Built on Process-First principles

DevOps-OS is not just a code generator. It is built on the **Process-First SDLC philosophy** — the idea that well-defined, repeatable processes must come before tool selection. Every scaffold command encodes a process decision into an immediately usable artefact.

Run `python -m cli.devopsos process-first` in your terminal to explore the philosophy interactively.

## Get started

- GitHub: [cloudengine-labs/devops_os](https://github.com/cloudengine-labs/devops_os)
- Docs: [cloudengine-labs.github.io/devops_os](https://cloudengine-labs.github.io/devops_os)
- License: MIT — free for every team
