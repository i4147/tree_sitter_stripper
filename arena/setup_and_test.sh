#!/usr/bin/env sh
# Create an isolated development environment and verify the consolidated tool.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}
ENV_DIR="$ROOT/.venv"
"$PYTHON" -m venv "$ENV_DIR"
"$ENV_DIR/bin/python" -m pip install --upgrade pip
"$ENV_DIR/bin/python" -m pip install -r "$ROOT/result/requirements.txt" pytest
"$ENV_DIR/bin/python" -m pytest -q "$ROOT/result/tests"
"$ENV_DIR/bin/python" "$ROOT/result/demos/run_examples.py"
