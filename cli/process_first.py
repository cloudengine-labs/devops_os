#!/usr/bin/env python3
"""
DevOps-OS: Process-First Ideology

cloudenginelabs.io is a process-first SDLC automation company.
This module educates users on what "Process First" means, how it maps
to DevOps-OS tooling, and provides beginner tips for further learning.
"""

import argparse
import sys


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

PROCESS_FIRST_SUMMARY = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║               🔄  PROCESS-FIRST  |  cloudenginelabs.io                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

  "Tools are only as good as the processes that govern them."
  — Saravanan Gnanaguru, Founder, CloudEngine Labs

  Process-First is the Systems Thinking of DevOps.

"""

THOUGHT_LEADERS = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THOUGHT LEADERS ON PROCESS-FIRST & SYSTEMS THINKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Gene Kim, Kevin Behr, and George Spafford
  (The Phoenix Project / The DevOps Handbook):

    "The First Way emphasises the performance of the entire system, as opposed
     to the performance of a specific silo of work or department."

    They define the "Three Ways" of DevOps, with the First Way focusing on
    Systems Thinking — optimising the whole flow from development through
    operations to the customer, not just individual components or stages.

  Patrick Debois
  (Founder of DevOpsDays):

    As the founder of DevOpsDays, Patrick Debois emphasised the need to fix
    the broken, inefficient processes between developers and operations before
    introducing new tools.  He showed that cultural and process problems, not
    technology gaps, are the root cause of slow, unreliable software delivery.

"""

WHAT_IS_PROCESS_FIRST = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WHAT IS PROCESS-FIRST?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Process-First is an engineering philosophy that places well-defined,
  repeatable SDLC (Software Development Life Cycle) processes at the
  centre of every engineering decision — before selecting tools, platforms,
  or frameworks.

  It is the Systems Thinking of DevOps: optimise the whole value stream
  from development to operations before optimising any individual step.

  Core principles:

    1. DEFINE before you BUILD
       Document the "why" and "what" of every workflow before writing a
       single line of pipeline code.

    2. STANDARDISE before you SCALE
       Create golden-path templates (CI/CD, GitOps, SRE) that every team
       can adopt without reinventing the wheel.

    3. AUTOMATE what is REPEATABLE
       If a process is done more than twice, automate it. Automation
       should encode the process, not bypass it.

    4. OBSERVE and ITERATE
       Every automated process must produce measurable outcomes (SLOs,
       SLAs, error budgets) so teams can improve continuously.

    5. CULTURE over TOOLING
       Processes exist to create shared understanding and accountability.
       The right culture makes any toolchain succeed; the wrong culture
       makes the best toolchain fail.

"""

MAPPING_TO_TOOLING = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW PROCESS-FIRST MAPS TO DEVOPS-OS TOOLING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────┬──────────────────────────────────────────┐
  │  Process-First Principle    │  DevOps-OS Tooling                       │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Define before you build    │  `devopsos scaffold cicd/gha/gitlab`     │
  │                             │  Interactive wizards capture intent       │
  │                             │  before generating any config file.      │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Standardise before scale   │  Golden-path scaffold templates for      │
  │                             │  GitHub Actions, GitLab CI, Jenkins,     │
  │                             │  ArgoCD, and Flux ensure every team      │
  │                             │  starts from a reviewed baseline.        │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Standardise the container  │  `devopsos scaffold devcontainer`        │
  │  runtime & Kubernetes env   │  encodes Docker/Podman runtime choice    │
  │                             │  and all Kubernetes CLI tools (kubectl,  │
  │                             │  helm, kustomize, argocd_cli, flux,      │
  │                             │  k9s, kind, minikube, kubeseal …) into a │
  │                             │  reproducible devcontainer.json so every │
  │                             │  engineer starts from the same baseline. │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Automate the repeatable    │  `devopsos scaffold argocd` encodes      │
  │                             │  the GitOps sync process as code;        │
  │                             │  `devopsos scaffold devcontainer`        │
  │                             │  encodes the dev-environment setup.      │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Observe and iterate        │  `devopsos scaffold sre` generates       │
  │                             │  Prometheus rules, Grafana dashboards,   │
  │                             │  and SLO manifests to close the          │
  │                             │  measure-improve feedback loop.          │
  ├─────────────────────────────┼──────────────────────────────────────────┤
  │  Culture over tooling       │  MCP server skills let AI assistants     │
  │                             │  (Claude, ChatGPT) coach engineers on    │
  │                             │  DevOps best practices — not just        │
  │                             │  generate config files.                  │
  └─────────────────────────────┴──────────────────────────────────────────┘

"""

