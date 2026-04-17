---
title: "Platform Engineering IDP"
description: "Conceptual platform engineering IDP flow from templates through the UI to generated automation."
weight: 15
---

# Platform Engineering IDP Concept

DevOps-OS can be used as a lightweight **internal developer platform (IDP)** experience: platform teams publish golden-path templates, and developers consume them through a guided self-service flow.

---

## Conceptual flow

<div style="overflow-x:auto; margin: 1rem 0;">
  <svg viewBox="0 0 1180 430" role="img" aria-labelledby="idp-title idp-desc" xmlns="http://www.w3.org/2000/svg" style="width:100%; min-width:980px; height:auto; border:1px solid #d1d5db; border-radius:12px; background:#ffffff;">
    <title id="idp-title">Platform engineering IDP conceptual flow</title>
    <desc id="idp-desc">Platform team templates flow into an IDP UI. A developer works from git code commit context, selects templates, chooses automation stages, submits, and receives generated delivery artifacts.</desc>

    <rect x="30" y="60" width="180" height="90" rx="14" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
    <text x="120" y="92" text-anchor="middle" font-size="22" font-weight="700" fill="#1e3a8a">Templates</text>
    <text x="120" y="118" text-anchor="middle" font-size="15" fill="#1f2937">Golden-path CI/CD</text>
    <text x="120" y="138" text-anchor="middle" font-size="15" fill="#1f2937">GitOps • SRE • DevEnv</text>

    <rect x="260" y="60" width="180" height="90" rx="14" fill="#ecfeff" stroke="#0891b2" stroke-width="2"/>
    <text x="350" y="92" text-anchor="middle" font-size="22" font-weight="700" fill="#164e63">IDP UI</text>
    <text x="350" y="118" text-anchor="middle" font-size="15" fill="#1f2937">Self-service catalog</text>
    <text x="350" y="138" text-anchor="middle" font-size="15" fill="#1f2937">Guardrails + standards</text>

    <rect x="490" y="60" width="180" height="90" rx="14" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2"/>
    <text x="580" y="92" text-anchor="middle" font-size="21" font-weight="700" fill="#4c1d95">Git code commit</text>
    <text x="580" y="118" text-anchor="middle" font-size="15" fill="#1f2937">Repository context</text>
    <text x="580" y="138" text-anchor="middle" font-size="15" fill="#1f2937">App or service intent</text>

    <rect x="720" y="40" width="210" height="70" rx="14" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="825" y="72" text-anchor="middle" font-size="20" font-weight="700" fill="#14532d">1. Select templates</text>
    <text x="825" y="95" text-anchor="middle" font-size="14" fill="#1f2937">pipeline, GitOps, SRE, devcontainer</text>

    <rect x="720" y="130" width="210" height="70" rx="14" fill="#fffbeb" stroke="#d97706" stroke-width="2"/>
    <text x="825" y="162" text-anchor="middle" font-size="20" font-weight="700" fill="#92400e">2. Select automation stages</text>
    <text x="825" y="185" text-anchor="middle" font-size="14" fill="#1f2937">build • test • deploy • monitor</text>

    <rect x="720" y="220" width="210" height="70" rx="14" fill="#fdf2f8" stroke="#db2777" stroke-width="2"/>
    <text x="825" y="252" text-anchor="middle" font-size="20" font-weight="700" fill="#9d174d">3. Click submit</text>
    <text x="825" y="275" text-anchor="middle" font-size="14" fill="#1f2937">approve and generate automation</text>

    <rect x="970" y="95" width="180" height="150" rx="14" fill="#f9fafb" stroke="#4b5563" stroke-width="2"/>
    <text x="1060" y="128" text-anchor="middle" font-size="22" font-weight="700" fill="#111827">Outputs</text>
    <text x="1060" y="156" text-anchor="middle" font-size="15" fill="#1f2937">Generated repo changes</text>
    <text x="1060" y="178" text-anchor="middle" font-size="15" fill="#1f2937">Workflow / YAML / config</text>
    <text x="1060" y="200" text-anchor="middle" font-size="15" fill="#1f2937">Standard delivery stages</text>
    <text x="1060" y="222" text-anchor="middle" font-size="15" fill="#1f2937">PR or commit-ready artifacts</text>

    <text x="120" y="42" text-anchor="middle" font-size="15" font-weight="700" fill="#334155">Platform team publishes</text>
    <text x="580" y="42" text-anchor="middle" font-size="15" font-weight="700" fill="#334155">Developer context</text>
    <text x="825" y="20" text-anchor="middle" font-size="15" font-weight="700" fill="#334155">Guided self-service steps</text>

    <line x1="210" y1="105" x2="260" y2="105" stroke="#475569" stroke-width="3"/>
    <polygon points="260,105 247,98 247,112" fill="#475569"/>
    <line x1="440" y1="105" x2="490" y2="105" stroke="#475569" stroke-width="3"/>
    <polygon points="490,105 477,98 477,112" fill="#475569"/>
    <line x1="670" y1="105" x2="720" y2="75" stroke="#475569" stroke-width="3"/>
    <polygon points="720,75 708,76 714,87" fill="#475569"/>
    <line x1="670" y1="105" x2="720" y2="165" stroke="#475569" stroke-width="3"/>
    <polygon points="720,165 708,161 716,153" fill="#475569"/>
    <line x1="670" y1="105" x2="720" y2="255" stroke="#475569" stroke-width="3"/>
    <polygon points="720,255 710,246 721,243" fill="#475569"/>
    <line x1="930" y1="75" x2="970" y2="125" stroke="#475569" stroke-width="3"/>
    <polygon points="970,125 958,120 966,112" fill="#475569"/>
    <line x1="930" y1="165" x2="970" y2="170" stroke="#475569" stroke-width="3"/>
    <polygon points="970,170 958,163 958,177" fill="#475569"/>
    <line x1="930" y1="255" x2="970" y2="215" stroke="#475569" stroke-width="3"/>
    <polygon points="970,215 959,217 968,226" fill="#475569"/>

    <rect x="40" y="335" width="1100" height="52" rx="12" fill="#111827"/>
    <text x="590" y="366" text-anchor="middle" font-size="18" font-weight="700" fill="#ffffff">Template → IDP UI → Git code commit → Developer selects templates → Select required automation stages → Click submit</text>
  </svg>
</div>

---

## What the diagram shows

1. **Platform teams** publish reusable templates into the IDP catalog.
2. The **IDP UI** gives developers a guided entry point with platform guardrails.
3. The flow starts from a **Git repository / code commit context** for the service being onboarded or updated.
4. The developer **selects the required templates** and **chooses automation stages** such as build, test, deploy, GitOps, or observability.
5. On **submit**, DevOps-OS generates the standardized delivery artifacts that can be committed or reviewed in Git.

---

## Example automation stages

| Stage | Typical DevOps-OS output |
|-------|---------------------------|
| Build & Test | [GitHub Actions / GitLab CI / Jenkins workflows]({{< relref "/docs/ci-cd" >}}) |
| Deploy | [ArgoCD or Flux GitOps configuration]({{< relref "/docs/gitops" >}}) |
| Observe | [Prometheus, Grafana, and SLO configuration]({{< relref "/docs/sre" >}}) |
| Developer Environment | [Dev Container configuration]({{< relref "/docs/dev-container" >}}) |

This makes DevOps-OS a practical way to present **platform engineering standards as a self-service IDP experience**.
