# Using DevOps-OS in GitHub Actions and Jenkins Pipelines

Let's discuss how you could leverage your DevOps-OS development container in both GitHub Actions and Jenkins pipelines for CI/CD workflows.

## Creating the DevOps-OS Repository

First, let's create a GitHub repository for your DevOps-OS:

1. Create a new repository on GitHub named "devops-os"
2. Structure it like this:
```
   devops-os/
   ├── .devcontainer/
   │   ├── Dockerfile
   │   ├── devcontainer.json
   │   ├── devcontainer.env.json
   │   ├── configure.py
   │   └── README.md
   ├── .github/
   │   └── workflows/
   │       └── example-pipeline.yml
   ├── jenkins/
   │   └── Jenkinsfile
   └── README.md
```

## Using DevOps-OS in GitHub Actions

### 1. Creating a Reusable GitHub Actions Workflow

You can create a reusable workflow that leverages your DevOps-OS container:

```yaml
# .github/workflows/devops-os-workflow.yml
name: DevOps-OS Reusable Workflow

on:
  workflow_call:
    inputs:
      languages:
        type: string
        default: '{"python": true, "java": true, "javascript": true, "go": true}'
        description: 'JSON string of languages to enable'
      cicd_tools:
        type: string
        default: '{"docker": true, "terraform": true, "kubectl": true}'
        description: 'JSON string of CI/CD tools to enable'
      kubernetes_tools:
        type: string
        default: '{"k9s": true, "kustomize": true, "argocd_cli": true, "flux": true}'
        description: 'JSON string of Kubernetes tools to enable'
      run_tests:
        type: boolean
        default: true
        description: 'Whether to run tests'
      k8s_deploy:
        type: boolean
        default: false
        description: 'Whether to deploy to Kubernetes'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourusername/devops-os:latest
      options: --user root
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure DevOps-OS Environment
        run: |
          mkdir -p /tmp/devops-config
          echo '${{ inputs.languages }}' > /tmp/devops-config/languages.json
          echo '${{ inputs.cicd_tools }}' > /tmp/devops-config/cicd_tools.json
          echo '${{ inputs.kubernetes_tools }}' > /tmp/devops-config/kubernetes_tools.json
          # Configure environment based on inputs
      
      - name: Run Tests
        if: ${{ inputs.run_tests }}
        run: |
          # Run appropriate tests based on the enabled languages/tools
          if [[ $(cat /tmp/devops-config/languages.json | jq '.python') == "true" ]]; then
            python -m pytest
          fi
          if [[ $(cat /tmp/devops-config/languages.json | jq '.java') == "true" ]]; then
            ./gradlew test
          fi
      
      - name: Deploy to Kubernetes
        if: ${{ inputs.k8s_deploy }}
        run: |
          # Setup kubeconfig
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" > $HOME/.kube/config
          chmod 600 $HOME/.kube/config
          
          # Apply Kubernetes manifests
          if [[ $(cat /tmp/devops-config/kubernetes_tools.json | jq '.kustomize') == "true" ]]; then
            kubectl apply -k ./k8s/
          else
            kubectl apply -f ./k8s/deployment.yaml
            kubectl apply -f ./k8s/service.yaml
          fi
          
          # Verify deployment
          kubectl rollout status deployment/my-app
```

### 2. Creating a Base Container for GitHub Actions

Add a GitHub Action to build and publish your DevOps-OS container to GitHub Container Registry:

```yaml
# .github/workflows/build-devops-os.yml
name: Build DevOps-OS Container

on:
  push:
    branches: [ main ]
    paths:
      - '.devcontainer/**'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Generate devcontainer.json
        run: |
          cd .devcontainer
          python configure.py
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push container
        uses: docker/build-push-action@v4
        with:
          context: .devcontainer
          push: true
          tags: ghcr.io/${{ github.repository }}/devops-os:latest
```

### 3. Using the DevOps-OS in a Project

In any project that needs the DevOps-OS environment:

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  devops-pipeline:
    uses: yourusername/devops-os/.github/workflows/devops-os-workflow.yml@main
    with:
      languages: '{"python": true, "java": false, "javascript": true, "go": false}'
      cicd_tools: '{"docker": true, "terraform": true, "kubectl": false}'
      kubernetes_tools: '{"k9s": true, "kustomize": true, "argocd_cli": false, "flux": false}'
      run_tests: true
      k8s_deploy: true
    secrets:
      KUBECONFIG: ${{ secrets.KUBECONFIG }}
