# ECM Distance Break with Theta-Gating

## Overview

This experiment demonstrates that geometric theta-gating (θ′) can guide ECM factorization decisions. Targets passing the θ′-gate receive extended ECM schedules, while ungated targets get only light passes.

## Quick Start

### Prerequisites

```bash
# System dependencies
sudo apt-get install gmp-ecm

# Python dependencies
pip install -r python/requirements.txt
```

### Run Complete Workflow

```bash
# 1. Generate 192-bit targets organized by distance tiers
python3 python/generate_targets_by_distance.py \
  --bits 192 --per-tier 25 \
  --tiers "1.0+2^-32,1.0+2^-24,1.0+2^-16,1.0+2^-12,1.125,1.25" \
  --fermats "2^24,2^28" \
  --out python/targets_by_distance.json

# 2. Run ECM with theta-gating (15 minutes per stage)
ECM_SIGMA=1 ECM_CKDIR=ckpts python3 python/run_distance_break.py \
  --targets python/targets_by_distance.json \
  --timeout-per-stage 900 \
  --checkpoint-dir ckpts \
  --use-sigma \
  --log logs/distance_break.jsonl

# 3. Generate summary report
python3 python/summarize_distance_break.py \
  --log logs/distance_break.jsonl \
  --out reports/distance_break_report.md \
  --emit-csv reports/distance_break_summary.csv
```

### Quick Test (128-bit, faster)

```bash
# Generate smaller targets
python3 python/generate_targets_by_distance.py \
  --bits 128 --per-tier 10 \
  --tiers "1.0+2^-32,1.0+2^-24" \
  --fermats "2^20" \
  --out python/targets_128bit.json

# Run with shorter timeout (5 minutes per stage)
ECM_SIGMA=1 ECM_CKDIR=ckpts python3 python/run_distance_break.py \
  --targets python/targets_128bit.json \
  --timeout-per-stage 300 \
  --checkpoint-dir ckpts \
  --use-sigma \
  --log logs/distance_break_128bit.jsonl

# Summarize
python3 python/summarize_distance_break.py \
  --log logs/distance_break_128bit.jsonl \
  --out reports/distance_break_128bit_report.md
```

## Scripts

### 1. generate_targets_by_distance.py

Generates balanced semiprime targets organized by distance tiers.

**Usage:**
```bash
python3 python/generate_targets_by_distance.py \
  --bits BITS \
  --per-tier N \
  --tiers "ratio1,ratio2,..." \
  --fermats "gap1,gap2,..." \
  --out OUTPUT.json \
  --seed SEED
```

**Parameters:**
- `--bits`: Target bit size for N (e.g., 128, 192, 256)
- `--per-tier`: Number of targets per tier
- `--tiers`: Comma-separated ratio targets (supports `1.0+2^-32` format)
- `--fermats`: Comma-separated Fermat gaps (supports `2^24` format)
- `--out`: Output JSON file path
- `--seed`: Random seed for reproducibility

**Output:** JSON file with metadata and targets array

### 2. run_distance_break.py

Runs ECM factorization with theta-gating on distance-organized targets.

**Usage:**
```bash
python3 python/run_distance_break.py \
  --targets TARGETS.json \
  --timeout-per-stage SECONDS \
  --checkpoint-dir DIR \
  --use-sigma \
  --log LOG.jsonl
```

**Parameters:**
- `--targets`: Path to targets JSON file
- `--timeout-per-stage`: Timeout in seconds per ECM stage (default: 900)
- `--checkpoint-dir`: Directory for ECM checkpoints (default: ckpts)
- `--use-sigma`: Enable deterministic sigma seeding and theta-gating
- `--log`: Log file path in JSONL format (default: logs/distance_break.jsonl)

**Environment Variables:**
- `ECM_SIGMA`: Enable sigma/gating (set to 1 as a boolean flag; actual sigma value used is 2147483647)
- `ECM_CKDIR`: Override checkpoint directory

**Output:** JSONL log file with run metadata and per-target results

### 3. summarize_distance_break.py

Analyzes results and generates markdown report.

**Usage:**
```bash
python3 python/summarize_distance_break.py \
  --log LOG.jsonl \
  --out REPORT.md \
  --emit-csv SUMMARY.csv
```

**Parameters:**
- `--log`: Path to JSONL log file
- `--out`: Output markdown report path (default: reports/distance_break_report.md)
- `--emit-csv`: Optional CSV summary file path

