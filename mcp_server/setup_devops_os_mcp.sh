#!/bin/bash
# setup_devops_os_mcp.sh
# One-command setup: clones devops_os, creates a Python venv, installs deps,
# and registers the MCP server with Claude Code.
#
# Usage:
#   # Install from GitHub (default) — clones into ~/devops_os
#   bash setup_devops_os_mcp.sh
#
#   # Use a custom install directory
#   INSTALL_DIR=~/my/path bash setup_devops_os_mcp.sh
#
#   # Already inside a clone? Register without re-cloning
#   bash mcp_server/setup_devops_os_mcp.sh --local
#
#   # Combine: specify directory and skip clone
#   INSTALL_DIR=/opt/devops_os bash setup_devops_os_mcp.sh --local

set -e

REPO_URL="https://github.com/cloudengine-labs/devops_os.git"
LOCAL_MODE=false

# --- Parse flags ---
for arg in "$@"; do
  case "$arg" in
    --local) LOCAL_MODE=true ;;
    --help|-h)
      sed -n '2,15p' "$0" | sed 's/^# //'
      exit 0
      ;;
  esac
done

# --- Resolve install directory ---
if [ "$LOCAL_MODE" = true ]; then
  # Use the repo that contains this script
  INSTALL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  echo "==> Local mode: using existing clone at $INSTALL_DIR"
else
  INSTALL_DIR="${INSTALL_DIR:-$HOME/devops_os}"
fi

# --- Check Python ---
PYTHON="${PYTHON:-$(which python3 2>/dev/null || which python 2>/dev/null)}"
if [ -z "$PYTHON" ]; then
  echo "Error: Python 3.10+ is required but was not found in PATH." >&2
  echo "Install it from https://www.python.org/downloads/ and re-run this script." >&2
  exit 1
fi

PYTHON_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "==> Using Python $PYTHON_VERSION at $PYTHON"

# --- Clone or update repo (skipped in local mode) ---
if [ "$LOCAL_MODE" = false ]; then
  if [ -d "$INSTALL_DIR/.git" ]; then
    echo "==> Repo already exists at $INSTALL_DIR — pulling latest..."
    git -C "$INSTALL_DIR" pull
  else
    echo "==> Cloning devops_os into $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
  fi
fi

# --- Create venv if not present ---
VENV_DIR="$INSTALL_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating Python virtual environment..."
  "$PYTHON" -m venv "$VENV_DIR"
fi

# --- Install dependencies ---
echo "==> Installing MCP server dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$INSTALL_DIR/mcp_server/requirements.txt"

VENV_PYTHON="$VENV_DIR/bin/python"

# --- Register with Claude Code ---
if claude mcp list 2>/dev/null | grep -q "^devops-os"; then
  echo "==> Removing existing devops-os entry to avoid duplicates..."
  claude mcp remove devops-os
fi

echo "==> Registering devops-os MCP server with Claude Code..."
claude mcp add --transport stdio devops-os --scope user \
  -- "$VENV_PYTHON" -m mcp_server.server \
  --env PYTHONPATH="$INSTALL_DIR"

echo ""
echo "✓ devops-os MCP server registered!"
echo ""
echo "  Verify : claude mcp list"
echo "  Test   : claude"
echo "           > Generate a GitHub Actions workflow for a Python app"
echo ""
echo "  To add to other tools see: $INSTALL_DIR/mcp_server/README.md"
