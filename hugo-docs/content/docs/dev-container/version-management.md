---
title: "Version Management"
description: "Manage programming language and tool versions via environment variables with security-aware recommendations"
weight: 40
---

## Overview

DevOps-OS provides a comprehensive version management system for dev containers that allows you to:

- **Track and manage versions** of programming languages and tools via environment variables
- **Receive security recommendations** for outdated or vulnerable versions
- **Use LTS or latest versions** based on your release strategy
- **Persist version preferences** to `.env` files for team consistency
- **Update versions programmatically** via MCP tools

## Environment Variables

All version configuration uses the `DEVOPS_OS_VERSION_` prefix for environment variables. Set these in your shell profile, Docker environment, or `.env` file.

### Supported Tools and Default Versions

#### Programming Languages

| Tool | Default | Latest | LTS Versions |
|------|---------|--------|--------------|
| python | 3.12 | 3.13 | 3.12, 3.11, 3.10 |
| node | 22 | 23 | 22, 20, 18 |
| java | 21 | 23 | 21, 17, 11 |
| go | 1.25.0 | 1.25.0 | 1.25.0, 1.24.0 |
| rust | 1.81.0 | 1.81.0 | 1.81.0 |
| ruby | 3.3 | 3.4 | 3.3, 3.2 |
| csharp | 8.0 | 8.0 | 8.0 |
| php | 8.3 | 8.3 | 8.3 |

#### CI/CD and DevOps Tools

| Tool | Default | Latest | LTS Versions |
|------|---------|--------|--------------|
| docker | 27.0.0 | 27.0.0 | 27.0.0, 26.0.0 |
| kubectl | 1.31.0 | 1.31.0 | 1.31.0, 1.30.0 |
| helm | 3.16.0 | 3.16.0 | 3.16.0, 3.15.0 |
| terraform | 1.9.0 | 1.9.0 | 1.9.0, 1.8.0 |
| prometheus | 3.5.1 | 3.5.1 | 3.5.1, 3.4.0 |
| grafana | 12.4.2 | 12.4.2 | 12.4.2, 11.5.0 |

### Setting Environment Variables

#### Option 1: Shell Profile

Add to your `.bashrc`, `.zshrc`, or similar:

```bash
export DEVOPS_OS_VERSION_PYTHON=3.12
export DEVOPS_OS_VERSION_GO=1.25.0
export DEVOPS_OS_VERSION_NODE=22
export DEVOPS_OS_VERSION_DOCKER=27.0.0
```

#### Option 2: .env File

Create a `.env` file in your project:

```env
# Programming Languages
DEVOPS_OS_VERSION_PYTHON=3.12
DEVOPS_OS_VERSION_NODE=22
DEVOPS_OS_VERSION_JAVA=21
DEVOPS_OS_VERSION_GO=1.25.0
DEVOPS_OS_VERSION_RUST=1.81.0
DEVOPS_OS_VERSION_RUBY=3.3

# DevOps Tools
DEVOPS_OS_VERSION_DOCKER=27.0.0
DEVOPS_OS_VERSION_KUBECTL=1.31.0
DEVOPS_OS_VERSION_TERRAFORM=1.9.0
```

#### Option 3: Docker Build Args

