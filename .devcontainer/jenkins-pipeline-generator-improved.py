#!/usr/bin/env python3
"""
DevOps-OS Jenkins Pipeline Generator

This script generates Jenkinsfile pipeline scripts for CI/CD pipelines
using the DevOps-OS container as the execution environment.

Features:
- Generates pipelines for build, test, deploy, or complete CI/CD
- Supports multiple programming languages
- Configurable Kubernetes deployment methods
- Customizable through command-line arguments or environment variables
- Parameterized pipeline support for runtime configuration
- Integration with Jenkins credentials
- Support for various source control management (SCM) systems
"""

import os
import sys
import argparse
import json
from string import Template
from pathlib import Path

# Default paths
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.getcwd()
ENV_CONFIG_PATH = os.path.join(TEMPLATE_DIR, "devcontainer.env.json")

# Default pipeline types
PIPELINE_TYPES = ["build", "test", "deploy", "complete", "parameterized"]

# Environment variable prefixes
ENV_PREFIX = "DEVOPS_OS_JENKINS_"

def parse_arguments():
    """Parse command line arguments with environment variable fallbacks."""
    parser = argparse.ArgumentParser(description="Generate Jenkins pipeline files for DevOps-OS")
    parser.add_argument("--name", 
                       help="Pipeline name",
                       default=os.environ.get(f"{ENV_PREFIX}NAME", "DevOps-OS"))
    parser.add_argument("--type", choices=PIPELINE_TYPES, 
                       help="Type of pipeline to generate",
                       default=os.environ.get(f"{ENV_PREFIX}TYPE", "complete"))
    parser.add_argument("--languages", 
                       help="Comma-separated list of languages to enable (python,java,javascript,go)",
                       default=os.environ.get(f"{ENV_PREFIX}LANGUAGES", "python,javascript"))
    parser.add_argument("--kubernetes", action="store_true", 
                       help="Include Kubernetes deployment steps",
                       default=os.environ.get(f"{ENV_PREFIX}KUBERNETES", "false").lower() in ("true", "1", "yes"))
    parser.add_argument("--registry", 
                       help="Container registry URL",
                       default=os.environ.get(f"{ENV_PREFIX}REGISTRY", "docker.io"))
    parser.add_argument("--k8s-method", choices=["kubectl", "kustomize", "argocd", "flux"],
                       help="Kubernetes deployment method",
                       default=os.environ.get(f"{ENV_PREFIX}K8S_METHOD", "kubectl"))
    parser.add_argument("--output", 
                       help="Output file path for generated Jenkinsfile",
                       default=os.environ.get(f"{ENV_PREFIX}OUTPUT", os.path.join(OUTPUT_DIR, "Jenkinsfile")))
    parser.add_argument("--custom-values", 
                       help="Path to custom values JSON file",
                       default=os.environ.get(f"{ENV_PREFIX}CUSTOM_VALUES"))
    parser.add_argument("--image", 
                       help="DevOps-OS container image to use",
                       default=os.environ.get(f"{ENV_PREFIX}IMAGE", "docker.io/yourorg/devops-os:latest"))
    parser.add_argument("--scm", choices=["git", "svn", "none"],
                       help="Source Control Management system to use",
                       default=os.environ.get(f"{ENV_PREFIX}SCM", "git"))
    parser.add_argument("--parameters", action="store_true",
                       help="Generate pipeline with parameters (for manual runs)",
                       default=os.environ.get(f"{ENV_PREFIX}PARAMETERS", "false").lower() in ("true", "1", "yes"))
    parser.add_argument("--env-file", 
                       help="Use DevOps-OS devcontainer.env.json for configuration",
                       default=os.environ.get(f"{ENV_PREFIX}ENV_FILE", ENV_CONFIG_PATH))
    
    args = parser.parse_args()
    
    # If type is 'parameterized', set parameters flag to True
    if args.type == "parameterized":
        args.parameters = True
    
    return args

def load_custom_values(file_path):
    """Load custom values from a JSON file."""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def load_env_config(file_path):
    """Load DevOps-OS environment configuration."""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            # Remove comments that start with // for JSON parsing
            lines = f.readlines()
            cleaned_json = ""
            for line in lines:
                if not line.strip().startswith("//"):
                    cleaned_json += line
            return json.loads(cleaned_json)
    return {}

def create_directory_structure(output_path):
    """Create the necessary directory structure."""
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    return output_path

