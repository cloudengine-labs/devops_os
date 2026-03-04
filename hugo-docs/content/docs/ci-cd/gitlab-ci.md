---
title: "GitLab CI"
weight: 22
---

# GitLab CI Pipeline Generator

Generate a complete `.gitlab-ci.yml` for your project in a single command. The generator creates multi-stage pipelines with language-specific test jobs, Docker build, and Kubernetes deployment.

---

## Basic Usage

```bash
python -m cli.scaffold_gitlab --name my-app --languages python --type complete
```

**Output:** `.gitlab-ci.yml` (default)  
Change the output path with `--output <path>`.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `my-app` | Application / pipeline name |
| `--type TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` |
| `--languages LANGS` | `python` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | off | Add a Kubernetes deploy stage |
| `--k8s-method METHOD` | `kubectl` | `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output FILE` | `.gitlab-ci.yml` | Output file path |
| `--image IMAGE` | `docker:24` | Default Docker image for pipeline jobs |
| `--branches BRANCHES` | `main` | Branches that trigger deploy jobs |
| `--kube-namespace NS` | _(empty)_ | Kubernetes namespace (empty = use `$KUBE_NAMESPACE` variable) |
| `--custom-values FILE` | _(none)_ | Path to custom values JSON file |

All options can be set via environment variables prefixed `DEVOPS_OS_GITLAB_`.

---

## Generated Pipeline Stages

### `build` stage

- Logs in to the GitLab Container Registry
- Runs language-specific compile / install steps (detected from project files)
- Builds and pushes a Docker image tagged with `$CI_COMMIT_SHORT_SHA` and `latest`

### `test` stage

| Language | Image | Test command |
|----------|-------|-------------|
| Python | `python:3.11-slim` | `pytest --cov` |
| Java | `maven:3.9-eclipse-temurin-17` | `mvn test` / `gradle test` |
| JavaScript | `node:20-slim` | `npm test` |
| Go | `golang:1.21` | `go test ./...` |

Each test job uploads JUnit / coverage artifacts automatically.

### `deploy` stage (requires `--kubernetes`)

| Method | What happens |
|--------|-------------|
| `kubectl` | `kubectl set image` + rollout status check |
| `kustomize` | `kustomize edit set image` + `kubectl apply` |
| `argocd` | `argocd app set` + sync + wait |
| `flux` | `flux reconcile image repository` + kustomization |

---

## Examples

### Python + Docker + kubectl deploy

```bash
python -m cli.scaffold_gitlab \
  --name flask-api \
  --languages python \
  --type complete \
  --kubernetes \
  --k8s-method kubectl \
  --branches main,production
# Output: .gitlab-ci.yml
```

Generated stages:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  APP_NAME: flask-api
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA

build:
  stage: build
  image: docker:24
  script:
    - docker login $CI_REGISTRY ...
    - docker build -t $CI_REGISTRY_IMAGE:$IMAGE_TAG .
    - docker push $CI_REGISTRY_IMAGE:$IMAGE_TAG

test:python:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - pytest --cov=./ --cov-report=xml -v

deploy:kubernetes:
  stage: deploy
  image: bitnami/kubectl:1.29
  script:
    - kubectl set image deployment/flask-api app=$CI_REGISTRY_IMAGE:$IMAGE_TAG
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

### Java build + test (no deploy)

```bash
python -m cli.scaffold_gitlab --name java-api --languages java --type test
# Output: .gitlab-ci.yml
```

### Multi-language with ArgoCD deploy

```bash
python -m cli.scaffold_gitlab \
  --name my-app \
  --languages python,go \
  --kubernetes --k8s-method argocd
# Output: .gitlab-ci.yml
```

---

## Environment Variables

```bash
export DEVOPS_OS_GITLAB_NAME=my-app
export DEVOPS_OS_GITLAB_TYPE=complete
export DEVOPS_OS_GITLAB_LANGUAGES=python,javascript
export DEVOPS_OS_GITLAB_KUBERNETES=true
export DEVOPS_OS_GITLAB_K8S_METHOD=kustomize

python -m cli.scaffold_gitlab
# Output: .gitlab-ci.yml
```

---

## Required GitLab CI/CD Variables

Set these in **GitLab → Settings → CI/CD → Variables**:

| Variable | Description |
|----------|-------------|
| `CI_REGISTRY_USER` | GitLab registry username (auto-set for GitLab) |
| `CI_REGISTRY_PASSWORD` | GitLab registry password (auto-set for GitLab) |
| `KUBE_CONTEXT` | kubectl context name |
| `KUBE_NAMESPACE` | Target Kubernetes namespace |
| `ARGOCD_SERVER` | ArgoCD server hostname (if using ArgoCD) |
| `ARGOCD_TOKEN` | ArgoCD API token (if using ArgoCD) |
