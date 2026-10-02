---
title: "Language-Specific Setup Guides"
weight: 62
---

# Language-Specific Dev Container Guides

Comprehensive setup guides for each supported programming language in the DevOps-OS dev container.

---

## Python

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages python \
  --python-version 3.12 \
  --build-tools make \
  --code-analysis-tools pylint,sonarqube
```

### Recommended Configuration

```json
{
  "languages": {
    "python": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true
  },
  "build_tools": {
    "make": true
  },
  "code_analysis": {
    "pylint": true,
    "sonarqube": true
  }
}
```

### Included Tools

- **Runtime**: Python 3.12 (configurable)
- **Package Manager**: pip, poetry (optional)
- **Testing**: pytest with coverage
- **Linting**: pylint, black, isort
- **IDE**: VS Code with Python extension, Pylance

### Common Workflows

```bash
# Create a FastAPI + async development environment
python -m devops_os.core.scaffold_devcontainer \
  --languages python \
  --cicd-tools docker,github_actions \
  --code-analysis-tools pylint \
  --build-tools make

# Data science with Python
python -m devops_os.core.scaffold_devcontainer \
  --languages python \
  --python-version 3.12 \
  --build-tools make
```

---

## JavaScript / Node.js

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages javascript,node \
  --node-version 22 \
  --build-tools make \
  --code-analysis-tools eslint
```

### Recommended Configuration

```json
{
  "languages": {
    "javascript": true,
    "node": true,
    "typescript": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true
  },
  "code_analysis": {
    "eslint": true
  }
}
```

### Included Tools

- **Runtime**: Node.js 22 (configurable)
- **Package Manager**: npm, yarn
- **Testing**: Jest, Mocha, Vitest
- **Linting**: ESLint, Prettier
- **IDE**: VS Code with ESLint, Prettier extensions

### Common Workflows

```bash
# React + TypeScript development
python -m devops_os.core.scaffold_devcontainer \
  --languages javascript,typescript,node \
  --cicd-tools docker,github_actions \
  --code-analysis-tools eslint

# Full-stack application (Node.js + React)
python -m devops_os.core.scaffold_devcontainer \
  --languages javascript,typescript,node \
  --cicd-tools docker,github_actions,terraform \
  --kubernetes-tools kubectl,helm,k9s
```

---

## Go

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages go \
  --go-version 1.25.0 \
  --cicd-tools docker,github_actions
```

### Recommended Configuration

```json
{
  "languages": {
    "go": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true,
    "terraform": true
  },
  "kubernetes": {
    "kubectl": true,
    "helm": true
  }
}
```

### Included Tools

- **Runtime**: Go 1.25.0 (configurable)
- **Package Manager**: Go modules
- **Testing**: go test, testify
- **Build**: go build, goreleaser
- **IDE**: VS Code with Go extension, delve debugger

### Common Workflows

```bash
# Microservice development with Kubernetes
python -m devops_os.core.scaffold_devcontainer \
  --languages go \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli

# CLI tool development
python -m devops_os.core.scaffold_devcontainer \
  --languages go \
  --cicd-tools docker,github_actions
```

---

## Java

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages java \
  --java-version 21 \
  --build-tools maven,gradle
```

### Recommended Configuration

```json
{
  "languages": {
    "java": true
  },
  "cicd": {
    "docker": true,
    "jenkins": true,
    "github_actions": true
  },
  "build_tools": {
    "maven": true,
    "gradle": true
  }
}
```

### Included Tools

- **Runtime**: OpenJDK 21 (configurable)
- **Build**: Maven 3.9+, Gradle 8.4+
- **Testing**: JUnit 5, Testcontainers
- **IDE**: VS Code with Java Pack, Maven, Gradle extensions
- **Debugging**: Remote debugging support

### Common Workflows

```bash
# Spring Boot microservice
python -m devops_os.core.scaffold_devcontainer \
  --languages java \
  --java-version 21 \
  --build-tools maven \
  --cicd-tools docker,github_actions,kubernetes

# Enterprise application with Jenkins
python -m devops_os.core.scaffold_devcontainer \
  --languages java \
  --java-version 21 \
  --build-tools gradle \
  --cicd-tools docker,jenkins
```

---

## Rust

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages rust \
  --rust-version latest