BEGINNER_TIPS = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TIPS FOR DEVOPS BEGINNERS — LEARN MORE WITH AI TOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Use AI tools like Claude, ChatGPT, or Gemini to deepen your understanding
  of process-first DevOps. Here are prompts you can try right now:

  📌 Understanding the ideology
     "Explain the process-first approach to SDLC automation and why
      defining processes before choosing tools leads to better outcomes."

  📌 CI/CD pipelines
     "What are the key stages of a production-grade CI/CD pipeline? Give
      me a process checklist before I start writing any pipeline code."

  📌 GitOps and ArgoCD
     "Walk me through the GitOps process: from code commit to production
      deployment using ArgoCD. What processes must exist before ArgoCD
      adds value?"

  📌 SRE fundamentals
     "What is the SRE process for setting SLOs and error budgets?
      How do I translate business requirements into Prometheus alert rules?"

  📌 Dev Containers
     "What developer-environment standardisation process should a team
      follow before adopting Dev Containers?"

  📌 Further reading (ask your AI assistant for summaries of)
     • The DevOps Handbook — Gene Kim et al.
     • Site Reliability Engineering — Google SRE book (sre.google/books)
     • Accelerate — Nicole Forsgren et al.
     • LinkedIn posts by Saravanan Gnanagur on process-first DevOps
       (search: "Saravanan Gnanagur process first" on LinkedIn)

  💡 Pro tip — Use DevOps-OS with AI:
     Install the DevOps-OS MCP server, connect it to Claude or ChatGPT,
     and ask:
       "Using the DevOps-OS tools, scaffold a process-first CI/CD setup
        for a Python microservice with GitOps delivery and SRE observability."

"""

BEST_PRACTICES = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BEST PRACTICES BY STAGE — SYSTEMS THINKING IN DEVOPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Applying Systems Thinking means defining the right process at each stage
  of the value stream before selecting or configuring any tool.

  🔨 BUILD
  ────────
  • Define build standards and conventions before choosing tools
    (Gradle, Maven, Make).
  • Standardise dependency management and enforce version-pinned builds.
  • Enforce reproducible builds across all teams and environments.
  • Use an artifact repository (Nexus) to cache, version, and audit
    build outputs.

  🐳 CONTAINERIZATION
  ────────────────────
  • Choose and document your container runtime (Docker or Podman) before
    writing the first Dockerfile — consistency prevents environment drift.
  • Standardise base images across all services: use a pinned, minimal
    base image (e.g. distroless or Alpine) and update it on a schedule.
  • Define a container image naming and tagging convention (e.g.
    <registry>/<org>/<service>:<gitsha>) before the first build.
  • Scan every image for vulnerabilities during the CI build stage —
    never push an unscanned image to a shared registry.
  • Use multi-stage Dockerfiles to keep production images small and
    free of build-time dependencies.
  • Configure your dev environment with `devopsos scaffold devcontainer`
    to standardise the container runtime for every team member.

  ☸️  KUBERNETES
  ──────────────
  • Define Kubernetes cluster topology and namespace strategy before
    deploying any workload.
  • Use a local cluster (kind or minikube) for development so that
    every engineer can reproduce production-like conditions locally.
  • Manage all manifests through version-controlled Kustomize overlays
    or Helm charts — no kubectl apply from a developer laptop in production.
  • Use GitOps (ArgoCD or Flux) as the single path to deploy and update
    workloads; direct kubectl changes to production are prohibited.
  • Manage Kubernetes secrets with Sealed Secrets (Kubeseal) so that
    encrypted secrets can be safely stored in Git.
  • Use k9s or Lens for day-two operations and cluster observability
    rather than ad-hoc kubectl commands.

  🧪 TEST & QUALITY
  ─────────────────
  • Define quality gates and acceptance criteria before writing tests.
  • Automate unit, integration, and end-to-end tests in every pipeline run.
  • Enforce code standards with static analysis (SonarQube, Checkstyle,
    ESLint, Pylint) as non-negotiable pipeline gates.
  • Fail fast: surface test failures early to prevent bad code from
    advancing to later stages.

  🏗️  IaC & INFRASTRUCTURE
  ─────────────────────────
  • Define infrastructure requirements and constraints before writing
    Terraform or Helm code.
  • Version-control every infrastructure definition — no manual changes
    to production environments.
  • Use Kustomize overlays to manage environment-specific configuration
    (dev / staging / production) from a single base.
  • Detect and alert on infrastructure drift regularly to maintain
    the desired state.

  🚀 DEPLOY & GITOPS
  ──────────────────
  • Define deployment runbooks and rollback procedures before the first
    production release.
  • Use GitOps (ArgoCD, Flux) to make deployment intent explicit in Git
    and fully auditable.
  • Implement blue/green or canary deployments to achieve zero-downtime
    releases.
  • Gate production deployments with automated approval workflows and
    post-deploy smoke tests.

  📈 SRE
  ──────
  • Define SLOs and SLAs before deploying to production — reliability
    targets must exist before you can measure them.
  • Use error budgets to balance reliability investment with feature
    velocity.
  • Alert on symptoms (SLO burn rate) rather than causes (CPU spikes).
  • Establish on-call rotations and incident runbooks before going live.

  📊 MONITORING
  ─────────────
  • Define what "good" looks like (golden signals: Rate, Errors, Duration,
    Saturation) before creating dashboards.
  • Instrument applications with standard metrics from day one.
  • Centralise logs, metrics, and traces in a single observability
    platform (ELK, Prometheus, Grafana).
  • Set alerting thresholds based on SLO objectives, not arbitrary values.

  🔒 SECURITY
  ───────────
  • Shift security left: enforce security scanning in the CI pipeline
    so vulnerabilities are caught before merge.
  • Manage Kubernetes secrets safely using Sealed Secrets (Kubeseal) —
    never store plaintext secrets in Git.
  • Scan container images for vulnerabilities as part of every build.
  • Enforce least-privilege access controls for all service accounts
    and CI/CD pipelines.

"""

