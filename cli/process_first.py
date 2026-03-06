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
  — Saravanan Gnanagur, Founder, CloudEngineLabs

"""

WHAT_IS_PROCESS_FIRST = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WHAT IS PROCESS-FIRST?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Process-First is an engineering philosophy that places well-defined,
  repeatable SDLC (Software Development Life Cycle) processes at the
  centre of every engineering decision — before selecting tools, platforms,
  or frameworks.

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

FULL_TEXT = (
    PROCESS_FIRST_SUMMARY
    + WHAT_IS_PROCESS_FIRST
    + MAPPING_TO_TOOLING
    + BEGINNER_TIPS
)


# ---------------------------------------------------------------------------
# Section helpers (used by --section flag)
# ---------------------------------------------------------------------------

SECTIONS = {
    "what": PROCESS_FIRST_SUMMARY + WHAT_IS_PROCESS_FIRST,
    "mapping": PROCESS_FIRST_SUMMARY + MAPPING_TO_TOOLING,
    "tips": PROCESS_FIRST_SUMMARY + BEGINNER_TIPS,
    "all": FULL_TEXT,
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
            "'what' (ideology overview), "
            "'mapping' (tooling map), "
            "'tips' (beginner AI prompts), "
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
