# DevOps-OS Skills Documentation Index

**Complete reference guide for all DevOps-OS skills documentation. Start here.**

---

## 📚 Documentation Overview

DevOps-OS **Skills** are AI-callable tool definitions that generate production-ready DevOps configurations. This documentation suite provides guides for users, developers, and architects.

---

## 🚀 Quick Start

### For Users (Developers & DevOps Engineers)

**Start here if you want to use skills to generate configs via Claude or ChatGPT:**

1. **[Skills Usage Guide](SKILLS-USAGE-GUIDE.md)** — How to use skills with Claude Desktop, ChatGPT, and OpenAI API
   - Available skills reference
   - Setup instructions for each platform
   - Example prompts by use case
   - Troubleshooting

2. **[Getting Started MCP](../GETTING-STARTED-MCP.md)** — Quick 5-minute setup guide
   - Clone and install
   - Configure Claude Desktop
   - First generation

### For Developers & Platform Engineers

**Start here if you want to extend, customize, or integrate skills:**

1. **[Skills Architecture](SKILLS-ARCHITECTURE.md)** — Technical deep dive into skill design
   - Architecture layers (definitions, gateway, generators)
   - Skill lifecycle (definition → implementation → integration → deployment)
   - Data flow and integration points
   - How to add new skills step-by-step

2. **[Skills Developer Guide](SKILLS-DEVELOPER-GUIDE.md)** — Practical patterns for extending skills
   - How to extend existing skills
   - How to create completely new skills  
   - Integration patterns (skill chaining, programmatic invocation)
   - Testing strategies
   - Deployment methods
   - Performance optimization

### For Architects & Decision Makers

**Start here if you're evaluating DevOps-OS for your organization:**

1. **[Process-First Philosophy](../docs/PROCESS-FIRST.md)** — Why DevOps-OS works and how it teaches best practices
   - The 5 core principles
   - How each skill encodes Process-First thinking
   - Cultural benefits of skill-based automation

2. **[MCP Setup Guide](../mcp_server/README.md)** — Production deployment options
   - Multiple setup methods (CLI, Desktop, IDE, Docker)
   - HTTP/HTTPS with authentication
   - Scaling and security considerations

---

## 📖 Full Documentation Map

### Core Documentation Files

```
devops_os_mcp/
├── GETTING-STARTED-MCP.md          ← Quick 5-minute start
├── README.md                        ← Project overview
├── PROMPT_SUGGESTIONS.md            ← AI prompt examples
│
├── skills/
│   ├── README.md                    ← [DEPRECATED: See SKILLS-USAGE-GUIDE.md]
│   ├── claude_tools.json            ← Claude skill definitions
│   └── openai_functions.json        ← OpenAI skill definitions
│
├── mcp_server/
│   └── README.md                    ← MCP server setup & deployment
│
└── docs/
    ├── SKILLS-USAGE-GUIDE.md        ← Using skills (MAIN REFERENCE)
    ├── SKILLS-ARCHITECTURE.md       ← Technical architecture (MAIN REFERENCE)
    ├── SKILLS-DEVELOPER-GUIDE.md    ← Extending skills (MAIN REFERENCE)
    ├── PROCESS-FIRST.md             ← Philosophy & principles
    ├── GITHUB-ACTIONS-README.md     ← GitHub Actions generator details
    ├── GITLAB-CI-README.md          ← GitLab CI generator details
    ├── JENKINS-PIPELINE-README.md   ← Jenkins generator details
    ├── ARGOCD-README.md             ← GitOps generators
    ├── SRE-CONFIGURATION-README.md  ← Observability generators
    └── ... more specialized guides
```

---

## 🎯 Skills Reference

### All Available Skills

