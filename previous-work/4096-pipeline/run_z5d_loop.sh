#!/usr/bin/env bash

set -euo pipefail

ITERATIONS=100
LOG_FILE="z5d_secure_key_gen_$(date +"%Y%m%d_%H%M%S").txt"

printf 'Writing %d runs to %s\n' "$ITERATIONS" "$LOG_FILE"

for run in $(seq 1 "$ITERATIONS"); do
    {
        printf '=== Run %02d ===\n' "$run"
        ./z5d_secure_key_gen --debug
        printf '\n'
    } >>"$LOG_FILE" 2>&1
done

{
    printf '=== Analysis Summary ===\n'
    python3 ./analyze_z5d_output.py "$LOG_FILE"
    printf '\n'
} >>"$LOG_FILE" 2>&1

printf 'Completed. Log saved to %s\n' "$LOG_FILE"