def generate_language_config(languages_str, env_config=None):
    """Generate language configuration JSON."""
    languages = languages_str.split(',')
    
    # Default to env_config if available, otherwise use languages from args
    if env_config and 'languages' in env_config:
        config = env_config['languages']
    else:
        config = {
            "python": "python" in languages,
            "java": "java" in languages,
            "javascript": "javascript" in languages, 
            "go": "go" in languages
        }
    
    return config

def generate_kubernetes_config(k8s_enabled, k8s_method, env_config=None):
    """Generate Kubernetes configuration JSON."""
    # Default to env_config if available
    if env_config and 'kubernetes' in env_config:
        return env_config['kubernetes']
    
    if not k8s_enabled:
        return {"k9s": False, "kustomize": False, "argocd_cli": False, "flux": False}
    
    config = {
        "k9s": True,
        "kustomize": k8s_method == "kustomize",
        "argocd_cli": k8s_method == "argocd",
        "flux": k8s_method == "flux",
        "kind": False,
        "minikube": False
    }
    return config

def generate_cicd_config(env_config=None):
    """Generate CI/CD tools configuration JSON."""
    if env_config and 'cicd' in env_config:
        return env_config['cicd']
    
    return {
        "docker": True,
        "terraform": True,
        "kubectl": True,
        "helm": True,
        "github_actions": True
    }

def generate_build_tools_config(env_config=None):
    """Generate build tools configuration JSON."""
    if env_config and 'build_tools' in env_config:
        return env_config['build_tools']
    
    return {
        "gradle": True,
        "maven": True,
        "ant": False,
        "make": True,
        "cmake": False
    }

def generate_code_analysis_config(env_config=None):
    """Generate code analysis tools configuration JSON."""
    if env_config and 'code_analysis' in env_config:
        return env_config['code_analysis']
    
    return {
        "sonarqube": True,
        "checkstyle": True,
        "pmd": False,
        "eslint": True,
        "pylint": True
    }

def generate_devops_tools_config(env_config=None):
    """Generate DevOps tools configuration JSON."""
    if env_config and 'devops_tools' in env_config:
        return env_config['devops_tools']
    
    return {
        "nexus": False,
        "prometheus": True,
        "grafana": True,
        "elk": True,
        "jenkins": True
    }

def generate_parameters_block(args, configs):
    """Generate pipeline parameters block."""
    if not args.parameters:
        return ""
    
    parameters = []
    
    # Add language parameters
    for lang, enabled in configs["languages"].items():
        param_name = f"{lang.upper()}_ENABLED"
        parameters.append(f"        booleanParam(name: '{param_name}', defaultValue: {str(enabled).lower()}, description: 'Enable {lang.capitalize()} tools')")
    
    # Add Kubernetes parameters if enabled
    if args.kubernetes:
        parameters.append(f"        booleanParam(name: 'KUBERNETES_DEPLOY', defaultValue: true, description: 'Deploy to Kubernetes')")
        parameters.append(f"        choice(name: 'K8S_METHOD', choices: ['kubectl', 'kustomize', 'argocd', 'flux'], defaultValue: '{args.k8s_method}', description: 'Kubernetes deployment method')")
        parameters.append(f"        choice(name: 'ENVIRONMENT', choices: ['dev', 'test', 'staging', 'prod'], defaultValue: 'dev', description: 'Deployment environment')")
    
    # Add registry parameter
    parameters.append(f"        string(name: 'REGISTRY_URL', defaultValue: '{args.registry}', description: 'Container registry URL')")
    parameters.append(f"        string(name: 'IMAGE_NAME', defaultValue: 'devops-os-app', description: 'Name of the container image')")
    parameters.append(f"        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Container image tag')")
    
    if parameters:
        return "    parameters {\n" + "\n".join(parameters) + "\n    }"
    return ""

def generate_environment_block(args, configs):
    """Generate pipeline environment block."""
    env_vars = []
    
    # Add default environment variables
    env_vars.append("        WORKSPACE_DIR = '${WORKSPACE}'")
    env_vars.append(f"        REGISTRY_URL = params.REGISTRY_URL ?: '{args.registry}'")
    env_vars.append("        IMAGE_NAME = params.IMAGE_NAME ?: 'devops-os-app'")
    env_vars.append("        IMAGE_TAG = params.IMAGE_TAG ?: 'latest'")
    
    if args.kubernetes:
        env_vars.append("        KUBERNETES_DEPLOY = params.KUBERNETES_DEPLOY ?: true")
        env_vars.append(f"        K8S_METHOD = params.K8S_METHOD ?: '{args.k8s_method}'")
        env_vars.append("        ENVIRONMENT = params.ENVIRONMENT ?: 'dev'")
    
    # Add language environment variables
    for lang, enabled in configs["languages"].items():
        env_vars.append(f"        {lang.upper()}_ENABLED = params.{lang.upper()}_ENABLED ?: {str(enabled).lower()}")
    
    if env_vars:
        return "    environment {\n" + "\n".join(env_vars) + "\n    }"
    return ""