USAGE_FOOTER = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO USE THIS COMMAND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python -m cli.devopsos process-first                              # full overview
  python -m cli.devopsos process-first --section what              # 5 core principles
  python -m cli.devopsos process-first --section mapping           # devopsos scaffold map
  python -m cli.devopsos process-first --section tips              # AI prompts for beginners
  python -m cli.devopsos process-first --section best_practices    # best practices by stage
  python -m cli.devopsos process-first --help                      # full option reference

  You can also run the standalone module:

  python -m cli.process_first [--section what|mapping|tips|best_practices|all]

  📖  Full docs: docs/PROCESS-FIRST.md

"""

FULL_TEXT = (
    PROCESS_FIRST_SUMMARY
    + THOUGHT_LEADERS
    + WHAT_IS_PROCESS_FIRST
    + MAPPING_TO_TOOLING
    + BEST_PRACTICES
    + BEGINNER_TIPS
)


# ---------------------------------------------------------------------------
# Section helpers (used by --section flag)
# ---------------------------------------------------------------------------

SECTIONS = {
    "what": PROCESS_FIRST_SUMMARY + THOUGHT_LEADERS + WHAT_IS_PROCESS_FIRST,
    "mapping": PROCESS_FIRST_SUMMARY + MAPPING_TO_TOOLING,
    "tips": PROCESS_FIRST_SUMMARY + BEGINNER_TIPS,
    "best_practices": PROCESS_FIRST_SUMMARY + BEST_PRACTICES,
    "all": FULL_TEXT + USAGE_FOOTER,
}


# ---------------------------------------------------------------------------
# Display logic
# ---------------------------------------------------------------------------

def display(section: str = "all") -> None:
    """Print the requested section to stdout."""
    if section not in SECTIONS:
        raise ValueError(f"Unknown section '{section}'. Choose from: {', '.join(SECTIONS)}")
    print(SECTIONS[section])


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Learn about the Process-First SDLC philosophy and how it maps to DevOps-OS tooling.",
    )
    parser.add_argument(
        "--section",
        choices=list(SECTIONS.keys()),
        default="all",
        help=(
            "Which section to display: "
            "'what' (ideology overview + thought leaders), "
            "'mapping' (tooling map), "
            "'tips' (beginner AI prompts), "
            "'best_practices' (best practices by stage), "
            "or 'all' (default)."
        ),
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_arguments(argv)
    display(args.section)


if __name__ == "__main__":
    main()