| Skill | Purpose | Documentation | Complexity |
|-------|---------|-----------------|-----------|
| **generate_github_actions_workflow** | CI/CD for GitHub | [Guide](SKILLS-USAGE-GUIDE.md#github-actions-workflows) | Medium |
| **generate_jenkins_pipeline** | CI/CD for Jenkins | [Guide](SKILLS-USAGE-GUIDE.md#jenkins-pipelines) | Medium |
| **generate_gitlab_ci_pipeline** | CI/CD for GitLab | [Guide](SKILLS-USAGE-GUIDE.md#gitlab-pipelines) | Medium |
| **generate_k8s_config** | Kubernetes manifests | [Guide](SKILLS-USAGE-GUIDE.md#kubernetes-configurations) | Medium |
| **generate_argocd_config** | GitOps with ArgoCD/Flux | [Architecture](SKILLS-ARCHITECTURE.md#core-skills-v047) | Advanced |
| **generate_sre_configs** | Observability & alerting | [Guide](SKILLS-USAGE-GUIDE.md#sre-observability) | Advanced |
| **scaffold_devcontainer** | Dev container setup | [Guide](SKILLS-USAGE-GUIDE.md#development-containers) | Simple |
| **generate_unittest_config** | Unit test scaffolding | [Architecture](SKILLS-ARCHITECTURE.md) | Simple |

---

## 💡 Use Cases & Examples

### Scenario 1: Solo Developer
**Goal:** Add CI/CD to my Python project

1. Read: [Skills Usage Guide → Example Prompts](SKILLS-USAGE-GUIDE.md#example-prompts-by-use-case)
2. Use: Claude Desktop + `generate_github_actions_workflow` skill
3. Result: Production-ready GitHub Actions workflow

**Time:** 5 minutes

---

### Scenario 2: DevOps Team Lead
**Goal:** Standardize CI/CD across 10 teams

1. Read: [Skills Architecture → Skill Design Best Practices](SKILLS-ARCHITECTURE.md#best-practices)
2. Plan: How to extend skills for your organization
3. Implement: Create custom skills using [Developer Guide](SKILLS-DEVELOPER-GUIDE.md#creating-a-completely-new-skill)
4. Deploy: Use Docker or MCP server HTTP endpoint
5. Train: Point teams to [Skills Usage Guide](SKILLS-USAGE-GUIDE.md#prompt-writing-tips)

**Time:** 2-3 days

---

### Scenario 3: Platform Engineer
**Goal:** Add Terraform IaC generation to DevOps-OS

1. Read: [Skills Developer Guide → Custom Skill Development](SKILLS-DEVELOPER-GUIDE.md#custom-skill-development)
2. Code: Create `TerraformGenerator` class
3. Test: Write unit and integration tests
4. Integrate: Add to MCP server and skill definitions
5. Deploy: Version bump and release

**Time:** 1-2 days

---

### Scenario 4: AI/ML Engineer
**Goal:** Integrate DevOps-OS skills into custom LLM application

1. Read: [Skills Architecture → Integration Points](SKILLS-ARCHITECTURE.md#integration-points)
2. Choose: Integration method (direct invocation, API, MCP)
3. Implement: Skill chaining patterns from [Developer Guide](SKILLS-DEVELOPER-GUIDE.md#integration-patterns)
4. Deploy: Use generated configs in your workflows

**Time:** 1 day

---

## 🔍 Finding Answers

### Common Questions

**Q: How do I use skills with Claude Desktop?**
→ See [Skills Usage Guide § Claude Desktop](SKILLS-USAGE-GUIDE.md#method-1-claude-desktop-recommended)

**Q: How do I extend an existing skill?**
→ See [Skills Developer Guide § Extending Skills](SKILLS-DEVELOPER-GUIDE.md#extending-skills)

**Q: What's the technical architecture behind skills?**
→ See [Skills Architecture § Architecture Layers](SKILLS-ARCHITECTURE.md#architecture-layers)

**Q: How do I create a completely new skill?**
→ See [Skills Developer Guide § Custom Skill Development](SKILLS-DEVELOPER-GUIDE.md#custom-skill-development)

**Q: How should I prompt Claude for better results?**
→ See [Skills Usage Guide § Prompt Writing Tips](SKILLS-USAGE-GUIDE.md#prompt-writing-tips)

**Q: How do I validate generated configurations?**
→ See [Skills Usage Guide § Output Validation](SKILLS-USAGE-GUIDE.md#validating-output)

**Q: How do I deploy the MCP server to production?**
→ See [MCP Server README § Production Deployment](../mcp_server/README.md#production-deployment)

**Q: How can I integrate skills into my Python application?**
→ See [Skills Developer Guide § Integration Patterns](SKILLS-DEVELOPER-GUIDE.md#integration-patterns)

---

## 📊 Skill Parameters Cheat Sheet

### Most Common Parameters

```python
# CI/CD Skills (GitHub Actions, Jenkins, GitLab)
generate_*_workflow(
    name="my-app",              # Application name
    workflow_type="complete",   # build | test | deploy | complete | reusable
    languages="python",         # python | javascript | java | go | ruby | php
    kubernetes=True,            # Include K8s deployment stage?
    k8s_method="argocd",        # kubectl | kustomize | argocd | flux
    branches="main,develop",    # Trigger branches
    matrix=True,                # Test across versions?
)

# Kubernetes Deployment
generate_k8s_config(
    app_name="my-app",
    image="ghcr.io/org/app:v1",
    replicas=3,
    port=8080,
    namespace="production",
)

# Observability
generate_sre_configs(
    app_name="my-app",
    alert_type="latency,error_rate",
    slo_target=0.999,  # 99.9% SLO
)
```

---

## 🚀 Next Steps

### For First-Time Users
1. Follow [Getting Started MCP](../GETTING-STARTED-MCP.md) (5 minutes)
2. Try first example from [Skills Usage Guide](SKILLS-USAGE-GUIDE.md#example-prompts-by-use-case)
3. Customize for your project

### For Extending DevOps-OS
1. Review [Skills Architecture](SKILLS-ARCHITECTURE.md) overview
2. Study [Skills Developer Guide](SKILLS-DEVELOPER-GUIDE.md)
3. Implement custom skill following step-by-step patterns
4. Submit PR to contribute back!

### For Production Deployment
1. Read [MCP Server README](../mcp_server/README.md#quick-start--which-method-is-right-for-you)
2. Choose deployment method based on your setup
3. Configure authentication and scaling
4. Train teams using [Skills Usage Guide](SKILLS-USAGE-GUIDE.md)

---

## 🤝 Contributing

Want to add a new skill or improve documentation?

1. Fork: [github.com/chefgs/devops_os_mcp](https://github.com/chefgs/devops_os_mcp)
2. Follow: [CONTRIBUTING.md](../CONTRIBUTING.md)
3. Read: [Skills Developer Guide](SKILLS-DEVELOPER-GUIDE.md)
4. Submit: Pull request with implementation, tests, and docs

---

## 📞 Support

- **Questions?** → [GitHub Discussions](https://github.com/chefgs/devops_os_mcp/discussions)
- **Found a bug?** → [GitHub Issues](https://github.com/chefgs/devops_os_mcp/issues)
- **Documentation issue?** → Create an issue with "docs:" prefix
- **Full documentation:** → [devops-os.io](https://devops-os.io/)

---

## 📄 Document Versions

| Document | Version | Last Updated | Audience |
|----------|---------|--------------|----------|
| SKILLS-USAGE-GUIDE.md | 1.0 | Oct 2, 2026 | Users, DevOps Engineers |
| SKILLS-ARCHITECTURE.md | 1.0 | Oct 2, 2026 | Developers, Architects |
| SKILLS-DEVELOPER-GUIDE.md | 1.0 | Oct 2, 2026 | Platform Engineers, Developers |
| SKILLS-DOCUMENTATION-INDEX.md | 1.0 | Oct 2, 2026 | All |

---

**DevOps-OS MCP Version:** 0.4.7  
**Last Updated:** October 2, 2026
