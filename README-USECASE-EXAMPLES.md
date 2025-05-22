# DevOps-OS Use Case Examples

This document provides practical examples and advanced use cases for each major functionality in the DevOps-OS repository.

---

## 1. Multi-Language Development Container

### Use Cases
- **Polyglot Microservices**: Develop and test services in Python, Java, Go, and JavaScript/TypeScript within a single, consistent environment.
- **Onboarding**: New team members can start coding immediately with all tools pre-installed.
- **Version Pinning**: Ensure all developers use the same versions of compilers, linters, and CI/CD tools.

### Example: Adding a New Language
Edit `.devcontainer/devcontainer.env.json` to enable Ruby support:
```json
{
  "languages": {
    "python": true,
    "java": true,
    "javascript": true,
    "go": true,
    "ruby": true
  }
}
```

---

## 2. CI/CD Generator Tools

### Use Cases
- **Rapid Pipeline Creation**: Instantly generate GitHub Actions or Jenkins pipelines for new projects.
- **Multi-Stack CI/CD**: Create pipelines for projects using multiple languages or frameworks.
- **Kubernetes Deployment**: Generate manifests and deployment scripts for cloud-native applications.

### Example: Generate a GitHub Actions Workflow
```bash
python3 .devcontainer/github-actions-generator-improved.py --language python --test pytest --docker true
```

---

## 3. Kubernetes Tools

### Use Cases
- **Local Cluster Management**: Use KinD or Minikube to spin up test clusters.
- **GitOps**: Deploy with ArgoCD CLI or Flux for continuous delivery.
- **Secret Management**: Use Kubeseal to manage encrypted secrets in Git.

### Example: Sealing a Secret
```bash
kubectl create secret generic mysecret --from-literal=password=supersecret --dry-run=client -o yaml | kubeseal --cert mycert.pem -o yaml > sealedsecret.yaml
```

---

## 4. Customization and Extensibility

### Use Cases
- **Add New Tools**: Edit the Dockerfile to install additional CLI tools or SDKs.
- **Change Tool Versions**: Update the `versions` section in `devcontainer.env.json` to pin or upgrade tool versions.

### Example: Add AWS CLI
Edit the Dockerfile:
```dockerfile
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo ./aws/install
```

---

## 5. Advanced CI/CD Scenarios

### Use Cases
- **Matrix Builds**: Test across multiple language versions using GitHub Actions matrix strategy.
- **Multi-Environment Deployments**: Generate separate pipelines for dev, staging, and prod.

### Example: Matrix Build in GitHub Actions
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest
```

---

For more detailed examples, see the individual guides listed in the main `README.md`.
