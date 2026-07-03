#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/devcontainer.env.json"

json_bool() {
  jq -r "$1 // false" "${CONFIG_FILE}"
}

install_python_tools() {
  if ! command -v python3 >/dev/null 2>&1; then
    return
  fi

  PYTHON_BIN="$(command -v python3)"
  sudo "${PYTHON_BIN}" -m pip install --no-cache-dir --upgrade pip
  sudo "${PYTHON_BIN}" -m pip install --no-cache-dir \
    pytest black flake8 mypy pipenv tox coverage pytest-cov pylint
}

install_node_tools() {
  if ! command -v npm >/dev/null 2>&1; then
    return
  fi

  if command -v eslint >/dev/null 2>&1 && command -v prettier >/dev/null 2>&1 && command -v jest >/dev/null 2>&1 && command -v tsc >/dev/null 2>&1; then
    return
  fi

  NPM_BIN="$(command -v npm)"
  sudo "${NPM_BIN}" install -g typescript jest prettier eslint
}

install_go_tools() {
  if ! command -v go >/dev/null 2>&1; then
    return
  fi

  if command -v golangci-lint >/dev/null 2>&1; then
    return
  fi

  go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
}

link_k8s_generator() {
  if [[ ! -f "${SCRIPT_DIR}/k8s-config-generator.py" ]]; then
    return
  fi

  sudo chmod +x "${SCRIPT_DIR}/k8s-config-generator.py"
  sudo ln -sf "${SCRIPT_DIR}/k8s-config-generator.py" /usr/local/bin/k8s-config-generator
}

if [[ "$(json_bool '.languages.python')" == "true" ]]; then
  install_python_tools
fi

if [[ "$(json_bool '.languages.node')" == "true" || "$(json_bool '.languages.javascript')" == "true" || "$(json_bool '.languages.typescript')" == "true" || "$(json_bool '.code_analysis.eslint')" == "true" ]]; then
  install_node_tools
fi

if [[ "$(json_bool '.languages.go')" == "true" ]]; then
  install_go_tools
fi

if [[ "$(jq -r '.kubernetes | any(.[]; . == true)' "${CONFIG_FILE}")" == "true" ]]; then
  link_k8s_generator
fi

printf 'Devcontainer bootstrap complete.\n'