```

### Recommended Configuration

```json
{
  "languages": {
    "rust": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true
  }
}
```

### Included Tools

- **Runtime**: Rust (latest toolchain)
- **Package Manager**: Cargo
- **Testing**: cargo test
- **Toolchain**: rustup, cargo-fmt, cargo-clippy
- **IDE**: VS Code with rust-analyzer

### Common Workflows

```bash
# System programming with Kubernetes integration
python -m devops_os.core.scaffold_devcontainer \
  --languages rust \
  --cicd-tools docker,github_actions \
  --kubernetes-tools kubectl,helm

# CLI tool development
python -m devops_os.core.scaffold_devcontainer \
  --languages rust \
  --cicd-tools docker,github_actions
```

---

## Ruby

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages ruby \
  --ruby-version 3.3
```

### Recommended Configuration

```json
{
  "languages": {
    "ruby": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true
  }
}
```

### Included Tools

- **Runtime**: Ruby 3.3 (configurable)
- **Package Manager**: Bundler, RubyGems
- **Testing**: RSpec, Minitest
- **Web Frameworks**: Rails, Sinatra, Hanami
- **IDE**: VS Code with Ruby extension

---

## C / C++

### Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages c,cpp \
  --build-tools cmake,make
```

### Recommended Configuration

```json
{
  "languages": {
    "c": true,
    "cpp": true
  },
  "build_tools": {
    "cmake": true,
    "make": true
  },
  "cicd": {
    "docker": true,
    "github_actions": true
  }
}
```

### Included Tools

- **Compilers**: GCC, Clang
- **Build**: CMake, Make
- **Testing**: Google Test (GTest), Catch2
- **Debugging**: GDB, LLDB
- **IDE**: VS Code with C++ Tools, CMake Tools

### Common Workflows

```bash
# System programming with containers
python -m devops_os.core.scaffold_devcontainer \
  --languages c,cpp \
  --build-tools cmake \
  --cicd-tools docker,github_actions

# Embedded systems development
python -m devops_os.core.scaffold_devcontainer \
  --languages c \
  --build-tools cmake,make
```

---

## Multi-Language Projects

### Full-Stack Application (Backend + Frontend)

```bash
# Python backend + React frontend
python -m devops_os.core.scaffold_devcontainer \
  --languages python,javascript,typescript,node \
  --cicd-tools docker,github_actions,terraform \
  --kubernetes-tools kubectl,helm,k9s \
  --devops-tools prometheus,grafana
```

### Microservices Architecture

```bash
# Go services + Python automation + TypeScript admin dashboard
python -m devops_os.core.scaffold_devcontainer \
  --languages go,python,typescript,node \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli,flux \
  --devops-tools prometheus,grafana,elk
```

### Legacy System Modernization

```bash
# Java legacy + Go new services + Python scripts
python -m devops_os.core.scaffold_devcontainer \
  --languages java,go,python \
  --build-tools maven,gradle,make \
  --cicd-tools docker,jenkins,github_actions \
  --kubernetes-tools kubectl,helm
```

---

## Environment Variables

All configuration can be set via environment variables for CI/CD integration:

```bash
export DEVOPS_OS_DEVCONTAINER_LANGUAGES=python,go
export DEVOPS_OS_DEVCONTAINER_CICD_TOOLS=docker,github_actions
export DEVOPS_OS_DEVCONTAINER_PYTHON_VERSION=3.12
export DEVOPS_OS_DEVCONTAINER_GO_VERSION=1.25.0

python -m devops_os.core.scaffold_devcontainer
```

---

## Best Practices

1. **Use version pinning** for reproducible environments
2. **Include build tools** that your project needs
3. **Enable code analysis** for quality gates
4. **Add DevOps tools** for local testing of infrastructure
5. **Mount Docker socket** for container operations
6. **Forward ports** for services you're developing or testing
7. **Use environment variables** for CI/CD automation

---

## Troubleshooting

### "Tool X not found in container"

Ensure the tool is enabled in `devcontainer.env.json` and rebuild:

```bash
# Edit .devcontainer/devcontainer.env.json to set tool to true
# Then rebuild
code . # Open in VS Code
# Run: Dev Containers: Rebuild Container
```

### Port already in use

If a forwarded port is already in use on your host, either:

1. Stop the conflicting service
2. Modify the port mapping in `devcontainer.json`
3. Use a different `.devcontainer/` directory for different projects

### Docker socket permission denied

Ensure Docker socket is properly mounted. Check your `devcontainer.json`:

```json
{
  "mounts": ["source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"]
}
```

---

## See Also

- [Dev Container Setup](./index.md) - Main CLI guide
- [MCP Dev Container Module](./mcp-setup.md) - AI assistant integration
- [Getting Started](../getting-started/) - Quick start guides
