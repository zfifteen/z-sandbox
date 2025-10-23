#!/usr/bin/env bash
set -euo pipefail
: "${J:=4}"                       # parallel jobs
: "${TIMEOUT:=1200}"              # per-stage timeout (sec)
: "${COUNT:=100}"                 # targets to run

export PYTHONUNBUFFERED=1

jq -r '.targets[].N' python/targets_filtered.json | head -"$COUNT" \
| parallel -j "$J" --halt soon,fail=1 \
  'python3 python/scaling_test.py --single {} --timeout-per-stage '"$TIMEOUT"

echo "DONE"