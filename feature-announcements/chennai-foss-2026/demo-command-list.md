# Chennai FOSS Demo Command List

This demo should show **Process-First DevOps automation for a Go service** with the fewest commands possible, while still telling the full story from **build → test → deploy → monitoring**.

## IDP onboarding POC page

- Open the lightweight onboarding dashboard: `feature-announcements/chennai-foss-2026/idp-onboarding-demo.html`
- Demo output is backed by the generated sample app assets in `feature-announcements/chennai-foss-2026/demo-output/go-idp-service/`

## Demo objective

Show that DevOps-OS can act as a **self-service internal developer platform (IDP) entry point** where platform teams publish reusable templates and application teams consume them with simple CLI commands.

---

## Recommended demo sequence

### 1. Start with Process-First

```bash
python -m cli.devopsos process-first --section mapping
python -m cli.devopsos process-first --section best_practices
```

**Why this comes first**
- Explains that the platform starts with process, not tooling.
- Gives the audience the map from SDLC stages to scaffold commands.
- Frames the rest of the demo as **golden-path automation**.

**Talk track**
- `mapping` shows which command represents each process.
- `best_practices` connects build, deploy, SRE, and monitoring into one system.

---

### 2. Standardise the Go developer platform

```bash
python -m cli.devopsos scaffold devcontainer \
  --languages go \
  --cicd-tools docker,terraform \
  --kubernetes-tools kubectl,helm,k9s,argocd_cli,flux
```

**What this demonstrates**
- Platform engineering baseline
- Reproducible developer environment
- Toolchain templatisation for Go delivery teams

**Why it matters**
- This is the **platform foundation**.
- Teams do not assemble tools manually; they inherit a standard Go DevOps workspace.

---

### 3. Add the Go test scaffold

```bash
python -m cli.devopsos scaffold unittest --name go-demo --languages go
```

**What this demonstrates**
- Quality gates start early
- Testing is part of the template, not an afterthought

**Why it matters**
- It shows that platform teams can templatise engineering guardrails, not just infrastructure.

---

### 4. Generate the main Go CI/CD workflow

```bash
python -m cli.devopsos scaffold gha \
  --name go-demo \
  --languages go \
  --type complete \
  --kubernetes \
  --k8s-method argocd
```

**What this demonstrates**
- Build, test, containerisation, and deployment pipeline generation
- One-command automation for a Go service
- Standard CI/CD template owned by the platform team

**Why this is the key demo command**
- It gives the fastest visible payoff.
- It proves the platform can turn process into an executable delivery template.

---

### 5. Generate GitOps deployment templates

```bash
python -m cli.devopsos scaffold argocd \
  --name go-demo \
  --repo https://github.com/your-org/go-demo.git \
  --path k8s \
  --auto-sync
```

**What this demonstrates**
- GitOps-based deployment model
- Promotion through Git rather than manual kubectl changes
- Separation of application code and deployment control

**Why it matters**
- This is where the demo shifts from CI/CD to **platform-controlled deployment automation**.

---

### 6. Generate SRE and monitoring templates

```bash
python -m cli.devopsos scaffold sre \
  --name go-demo \
  --team platform \
  --slo-target 99.9
```

**What this demonstrates**
- Prometheus alerts
- Grafana dashboard
- SLO definition
- Monitoring as a built-in part of delivery

**Why it matters**
- It closes the loop from build to monitoring.
- The audience sees that observability is also templatized and self-service.

---

## Best short-form demo flow

If time is limited, use this exact sequence:

```bash
python -m cli.devopsos process-first --section mapping
python -m cli.devopsos scaffold devcontainer --languages go --cicd-tools docker,terraform --kubernetes-tools kubectl,helm,k9s,argocd_cli,flux
python -m cli.devopsos scaffold unittest --name go-demo --languages go
python -m cli.devopsos scaffold gha --name go-demo --languages go --type complete --kubernetes --k8s-method argocd
python -m cli.devopsos scaffold argocd --name go-demo --repo https://github.com/your-org/go-demo.git --path k8s --auto-sync
python -m cli.devopsos scaffold sre --name go-demo --team platform --slo-target 99.9
```

This is the most effective story because it moves in a natural order:

1. **Explain the process**
2. **Create the standard platform workspace**
3. **Add quality automation**
4. **Generate CI/CD**
5. **Generate GitOps deployment**
6. **Generate monitoring and SRE artefacts**

---

## How to tie the commands together in the talk

| Demo step | Command outcome | Platform engineering meaning | Templatisation meaning | IDP meaning |
|---|---|---|---|---|
| Process-First | Shared delivery model | Platform defines the operating model | Standard process blueprint | Developers consume a guided workflow |
| Dev Container | Standard Go workspace | Platform curates tools once | Reusable environment template | Self-service developer setup |
| Unit test scaffold | Standard quality baseline | Platform encodes quality expectations | Reusable test starter template | Developers get guardrails on demand |
| GitHub Actions scaffold | Standard CI/CD workflow | Platform owns golden path delivery | Reusable pipeline template | Teams generate pipelines without tickets |
| ArgoCD scaffold | Standard deployment model | Platform enforces GitOps | Reusable deployment template | Teams self-serve deployments through Git |
| SRE scaffold | Standard observability baseline | Platform embeds reliability practices | Reusable monitoring template | Teams self-serve alerts, dashboards, and SLOs |

---

## Core message for Chennai FOSS

DevOps-OS should be presented not as "another generator", but as:

- a **platform engineering accelerator**
- a **templatisation engine for DevOps processes**
- a lightweight **IDP interface** for self-service delivery

The strongest demo message is:

> **Process-First defines the golden path, DevOps-OS turns it into templates, and the CLI becomes the self-service IDP experience for Go-based delivery teams.**
