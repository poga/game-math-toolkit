#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "Error: uv not found."
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv sync

echo ""
echo "Setup complete! Try an example notebook:"
echo "  uv run marimo edit notebooks/progression.py"