In your `devcontainer.json`:

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "args": {
      "DEVOPS_OS_VERSION_PYTHON": "3.13",
      "DEVOPS_OS_VERSION_GO": "1.25.0",
      "DEVOPS_OS_VERSION_NODE": "22"
    }
  }
}
```

## Using MCP Tools for Version Management

### Get Current Version Configuration

Retrieve the currently configured versions for any tool:

```bash
get_version_config(tools="python,go,node")
```

Response:
```json
{
  "current_versions": {
    "python": "3.12",
    "go": "1.25.0",
    "node": "22"
  },
  "tools_info": {
    "python": {
      "current": "3.12",
      "default": "3.12",
      "latest": "3.13",
      "lts": ["3.12", "3.11", "3.10"],
      "status": "lts"
    },
    "go": {
      "current": "1.25.0",
      "default": "1.25.0",
      "latest": "1.25.0",
      "lts": ["1.25.0", "1.24.0"],
      "status": "latest"
    }
  }
}
```

### Check for Available Updates

Find out which tools have newer versions available:

```bash
check_version_updates(tools="python,java,docker")
```

Response:
```json
{
  "available_updates": {
    "python": {
      "tool": "python",
      "current": "3.10",
      "latest": "3.13",
      "can_update": true,
      "can_update_lts": true,
      "status": "stable",
      "security_level": "deprecated"
    },
    "java": {
      "tool": "java",
      "current": "21",
      "latest": "23",
      "can_update": true,
      "status": "lts",
      "security_level": "stable"
    }
  },
  "security_updates": {
    "python": {
      "current": "3.10",
      "current_security": "deprecated",
      "recommended": "3.13",
      "urgency": "medium",
      "reason": "Current version has deprecated security issues"
    }
  },
  "summary": {
    "tools_checked": 3,
    "updates_available": 2,
    "security_issues": 1
  }
}
```

### Get Version Suggestions

Get recommended versions based on your release strategy:

```bash
# Get latest stable versions
suggest_versions(tools="python,java,node", prefer_lts=false)

# Get LTS versions
suggest_versions(tools="python,java,node", prefer_lts=true)
```

Response:
```json
{
  "suggested_versions": {
    "python": "3.13",
    "java": "23",
    "node": "23"
  },
  "current_versions": {
    "python": "3.12",
    "java": "21",
    "node": "22"
  },
  "strategy": "latest-stable",
  "recommendations": [
    {
      "tool": "python",
      "current": "3.12",
      "suggested": "3.13",
      "rationale": "Latest stable version for python"
    }
  ]
}
```

### Update Tool Versions

Update versions in your environment variables:

```bash
update_versions('{"python": "3.13", "go": "1.25.0", "docker": "27.0.0"}')
```

Response:
```json
{
  "success": true,
  "updates": {
    "python": {
      "requested": "3.13",
      "success": true
    },
    "go": {
      "requested": "1.25.0",
      "success": true
    },
    "docker": {
      "requested": "27.0.0",
      "success": true
    }
  },
  "new_versions": {
    "python": "3.13",
    "go": "1.25.0",
    "docker": "27.0.0"
  },
  "errors": []
}
```

### Check Security Issues

Identify critical security issues in your tool versions:

```bash
check_security_issues(tools="python,java,docker")
```

Response:
```json
{
  "security_assessment": {
    "critical": {
      "python": {
        "current": "3.8",
        "current_security": "critical",
        "recommended": "3.13",
        "urgency": "critical"
      }
    },
    "high": {},
    "medium": {
      "java": {
        "current": "11",
        "current_security": "deprecated",
        "recommended": "21",
        "urgency": "medium"
      }
    },
    "low": {}
  },
  "summary": {
    "tools_checked": 3,
    "with_issues": 2,
    "critical_count": 1,
    "high_count": 0
  },
  "current_versions": {
    "python": "3.8",
    "java": "11",
    "docker": "27.0.0"
  }
}
```

## Security Status Levels

Understanding version security status helps you prioritize updates:

### Status Definitions

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **latest** | Current release version | Optional update, typically safe |
| **lts** | Long-Term Support version | Stable, recommended for production |
| **stable** | Supported release | Stable, safe to use |
| **deprecated** | Older version, still supported | Update recommended within 6-12 months |
| **eol** | End-of-Life, no longer supported | Update immediately |

### Security Levels

| Level | Urgency | Description | Action |
|-------|---------|-------------|--------|
| **stable** | Low | No known security issues | No action needed |
| **high** | High | Known high-severity vulnerabilities | Update within weeks |
| **deprecated** | Medium | Version approaching EOL | Plan upgrade within months |
| **critical** | Critical | Active, exploitable vulnerabilities | Update immediately |

## Common Workflows

### 1. Audit Current Versions

Check what versions are currently configured:

```bash
get_version_config()  # Get all tools
get_version_config(tools="python,go")  # Specific tools
```

### 2. Plan Security Updates

Identify and plan security updates:

```bash
check_security_issues()  # Check all
check_security_issues(tools="python,java,docker")  # Specific tools
```

### 3. Upgrade to LTS Versions

Get LTS version recommendations and update:

```bash
suggest_versions(prefer_lts=true)  # Get LTS suggestions
update_versions('{"python": "3.12", "java": "21", "node": "22"}')
```

### 4. Adopt Latest Stable Versions

Stay up-to-date with latest releases:

```bash
check_version_updates()  # See what's available
suggest_versions(prefer_lts=false)  # Get latest suggestions
update_versions('{"python": "3.13", "java": "23", "go": "1.25.0"}')
```

### 5. Configure Team Standards

Create a `.env` file for your team to ensure consistency:

```env
# .env - Team DevOps Standards
DEVOPS_OS_VERSION_PYTHON=3.12
DEVOPS_OS_VERSION_NODE=22
DEVOPS_OS_VERSION_JAVA=21
DEVOPS_OS_VERSION_GO=1.25.0
DEVOPS_OS_VERSION_DOCKER=27.0.0
DEVOPS_OS_VERSION_KUBECTL=1.31.0
DEVOPS_OS_VERSION_TERRAFORM=1.9.0
DEVOPS_OS_VERSION_PROMETHEUS=3.5.1
```

Commit this to your repository and load it in your dev container.

## Integration with scaffold_devcontainer

When generating a dev container configuration, version environment variables are automatically respected:

```bash
scaffold_devcontainer(
  languages="python,go,java",
  cicd_tools="docker,github_actions",
  python_version="3.13",  # Override default
  go_version="1.25.0",
  java_version="21"
)
```

The tool will:
1. Check for environment variables (`DEVOPS_OS_VERSION_*`)
2. Use provided parameters if specified
3. Fall back to defaults from the version database
4. Generate the dev container with specified versions

## Version Validation

The version manager validates versions against the known version database:

- ✓ Exact versions (e.g., "3.12", "1.25.0") are validated
- ✓ LTS versions can be queried
- ✓ Version comparison handles multi-part versions
- ✗ Arbitrary versions are rejected
- ✗ EOL versions trigger security warnings

Example validation:
```bash
update_versions('{"python": "3.15"}')  # Invalid - not in database
# Response: {"success": false, "errors": [{"tool": "python", "message": "Failed to update python"}]}

