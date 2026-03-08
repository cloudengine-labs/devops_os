#!/usr/bin/env python3
"""
DevOps-OS CI/CD Generator Helper

Generate both GitHub Actions workflows and Jenkins pipelines in one step.
Uses the scaffold_gha and scaffold_jenkins modules directly — no subprocess
calls, no external script files required.

Usage:
    python -m cli.scaffold_cicd [options]
    python -m cli.devopsos scaffold cicd [options]
"""

import os
import sys
import argparse


def _run_module_main(module_main, flags: list) -> bool:
    """Call *module_main()* with the given CLI flag list via sys.argv swap.

    Returns True on success, False if the module exits with a non-zero code.
    """
    saved = sys.argv[:]
    sys.argv = sys.argv[:1] + flags
    try:
        module_main()
        return True
    except SystemExit as exc:
        if exc.code not in (None, 0):
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  Error ({type(exc).__name__}): {exc}")
        return False
    finally:
        sys.argv = saved


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate CI/CD configurations (GitHub Actions + Jenkins) for DevOps-OS"
    )
    parser.add_argument("--name", help="CI/CD pipeline name", default="DevOps-OS")
    parser.add_argument(
        "--type",
        choices=["build", "test", "deploy", "complete"],
        help="Type of CI/CD pipeline to generate",
        default="complete",
    )
    parser.add_argument(
        "--languages",
        help="Comma-separated list of languages",
        default="python,javascript",
    )
    parser.add_argument(
        "--kubernetes",
        action="store_true",
        help="Include Kubernetes deployment steps",
    )
    parser.add_argument(
        "--k8s-method",
        choices=["kubectl", "kustomize", "argocd", "flux"],
        help="Kubernetes deployment method",
        default="kubectl",
    )
    parser.add_argument("--output-dir", help="Root output directory", default=os.getcwd())
    parser.add_argument("--registry", help="Container registry URL", default="docker.io")
    parser.add_argument(
        "--image",
        help="DevOps-OS container image",
        default="docker.io/yourorg/devops-os:latest",
    )
    parser.add_argument("--custom-values", help="Path to custom values JSON file")
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Enable matrix builds for GitHub Actions",
    )
    parser.add_argument(
        "--parameters",
        action="store_true",
        help="Enable parameterized builds for Jenkins",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Generate GitHub Actions workflow only",
    )
    parser.add_argument(
        "--jenkins",
        action="store_true",
        help="Generate Jenkins pipeline only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate both GitHub Actions and Jenkins (default when neither --github nor --jenkins is given)",
    )

    args = parser.parse_args()

    # Default to --all when neither --github nor --jenkins is specified
    if not (args.github or args.jenkins or args.all):
        args.all = True

    if args.all:
        args.github = True
        args.jenkins = True

    return args


def run_github_generator(args) -> bool:
    """Generate GitHub Actions workflow using the scaffold_gha module."""
    import cli.scaffold_gha as scaffold_gha  # noqa: PLC0415 (local import to avoid circular)

    print("Generating GitHub Actions workflow...")

    github_output = os.path.join(args.output_dir, ".github", "workflows")
    os.makedirs(github_output, exist_ok=True)

    flags = [
        "--name", args.name,
        "--type", args.type,
        "--languages", args.languages,
        "--registry", args.registry,
        "--image", args.image,
        "--output", github_output,
    ]
    if args.kubernetes:
        flags += ["--kubernetes", "--k8s-method", args.k8s_method]
    if args.matrix:
        flags.append("--matrix")
    if args.custom_values:
        flags += ["--custom-values", args.custom_values]

    ok = _run_module_main(scaffold_gha.main, flags)
    if ok:
        print("GitHub Actions workflow generated successfully!")
    else:
        print("Error generating GitHub Actions workflow. Check output above.")
    return ok


def run_jenkins_generator(args) -> bool:
    """Generate Jenkins pipeline using the scaffold_jenkins module."""
    import cli.scaffold_jenkins as scaffold_jenkins  # noqa: PLC0415

    print("Generating Jenkins pipeline...")

    jenkins_output = os.path.join(args.output_dir, "Jenkinsfile")

    flags = [
        "--name", args.name,
        "--type", args.type,
        "--languages", args.languages,
        "--registry", args.registry,
        "--image", args.image,
        "--output", jenkins_output,
    ]
    if args.kubernetes:
        flags += ["--kubernetes", "--k8s-method", args.k8s_method]
    if args.parameters:
        flags.append("--parameters")
    if args.custom_values:
        flags += ["--custom-values", args.custom_values]

    ok = _run_module_main(scaffold_jenkins.main, flags)
    if ok:
        print("Jenkins pipeline generated successfully!")
    else:
        print("Error generating Jenkins pipeline. Check output above.")
    return ok

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
