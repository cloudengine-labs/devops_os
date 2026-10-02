# DevOps-OS Skills Developer Guide

**Complete guide for DevOps engineers, platform engineers, and developers who want to extend DevOps-OS skills or integrate them into custom workflows.**

---

## Table of Contents

1. [Extending Skills](#extending-skills)
2. [Custom Skill Development](#custom-skill-development)
3. [Integration Patterns](#integration-patterns)
4. [Testing Skills](#testing-skills)
5. [Deployment](#deployment)
6. [Performance & Optimization](#performance--optimization)
7. [Monitoring & Debugging](#monitoring--debugging)

---

## Extending Skills

### Understanding the Extension Points

```
User Prompt
    ↓
┌─────────────────────────────────────────┐
│  Existing Skill Definition (JSON)       │  ← Extend: Add parameters
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  MCP Server Route (server.py)            │  ← Extend: Add logic
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Core Generator (devops_os/core/)        │  ← Extend: Enhanced generation
└─────────────────────────────────────────┘
    ↓
Generated Config
```

### Extending an Existing Skill

**Scenario:** Add support for "GitOps" workflow type to GitHub Actions

#### Step 1: Update Skill Definition

**File:** `skills/claude_tools.json`

```json
{
  "name": "generate_github_actions_workflow",
  "input_schema": {
    "properties": {
      "workflow_type": {
        "enum": [
          "build",
          "test", 
          "deploy",
          "complete",
          "gitops"  // ADD THIS
        ]
      }
    }
  }
}
```

**File:** `skills/openai_functions.json`

```json
{
  "function": {
    "parameters": {
      "properties": {
        "workflow_type": {
          "enum": [
            "build",
            "test",
            "deploy", 
            "complete",
            "gitops"  // ADD THIS
          ]
        }
      }
    }
  }
}
```

#### Step 2: Update MCP Server Route

**File:** `mcp_server/server.py`

```python
@mcp.tool()
def generate_github_actions_workflow(
    name: str = "my-app",
    workflow_type: str = "complete",  # Already supports new value
    languages: str = "python",
    kubernetes: bool = False,
    k8s_method: str = "kubectl",
    branches: str = "main",
    matrix: bool = False,
) -> str:
    """Generate a GitHub Actions CI/CD workflow YAML file."""
    
    # NEW: Handle gitops workflow type
    if workflow_type == "gitops":
        # Use GitOps-specific generator
        from devops_os.core.github_actions_gitops import GitHubActionsGitOpsGenerator
        generator = GitHubActionsGitOpsGenerator(name=name, languages=languages)
        return generator.generate()
    
    # EXISTING: Handle other workflow types
    from devops_os.core.github_actions_generator import GitHubActionsGenerator
    generator = GitHubActionsGenerator(
        name=name,
        workflow_type=workflow_type,
        languages=languages,
        kubernetes=kubernetes,
        k8s_method=k8s_method,
        branches=branches,
        matrix=matrix,
    )
    return generator.generate()
```

#### Step 3: Update Validation

**File:** `mcp_server/validators.py`

```python
def validate_tool_inputs(tool_name: str, inputs: dict) -> dict:
    """Validate and normalize skill inputs."""
    
    if tool_name == "generate_github_actions_workflow":
        workflow_type = inputs.get("workflow_type", "complete")
        
        # NEW: Validate gitops value
        valid_types = {"build", "test", "deploy", "complete", "gitops"}
        if workflow_type not in valid_types:
            raise ValidationError(
                f"Invalid workflow_type: {workflow_type}. "
                f"Must be one of: {valid_types}"
            )
        
        # ... rest of validation
    
    return inputs
```

#### Step 4: Test the Extension

```python
# test_github_actions_gitops.py
def test_generate_gitops_workflow():
    from mcp_server.server import generate_github_actions_workflow
    
    result = generate_github_actions_workflow(
        name="my-app",
        workflow_type="gitops",  # NEW VALUE
        languages="python"
    )
    
    assert "ArgoCD" in result or "Flux" in result
    assert "git commit" in result
    assert "push" in result
```

---

## Custom Skill Development

### Creating a Completely New Skill

**Scenario:** Create a skill to generate Terraform configurations for infrastructure

#### Step 1: Create Core Generator

**File:** `devops_os/core/terraform_generator.py`

```python
"""Generate Terraform configurations for cloud infrastructure."""

import json
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class TerraformConfig:
    """Terraform configuration model."""
    provider: str  # aws, gcp, azure
    region: str
    project_name: str
    environment: str
    resources: list


class TerraformGenerator:
    """Generate Terraform main.tf, variables.tf, outputs.tf."""
    
    def __init__(self, provider: str = "aws", region: str = "us-east-1"):
        self.provider = provider
        self.region = region
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load Terraform templates."""
        return {
            "aws_provider": """
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
""",
            "variables": """
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "${self.region}"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}
""",
        }
    
    def generate(
        self,
        project_name: str,
        environment: str,
        resources: list,
    ) -> str:
        """
        Generate complete Terraform configuration.
        
        Args:
            project_name: Name of the project
            environment: Environment (dev, staging, prod)
            resources: List of resources to create
        
        Returns:
            Terraform configuration as string
        """
        config = TerraformConfig(
            provider=self.provider,
            region=self.region,
            project_name=project_name,
            environment=environment,
            resources=resources,
        )
        
        tf_code = self._build_configuration(config)
        return tf_code
    
    def _build_configuration(self, config: TerraformConfig) -> str:
        """Build the complete Terraform configuration."""
        lines = []
        
        # Provider section
        lines.append(self.templates["aws_provider"])
        
        # Variables section
        lines.append(self.templates["variables"])
        
        # Resource sections
        for resource in config.resources:
            lines.append(self._generate_resource(resource))
        
        # Outputs section
        lines.append(self._generate_outputs(config.resources))
        
        return "\n".join(lines)
    
    def _generate_resource(self, resource: Dict[str, Any]) -> str:
        """Generate individual resource block."""
        resource_type = resource.get("type", "unknown")
        resource_name = resource.get("name", "resource")
        
        if resource_type == "s3_bucket":
            return f"""
resource "aws_s3_bucket" "{resource_name}" {{
  bucket = "${{var.project_name}}-${{var.environment}}-{resource_name}"
  
  tags = {{
    Name        = "{resource_name}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}
"""
        elif resource_type == "rds_instance":
            return f"""
resource "aws_db_instance" "{resource_name}" {{
  identifier = "${{var.project_name}}-{resource_name}"
  engine     = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  tags = {{
    Name        = "{resource_name}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}
"""
        else:
            return f"# Resource: {resource_type} ({resource_name})\n"
    
    def _generate_outputs(self, resources: list) -> str:
        """Generate outputs section."""
        lines = ["# Outputs"]
        for resource in resources:
            resource_name = resource.get("name", "resource")
            resource_type = resource.get("type", "unknown")
            
            if resource_type == "s3_bucket":
                lines.append(f"""
output "{resource_name}_bucket_name" {{
  value = aws_s3_bucket.{resource_name}.id
}}
""")
        
        return "\n".join(lines)
```

#### Step 2: Register with MCP Server

**File:** `mcp_server/server.py`

```python
from devops_os.core.terraform_generator import TerraformGenerator

@mcp.tool()
def generate_terraform_config(
    project_name: str = "my-project",
    environment: str = "dev",
    cloud_provider: str = "aws",
    region: str = "us-east-1",
    resources: str = "s3_bucket,rds_instance",
) -> str:
    """
    Generate Terraform infrastructure-as-code configuration.
    
    Args:
        project_name: Name of the project
        environment: Environment (dev, staging, prod)
        cloud_provider: Cloud provider (aws, gcp, azure)
        region: Region/location for resources
        resources: Comma-separated list of resources (s3_bucket, rds_instance, vpc, etc.)
    
    Returns:
        Terraform configuration (main.tf + variables.tf + outputs.tf)
    """
    validate_tool_inputs("generate_terraform_config", {
        "project_name": project_name,
        "environment": environment,
        "cloud_provider": cloud_provider,
    })
    
    generator = TerraformGenerator(provider=cloud_provider, region=region)
    
    # Parse resources
    resource_list = [
        {"type": r.strip(), "name": r.strip().replace("_", "")}
        for r in resources.split(",")
    ]
    
    return generator.generate(
        project_name=project_name,
        environment=environment,
        resources=resource_list,
    )
```

#### Step 3: Add to Skill Definitions

**File:** `skills/claude_tools.json`

```json
{
  "name": "generate_terraform_config",
  "description": "Generate Terraform infrastructure-as-code configuration for AWS, GCP, or Azure",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_name": {
        "type": "string",
        "description": "Name of the project",
        "default": "my-project"
      },
      "environment": {
        "type": "string",
        "enum": ["dev", "staging", "prod"],
        "description": "Environment name",
        "default": "dev"
      },
      "cloud_provider": {
        "type": "string",
        "enum": ["aws", "gcp", "azure"],
        "description": "Cloud provider",
        "default": "aws"
      },
      "region": {
        "type": "string",
        "description": "Region for resources (e.g., us-east-1, us-central1)",
        "default": "us-east-1"
      },
      "resources": {
        "type": "string",
        "description": "Comma-separated resource types (s3_bucket, rds_instance, vpc, etc.)",
        "default": "s3_bucket"
      }
    }
  }
}
```

#### Step 4: Write Tests

**File:** `tests/test_terraform_generator.py`

```python
import pytest
from devops_os.core.terraform_generator import TerraformGenerator


def test_generate_terraform_aws():
    """Test Terraform generation for AWS."""
    generator = TerraformGenerator(provider="aws", region="us-east-1")
    
    result = generator.generate(
        project_name="payment-service",
        environment="prod",
        resources=[
            {"type": "s3_bucket", "name": "data"},
            {"type": "rds_instance", "name": "db"},
        ]
    )
    
    # Verify output structure
    assert "terraform {" in result
    assert "provider \"aws\"" in result
    assert "aws_s3_bucket" in result
    assert "aws_db_instance" in result
    assert "output" in result


def test_validate_environment():
    """Test that invalid environments are rejected."""
    with pytest.raises(ValidationError):
        generate_terraform_config(
            project_name="test",
            environment="invalid_env"
        )
```

---

## Integration Patterns

### Pattern 1: Skill Chaining

Generate multiple related configs in sequence:

```python
"""Example: Full stack generation"""

# 1. Generate Terraform infrastructure
response1 = client.messages.create(
    model="claude-opus-4-5",
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Generate Terraform for an AWS RDS database and S3 bucket for dev environment"
    }]
)

# Extract Terraform config
terraform_output = extract_tool_output(response1, "generate_terraform_config")

# 2. Generate Kubernetes manifests that reference the infrastructure
response2 = client.messages.create(
    model="claude-opus-4-5",
    tools=tools,
    messages=[{
        "role": "user",
        "content": f"Generate Kubernetes manifests that connect to the database created by: {terraform_output}"
    }]
)

# 3. Generate GitHub Actions to provision infrastructure
response3 = client.messages.create(
    model="claude-opus-4-5",
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Generate GitHub Actions workflow that applies the Terraform config and deploys to Kubernetes"
    }]
)
```

### Pattern 2: Programmatic Tool Invocation

```python
"""Example: Invoke skills without Claude"""

from mcp_server.server import (
    generate_github_actions_workflow,
    generate_k8s_config,
    generate_sre_configs,
)

# Generate all configs for a microservice
workflow = generate_github_actions_workflow(
    name="payment-api",
    workflow_type="complete",
    languages="python",
    kubernetes=True,
    k8s_method="argocd"
)

manifests = generate_k8s_config(
    app_name="payment-api",
    image="ghcr.io/myorg/payment-api:v1.0",
    replicas=3,
    namespace="production"
)

observability = generate_sre_configs(
    app_name="payment-api",
    alert_type="latency,error_rate",
    slo_target=0.999
)

# Write all to files
with open(".github/workflows/cicd.yml", "w") as f:
    f.write(workflow)

with open("k8s/deployment.yaml", "w") as f:
    f.write(manifests)

with open("observability/sre-config.yaml", "w") as f:
    f.write(observability)
```

### Pattern 3: Skill Wrapping with Custom Logic

```python
"""Example: Wrapper that adds custom pre/post processing"""

def generate_hardened_github_actions(
    name: str,
    languages: str,
    compliance: str = "cis"  # cis, pci-dss, hipaa, sox
) -> str:
    """
    Generate GitHub Actions workflow with security hardening.
    
    1. Generate base workflow
    2. Add SBOM generation (compliance)
    3. Add vulnerability scanning
    4. Add SAST/DAST scanning
    5. Add audit logging
    """
    
    # Step 1: Generate base workflow
    base_workflow = generate_github_actions_workflow(
        name=name,
        languages=languages,
        workflow_type="complete"
    )
    
    # Step 2-5: Inject security stages
    workflow_yaml = yaml.safe_load(base_workflow)
    
    workflow_yaml["jobs"]["security"] = {
        "runs-on": "ubuntu-latest",
        "steps": [
            {
                "name": "Run SBOM generation",
                "run": f"syft {name} -o spdx > sbom.spdx.json"
            },
            {
                "name": "Vulnerability scan",
                "run": "grype sbom.spdx.json"
            },
            {
                "name": "SAST scan",
                "run": "semgrep --config=p/security-audit"
            },
            {
                "name": "Audit logs",
                "run": "echo 'Security scan complete' | auditd"
            }
        ]
    }
    
    return yaml.dump(workflow_yaml)
```

---

## Testing Skills

### Unit Tests

**File:** `tests/test_my_skill.py`

```python
import pytest
from mcp_server.server import generate_my_skill
from mcp_server.validators import validate_tool_inputs, ValidationError


class TestMySkill:
    """Test suite for my-skill."""
    
    def test_generate_with_defaults(self):
        """Test skill with default parameters."""
        result = generate_my_skill()
        assert result is not None
        assert len(result) > 0
    
    def test_generate_with_custom_params(self):
        """Test skill with custom parameters."""
        result = generate_my_skill(
            name="custom-app",
            param1="option1"
        )
        assert "custom-app" in result
        assert "option1" in result
    
    def test_validate_invalid_params(self):
        """Test validation rejects invalid inputs."""
        with pytest.raises(ValidationError):
            validate_tool_inputs("generate_my_skill", {
                "param1": "invalid_value"
            })
    
    def test_output_format(self):
        """Test output is valid YAML/JSON."""
        result = generate_my_skill(name="test")
        import yaml
        parsed = yaml.safe_load(result)
        assert parsed is not None


# Run tests
# pytest tests/test_my_skill.py -v
```

### Integration Tests

**File:** `tests/test_skill_integration.py`

```python
def test_github_actions_+ _k8s_integration():
    """Test that generated GitHub Actions works with generated K8s config."""
    
    # Generate GitHub Actions workflow
    workflow = generate_github_actions_workflow(
        name="test-app",
        kubernetes=True,
        k8s_method="kubectl"
    )
    
    # Generate K8s manifests
    k8s = generate_k8s_config(
        app_name="test-app",
        image="test-app:latest"
    )
    
    # Verify integration points
    assert "kubectl" in workflow  # Workflow uses kubectl
    assert "apiVersion" in k8s  # K8s is valid manifests
    assert "test-app" in workflow  # Same app name
```

### Performance Tests

```python
import time

def test_skill_performance():
    """Ensure skill generation completes in reasonable time."""
    start = time.time()
    
    result = generate_github_actions_workflow(
        name="perf-test",
        workflow_type="complete",
        languages="python,javascript,java"
    )
    
    elapsed = time.time() - start
    
    assert elapsed < 5.0  # Must complete in under 5 seconds
    assert len(result) > 100  # Must generate meaningful output
```

---

## Deployment

### Development Environment

```bash
# Install in development mode
pip install -e .
pip install -r mcp_server/requirements.txt

# Run MCP server locally
python -m mcp_server.server

# Test with Claude Desktop
# Edit ~/.config/Claude/claude_desktop_config.json
# Restart Claude
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN pip install -r mcp_server/requirements.txt

# Run MCP server
CMD ["python", "-m", "mcp_server.server"]
```

```bash
docker build -t devops-os-mcp .
docker run -e DEVOPS_OS_TRANSPORT=streamable-http devops-os-mcp
```

### Production Deployment

See `GETTING-STARTED-MCP.md` for:
- JWT authentication setup
- HTTPS configuration
- Rate limiting
- Scaling considerations

---

## Performance & Optimization

### Caching Generated Configs

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def generate_github_actions_workflow_cached(
    name: str,
    workflow_type: str,
    languages: str,
    kubernetes: bool,
) -> str:
    """Cache generated workflows to avoid recomputation."""
    # ... generation logic
```

### Async Skill Invocation

```python
import asyncio

async def generate_multiple_configs():
    """Generate configs concurrently."""
    
    tasks = [
        asyncio.create_task(
            asyncio.to_thread(generate_github_actions_workflow, ...)
        ),
        asyncio.create_task(
            asyncio.to_thread(generate_k8s_config, ...)
        ),
        asyncio.create_task(
            asyncio.to_thread(generate_sre_configs, ...)
        ),
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

---

## Monitoring & Debugging

### Logging

```python
from mcp_server.logging import get_logger

logger = get_logger(__name__)

def generate_my_skill(name: str) -> str:
    logger.info("Generating my-skill", extra={"name": name})
    
    try:
        result = _do_generation(name)
        logger.info("Successfully generated", extra={"size": len(result)})
        return result
    except Exception as e:
        logger.error("Generation failed", extra={"error": str(e)})
        raise
```

### Debugging MCP Server

```bash
# Enable debug logging
export DEVOPS_OS_LOG_LEVEL=DEBUG
python -m mcp_server.server

# Check correlation ID for request tracing
grep "correlation_id=abc123" logs/mcp.log
```

---

**Last Updated:** October 2, 2026  
**DevOps-OS MCP Version:** 0.4.7