**Output:** Markdown report with statistics, exemplar cases, and full result table

## Theta-Gate

The θ′-gate is implemented in `python/manifold_128bit.py`:

```python
def theta_gate(N, width_factor=0.155, k=0.3):
    """
    Returns True if N's geometry suggests factors close to sqrt(N).
    """
    theta = theta_prime(mpf(N), mpf(k))
    width = mpf(width_factor)
    bound_lower = theta - width / 2
    bound_upper = theta + width / 2
    
    sqrt_n_norm = fmod(mpf(N).sqrt(), phi)
    return bound_lower <= sqrt_n_norm <= bound_upper
```

**Parameters:**
- `width_factor = 0.155`: Acceptance region width
- `k = 0.3`: Exponent in theta-prime calculation

**Result:**
- `True`: Target receives full ECM schedule (35d→40d→45d→50d)
- `False`: Target receives light schedule (35d only)

## ECM Schedules

### Full Schedule (θ′-gated)

| Stage | B1 | Curves | Expected Factor Size |
|-------|-----|--------|---------------------|
| 35d | 11,000,000 | 20 | ~35 decimal digits |
| 40d | 110,000,000 | 20 | ~40 decimal digits |
| 45d | 850,000,000 | 20 | ~45 decimal digits |
| 50d | 2,900,000,000 | 20 | ~50 decimal digits |

### Light Schedule (ungated)

| Stage | B1 | Curves | Expected Factor Size |
|-------|-----|--------|---------------------|
| 35d | 11,000,000 | 20 | ~35 decimal digits |

## Results Format

### JSONL Log Entry

Each target produces a log entry:

```json
{
  "idx": 1,
  "id": "T01-001",
  "N_bits": 192,
  "N_head": "422186165851085272866699",
  "N_tail": "566995913616555269427528",
  "tier": 1,
  "tier_type": "ratio",
  "ratio_target": 1.0000000002328306,
  "ratio_actual": 1.0000000002328306,
  "gate": true,
  "schedule_type": "full",
  "status": "factored",
  "stage": "35d",
  "time_sec": 123.456,
  "stages_attempted": [...],
  "integrity": true,
  "p_bits": 96,
  "q_bits": 96
}
```

### Markdown Report

Generated by `summarize_distance_break.py`:
- Run configuration
- Overall statistics
- Per-tier breakdown
- Exemplar gated success (if found)
- Full table of factored targets

## File Organization

```
z-sandbox/
├── python/
│   ├── generate_targets_by_distance.py
│   ├── run_distance_break.py
│   ├── summarize_distance_break.py
│   ├── manifold_128bit.py (contains theta_gate)
│   ├── ecm_backend.py (ECM interface)
│   ├── targets_by_distance.json (generated)
│   └── targets_128bit.json (optional, for testing)
├── logs/
│   ├── distance_break.jsonl (generated)
│   └── distance_break_128bit.jsonl (optional)
├── reports/
│   ├── existence_proof.md (documentation)
│   ├── distance_break_report.md (generated)
│   └── distance_break_summary.csv (optional)
└── ckpts/ (generated, gitignored)
    └── ecm_ck_*.sav (ECM checkpoint files)
```

## Troubleshooting

### ECM not found

```bash
sudo apt-get install gmp-ecm
ecm --help  # Verify installation
```

### Python dependencies

```bash
pip install -r python/requirements.txt
```

### Timeout too short

For 192-bit targets, 900 seconds (15 minutes) per stage is recommended. For testing, use 128-bit targets with 300-second timeouts.

### No gated successes

- Increase `--timeout-per-stage`
- Increase number of curves in schedules (edit `run_distance_break.py`)
- Try 128-bit targets (easier to factor)
- Check that `--use-sigma` is enabled

### Checkpoint directory issues

```bash
mkdir -p ckpts
ECM_CKDIR=ckpts python3 python/run_distance_break.py ...
```

## Documentation

- **Existence Proof Framework:** `reports/existence_proof.md`
- **This README:** `reports/README_distance_break.md`
- **Issue Reference:** Minimal Existence Demonstration (MED)

## Citation

```
z-sandbox: Geometric Theta-Gating for ECM Factorization
Repository: zfifteen/z-sandbox
Framework: Minimal Existence Demonstration (MED)
ECM Backend: GMP-ECM 7.0.5
```
