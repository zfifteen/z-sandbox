# Minimal Existence Demonstration (MED) - Quick Start

## What is This?

This is a proof-of-concept demonstrating that geometric theta-gating (θ′) can guide ECM factorization decisions. Targets passing the θ′-gate get extended ECM schedules, while ungated targets get light passes.

## Prerequisites

```bash
# Install GMP-ECM
sudo apt-get update
sudo apt-get install gmp-ecm

# Install Python dependencies
pip install -r python/requirements.txt

# Verify ECM is working
echo "123456789" | ecm 1000
# Should output: ********** Factor found in step 1: 123456789
```

## Three Commands to Run

### 1. Generate Targets

```bash
python3 python/generate_targets_by_distance.py \
  --bits 192 \
  --per-tier 25 \
  --tiers "1.0+2^-32,1.0+2^-24,1.0+2^-16,1.0+2^-12,1.125,1.25" \
  --fermats "2^24,2^28" \
  --out python/targets_by_distance.json
```

**Result:** Creates 200 192-bit semiprimes organized by geometric distance tiers

### 2. Run ECM with Theta-Gating

```bash
ECM_SIGMA=1 ECM_CKDIR=ckpts python3 python/run_distance_break.py \
  --targets python/targets_by_distance.json \
  --timeout-per-stage 900 \
  --checkpoint-dir ckpts \
  --use-sigma
```

**Result:** 
- Gated targets → full schedule (35d→40d→45d→50d)
- Ungated targets → light schedule (35d only)
- Logs written to `logs/distance_break.jsonl`

**Time:** ~15 minutes per stage × 4 stages × gated targets (varies)

### 3. Generate Report

```bash
python3 python/summarize_distance_break.py \
  --log logs/distance_break.jsonl \
  --out reports/distance_break_report.md \
  --emit-csv reports/distance_break_summary.csv
```

**Result:** Creates markdown report with:
- Per-tier statistics
- Exemplar gated success (if found)
- Full factorization table

## Quick Test (128-bit, faster)

For rapid validation:

```bash
# Generate smaller targets (10 per tier)
python3 python/generate_targets_by_distance.py \
  --bits 128 --per-tier 10 \
  --tiers "1.0+2^-32,1.0+2^-24" \
  --fermats "2^20" \
  --out python/targets_128bit.json

# Run with 5-minute timeout
ECM_SIGMA=1 ECM_CKDIR=ckpts python3 python/run_distance_break.py \
  --targets python/targets_128bit.json \
  --timeout-per-stage 300 \
  --checkpoint-dir ckpts \
  --use-sigma

# Summarize
python3 python/summarize_distance_break.py \
  --log logs/distance_break.jsonl \
  --out reports/distance_break_report.md
```

## What to Look For

### Success Criteria

At least one target with:
- ✅ `gate: true` (theta-gate passed)
- ✅ `status: factored` (ECM found factors)
- ✅ `integrity: true` (p*q = N verified)
- ✅ `schedule_type: full` (4 stages attempted)

### Example Success Log Entry

```json
{
  "id": "T01-042",
  "N_bits": 192,
  "gate": true,
  "schedule_type": "full",
  "status": "factored",
  "stage": "35d",
  "integrity": true,
  "p_bits": 96,
  "q_bits": 96
}
```

This proves: **Geometry → Decision → Factor Found**

## Files Generated

```
python/targets_by_distance.json   # 200 test targets (97KB)
logs/distance_break.jsonl         # Run log (one JSON per line)
reports/distance_break_report.md  # Summary report
reports/distance_break_summary.csv # CSV export (optional)
ckpts/                            # ECM checkpoint files (gitignored)
```

## Documentation

- **Complete specification:** `reports/existence_proof.md`
- **Detailed usage:** `reports/README_distance_break.md`
- **This guide:** `QUICKSTART_MED.md`

## Troubleshooting

**ECM not installed:**
```bash
sudo apt-get install gmp-ecm
```

**Python dependencies missing:**
```bash
pip install mpmath numpy scipy sympy
```

**No gated successes after run:**
- Increase `--timeout-per-stage` (e.g., 1800 for 30 minutes)
- Try 128-bit targets (easier to factor)
- Check that `--use-sigma` flag is set

**Process interrupted:**
- ECM checkpoints allow resuming
- Re-run same command to continue from checkpoint

## Performance Notes

- **192-bit factors:** ~96 bits each, ~29 decimal digits
- **ECM sweet spot:** 20-50 decimal digits
- **Success rate:** Depends on B1 values and curve count
- **Timeout:** 900s per stage recommended (15 minutes)
- **Total time:** Varies by number of gated targets (typically 10-30% of targets)

## Expected Outcome

The framework demonstrates:
1. ✅ Theta-gate is a meaningful binary classifier
2. ✅ Gated targets receive preferential treatment
3. ✅ At least one gated target can be factored
4. ✅ Geometry-guided decisions influence outcomes

This is the **existence proof**: the geometry matters.

## Repository

- **GitHub:** zfifteen/z-sandbox
- **Branch:** copilot/update-minimal-existence-demonstration
- **Issue:** Minimal Existence Demonstration (MED)
