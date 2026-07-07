# DevOps-OS Blog Posts

This folder contains blog articles written about the DevOps-OS project.  
Posts are published to [gsaravanan.com](https://gsaravanan.com) via the content hub at  
[chefgs/gsaravanan-content-hub](https://github.com/chefgs/gsaravanan-content-hub/tree/main/src/content/posts).

---

## How to add a new post

1. Create a new `.md` file in this folder.
2. Name it: `YYYY-MM-DD-your-post-slug.md`  
   The date prefix drives the publish schedule.
3. Add the required frontmatter (see template below).
4. Write the post body in standard Markdown below the closing `---`.
5. Open a PR — the automated publish workflow picks it up on the `publishedAt` date.

---

## Required frontmatter

```yaml
---
title: "Your Post Title Here"
slug: "your-post-slug-here"
description: "One or two sentence SEO description (under 160 chars)."
topic: "devops-automation"
tags: ["Tag1", "Tag2", "Tag3"]
publishedAt: "YYYY-MM-DD"
featured: false
---
```

### Field reference

| Field | Required | Notes |
|-------|----------|-------|
| `title` | ✅ | Human-readable headline |
| `slug` | ✅ | URL path — must be unique, lowercase, hyphenated |
| `description` | ✅ | SEO meta description, ≤ 160 characters |
| `topic` | ✅ | Top-level category (see list below) |
| `tags` | ✅ | Array of tags — use PascalCase, 3–6 tags |
| `publishedAt` | ✅ | ISO date `YYYY-MM-DD` — post goes live on this date |
| `featured` | ✅ | `true` shows the post in the featured section |

### Approved topics

| Topic slug | Use for |
|------------|---------|
| `devops-automation` | General DevOps-OS platform content |
| `ci-cd` | GitHub Actions, GitLab CI, Jenkins pipelines |
| `gitops` | ArgoCD, Flux CD, Kubernetes delivery |
| `sre-observability` | Prometheus, Grafana, SLO, alerting |
| `platform-engineering` | Hardening, compliance, IDP concepts |
| `developer-experience` | Dev container, onboarding, tooling |
| `ai-devops` | MCP server, AI-assisted automation |
| `devops-culture` | Process-First philosophy, principles |

---

## Automation

A scheduled GitHub Actions workflow (`.github/workflows/publish-blogs.yml`) reads this folder,
checks `publishedAt` against today's date, and copies eligible posts into the content hub repo.
Posts already published are tracked to prevent duplicates.
A run summary is emailed to the configured address after each job.

See the workflow file for setup instructions and required secrets.
