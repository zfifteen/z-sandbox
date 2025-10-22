# 100-Target Validation Quick Start Guide

This guide helps you quickly run the 100-target validation workflow for 256-bit factorization.

## Prerequisites

```bash
pip install sympy mpmath numpy scipy
```

## Quick Start (10-Sample Test)

Test the workflow with a small sample (takes ~5 minutes):

```bash
cd python

# 1. Generate 10 targets (8 unbiased, 2 biased)
python3 generate_256bit_targets.py \
    --unbiased 8 \
    --biased 2 \
    --output targets_10sample.json \
    --seed 42

# 2. Run batch factorization (2 workers, short timeout for testing)
python3 batch_factor.py \
    --targets targets_10sample.json \
    --output results_10sample.json \
    --workers 2 \
    --timeout-unbiased 60 \
    --timeout-biased 60 \
    --max-targets 10

# 3. Analyze results
python3 analyze_100sample.py \
    --results results_10sample.json \
    --output ANALYSIS_10SAMPLE.md

# 4. View report
cat ANALYSIS_10SAMPLE.md
```

## Full 100-Sample Workflow

Run the full validation (takes ~10-12 hours on 8-core machine):

```bash
cd python

# 1. Generate 100 targets (80 unbiased, 20 biased)
python3 generate_256bit_targets.py \
    --unbiased 80 \
    --biased 20 \
    --output targets_256bit_100sample.json \
    --seed 42

# 2. Run batch factorization (8 workers, production timeouts)
# IMPORTANT: This will take ~10-12 hours!
nohup python3 batch_factor.py \
    --targets targets_256bit_100sample.json \
    --output factorization_results_100sample.json \
    --workers 8 \
    --timeout-unbiased 3600 \
    --timeout-biased 300 \
    --checkpoint checkpoint_100sample.json \
    > batch_100.log 2>&1 &

# Monitor progress
tail -f batch_100.log

# Or check checkpoint
python3 -c "import json; d=json.load(open('checkpoint_100sample.json')); print(f\"Completed: {d['completed_count']}/100\")"

# 3. When complete, analyze results
python3 analyze_100sample.py \
    --results factorization_results_100sample.json \
    --output ANALYSIS_100SAMPLE.md

# 4. View comprehensive report
cat ANALYSIS_100SAMPLE.md
```

## Key Parameters

### Target Generation

- `--unbiased N`: Number of unbiased (cryptographically random) targets
- `--biased N`: Number of biased (close factor) targets
- `--seed N`: Random seed for reproducibility
- `--output FILE`: Output JSON file

### Batch Factorization

- `--workers N`: Number of parallel workers (max: CPU count)
- `--timeout-unbiased N`: Timeout per unbiased target in seconds (default: 3600 = 1 hour)
- `--timeout-biased N`: Timeout per biased target in seconds (default: 300 = 5 minutes)
- `--checkpoint FILE`: Checkpoint file for crash recovery
- `--max-targets N`: Limit number of targets to process

### Analysis

- `--results FILE`: Input results JSON file
- `--output FILE`: Output markdown report

## Interpreting Results

The analysis report will show:

1. **Unbiased Success Rate** - Can we factor cryptographically random 256-bit?
   - If > 0%: ECM works but needs significant compute
   - If = 0%: Capability ceiling identified, pivot to 192-bit

2. **Biased Success Rate** - Control group validation
   - Expected: > 90%
   - If < 90%: Possible implementation regression

3. **95% Confidence Intervals** - Statistical rigor via Wilson CI
   - Shows plausible range for true success rate

## Checkpointing and Resume

If the batch job crashes or is interrupted:

```bash
# Resume from checkpoint
python3 batch_factor.py \
    --targets targets_256bit_100sample.json \
    --output factorization_results_100sample.json \
    --workers 8 \
    --checkpoint checkpoint_100sample.json \
    # ... (same parameters as before)
```

The script will automatically skip already-completed targets.

## Troubleshooting

### Job too slow?
- Reduce `--timeout-unbiased` (but may reduce success rate)
- Increase `--workers` (up to CPU count)

### Out of memory?
- Reduce `--workers`
- Process in batches with `--max-targets`

### Checkpoint corrupted?
- Delete checkpoint file and restart (will lose progress)

## Testing

Before running the full 100-sample, test the workflow:

```bash
# Run unit tests
python3 test_100sample.py

# Run integration tests
python3 test_factorization_256bit.py
```

All 30 tests should pass.

## Expected Runtime

On an 8-core machine:

- **10-sample**: ~10 minutes
- **100-sample**: ~10-12 hours
  - Unbiased: ~80 hours single-threaded → ~10 hours with 8 workers
  - Biased: ~100 minutes (most finish quickly)

## Resource Requirements

- **CPU**: 8+ cores recommended
- **RAM**: 8 GB minimum, 32 GB recommended
- **Disk**: 1 GB for logs and checkpoints
- **Time**: 10-12 hours for full 100-sample

## Security

All code has been validated with CodeQL (0 alerts).

## Support

See `README_FACTORIZATION_256BIT.md` for full documentation.
