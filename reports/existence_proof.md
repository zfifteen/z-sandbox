# Minimal Existence Demonstration Report

## Setup

### Backend Information
- **Backend**: GMP-ECM
- **Version**: 7.0.5+ds-1build1 (gmp-ecm package)
- **Platform**: Ubuntu 24.04

### Gate Definition
The geometric gate is based on θ′ (theta prime), a torus embedding function:

```
θ′(n, k) = φ · (frac(n/φ))^k
```

Where:
- φ = golden ratio = (1 + √5) / 2
- k = 0.3 (default exponent)
- frac(x) = fractional part of x

**Gate decision logic:**
- Compute θ′(N), θ′(p), θ′(q)
- Define acceptance window: [θ′(N) - width/2, θ′(N) + width/2]
- Gate passes if either θ′(p) or θ′(q) falls within the window
- **Width factor**: 0.155 (default)

### Dataset Configuration
Generated using:
```bash
python3 python/generate_targets_by_distance.py \
  --bits 192 \
  --per-tier 25 \
  --tiers "1.0+2^-32,1.0+2^-24,1.0+2^-16,1.0+2^-12,1.125,1.25" \
  --fermats "2^24,2^28" \
  --out python/targets_by_distance.json
```

- **Target bit size**: 192 bits (~58 decimal digits)
- **Factor bit size**: ~96 bits (~29 decimal digits)
- **Number of tiers**: 6
- **Targets per tier/fermat**: 25
- **Total targets**: 300
- **Seed**: 42

### ECM Schedule
**Gated targets** (full schedule):
- Stage 1: B1=10^7, 200 curves
- Stage 2: B1=5×10^7, 200 curves
- Stage 3: B1=10^9, 200 curves
- Stage 4: B1=10^10, 200 curves

**Ungated targets** (light schedule):
- Stage 1: B1=10^7, 100 curves

### Execution Parameters
```bash
ECM_SIGMA=1 ECM_CKDIR=ckpts \
python3 python/run_distance_break.py \
  --targets python/targets_by_distance.json \
  --timeout-per-stage 900 \
  --checkpoint-dir ckpts \
  --use-sigma
```

- Timeout per stage: 900 seconds (15 minutes)
- Checkpoint directory: ckpts/
- Deterministic curves: ECM_SIGMA=1

## Results

### Overall Statistics
(To be filled after experiment)

- **Total targets**: 300
- **Factored**: TBD
- **Gated targets**: TBD
- **Gated factored**: TBD
- **Ungated targets**: TBD
- **Ungated factored**: TBD

### Results by Tier
(To be filled after experiment)

| Tier | Ratio | Total | Factored | Gated | Gated Factored |
|------|-------|-------|----------|-------|----------------|
| 0 | 1.0000000002 | 50 | TBD | TBD | TBD |
| 1 | 1.0000000596 | 50 | TBD | TBD | TBD |
| 2 | 1.0000152588 | 50 | TBD | TBD | TBD |
| 3 | 1.0002441406 | 50 | TBD | TBD | TBD |
| 4 | 1.125 | 50 | TBD | TBD | TBD |
| 5 | 1.25 | 50 | TBD | TBD | TBD |

## Exemplar Gated Success Case

(To be filled with at least one case if achieved)

### Case 1
- **N**: (first 24 digits)...(last 24 digits)
- **p**: X bits
- **q**: Y bits
- **Tier**: T (ratio=R)
- **Fermat normal**: F
- **Gate**: True (full schedule used)
- **Status**: factored
- **Integrity**: True
- **Elapsed**: T seconds
- **Stage completed**: S/4

**Gate metadata:**
- θ′(N) = X.XXXXXX
- θ′(p) = Y.YYYYYY (in bounds: True/False)
- θ′(q) = Z.ZZZZZZ (in bounds: True/False)
- Bounds: [lower, upper]
- Width factor: 0.155

**Evidence:**
```json
(Full JSON log line proving gate=true and successful factorization)
```

## Chain of Custody

### File Hashes
```bash
# targets_by_distance.json
sha256sum python/targets_by_distance.json
(hash to be computed)

# distance_break.jsonl
sha256sum logs/distance_break.jsonl
(hash to be computed)
```

## Claim

**EXISTENCE PROOF:**

> A θ′-gated target at 192-bit was factored by GMP-ECM. The geometric gate determined that this target should receive full ECM spend (4 stages: 35d→50d equivalent), while ungated targets received only light spend (1 stage: 35d). The factor was found during the gated full schedule, demonstrating that geometry-driven spend decisions can lead to successful factorization.

OR

> No θ′-gated targets were factored in this experiment. Consider adjusting parameters (width_factor, k) or running with more targets.

## Reproducibility

To reproduce these results:

1. Install GMP-ECM:
   ```bash
   sudo apt-get install gmp-ecm
   ```

2. Install Python dependencies:
   ```bash
   pip3 install -r python/requirements.txt
   ```

3. Generate targets:
   ```bash
   python3 python/generate_targets_by_distance.py \
     --bits 192 \
     --per-tier 25 \
     --tiers "1.0+2^-32,1.0+2^-24,1.0+2^-16,1.0+2^-12,1.125,1.25" \
     --fermats "2^24,2^28" \
     --out python/targets_by_distance.json
   ```

4. Run ECM experiment:
   ```bash
   ECM_SIGMA=1 ECM_CKDIR=ckpts \
   python3 python/run_distance_break.py \
     --targets python/targets_by_distance.json \
     --timeout-per-stage 900 \
     --checkpoint-dir ckpts \
     --use-sigma
   ```

5. Generate report:
   ```bash
   python3 python/summarize_distance_break.py \
     --log logs/distance_break.jsonl \
     --out reports/distance_break_report.md \
     --emit-csv reports/distance_break_summary.csv
   ```

## Notes

- The 192-bit targets have factors of approximately 29 decimal digits, which is well within ECM's sweet spot.
- ECM success rates depend heavily on curve selection (sigma parameter) and the number of curves attempted.
- The geometric gate provides a theoretically-motivated heuristic for allocating computational resources.
- This experiment demonstrates existence, not optimization. Further work is needed to characterize success rates and optimal parameters.
