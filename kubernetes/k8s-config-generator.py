#!/usr/bin/env python3
"""
Kubernetes Configuration Generator for DevOps-OS

This script generates Kubernetes configuration files based on templates
and environment variables. It can generate configurations for various
deployment methods including Kubectl, Kustomize, ArgoCD, and Flux CD.
"""

import os
import sys
import shutil
import argparse
import json
from string import Template

# Default paths
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_KUBE_DIR = os.path.join(TEMPLATE_DIR, "kubernetes-templates")
OUTPUT_DIR = os.path.join(os.getcwd(), "k8s")

# Supported deployment methods
DEPLOYMENT_METHODS = ["kubectl", "kustomize", "argocd", "flux"]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Kubernetes configuration files")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--environment", default="dev", choices=["dev", "test", "staging", "prod"], 
                       help="Target environment")
    parser.add_argument("--registry", default="ghcr.io/your-org", 
                       help="Container registry URL")
    parser.add_argument("--image-tag", default="latest", 
                       help="Container image tag")
    parser.add_argument("--replicas", default="2", 
                       help="Number of replicas")
    parser.add_argument("--method", default="kubectl", choices=DEPLOYMENT_METHODS, 
                       help="Deployment method")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, 
                       help="Output directory for generated files")
    parser.add_argument("--custom-values", 
                       help="Path to custom values JSON file")
    
    return parser.parse_args()

def load_custom_values(file_path):
    """Load custom values from a JSON file."""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def create_directory_structure(args, deployment_method):
    """Create the necessary directory structure based on deployment method."""
    base_output_dir = args.output_dir
    
    if deployment_method == "kustomize":
        # Create base and overlay directories
        os.makedirs(os.path.join(base_output_dir, "base"), exist_ok=True)
        os.makedirs(os.path.join(base_output_dir, "overlays", args.environment), exist_ok=True)
    elif deployment_method in ["argocd", "flux"]:
        # Create GitOps directory structure
        os.makedirs(os.path.join(base_output_dir, deployment_method), exist_ok=True)
    else:
        # Simple kubectl structure
        os.makedirs(base_output_dir, exist_ok=True)
    
    return base_output_dir

def substitute_variables(template_path, output_path, values):
    """Substitute variables in a template file and write to output."""
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    result = template.safe_substitute(values)
    
    with open(output_path, 'w') as f:
        f.write(result)

def copy_template_files(args, custom_values):
    """Copy and update template files based on deployment method."""
    method = args.method
    env = args.environment
    base_output_dir = create_directory_structure(args, method)
    
    # Prepare values for template substitution
    values = {
        "APP_NAME": args.app_name,
        "ENVIRONMENT": env,
        "CONTAINER_REGISTRY": args.registry,
        "IMAGE_TAG": args.image_tag,
        "REPLICAS": args.replicas,
        "FEATURE_FLAGS": "false" if env == "prod" else "true",
        "DB_USER": "dbuser",
        "DB_PASSWORD": "placeholder",  # Should be replaced with actual secrets
        "DB_HOST": f"db-{env}",
        "DB_NAME": f"{args.app_name}-{env}",
        "API_KEY": "placeholder"  # Should be replaced with actual secrets
    }
    
    # Update with custom values
    values.update(custom_values)
    
    if method == "kubectl":
        # Simple kubectl deployment
        template_path = os.path.join(TEMPLATE_KUBE_DIR, "sample-app-deployment.yaml")
        output_path = os.path.join(base_output_dir, "deployment.yaml")
        substitute_variables(template_path, output_path, values)
        
    elif method == "kustomize":
        # Kustomize deployment
        # Copy base templates
        base_template = os.path.join(TEMPLATE_KUBE_DIR, "sample-app-deployment.yaml")
        base_output = os.path.join(base_output_dir, "base", "deployment.yaml")
        substitute_variables(base_template, base_output, values)
        
        # Copy kustomization templates
        base_kustomize = os.path.join(TEMPLATE_KUBE_DIR, "kustomize", "base", "kustomization.yaml")
        overlay_kustomize = os.path.join(TEMPLATE_KUBE_DIR, "kustomize", "overlays", "env", "kustomization.yaml")
        
        base_kustomize_out = os.path.join(base_output_dir, "base", "kustomization.yaml")
        overlay_kustomize_out = os.path.join(base_output_dir, "overlays", env, "kustomization.yaml")
        
        substitute_variables(base_kustomize, base_kustomize_out, values)
        substitute_variables(overlay_kustomize, overlay_kustomize_out, values)
        
    elif method == "argocd":
        # ArgoCD deployment
        template_path = os.path.join(TEMPLATE_KUBE_DIR, "argocd", "application.yaml")
        output_path = os.path.join(base_output_dir, "argocd", "application.yaml")
        substitute_variables(template_path, output_path, values)
        
    elif method == "flux":
        # Flux deployment
        template_path = os.path.join(TEMPLATE_KUBE_DIR, "flux", "deployment.yaml")
        output_path = os.path.join(base_output_dir, "flux", "deployment.yaml")
        substitute_variables(template_path, output_path, values)
    
    print(f"\nKubernetes configuration generated successfully in {base_output_dir}")
    print(f"Deployment method: {method.upper()}")
    print(f"Environment: {env}")
    print(f"Application: {args.app_name}")
    if method == "kustomize":
        print("\nTo apply with kustomize, run:")
        print(f"kubectl apply -k {os.path.join(base_output_dir, 'overlays', env)}")
    elif method == "kubectl":
        print("\nTo apply with kubectl, run:")
        print(f"kubectl apply -f {os.path.join(base_output_dir, 'deployment.yaml')}")
    elif method == "argocd":
        print("\nTo apply with ArgoCD, run:")
        print(f"argocd app create {args.app_name} --repo https://github.com/your-org/your-repo.git --path kubernetes/overlays/{env} --dest-server https://kubernetes.default.svc --dest-namespace {args.app_name}-{env}")
    elif method == "flux":
        print("\nTo apply with Flux, run:")
        print("flux create source git my-app --url=https://github.com/your-org/your-repo")
        print(f"flux create kustomization my-app --source=my-app --path=./kubernetes/overlays/{env}")

def main():
    """Main function."""
    args = parse_arguments()
    custom_values = load_custom_values(args.custom_values)
    copy_template_files(args, custom_values)

if __name__ == "__main__":
    main()
