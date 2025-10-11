#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip pre-commit -r python/requirements.txt
pre-commit install
echo "Bootstrap complete."