def generate_build_stage(configs):
    """Generate pipeline build stage."""
    build_steps = []
    
    # Add checkout step
    build_steps.append("                checkout scm")
    
    # Add language-specific build steps
    if configs["languages"].get("python", False):
        build_steps.append("""                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f setup.py ]; then
                        pip install -e .
                    elif [ ${PYTHON_ENABLED} = 'true' ] && [ -f pyproject.toml ]; then
                        pip install -e .
                    fi
                '''""")
    
    if configs["languages"].get("java", False):
        build_steps.append("""                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn -B package --file pom.xml
                    fi
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f build.gradle ]; then
                        ./gradlew build
                    fi
                '''""")
    
    if configs["languages"].get("javascript", False):
        build_steps.append("""                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm ci
                        npm run build --if-present
                    fi
                '''""")
    
    if configs["languages"].get("go", False):
        build_steps.append("""                sh '''
                    if [ ${GO_ENABLED} = 'true' ] && [ -f go.mod ]; then
                        go build -v ./...
                    fi
                '''""")
    
    # Add artifact archiving step
    build_steps.append("""                archiveArtifacts artifacts: '**/target/*.jar, **/dist/*, **/build/*, **/*.zip, **/*.tar.gz', allowEmptyArchive: true""")
    
    return "        stage('Build') {\n            steps {\n" + "\n".join(build_steps) + "\n            }\n        }"

def generate_test_stage(configs):
    """Generate pipeline test stage."""
    test_steps = []
    
    # Add language-specific test steps
    if configs["languages"].get("python", False):
        test_steps.append("""                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f requirements.txt ]; then
                        pip install -r requirements.txt pytest pytest-cov
                    fi
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -d tests ]; then
                        python -m pytest --cov=./ --cov-report=xml
                    fi
                '''""")
        if configs.get("code_analysis", {}).get("pylint", False):
            test_steps.append("""                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && command -v pylint &> /dev/null; then
                        pylint --disable=C0111 **/*.py || true
                    fi
                '''""")
    
    if configs["languages"].get("java", False):
        test_steps.append("""                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn -B test --file pom.xml
                    fi
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f build.gradle ]; then
                        ./gradlew test
                    fi
                '''""")
        if configs.get("code_analysis", {}).get("checkstyle", False):
            test_steps.append("""                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn checkstyle:checkstyle || true
                    fi
                '''""")
    
    if configs["languages"].get("javascript", False):
        test_steps.append("""                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm test || true
                    fi
                '''""")
        if configs.get("code_analysis", {}).get("eslint", False):
            test_steps.append("""                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ] && grep -q eslint package.json; then
                        npm run lint || true
                    fi
                '''""")
    
    if configs["languages"].get("go", False):
        test_steps.append("""                sh '''
                    if [ ${GO_ENABLED} = 'true' ] && [ -f go.mod ]; then
                        go test -v ./...
                    fi
                '''""")
    
    # Add test results collection step
    test_steps.append("""                junit '**/target/surefire-reports/*.xml, **/test-results/*.xml, **/junit-reports/*.xml', allowEmptyResults: true""")
    
    return "        stage('Test') {\n            steps {\n" + "\n".join(test_steps) + "\n            }\n        }"

