# Devcontainer Status

Active generation paths:

- `python -m devops_os.core.scaffold_devcontainer` on a fresh target generates `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.devcontainer/devcontainer.env.json` from templates.
- MCP server exposes `scaffold_devcontainer` tool for AI assistants (Claude, ChatGPT, Cursor)

Active source files:

- `devops_os/core/devcontainer_templates.py`
- `devops_os/core/scaffold_devcontainer.py`
- `mcp_server/server.py` (MCP tool integration)
