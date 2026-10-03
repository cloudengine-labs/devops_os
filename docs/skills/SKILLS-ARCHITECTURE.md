# DevOps-OS Skills Architecture

**Complete technical documentation of the DevOps-OS AI Skills system, including architecture, skill lifecycle, and extension patterns.**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Layers](#architecture-layers)
3. [Skill Lifecycle](#skill-lifecycle)
4. [Data Flow](#data-flow)
5. [Skill Definitions](#skill-definitions)
6. [Integration Points](#integration-points)
7. [Adding New Skills](#adding-new-skills)
8. [Validation & Testing](#validation--testing)

---

## Overview

DevOps-OS **Skills** are tool/function definitions that expose DevOps-OS generators as AI-callable endpoints. They form the bridge between natural language prompts and production-ready infrastructure configurations.

### Key Components

```
┌──────────────────────────────────────────────────────────────────┐
│                        AI Assistants                             │
│            (Claude, ChatGPT, Cursor, VS Code Copilot)            │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                     Skill Definitions (JSON)                     │
│  ┌──────────────────────┐    ┌───────────────────────────────┐   │
│  │  claude_tools.json   │    │  openai_functions.json        │   │
│  │  (Anthropic format)  │    │  (OpenAI format)              │   │
│  └──────────────────────┘    └───────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              MCP Server / API Gateway                             │
│                  (mcp_server/server.py)                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              Skill Implementation Functions                       │
│  - generate_github_actions_workflow()                            │
│  - generate_jenkins_pipeline()                                   │
│  - generate_k8s_config()                                         │
│  - scaffold_devcontainer()                                       │
│  - generate_gitlab_ci_pipeline()                                 │
│  - generate_argocd_config()                                      │
│  - generate_sre_configs()                                        │
│  - generate_unittest_config()                                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              DevOps-OS Core Generators                            │
│                 (devops_os/core/)                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Architecture Layers

### 1. **Skill Definition Layer** (`skills/`)

**Purpose:** Define what capabilities are exposed to AI systems.

**Files:**
- `claude_tools.json` — Anthropic tool format (JSON Schema)
- `openai_functions.json` — OpenAI function format (JSON Schema)

**Structure:**
```json
{
  "name": "skill_identifier",
  "description": "What this skill does",
  "input_schema": {
    "type": "object",
    "properties": {
      "parameter_name": {
        "type": "string|number|boolean",
        "description": "Parameter description",
        "enum": ["option1", "option2"],
        "default": "default_value"
      }
    },
    "required": ["required_params"]
  }
}
```

**Key Design Principles:**
- **Discoverability:** Descriptions are clear enough for AI to understand without documentation
- **Flexibility:** Input parameters are optional with sensible defaults
- **Constraint:** Enums limit AI creativity to validated choices
- **Consistency:** Same skill available in both Claude and OpenAI formats

---

### 2. **Gateway Layer** (`mcp_server/server.py`)

**Purpose:** Receive skill invocations and route them to implementations.

**Implementation Pattern:**
```python
@mcp_server.tool()
def generate_github_actions_workflow(
    name: str = "my-app",
    workflow_type: str = "complete",
    languages: str = "python",
    kubernetes: bool = False,
    k8s_method: str = "kubectl",
    branches: str = "main",
    matrix: bool = False,
) -> str:
    """Docstring becomes the skill description in JSON definitions."""
    # 1. Parse and validate inputs
    # 2. Call core generator
    # 3. Return YAML or JSON as string
```

**Key Responsibilities:**
- Input validation (via `validators.py`)
- Correlation ID tracking (for debugging)
- Response enhancement (prompt suggestions)
- Error handling and logging
- Concurrency management

---

### 3. **Core Generator Layer** (`devops_os/core/`)

**Purpose:** Implement the actual generation logic.

**Pattern:**
```python
# devops_os/core/github_actions_generator.py

class GitHubActionsGenerator:
    def __init__(self, config):
        self.config = config
    
    def generate(self, name, workflow_type, languages, ...):
        # 1. Build workflow structure
        # 2. Add stages (build, test, deploy)
        # 3. Configure language-specific steps
        # 4. Add Kubernetes deployment if requested
        # 5. Return YAML string
        return yaml.dump(workflow)
```

**Key Patterns:**
- Template-based generation (YAML/Jinja2)
- Configuration composition (build modules, add language, add K8s)
- Process-First integration (encoding best practices)
- Immutable defaults (sensible starting points)

---

## Skill Lifecycle

### Phase 1: Definition
```
1. Identify new DevOps capability needed
   ↓
2. Define as JSON schema in claude_tools.json
   ↓
3. Add parallel definition to openai_functions.json
   ↓
4. Document in skills/README.md
```

### Phase 2: Implementation
```
1. Create generator class in devops_os/core/
   ↓
2. Implement in mcp_server/server.py as @mcp_server.tool()
   ↓
3. Add input validation rules to validators.py
   ↓
4. Write unit tests in tests/
```

### Phase 3: Integration
```
1. Test with Claude API (claude_tools.json)
   ↓
2. Test with OpenAI API (openai_functions.json)
   ↓
3. Add example prompts to documentation
   ↓
4. Update README, GETTING-STARTED-MCP.md
```

### Phase 4: Deployment
```
1. Commit to main branch
   ↓
2. Tag release (semantic versioning)
   ↓
3. Users git pull to get new skills
   ↓
4. Restart MCP server / Claude Desktop
```

---

## Data Flow

### Request Flow

```
User Prompt (Natural Language)
    ↓
AI System (Claude/ChatGPT)
    ↓
    Matches prompt to skill
    ↓
    Calls skill with parameters
    ↓
MCP Server / API Endpoint
    ↓
    Validates inputs (validators.py)
    ↓
    Logs request (logging.py, correlation_id)
    ↓
Core Generator
    ↓
    Builds configuration
    ↓
    Applies Process-First principles
    ↓
ResponseEnhancer
    ↓
    Adds prompt suggestions
    ↓
    Formats output
    ↓
AI System (receives response)
    ↓
    Presents to user with explanation
    ↓
User (gets production-ready YAML + explanation)
```

### Response Format

**Skill Response (from MCP server):**
```python
{
    "generated_config": "---\napiVersion: v1\nkind: Deployment\n...",
    "format": "yaml",
    "type": "kubernetes_deployment",
    "prompt_suggestions": [
        {
            "suggestion_text": "Consider adding resource limits for production",
            "suggestion_category": "best_practice",
            "confidence": "high"
        }
    ],
    "explanation": "This Deployment includes..."
}
```

---

## Skill Definitions

### Core Skills (v0.4.7)

| Skill | Generator | Input Parameters | Output Format |
|-------|-----------|------------------|---------------|
| `generate_github_actions_workflow` | `GitHubActionsGenerator` | name, workflow_type, languages, kubernetes, k8s_method, branches, matrix | YAML |
| `generate_jenkins_pipeline` | `JenkinsGenerator` | name, pipeline_type, languages, kubernetes, k8s_method, parameters | Groovy |
| `generate_gitlab_ci_pipeline` | `GitLabCIGenerator` | name, pipeline_type, languages, kubernetes, k8s_method | YAML |
| `generate_k8s_config` | `KubernetesGenerator` | app_name, image, replicas, port, namespace, deploy_method | YAML |
| `generate_argocd_config` | `ArgoCDGenerator` | app_name, repo_url, path, namespace, deploy_method, enable_canary | YAML |
| `generate_sre_configs` | `SREGenerator` | app_name, alert_type, metrics, slo_target | YAML (multi-file) |
| `scaffold_devcontainer` | `DevContainerGenerator` | languages, tools, extensions | JSON + .env |
| `generate_unittest_config` | `UnitTestGenerator` | app_name, language, test_framework, ci_integration | YAML/JSON config |

### Skill Parameter Types

**Enums (Validated Choices):**
- `workflow_type`: "build", "test", "deploy", "complete", "reusable"
- `languages`: Comma-separated from: "python", "javascript", "java", "go", "ruby", "php", "rust"
- `k8s_method`: "kubectl", "kustomize", "argocd", "flux"
- `deploy_method`: "kubectl", "kustomize", "helm", "argocd", "flux"

**Strings (Free-form):**
- `name`: Application name
- `app_name`: Application name
- `repo_url`: Git repository URL
- `image`: Docker image URI

**Booleans (Features):**
- `kubernetes`: Enable Kubernetes deployment stage
- `matrix`: Enable matrix builds across OS/versions
- `parameters`: Enable parameterized builds (Jenkins)
- `enable_canary`: Enable canary deployments (ArgoCD)

---

## Integration Points

### 1. **Claude Desktop / API**

**Integration Method:** Load `claude_tools.json`

```python
import anthropic
import json

with open("skills/claude_tools.json") as f:
    tools = json.load(f)

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-5",
    tools=tools,
    messages=[{"role": "user", "content": "..."}]
)

# Tool invocation via MCP server
```

**Protocol:** Model Context Protocol (stdio, HTTP, WebSocket)

---

### 2. **OpenAI / ChatGPT**

**Integration Method:** Load `openai_functions.json`

```python
from openai import OpenAI
import json

with open("skills/openai_functions.json") as f:
    tools = json.load(f)

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    tools=tools,
    messages=[{"role": "user", "content": "..."}]
)

# Tool invocation via API or MCP server
```

**Protocol:** OpenAI Function Calling API

---

### 3. **Custom GPT Actions**

**Integration Method:** Expose MCP server as HTTP endpoint + OpenAPI schema

```yaml
# Generated OpenAPI spec from skills
openapi: 3.1.0
paths:
  /tools/generate_github_actions_workflow:
    post:
      parameters: [from claude_tools.json schema]
```

---

### 4. **IDE Integration**

**Cursor IDE, VS Code Copilot, Windsurf, Zed:**

Uses MCP protocol to communicate with local MCP server.

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/devops_os"
    }
  }
}
```

---

## Adding New Skills

### Step-by-Step Process

#### 1. Create the Generator Class

**File:** `devops_os/core/my_generator.py`

```python
class MyGenerator:
    def generate(self, param1: str, param2: bool, ...) -> str:
        """
        Generate my-skill configuration.
        
        Args:
            param1: Description
            param2: Description
        
        Returns:
            Configuration as YAML/JSON string
        """
        config = {}
        # ... build config
        return yaml.dump(config)
```

#### 2. Implement in MCP Server

**File:** `mcp_server/server.py`

```python
from devops_os.core.my_generator import MyGenerator

@mcp.tool()
def generate_my_config(
    name: str = "my-app",
    param1: str = "default",
    param2: bool = False,
) -> str:
    """Generate my-skill configuration."""
    generator = MyGenerator()
    return generator.generate(name=name, param1=param1, param2=param2)
```

#### 3. Add Input Validation

**File:** `mcp_server/validators.py`

```python
def validate_my_config_inputs(inputs):
    # Validate that param1 is one of allowed values
    # Validate param2 constraint
    # Return cleaned inputs or raise ValidationError
    pass
```

#### 4. Define JSON Schema for Claude

**File:** `skills/claude_tools.json`

```json
{
  "name": "generate_my_config",
  "description": "Generate my-skill configuration.",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Application name",
        "default": "my-app"
      },
      "param1": {
        "type": "string",
        "enum": ["option1", "option2"],
        "description": "Param1 description",
        "default": "option1"
      },
      "param2": {
        "type": "boolean",
        "description": "Enable param2",
        "default": false
      }
    },
    "required": []
  }
}
```

#### 5. Define for OpenAI

**File:** `skills/openai_functions.json`

```json
{
  "type": "function",
  "function": {
    "name": "generate_my_config",
    "description": "Generate my-skill configuration.",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Application name"
        },
        "param1": {
          "type": "string",
          "enum": ["option1", "option2"],
          "description": "Param1 description"
        },
        "param2": {
          "type": "boolean",
          "description": "Enable param2"
        }
      },
      "required": []
    }
  }
}
```

#### 6. Write Tests

**File:** `tests/test_my_generator.py`

```python
def test_generate_my_config():
    result = generate_my_config(name="test", param1="option1")
    assert "expected_field" in result
    assert result is not None
```

#### 7. Update Documentation

- Add to `skills/README.md`
- Add example prompt to `PROMPT_SUGGESTIONS.md`
- Add to `GETTING-STARTED-MCP.md`

---

## Validation & Testing

### Input Validation

**All skills validate inputs before processing:**

```python
# validators.py
def validate_tool_inputs(tool_name: str, inputs: dict) -> dict:
    """Validate and normalize skill inputs."""
    
    if tool_name == "generate_github_actions_workflow":
        # Validate workflow_type is in enum
        if inputs.get("workflow_type") not in ["build", "test", "deploy", "complete"]:
            raise ValidationError("Invalid workflow_type")
        
        # Validate languages are supported
        supported = {"python", "javascript", "java", "go", "ruby", "php"}
        langs = set(inputs.get("languages", "").split(","))
        if not langs.issubset(supported):
            raise ValidationError(f"Unsupported languages: {langs - supported}")
    
    return inputs
```

### Testing Strategy

**Unit Tests:** Each generator has unit tests in `tests/`

```python
pytest tests/ -v
```

**MCP Protocol Tests:** Verify tools work via MCP server

```python
pytest mcp_server/test_server.py -v
```

**Integration Tests:** Test full end-to-end flow

```python
pytest tests/test_comprehensive.py -v
```

---

## Best Practices

### Skill Design

1. **Keep Descriptions Clear** — AI must understand without external docs
2. **Use Sensible Defaults** — Users shouldn't have to specify everything
3. **Provide Enums for Constrained Values** — Prevents invalid inputs
4. **Document Required vs. Optional** — Set `required` array in schema
5. **Version Skills Carefully** — Breaking changes require major version bump

### Implementation

1. **Validate Early** — Check inputs before expensive operations
2. **Fail Fast** — Return meaningful error messages
3. **Encode Best Practices** — Each skill should teach DevOps patterns
4. **Support Multiple Patterns** — Different teams, different needs
5. **Test Thoroughly** — Unit, integration, and end-to-end tests

### Documentation

1. **Example Prompts** — Show what prompts generate what configs
2. **Parameter Guide** — Explain each parameter and its options
3. **Output Format** — Describe what the user receives
4. **Use Cases** — When to use this skill
5. **Limitations** — What this skill doesn't do (yet)

---

## References

- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Anthropic Tools:** [Anthropic API Docs](https://docs.anthropic.com/claude/reference/tool-use)
- **OpenAI Functions:** [OpenAI API Docs](https://platform.openai.com/docs/guides/function-calling)
- **Process-First Philosophy:** See `docs/getting-started/PROCESS-FIRST.md`

---

**Last Updated:** October 2, 2026  
**Version:** DevOps-OS MCP 0.4.7
