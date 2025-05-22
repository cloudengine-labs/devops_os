#!/usr/bin/env python3
"""
DevOps-OS CI/CD Generator Helper

This script simplifies using the DevOps-OS CI/CD generators by providing
a unified interface for creating both GitHub Actions workflows and Jenkins
pipelines with consistent configuration.

Usage:
    python generate-cicd.py --type [complete|build|test|deploy] [options]
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_GENERATOR = os.path.join(SCRIPT_DIR, "github-actions-generator-improved.py")
JENKINS_GENERATOR = os.path.join(SCRIPT_DIR, "jenkins-pipeline-generator-improved.py")
ENV_CONFIG_PATH = os.path.join(SCRIPT_DIR, "devcontainer.env.json")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate CI/CD configurations for DevOps-OS")
    parser.add_argument("--name", help="CI/CD name", default="DevOps-OS")
    parser.add_argument("--type", choices=["build", "test", "deploy", "complete"], 
                       help="Type of CI/CD to generate", default="complete")
    parser.add_argument("--languages", help="Comma-separated list of languages", 
                       default="python,javascript")
    parser.add_argument("--kubernetes", action="store_true", help="Include Kubernetes deployment steps")
    parser.add_argument("--k8s-method", choices=["kubectl", "kustomize", "argocd", "flux"],
                       help="Kubernetes deployment method", default="kubectl")
    parser.add_argument("--output-dir", help="Output directory", default=os.getcwd())
    parser.add_argument("--registry", help="Container registry URL", default="docker.io")
    parser.add_argument("--image", help="DevOps-OS container image", 
                       default="docker.io/yourorg/devops-os:latest")
    parser.add_argument("--custom-values", help="Path to custom values JSON file")
    parser.add_argument("--matrix", action="store_true", help="Enable matrix builds for GitHub Actions")
    parser.add_argument("--parameters", action="store_true", 
                       help="Enable parameterized builds for Jenkins")
    parser.add_argument("--github", action="store_true", help="Generate GitHub Actions workflow")
    parser.add_argument("--jenkins", action="store_true", help="Generate Jenkins pipeline")
    parser.add_argument("--all", action="store_true", help="Generate both GitHub Actions and Jenkins")
    
    args = parser.parse_args()
    
    # If neither --github, --jenkins, or --all is specified, default to --all
    if not (args.github or args.jenkins or args.all):
        args.all = True
    
    # If --all is specified, set both --github and --jenkins
    if args.all:
        args.github = True
        args.jenkins = True
    
    return args

def run_github_generator(args):
    """Run the GitHub Actions workflow generator."""
    print("Generating GitHub Actions workflow...")
    
    # Create output directory for GitHub Actions
    github_output = os.path.join(args.output_dir, ".github/workflows")
    os.makedirs(github_output, exist_ok=True)
    
    # Build the command
    cmd = [
        "python3", GITHUB_GENERATOR,
        "--name", args.name,
        "--type", args.type,
        "--languages", args.languages,
        "--registry", args.registry,
        "--image", args.image,
        "--output", github_output,
        "--env-file", ENV_CONFIG_PATH
    ]
    
    # Add optional arguments
    if args.kubernetes:
        cmd.append("--kubernetes")
        cmd.extend(["--k8s-method", args.k8s_method])
    
    if args.matrix:
        cmd.append("--matrix")
    
    if args.custom_values:
        cmd.extend(["--custom-values", args.custom_values])
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("GitHub Actions workflow generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating GitHub Actions workflow: {e}")
        return False
    
    return True

def run_jenkins_generator(args):
    """Run the Jenkins pipeline generator."""
    print("Generating Jenkins pipeline...")
    
    # Create output path for Jenkins
    jenkins_output = os.path.join(args.output_dir, "Jenkinsfile")
    
    # Build the command
    cmd = [
        "python3", JENKINS_GENERATOR,
        "--name", args.name,
        "--type", args.type,
        "--languages", args.languages,
        "--registry", args.registry,
        "--image", args.image,
        "--output", jenkins_output,
        "--env-file", ENV_CONFIG_PATH
    ]
    
    # Add optional arguments
    if args.kubernetes:
        cmd.append("--kubernetes")
        cmd.extend(["--k8s-method", args.k8s_method])
    
    if args.parameters:
        cmd.append("--parameters")
    
    if args.custom_values:
        cmd.extend(["--custom-values", args.custom_values])
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Jenkins pipeline generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating Jenkins pipeline: {e}")
        return False
    
    return True

def create_readme(args):
    """Create a README.md file explaining the generated CI/CD files."""
    readme_path = os.path.join(args.output_dir, "CICD-README.md")
    
    with open(readme_path, "w") as f:
        f.write(f"# {args.name} CI/CD Configuration\n\n")
        f.write("This directory contains CI/CD configuration files generated by DevOps-OS.\n\n")
        
        if args.github:
            f.write("## GitHub Actions Workflow\n\n")
            f.write(f"- Type: {args.type}\n")
            f.write(f"- Languages: {args.languages}\n")
            if args.kubernetes:
                f.write(f"- Kubernetes Deployment Method: {args.k8s_method}\n")
            if args.matrix:
                f.write("- Matrix Build: Enabled\n")
            f.write("\nWorkflow location: `.github/workflows/`\n\n")
        
        if args.jenkins:
            f.write("## Jenkins Pipeline\n\n")
            f.write(f"- Type: {args.type}\n")
            f.write(f"- Languages: {args.languages}\n")
            if args.kubernetes:
                f.write(f"- Kubernetes Deployment Method: {args.k8s_method}\n")
            if args.parameters:
                f.write("- Parameterized: Enabled\n")
            f.write("\nPipeline location: `Jenkinsfile`\n\n")
        
        f.write("## Usage\n\n")
        
        if args.github:
            f.write("### GitHub Actions\n\n")
            f.write("The GitHub Actions workflow will automatically run when you push to your repository.\n\n")
        
        if args.jenkins:
            f.write("### Jenkins\n\n")
            f.write("To use the Jenkins pipeline:\n\n")
            f.write("1. Create a new Jenkins Pipeline job\n")
            f.write("2. Configure it to use the Jenkinsfile in your repository\n")
            if args.parameters:
                f.write("3. The pipeline includes parameters you can configure for each build\n\n")
        
        f.write("\n## Generated with DevOps-OS\n\n")
        f.write("These CI/CD configurations were generated using DevOps-OS CI/CD generators.\n")
        f.write("For more information, see the DevOps-OS documentation.\n")
    
    print(f"Created CI/CD README: {readme_path}")

def main():
    """Main function."""
    args = parse_arguments()
    
    success = True
    
    if args.github:
        if not run_github_generator(args):
            success = False
    
    if args.jenkins:
        if not run_jenkins_generator(args):
            success = False
    
    if success:
        create_readme(args)
        print("\nCI/CD generation completed successfully!")
    else:
        print("\nCI/CD generation completed with errors. Please check the output above.")

if __name__ == "__main__":
    main()
