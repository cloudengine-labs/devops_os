# DevOps-OS Manual Smoke Testing

This guide is for fast local validation of the main DevOps-OS feature surface without running the full pytest suite.

Use it when you want to verify:

- CLI scaffold generators still run end-to-end
- `devopsos init` still generates the template-backed devcontainer set
- MCP tool functions still return valid-looking output

This is a smoke check, not exhaustive coverage.

## What It Covers

The smoke script validates:

- `scaffold gha`
- `scaffold jenkins`
- `scaffold gitlab`
- `scaffold argocd`
- `scaffold sre`
- `scaffold devcontainer`
- `scaffold cicd`
- `scaffold unittest`
- `process-first`
- `init`
- MCP tool functions in `mcp_server/server.py`

It runs entirely in temporary directories and does not modify repo-tracked files.

## Prerequisites

Install the same local dependencies used by the CLI and MCP server:

```bash
pip install -r cli/requirements.txt -r mcp_server/requirements.txt
```

If you also want the full automated suite:

```bash
pip install pytest pytest-html
```

## Run the Smoke Script

From the repository root:

```bash
python scripts/manual_test_devops_os.py
```

If your local environment does not have MCP dependencies installed yet, you can still run the CLI and `init` smoke checks:

```bash
python scripts/manual_test_devops_os.py --skip-mcp
```

If you want to inspect the generated files afterwards:

```bash
python scripts/manual_test_devops_os.py --keep-temp
```

The script prints a `PASS` line for each validated surface and ends with:

```text
All manual smoke tests passed.
```

## What the Script Actually Verifies

- CLI commands exit successfully
- expected output files are created
- key generated content looks structurally correct
- `init` still creates:
  - `.devcontainer/Dockerfile`
  - `.devcontainer/devcontainer.json`
  - `.devcontainer/devcontainer.env.json`
- `scaffold devcontainer` still creates only:
  - `.devcontainer/devcontainer.json`
  - `.devcontainer/devcontainer.env.json`
- MCP functions return parseable JSON or expected YAML/text fragments

If MCP dependencies are missing and you did not pass `--skip-mcp`, the script fails fast with an install hint.

## Manual Checks Still Worth Doing

The script does not replace these higher-confidence checks:

1. Rebuild a generated devcontainer in VS Code or Cursor.
2. Run the full pytest suite:

```bash
python -m pytest cli/test_cli.py mcp_server/test_server.py tests/test_comprehensive.py -v
```

3. If you changed MCP setup or editor integration, validate one real client config:
   - `.cursor/mcp.json`
   - `.claude/settings.local.json`
   - VS Code MCP config

## When to Use This

Use this script before a commit when you changed:

- CLI command wiring
- scaffold generators
- devcontainer generation
- MCP tool wrappers
- docs that describe command behavior and expected outputs