update_versions('{"python": "3.13"}')  # Valid
# Response: {"success": true, ...}
```

## Persisting Configuration

Save your version configuration to a `.env` file for persistence:

```bash
from mcp_server.version_manager import VersionManager

vm = VersionManager()
versions = {
    "python": "3.13",
    "go": "1.25.0",
    "java": "21",
    "node": "22",
    "docker": "27.0.0"
}
vm.save_env_file(".env", versions)
```

Then load it in your dev container:

```dockerfile
RUN if [ -f .env ]; then set -a && source .env && set +a; fi
```

## Best Practices

1. **Use LTS versions for production** - They receive security updates longer
2. **Keep versions synchronized across teams** - Use `.env` files in git
3. **Check security issues regularly** - Use `check_security_issues()` weekly
4. **Test before upgrading major versions** - Use `suggest_versions()` for planning
5. **Document version choices** - Add comments to your `.env` file explaining why
6. **Automate version updates** - Use MCP tools in CI/CD pipelines
7. **Review security advisories** - Monitor updates from tool maintainers

## Troubleshooting

### Environment Variables Not Loading

Ensure variables are exported before using MCP tools:

```bash
export DEVOPS_OS_VERSION_PYTHON=3.13
source .env  # If using .env file
```

### Invalid Version Error

Check that the version exists in the database:

```bash
get_version_config(tools="python")  # See available versions
# The "lts" and "latest" fields show valid versions
```

### Version Not Changing

Verify the update was successful:

```bash
update_versions('{"python": "3.13"}')  # Returns success status
get_version_config(tools="python")  # Verify new version
```

## Related Documentation

- [MCP Setup Guide](../mcp-setup/) - Configure MCP for dev containers
- [Language Guides](../language-guides/) - Language-specific configuration
- [Development Containers](../) - Overview of dev container setup
