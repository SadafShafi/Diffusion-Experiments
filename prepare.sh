#!/usr/bin/env bash
### a shell script to load the python environemnt, if there is none, it should make one and install requirements file
# Usage: source prepare.sh   (must be sourced so the environment stays active in your shell)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_VERSION="3.12"

if [ ! -d "$VENV_DIR" ]; then
    echo "No environment found, creating one in $VENV_DIR ..."
    uv venv --python "$PYTHON_VERSION" "$VENV_DIR" || return 1 2>/dev/null || exit 1
    source "$VENV_DIR/bin/activate"
    uv pip install -r "$PROJECT_DIR/requirements.txt" || return 1 2>/dev/null || exit 1
else
    source "$VENV_DIR/bin/activate"
fi

echo "Environment active: $(python --version) at $VENV_DIR"