```

## Using DevOps-OS in Jenkins

### 1. Creating a Jenkins Pipeline with Your Container

You can create a Jenkins pipeline that uses your DevOps-OS container:

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'ghcr.io/yourusername/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    parameters {
        booleanParam(name: 'PYTHON_ENABLED', defaultValue: true, description: 'Enable Python tools')
        booleanParam(name: 'JAVA_ENABLED', defaultValue: true, description: 'Enable Java tools')
        booleanParam(name: 'JS_ENABLED', defaultValue: true, description: 'Enable JavaScript tools')
        booleanParam(name: 'DOCKER_ENABLED', defaultValue: true, description: 'Enable Docker tools')
        booleanParam(name: 'KUBERNETES_DEPLOY', defaultValue: false, description: 'Deploy to Kubernetes')
        booleanParam(name: 'KUSTOMIZE_ENABLED', defaultValue: true, description: 'Use Kustomize for Kubernetes deployments')
        booleanParam(name: 'ARGOCD_ENABLED', defaultValue: false, description: 'Use ArgoCD for deployments')
    }
    
    stages {
        stage('Configure Environment') {
            steps {
                script {
                    // Generate a custom configuration file based on parameters
                    def config = [
                        languages: [
                            python: params.PYTHON_ENABLED,
                            java: params.JAVA_ENABLED,
                            javascript: params.JS_ENABLED,
                            go: false
                        ],
                        cicd: [
                            docker: params.DOCKER_ENABLED,
                            terraform: false,
                            kubectl: params.KUBERNETES_DEPLOY,
                            helm: params.KUBERNETES_DEPLOY,
                            github_actions: false
                        ],
                        kubernetes: [
                            k9s: params.KUBERNETES_DEPLOY,
                            kustomize: params.KUSTOMIZE_ENABLED,
                            argocd_cli: params.ARGOCD_ENABLED,
                            flux: false,
                            kubeseal: false,
                            kind: false,
                            minikube: false,
                            openshift_cli: false
                        ]
                    ]
                    
                    writeJSON file: 'devops-config.json', json: config
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    if (params.PYTHON_ENABLED) {
                        sh 'pip install -r requirements.txt'
                    }
                    if (params.JAVA_ENABLED) {
                        sh './gradlew build'
                    }
                    if (params.JS_ENABLED) {
                        sh 'npm install && npm run build'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    if (params.PYTHON_ENABLED) {
                        sh 'pytest'
                    }
                    if (params.JAVA_ENABLED) {
                        sh './gradlew test'
                    }
                    if (params.JS_ENABLED) {
                        sh 'npm test'
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                expression { return params.KUBERNETES_DEPLOY }
            }
            steps {
                script {
                    // Setup kubeconfig from credentials
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh """
                            mkdir -p \$HOME/.kube
                            cp \$KUBECONFIG \$HOME/.kube/config
                            chmod 600 \$HOME/.kube/config
                        """
                        
                        if (params.KUSTOMIZE_ENABLED) {
                            sh 'kubectl apply -k ./k8s/'
                        } else {
                            sh '''
                                kubectl apply -f ./k8s/deployment.yaml
                                kubectl apply -f ./k8s/service.yaml
                            '''
                        }
                        
                        if (params.ARGOCD_ENABLED) {
                            sh """
                                argocd login \$ARGOCD_SERVER --username \$ARGOCD_USERNAME --password \$ARGOCD_PASSWORD
                                argocd app sync my-application
                                argocd app wait my-application --health
                            """
                        } else {
                            sh 'kubectl rollout status deployment/my-app'
                        }
                    }
                }
            }
        }
    }
}
```

### 2. Creating a Jenkins Shared Library

For more advanced usage, create a Jenkins Shared Library that provides pre-configured pipelines using your DevOps-OS:

