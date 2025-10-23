#!/usr/bin/env bash
set -euo pipefail
: "${J:=4}"                        # parallel jobs
: "${TIMEOUT:=1200}"               # per-stage timeout (sec)
: "${COUNT:=100}"                  # targets to run
: "${ECM_CKDIR:=checkpoints}"      # checkpoint directory
: "${ECM_SIGMA:=0}"                # set to 1 for deterministic curves

export PYTHONUNBUFFERED=1

if ! command -v parallel >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install parallel
  else
    echo "GNU parallel not found and Homebrew missing; please install parallel." >&2
    exit 1
  fi
fi

jq -r '.targets[0:'"$COUNT"'] .N' python/targets_1500.json | parallel -j "$J" --halt soon,fail=1 'ECM_CKDIR='"$ECM_CKDIR"' ECM_SIGMA='"$ECM_SIGMA"' python3 python/scaling_test.py --single {} --timeout-per-stage '"$TIMEOUT"' --checkpoint-dir '"$ECM_CKDIR"' --use-sigma'

echo "DONE"
