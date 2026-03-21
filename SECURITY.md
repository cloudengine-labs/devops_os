# Security Policy

## About This Repository

**DevOps-OS** is a DevOps automation platform — it is a **developer tool** that *generates* CI/CD pipeline configs, Kubernetes manifests, ArgoCD/Flux configurations, SRE alert rules, and Grafana dashboards. It is not a web application, does not store user data, and does not expose network services in production (the MCP server is intended for local/trusted AI-assistant use only).

Because of this nature, the security model here is meaningfully different from a typical web service or library. This document describes what counts as a security concern, and how to report it.

---

## Scope of Security Concerns

### ✅ In Scope

These are valid security issues for this repository:

1. **Insecure patterns in generated configs** — If DevOps-OS scaffolds a CI/CD pipeline, Kubernetes manifest, or ArgoCD/Flux config that contains an insecure default (e.g., `privileged: true` containers, world-readable secrets, overly broad RBAC rules, or disabled TLS verification), that is a security issue in the generator itself.

2. **Insecure defaults in SRE/observability outputs** — Alert rules or Grafana dashboard configs that could expose sensitive metric data without authentication by default.

3. **Dependency vulnerabilities** — A known CVE in a direct Python dependency (`cli/requirements.txt`, `mcp_server/requirements.txt`) or Go module (`go-project/go.mod`) that could allow code execution, privilege escalation, or data exfiltration when a user runs the tool.

4. **CLI argument injection** — User-controlled values passed to `devopsos` sub-commands that are not properly sanitised before being written into generated files, allowing malicious content injection into output configs.

5. **MCP server issues** — The local MCP server (`mcp_server/`) handles tool calls from AI assistants (Claude, ChatGPT). Security issues here include unauthenticated remote code paths, arbitrary file-write vulnerabilities, or path-traversal in generated output paths.

6. **Supply-chain / build integrity** — Issues with the GitHub Actions workflows in `.github/workflows/` that could allow a third party to inject malicious code into the project's own CI pipeline.

### ❌ Out of Scope

The following are **not** treated as security vulnerabilities in this repository:

- Security of the infrastructure that a *user* deploys using the generated configs — DevOps-OS is a code generator; the security of generated code after it leaves this tool is the responsibility of the engineer who deploys it.
- General best-practice suggestions for the generated configs that are not objectively insecure defaults (e.g., "use a more restrictive network policy").
- Vulnerabilities in tools that DevOps-OS *generates config for* (e.g., a CVE in Argo CD itself) — report those upstream.
- Issues that require physical access to the developer's machine.

---

## Supported Versions

Only the **latest released version** of DevOps-OS receives security fixes. We do not backport patches to older versions.

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Yes     |
| Older   | ❌ No      |

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report vulnerabilities privately by emailing:

**g.gsaravanan@gmail.com**

Please include:
- A clear description of the vulnerability and its potential impact.
- The version of DevOps-OS you are using (`devopsos --version`).
- Steps to reproduce the issue, or a minimal proof-of-concept.
- Any relevant generated output files (scrub any real secrets before sending).

### What to Expect

- **Acknowledgement within 5 business days** of receiving your report.
- **Triage within 10 business days** — we will confirm whether it is in scope and agree on a severity rating.
- **Fix and disclosure** — for confirmed vulnerabilities, we aim to release a patch and publish a coordinated disclosure within 60 days. We will credit reporters by name (or anonymously, if preferred) in the CHANGELOG.

---

## Security Best Practices for Users

Because DevOps-OS generates infrastructure-as-code that will be deployed by others, we recommend:

1. **Review every generated file before committing or deploying it.** Generated configs are starting points, not final production configs. Always review them for your specific security requirements.

2. **Pin dependency versions in generated pipelines.** The scaffolded GitHub Actions workflows use version-pinned actions where possible; keep those pins up to date.

3. **Restrict ArgoCD AppProject source repositories** — the `--allow-any-source-repo` flag in `devopsos scaffold argocd` is disabled by default for a reason. Only enable it in trusted environments.

4. **Run the MCP server locally only** — `mcp_server/server.py` is designed to be used as a local stdio server by your AI assistant. Do not expose it on a public network interface.

5. **Keep your DevOps-OS installation up to date** — run `pip install --upgrade devopsos` or pull the latest version from this repository regularly.