def generate_deploy_stage(args, configs):
    """Generate pipeline deploy stage."""
    deploy_steps = []
    
    # Add Docker build and push steps
    deploy_steps.append("""                script {
                    def imageName = "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}"
                    docker.withRegistry('https://' + REGISTRY_URL, 'registry-credentials') {
                        def customImage = docker.build(imageName)
                        customImage.push()
                    }
                }""")
    
    # Add Kubernetes deployment steps if enabled
    if args.kubernetes:
        deploy_steps.append("""                script {
                    if (env.KUBERNETES_DEPLOY == 'true') {
                        // Set up Kubernetes credentials
                        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                            sh 'mkdir -p ~/.kube && cp $KUBECONFIG ~/.kube/config && chmod 600 ~/.kube/config'
                            
                            if (env.K8S_METHOD == 'kubectl') {
                                sh '''
                                    kubectl apply -f ./k8s/deployment.yaml
                                    kubectl apply -f ./k8s/service.yaml
                                    kubectl rollout status deployment/my-app
                                '''
                            } else if (env.K8S_METHOD == 'kustomize') {
                                sh '''
                                    kubectl apply -k ./k8s/overlays/${ENVIRONMENT}
                                    kubectl rollout status deployment/my-app
                                '''
                            } else if (env.K8S_METHOD == 'argocd') {
                                withCredentials([
                                    string(credentialsId: 'argocd-server', variable: 'ARGOCD_SERVER'),
                                    usernamePassword(credentialsId: 'argocd-credentials', usernameVariable: 'ARGOCD_USERNAME', passwordVariable: 'ARGOCD_PASSWORD')
                                ]) {
                                    sh '''
                                        argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure
                                        argocd app sync my-application
                                        argocd app wait my-application --health
                                    '''
                                }
                            } else if (env.K8S_METHOD == 'flux') {
                                sh '''
                                    flux reconcile source git flux-system
                                    flux reconcile kustomization flux-system
                                '''
                            }
                        }
                    }
                }""")
    
    # Add deployment notification step
    deploy_steps.append("""                sh '''
                    echo "Deployment completed successfully"
                '''""")
    
    deploy_stage = "        stage('Deploy') {\n"
    
    # Add deployment approval for production
    deploy_stage += """            when {
                expression { 
                    return env.ENVIRONMENT != 'prod' || (env.ENVIRONMENT == 'prod' && currentBuild.resultIsBetterOrEqualTo('SUCCESS'))
                }
            }
"""
    
    # Add inputs for production deployment
    if args.kubernetes:
        deploy_stage += """            input {
                message "Deploy to production?"
                ok "Yes"
                submitter "admin"
                parameters {
                    string(name: 'CONFIRM_DEPLOY', defaultValue: 'no', description: 'Type YES to confirm deployment to production')
                }
                when {
                    expression { return env.ENVIRONMENT == 'prod' }
                }
            }
"""
    
    deploy_stage += "            steps {\n" + "\n".join(deploy_steps) + "\n            }\n        }"
    
    return deploy_stage

def generate_pipeline(args, configs):
    """Generate Jenkins pipeline."""
    pipeline = [
        "pipeline {",
        "    agent {",
        "        docker {",
        f"            image '{args.image}'",
        "            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'",
        "        }",
        "    }"
    ]
    
    # Add parameters block if enabled
    params_block = generate_parameters_block(args, configs)
    if params_block:
        pipeline.append(params_block)
    
    # Add environment block
    env_block = generate_environment_block(args, configs)
    if env_block:
        pipeline.append(env_block)
    
    # Add options block
    pipeline.append("""    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        ansiColor('xterm')
    }""")
    
    # Add stages
    pipeline.append("    stages {")
    
    # Add build stage if requested
    if args.type in ["build", "complete", "parameterized"]:
        pipeline.append(generate_build_stage(configs))
    
    # Add test stage if requested
    if args.type in ["test", "complete", "parameterized"]:
        pipeline.append(generate_test_stage(configs))
    
    # Add deploy stage if requested
    if args.type in ["deploy", "complete", "parameterized"]:
        pipeline.append(generate_deploy_stage(args, configs))
    
    pipeline.append("    }")
    
    # Add post section
    pipeline.append("""    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }""")
    
    pipeline.append("}")
    
    return "\n".join(pipeline)

def main():
    """Main function."""
    args = parse_arguments()
    output_path = create_directory_structure(args.output)
    custom_values = load_custom_values(args.custom_values)
    env_config = load_env_config(args.env_file)
    
    # Generate configuration objects
    configs = {
        "languages": generate_language_config(args.languages, env_config),
        "kubernetes": generate_kubernetes_config(args.kubernetes, args.k8s_method, env_config),
        "cicd": generate_cicd_config(env_config),
        "build_tools": generate_build_tools_config(env_config),
        "code_analysis": generate_code_analysis_config(env_config),
        "devops_tools": generate_devops_tools_config(env_config)
    }
    
    # Generate pipeline content
    pipeline_content = generate_pipeline(args, configs)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(pipeline_content)
    
    print(f"Jenkins pipeline generated: {output_path}")
    print(f"Type: {args.type}")
    print(f"Languages: {args.languages}")
    if args.kubernetes:
        print(f"Kubernetes deployment method: {args.k8s_method}")
    if args.parameters:
        print("Pipeline includes runtime parameters")

if __name__ == "__main__":
    main()
