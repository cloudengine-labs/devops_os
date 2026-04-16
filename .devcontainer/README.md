# Devcontainer Status

The checked-in repo-local devcontainer stack has been retired.

Active generation paths:

- `python -m cli.devopsos init` on a fresh target generates `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.devcontainer/devcontainer.env.json` from templates.
- `python -m cli.devopsos scaffold devcontainer` generates the legacy two-file `.devcontainer/devcontainer.json` and `.devcontainer/devcontainer.env.json`.

Active source files:

- `cli/devcontainer_templates.py`
- `cli/templates/devcontainer/`
- `cli/scaffold_devcontainer.py`

Archived legacy implementation:

- `.legacy/devcontainer/`