```groovy
// vars/devopsOsPipeline.groovy
def call(Map config = [:]) {
    def pythonEnabled = config.pythonEnabled ?: true
    def javaEnabled = config.javaEnabled ?: false
    def jsEnabled = config.jsEnabled ?: false
    def kubernetesEnabled = config.kubernetesEnabled ?: false
    def kustomizeEnabled = config.kustomizeEnabled ?: true
    def argocdEnabled = config.argocdEnabled ?: false
    
    pipeline {
        agent {
            docker {
                image 'ghcr.io/yourusername/devops-os:latest'
                args '-v /var/run/docker.sock:/var/run/docker.sock'
            }
        }
        
        stages {
            stage('Build and Test') {
                steps {
                    script {
                        // Use preconfigured tools based on parameters
                        if (pythonEnabled) {
                            sh 'python -m pytest'
                        }
                        if (javaEnabled) {
                            sh './gradlew test'
                        }
                        if (jsEnabled) {
                            sh 'npm test'
                        }
                    }
                }
            }
            
            stage('Deploy to Kubernetes') {
                when {
                    expression { return kubernetesEnabled }
                }
                steps {
                    script {
                        // Use Kubernetes deployment tools
                        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                            sh """
                                mkdir -p \$HOME/.kube
                                cp \$KUBECONFIG \$HOME/.kube/config
                                chmod 600 \$HOME/.kube/config
                            """
                            
                            if (kustomizeEnabled) {
                                sh 'kubectl apply -k ./k8s/'
                            } else {
                                sh '''
                                    kubectl apply -f ./k8s/deployment.yaml
                                    kubectl apply -f ./k8s/service.yaml
                                '''
                            }
                            
                            if (argocdEnabled) {
                                sh """
                                    argocd login \$ARGOCD_SERVER --username \$ARGOCD_USERNAME --password \$ARGOCD_PASSWORD
                                    argocd app sync my-application
                                    argocd app wait my-application --health
                                """
                            } else {
                                sh 'kubectl rollout status deployment/my-app'
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Then in your project's Jenkinsfile:

```groovy
// Jenkinsfile in your project
@Library('devops-os-library') _

devopsOsPipeline(
    pythonEnabled: true,
    javaEnabled: false,
    jsEnabled: true,
    kubernetesEnabled: true,
    kustomizeEnabled: true,
    argocdEnabled: false
)
```

## Advanced CI/CD Integration Strategies

### 1. Dynamic Configuration Generation

You can dynamically generate the dev container configuration during the CI/CD process:

```yaml
# GitHub Actions example with dynamic configuration
- name: Generate DevOps-OS Configuration
  run: |
    cd .devcontainer
    cat > devcontainer.env.json << EOF
    {
      "languages": {
        "python": ${{ github.event.inputs.python_enabled || 'true' }},
        "java": ${{ github.event.inputs.java_enabled || 'false' }},
        "javascript": ${{ github.event.inputs.js_enabled || 'true' }},
        "go": ${{ github.event.inputs.go_enabled || 'false' }}
      },
      "cicd": {
        "docker": true,
        "terraform": ${{ github.event.inputs.terraform_enabled || 'false' }},
        "kubectl": ${{ github.event.inputs.kubectl_enabled || 'false' }},
        "helm": ${{ github.event.inputs.helm_enabled || 'false' }}
      },
      "kubernetes": {
        "k9s": ${{ github.event.inputs.k9s_enabled || 'false' }},
        "kustomize": ${{ github.event.inputs.kustomize_enabled || 'false' }},
        "argocd_cli": ${{ github.event.inputs.argocd_enabled || 'false' }},
        "flux": ${{ github.event.inputs.flux_enabled || 'false' }},
        "kind": ${{ github.event.inputs.kind_enabled || 'false' }},
        "minikube": ${{ github.event.inputs.minikube_enabled || 'false' }}
      }
    }
    EOF
    python configure.py
```

### 2. Matrix Testing with Different Tools

```yaml
# GitHub Actions matrix testing
jobs:
  test:
    strategy:
      matrix:
        language: [python, java, javascript, go]
        include:
          - language: python
            test_command: pytest
          - language: java
            test_command: ./gradlew test
          - language: javascript
            test_command: npm test
          - language: go
            test_command: go test ./...
    
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourusername/devops-os:latest
    
    steps:
      - uses: actions/checkout@v3
      - name: Configure for ${{ matrix.language }}
        run: |
          cd .devcontainer
          python configure.py --enable-only-language ${{ matrix.language }}
      - name: Run tests
        run: ${{ matrix.test_command }}
```

## Benefits of This Approach

1. **Consistent Environments**: The same container is used for local development, CI/CD pipelines, and production
2. **Flexible Configuration**: Dynamically enable only the tools needed for each pipeline
3. **Reduced Setup Time**: No need to install tools in the CI/CD environment
4. **Version Control**: Tool configurations are version controlled with your code
5. **Reusable Workflows**: Create standardized pipelines that can be reused across projects

By creating and sharing your DevOps-OS container, you provide a standardized environment that can be used across the entire software development lifecycle, from local development to CI/CD pipelines, ensuring consistency and reliability throughout.