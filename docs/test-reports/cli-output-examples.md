# DevOps-OS CLI Output Examples

This document captures real CLI output from the DevOps-OS scaffold commands, serving as a visual reference for what each command produces.

---

## Table of Contents

- [devopsos --help](#devopsos---help)
- [devopsos scaffold --help](#devopsos-scaffold---help)
- [scaffold gitlab](#scaffold-gitlab)
- [scaffold gha (GitHub Actions)](#scaffold-gha-github-actions)
- [scaffold argocd](#scaffold-argocd)
- [scaffold sre](#scaffold-sre)
- [scaffold jenkins](#scaffold-jenkins)
- [Error Handling](#error-handling)

---

## `devopsos --help`

```
$ python -m cli.devopsos --help

 Usage: python -m cli.devopsos [OPTIONS] COMMAND [ARGS]...

 Unified DevOps-OS CLI tool

╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --install-completion   Install completion for the current shell.          │
│ --show-completion      Show completion for the current shell.             │
│ --help                 Show this message and exit.                        │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ init       Interactive project initializer.                               │
│ scaffold   Scaffold CI/CD or K8s resources.                               │
╰───────────────────────────────────────────────────────────────────────────╯
```

---

## `devopsos scaffold --help`

```
$ python -m cli.devopsos scaffold --help

 Usage: python -m cli.devopsos scaffold [OPTIONS] TARGET

 Scaffold CI/CD or K8s resources.

╭─ Arguments ────────────────────────────────────────────────────────────────╮
│ *    target   TEXT  What to scaffold: cicd | gha | gitlab | jenkins |      │
│                     argocd | sre [required]                                │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --tool   TEXT  Tool type (e.g., github, jenkins, argo, flux)               │
│ --help         Show this message and exit.                                 │
╰────────────────────────────────────────────────────────────────────────────╯
```

---

## scaffold gitlab

### Build pipeline — single language

**Command:**
```bash
python -m cli.scaffold_gitlab \
  --name myapp \
  --type build \
  --languages python \
  --output .gitlab-ci.yml
```

**CLI output:**
```
GitLab CI pipeline generated: .gitlab-ci.yml
Type: build
Languages: python
```

**Generated `.gitlab-ci.yml`:**
```yaml
stages:
- build
variables:
  APP_NAME: myapp
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA
  REGISTRY: $CI_REGISTRY
  REGISTRY_IMAGE: $CI_REGISTRY_IMAGE
build:
  stage: build
  image: docker:24
  services:
  - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: /certs
  script:
  - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  - if [ -f setup.py ] || [ -f pyproject.toml ]; then pip install -e .; fi
  - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  - docker build -t $REGISTRY_IMAGE:$IMAGE_TAG .
  - docker push $REGISTRY_IMAGE:$IMAGE_TAG
  - docker tag $REGISTRY_IMAGE:$IMAGE_TAG $REGISTRY_IMAGE:latest
  - docker push $REGISTRY_IMAGE:latest
  rules:
  - if: $CI_COMMIT_BRANCH
    when: always
```

---

### Complete pipeline — multiple languages + Kubernetes

**Command:**
```bash
python -m cli.scaffold_gitlab \
  --name api \
  --type complete \
  --languages python,go \
  --kubernetes \
  --k8s-method kubectl \
  --output .gitlab-ci.yml
```

**CLI output:**
```
GitLab CI pipeline generated: .gitlab-ci.yml
Type: complete
Languages: python,go
Kubernetes deployment method: kubectl
```

**Generated `.gitlab-ci.yml`:**
```yaml
stages:
- build
- test
- deploy
variables:
  APP_NAME: api
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA
  REGISTRY: $CI_REGISTRY
  REGISTRY_IMAGE: $CI_REGISTRY_IMAGE
build:
  stage: build
  image: docker:24
  services:
  - docker:24-dind
  script:
  - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  - if [ -f setup.py ] || [ -f pyproject.toml ]; then pip install -e .; fi
  - if [ -f go.mod ]; then go build -v ./...; fi
  - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  - docker build -t $REGISTRY_IMAGE:$IMAGE_TAG .
  - docker push $REGISTRY_IMAGE:$IMAGE_TAG
  rules:
  - if: $CI_COMMIT_BRANCH
    when: always
test:python:
  stage: test
  image: python:3.11-slim
  script:
  - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  - pip install pytest pytest-cov
  - if [ -d tests ] || [ -d test ]; then python -m pytest --cov=./ --cov-report=xml -v; fi
  coverage: /TOTAL.*\s+(\d+%)$/
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  rules:
  - if: $CI_COMMIT_BRANCH
    when: always
  - if: $CI_MERGE_REQUEST_ID
    when: always
test:go:
  stage: test
  image: golang:1.21
  script:
  - if [ -f go.mod ]; then go test -v -coverprofile=coverage.out ./...; fi
  - if [ -f coverage.out ]; then go tool cover -func=coverage.out; fi
  rules:
  - if: $CI_COMMIT_BRANCH
    when: always
  - if: $CI_MERGE_REQUEST_ID
    when: always
deploy:kubernetes:
  stage: deploy
  image: bitnami/kubectl:1.29
  environment:
    name: $CI_COMMIT_BRANCH
    url: https://$APP_NAME.$KUBE_NAMESPACE.example.com
  script:
  - kubectl config use-context $KUBE_CONTEXT
  - kubectl set image deployment/$APP_NAME $APP_NAME=$REGISTRY_IMAGE:$IMAGE_TAG --namespace=$KUBE_NAMESPACE
  - kubectl rollout status deployment/$APP_NAME --namespace=$KUBE_NAMESPACE
  rules:
  - if: $CI_COMMIT_BRANCH == "main"
    when: on_success
```

---

## scaffold gha (GitHub Actions)

### Complete workflow — Python + Java + ArgoCD deploy

**Command:**
```bash
python -m cli.scaffold_gha \
  --name my-workflow \
  --type complete \
  --languages python,java \
  --kubernetes \
  --k8s-method argocd \
  --output .github/workflows/
```

**CLI output:**
```
GitHub Actions workflow generated: .github/workflows/my-workflow-complete.yml
Type: complete
Languages: python,java
Kubernetes deployment method: argocd
```

**Generated `my-workflow-complete.yml` (excerpt):**
```yaml
name: my-workflow CI/CD
'on':
  push:
    branches:
    - main
  pull_request:
    branches:
    - main
  workflow_dispatch:
    inputs:
      environment:
        description: Environment to deploy to
        required: true
        default: dev
        type: choice
        options:
        - dev
        - test
        - staging
        - prod
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourorg/devops-os:latest
      options: --user root
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    - name: Install Python dependencies
      run: if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Build Python package
      run: if [ -f setup.py ]; then pip install -e .; elif [ -f pyproject.toml ]; then pip install -e .; fi
    - name: Build with Maven
      run: if [ -f pom.xml ]; then mvn -B package --file pom.xml; fi
    - name: Build with Gradle
      run: if [ -f build.gradle ]; then ./gradlew build; fi
  test:
    needs: [build]
    runs-on: ubuntu-latest
    steps:
    - name: Run Python tests
      run: if [ -d tests ]; then python -m pytest --cov=./ --cov-report=xml; fi
    - name: Run Java tests with Maven
      run: if [ -f pom.xml ]; then mvn -B test --file pom.xml; fi
  deploy:
    needs: [test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy with ArgoCD
      run: |
        argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure
        argocd app sync my-application
        argocd app wait my-application --health
      env:
        ARGOCD_SERVER: ${{ secrets.ARGOCD_SERVER }}
        ARGOCD_USERNAME: ${{ secrets.ARGOCD_USERNAME }}
        ARGOCD_PASSWORD: ${{ secrets.ARGOCD_PASSWORD }}
```

---

## scaffold argocd

### ArgoCD Application + AppProject

**Command:**
```bash
python -m cli.scaffold_argocd \
  --name my-app \
  --repo https://github.com/myorg/my-app.git \
  --project team-a \
  --output-dir ./gitops/
```

**CLI output:**
```
GitOps configs generated (argocd):
  ./gitops/argocd/application.yaml
  ./gitops/argocd/appproject.yaml
```

**Generated `argocd/application.yaml`:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  labels:
    app.kubernetes.io/name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/my-app.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    syncOptions:
    - CreateNamespace=true
```

**Generated `argocd/appproject.yaml`:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-a
  namespace: argocd
spec:
  description: Project for my-app deployments
  sourceRepos:
  - https://github.com/myorg/my-app.git
  destinations:
  - namespace: default
    server: https://kubernetes.default.svc
  - namespace: argocd
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: '*'
    kind: Namespace
  namespaceResourceWhitelist:
  - group: apps
    kind: Deployment
  - group: apps
    kind: StatefulSet
  - group: ''
    kind: Service
  - group: ''
    kind: ConfigMap
  - group: ''
    kind: Secret
  - group: networking.k8s.io
    kind: Ingress
```

### Flux Kustomization

**Command:**
```bash
python -m cli.scaffold_argocd \
  --name my-app \
  --method flux \
  --repo https://github.com/myorg/my-app.git \
  --output-dir ./gitops/
```

**CLI output:**
```
GitOps configs generated (flux):
  ./gitops/flux/gitrepository.yaml
  ./gitops/flux/kustomization.yaml
```

---

## scaffold sre

### Availability SLO with Prometheus alert rules

**Command:**
```bash
python -m cli.scaffold_sre \
  --name payment-svc \
  --team payments \
  --slo-type availability \
  --slo-target 99.9 \
  --output-dir ./sre/
```

**CLI output:**
```
SRE configs generated:
  ./sre/alert-rules.yaml
  ./sre/grafana-dashboard.json
  ./sre/slo.yaml
  ./sre/alertmanager-config.yaml
```

**Generated `alert-rules.yaml` (excerpt):**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: payment-svc-sre-rules
  namespace: default
  labels:
    app: payment-svc
    team: payments
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: payment-svc.availability
    interval: 30s
    rules:
    - alert: Payment_SvcHighErrorRate
      expr: rate(http_requests_total{job="payment-svc",status=~"5.."}[5m])
             / rate(http_requests_total{job="payment-svc"}[5m]) > 0.001
      for: 5m
      labels:
        severity: critical
        team: payments
        slo: availability
      annotations:
        summary: High error rate on payment-svc
        description: >
          Error rate for payment-svc is above 0.1% (SLO target 99.9%).
          Current value: {{ $value | humanizePercentage }}
        runbook_url: https://wiki.example.com/runbooks/payment-svc/high-error-rate
    - alert: Payment_SvcSLOBurnRate
      expr: >
        (rate(http_requests_total{job="payment-svc",status=~"5.."}[1h])
          / rate(http_requests_total{job="payment-svc"}[1h]))
          > 14400.0 * 0.001
      for: 2m
      labels:
        severity: critical
        slo: error-budget
```

**Generated `slo.yaml`:**
```yaml
version: prometheus/v1
service: payment-svc
labels:
  owner: payments
  repo: https://github.com/myorg/payment-svc
slos:
- name: availability
  description: "payment-svc availability SLO — 99.9% of requests succeed"
  objective: 99.9
  sli:
    events:
      error_query: rate(http_requests_total{job="payment-svc",status=~"(5..)"}[{{.window}}])
      total_query: rate(http_requests_total{job="payment-svc"}[{{.window}}])
  alerting:
    name: Payment-SvcAvailabilitySLO
    labels:
      team: payments
    page_alert:
      labels:
        severity: critical
    ticket_alert:
      labels:
        severity: warning
```

---

## scaffold jenkins

### Complete Jenkins pipeline — Python + kubectl deploy

**Command:**
```bash
python -m cli.scaffold_jenkins \
  --name my-pipeline \
  --type complete \
  --languages python \
  --kubernetes \
  --k8s-method kubectl \
  --output Jenkinsfile
```

**CLI output:**
```
Jenkins pipeline generated: Jenkinsfile
Type: complete
Languages: python
Kubernetes deployment method: kubectl
```

**Generated `Jenkinsfile` (excerpt):**
```groovy
pipeline {
    agent {
        docker {
            image 'docker.io/yourorg/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    environment {
        REGISTRY_URL  = params.REGISTRY_URL  ?: 'docker.io'
        IMAGE_NAME    = params.IMAGE_NAME    ?: 'devops-os-app'
        IMAGE_TAG     = params.IMAGE_TAG     ?: 'latest'
        PYTHON_ENABLED = params.PYTHON_ENABLED ?: true
        K8S_METHOD    = params.K8S_METHOD    ?: 'kubectl'
    }
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -d tests ]; then
                        python -m pytest --cov=./ --cov-report=xml
                    fi
                '''
                junit '**/test-results/*.xml', allowEmptyResults: true
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    kubectl set image deployment/$APP_NAME \
                      $APP_NAME=$REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG \
                      --namespace=$KUBE_NAMESPACE
                    kubectl rollout status deployment/$APP_NAME \
                      --namespace=$KUBE_NAMESPACE
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
```

---

## Error Handling

### Unknown scaffold target

**Command:**
```bash
python -m cli.devopsos scaffold unknown
```

**CLI output:**
```
Unknown scaffold target.
```

---

## Test Suite Summary

The full test suite covers all scaffold commands. Run it with:

```bash
pip install -r cli/requirements.txt -r mcp_server/requirements.txt pytest pytest-html
python -m pytest cli/test_cli.py mcp_server/test_server.py tests/test_comprehensive.py \
  -v --html=docs/test-reports/test-report.html --self-contained-html
```

**Latest results:**

| Test File | Passed | Xfailed | Failed |
|-----------|-------:|--------:|-------:|
| `cli/test_cli.py` | 15 | 0 | 0 |
| `mcp_server/test_server.py` | 20 | 0 | 0 |
| `tests/test_comprehensive.py` | 127 | 3 | 0 |
| **Total** | **162** | **3** | **0** |

The 3 `xfail` tests are intentional — they document known bugs tracked for future fixes:

| Test | Bug |
|------|-----|
| `test_deploy_pipeline_no_kubernetes_empty_stages` | `scaffold_gitlab.py` produces empty `stages: []` when `type=deploy` and `kubernetes=False` |
| `test_slo_manifest_error_rate_bug` | `scaffold_sre.py` produces empty `slos: []` when `slo_type=error_rate` |
| `test_allow_any_source_repo_not_available_in_mcp` | MCP server `generate_argocd_config()` does not expose `allow_any_source_repo` parameter |

> The interactive HTML test report is at [`docs/test-reports/test-report.html`](test-report.html).
