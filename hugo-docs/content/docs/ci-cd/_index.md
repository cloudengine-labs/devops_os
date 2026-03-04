---
title: "CI/CD Generators"
weight: 20
bookCollapseSection: true
---

# CI/CD Generators

DevOps-OS provides one-command scaffolding for three major CI/CD platforms:

| Platform | Description | Guide |
|----------|-------------|-------|
| ⚙️ **GitHub Actions** | Generate complete GitHub Actions workflow YAML files with build, test, deploy, and reusable workflow types. | [GitHub Actions →]({{< relref "/docs/ci-cd/github-actions" >}}) |
| 🦊 **GitLab CI** | Generate `.gitlab-ci.yml` pipelines with multi-stage jobs, Docker build, Kubernetes deploy, and language-specific test jobs. | [GitLab CI →]({{< relref "/docs/ci-cd/gitlab-ci" >}}) |
| 🔧 **Jenkins** | Generate Jenkinsfiles using the declarative pipeline syntax, with parameterized builds and Kubernetes deployment support. | [Jenkins →]({{< relref "/docs/ci-cd/jenkins" >}}) |

---

## All three generators share the same conventions

- **Language selection:** `--languages python,java,javascript,go`
- **Kubernetes deploy:** `--kubernetes --k8s-method [kubectl|kustomize|argocd|flux]`
- **Custom overrides:** `--custom-values path/to/values.json`
- **Environment variables:** Every flag has a `DEVOPS_OS_<CMD>_*` env-var alternative for CI/CD usage
- **Output control:** `--output` (file path) or `--output-dir` (directory)

See [CLI Reference]({{< relref "/docs/reference" >}}) for complete option tables.
