# Process-First Philosophy — DevOps-OS

> *"Tools are only as good as the processes that govern them."*
> — Saravanan Gnanagur, Founder, CloudEngineLabs

---

## What is Process-First?

[cloudenginelabs.io](https://cloudenginelabs.io) is a **Process-First SDLC automation company**.
Process-First is an engineering philosophy that places well-defined, repeatable
Software Development Life Cycle (SDLC) processes at the centre of every engineering
decision — before selecting tools, platforms, or frameworks.

The guiding question is always: **"Do we have the right process before we pick the tool?"**

---

## The 5 Core Principles

| # | Principle | What it means in practice |
|---|-----------|--------------------------|
| 1 | **Define before you Build** | Document the "why" and "what" of every workflow before writing a single line of pipeline code. |
| 2 | **Standardise before you Scale** | Create golden-path templates (CI/CD, GitOps, SRE) that every team can adopt without reinventing the wheel. |
| 3 | **Automate what is Repeatable** | If a process is done more than twice, automate it. Automation should *encode* the process, not bypass it. |
| 4 | **Observe and Iterate** | Every automated process must produce measurable outcomes (SLOs, SLAs, error budgets) so teams can improve continuously. |
| 5 | **Culture over Tooling** | Processes create shared understanding and accountability. The right culture makes any toolchain succeed; the wrong culture makes the best toolchain fail. |

---

## How Process-First Maps to DevOps-OS Tooling

Each `devopsos scaffold` command encodes one or more Process-First principles into an
immediately usable configuration artefact:

| Process-First Principle | DevOps-OS Command | What it generates |
|-------------------------|-------------------|-------------------|
| **Define before you Build** | `devopsos scaffold cicd` / `gha` / `gitlab` | Interactive wizards capture intent before generating any config file |
| **Standardise before Scale** | `devopsos scaffold gha`, `gitlab`, `jenkins` | Golden-path templates for GitHub Actions, GitLab CI, and Jenkins — reviewed baselines every team can adopt |
| **Automate the Repeatable** | `devopsos scaffold argocd` | GitOps sync process encoded as an ArgoCD `Application` + `AppProject` CR |
| **Automate the Repeatable** | `devopsos scaffold devcontainer` | Developer environment setup encoded as `devcontainer.json` — reproducible for every team member |
| **Observe and Iterate** | `devopsos scaffold sre` | Prometheus alert rules, Grafana dashboards, and SLO manifests — close the measure-improve feedback loop |
| **Culture over Tooling** | `devopsos` MCP server skills | AI assistants (Claude, ChatGPT) coach engineers on DevOps best practices, not just generate config files |

---

## The `process-first` CLI Command

DevOps-OS ships a built-in `process-first` command to surface this philosophy
interactively in your terminal.

### Usage

```bash
# Full overview (default)
python -m cli.devopsos process-first

# Section: what Process-First is and the 5 core principles
python -m cli.devopsos process-first --section what

# Section: how each principle maps to a DevOps-OS scaffold command
python -m cli.devopsos process-first --section mapping

# Section: AI prompts and reading recommendations for beginners
python -m cli.devopsos process-first --section tips
```

You can also invoke the module directly:

```bash
python -m cli.process_first
python -m cli.process_first --section mapping
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--section` | `all` | `what` · `mapping` · `tips` · `all` |

### Where does this command help?

| Situation | Recommended section |
|-----------|---------------------|
| New team member onboarding | `all` — read the full overview first |
| Pre-sprint process alignment meeting | `mapping` — show how each scaffold encodes a principle |
| Self-study / learning DevOps from scratch | `tips` — use the AI prompts to go deep |
| Quick philosophy refresh | `what` — re-read the 5 core principles |

---

## Tips for DevOps Beginners — Learn More with AI Tools

Use AI tools like **Claude**, **ChatGPT**, or **Gemini** to deepen your understanding of
Process-First DevOps. Here are prompts you can try right now:

### Understanding the ideology

> "Explain the process-first approach to SDLC automation and why defining processes before
> choosing tools leads to better outcomes."

### CI/CD pipelines

> "What are the key stages of a production-grade CI/CD pipeline? Give me a process checklist
> before I start writing any pipeline code."

### GitOps and ArgoCD

> "Walk me through the GitOps process: from code commit to production deployment using ArgoCD.
> What processes must exist before ArgoCD adds value?"

### SRE fundamentals

> "What is the SRE process for setting SLOs and error budgets? How do I translate business
> requirements into Prometheus alert rules?"

### Dev Containers

> "What developer-environment standardisation process should a team follow before adopting
> Dev Containers?"

### Using DevOps-OS with AI

Install the DevOps-OS MCP server, connect it to Claude or ChatGPT, and ask:

> "Using the DevOps-OS tools, scaffold a process-first CI/CD setup for a Python microservice
> with GitOps delivery and SRE observability."

See [mcp_server/README.md](../mcp_server/README.md) for setup instructions.

---

## Further Reading

| Resource | Where |
|----------|-------|
| *The DevOps Handbook* — Gene Kim et al. | Your preferred book retailer |
| *Site Reliability Engineering* — Google SRE book | [sre.google/books](https://sre.google/books) |
| *Accelerate* — Nicole Forsgren et al. | Your preferred book retailer |
| Saravanan Gnanagur on LinkedIn | Search **"Saravanan Gnanagur process first"** on [LinkedIn](https://www.linkedin.com) |

---

## Related Documentation

| Topic | Document |
|-------|---------|
| Full CLI reference | [CLI-COMMANDS-REFERENCE.md](CLI-COMMANDS-REFERENCE.md) |
| Getting started (first pipeline in 5 min) | [GETTING-STARTED.md](GETTING-STARTED.md) |
| GitHub Actions deep dive | [GITHUB-ACTIONS-README.md](GITHUB-ACTIONS-README.md) |
| GitLab CI deep dive | [GITLAB-CI-README.md](GITLAB-CI-README.md) |
| Jenkins deep dive | [JENKINS-PIPELINE-README.md](JENKINS-PIPELINE-README.md) |
| ArgoCD / Flux deep dive | [ARGOCD-README.md](ARGOCD-README.md) |
| SRE configuration deep dive | [SRE-CONFIGURATION-README.md](SRE-CONFIGURATION-README.md) |
| MCP server (AI integration) | [../mcp_server/README.md](../mcp_server/README.md) |
