import typer
from InquirerPy import inquirer

# Import the refactored main functions from scaffold scripts
import cli.scaffold_cicd as scaffold_cicd
import cli.scaffold_gha as scaffold_gha
import cli.scaffold_jenkins as scaffold_jenkins

app = typer.Typer(help="Unified DevOps-OS CLI tool")

@app.command()
def init():
    """Interactive project initializer."""
    typer.echo("Welcome to DevOps-OS Init Wizard!")
    ci_tool = inquirer.select(
        message="Choose CI tool:",
        choices=["GitHub Actions", "Jenkins"],
    ).execute()
    k8s_tool = inquirer.select(
        message="Choose Kubernetes deployment type:",
        choices=["Kustomize", "ArgoCD", "Flux"],
    ).execute()
    typer.echo(f"Selected CI: {ci_tool}, K8s: {k8s_tool}")
    # Add more prompts and logic as needed

@app.command()
def scaffold(
    target: str = typer.Argument(..., help="What to scaffold: cicd | gha | jenkins | k8s"),
    tool: str = typer.Option(None, help="Tool type (e.g., github, jenkins, argo, flux)"),
):
    """Scaffold CI/CD or K8s resources."""
    if target == "cicd":
        scaffold_cicd.main()
    elif target == "gha":
        scaffold_gha.main()
    elif target == "jenkins":
        scaffold_jenkins.main()
    else:
        typer.echo("Unknown scaffold target.")

if __name__ == "__main__":
    app()
