# Monte Carlo RSA Benchmark Documentation (MC-BENCH-001)

## Overview

This document describes the Monte Carlo factorization benchmark for RSA challenge numbers, comparing φ-biased sampling with standard Monte Carlo approaches.

## Important Note on Factorization Success

**RSA challenge numbers cannot be factored by simple Monte Carlo sampling alone.** The benchmark demonstrates:

1. **Algorithmic differences**: How φ-biased sampling compares to standard sampling
2. **Candidate quality**: Distribution of candidates near √N
3. **Performance characteristics**: Candidates generated per second, memory usage
4. **Integration potential**: How Monte Carlo enhances existing factorization methods

The benchmark is **NOT** expected to factor RSA-100 or larger numbers directly. Instead, it validates:
- Sampling efficiency
- φ-bias effectiveness on smaller semiprimes
- Integration with Z5D/GVA methods

## Benchmark Modes

### Mode 1: Small Semiprimes (Validation)

Test on small semiprimes (40-100 bits) where factors can be found:

```bash
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py --small-test
```

This validates that:
- φ-biased sampling finds factors faster than standard sampling
- The 40% improvement claim is measurable
- RNG policy (PCG64) ensures reproducibility

### Mode 2: RSA Challenge Characterization

Characterize candidate distribution for RSA challenges:

```bash
PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py \
  --rsa-ids RSA-100 RSA-129 \
  --seeds 42 12345 \
  --characterize
```

Outputs:
- Candidate density near √N
- φ-modulation effects
- Variance reduction potential

### Mode 3: Integration Benchmark

Benchmark Monte Carlo + Z5D/GVA hybrid:

```bash
PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py \
  --rsa-ids RSA-100 \
  --integration-mode
```

This requires integration with existing candidate builders (future work).

## Replay Winning Seed/Method

After running a benchmark, you can replay the exact winning configuration from the CSV to dump candidates for debugging or verification:

```python
# Read the benchmark CSV
import pandas as pd
df = pd.read_csv('monte_carlo_rsa_benchmark.csv')

# Find the best result (e.g., fastest factorization)
best = df[df['factor_found'] == True].sort_by('wall_time_seconds').iloc[0]

# Replay with exact parameters
from monte_carlo import FactorizationMonteCarloEnhancer

enhancer = FactorizationMonteCarloEnhancer(seed=int(best['seed']))
candidates = enhancer.biased_sampling_with_phi(
    N=int(best['N_decimal'].replace('...', '')),  # Use actual N from your test
    num_samples=int(best['samples_per_try']),
    mode=best['sampling_mode']
)

print(f"Replayed {best['method']} with seed {best['seed']}")
print(f"Generated {len(candidates)} candidates")
print(f"First 10: {candidates[:10]}")

# Verify factor is in candidates
if best['factor_value'] in candidates:
    print(f"✓ Factor {best['factor_value']} confirmed in candidates")
```

### One-Liner Replay

For quick verification without pandas:

```bash
# Extract winning row from CSV (example: row 3 found RSA-100 in 15.2s)
SEED=42 MODE=qmc N=77 SAMPLES=1000

# Replay
PYTHONPATH=python python3 -c "
from monte_carlo import FactorizationMonteCarloEnhancer
e = FactorizationMonteCarloEnhancer(seed=$SEED)
c = e.biased_sampling_with_phi(N=$N, num_samples=$SAMPLES, mode='$MODE')
print(f'Replayed: {len(c)} candidates, first 10: {c[:10]}')
"
```

This is useful for:
- Bug reports: "Seed 42 with QMC mode on N=899 produces..."
- Paper citations: "Using the published seed/mode from the benchmark..."
- Regression testing: "Version X.Y still produces the same candidates..."

## Output Format

CSV columns:
- `method`: 'phi_biased_monte_carlo' or 'standard_monte_carlo'
- `rsa_id`: RSA challenge ID
- `N_digits`: Decimal digits of N
- `N_bits`: Bit length of N
- `candidates_tested`: Total candidates generated
- `factor_found`: Boolean (expected False for RSA challenges)
- `wall_time_seconds`: Execution time
- `seed`: RNG seed for reproducibility
- `samples_per_try`: Candidates per sampling iteration
- `numpy_version`: NumPy version for cross-version validation

## Acceptance Criteria (from issue)

The original issue requested:

> **MC-BENCH-001:** A/B benchmark script comparing `biased_sampling_with_phi` vs existing builders on RSA-100/129/155/250/260 with fixed seeds; publish CSV (tries to hit, wall time, candidates tested).

**Clarification**: The "tries to hit" metric only makes sense for factorizable numbers in reasonable time. For RSA challenges, we benchmark:
1. Candidates generated per second
2. Distribution quality (φ-bias vs uniform)
3. Memory efficiency
4. Reproducibility across seeds/versions

The benchmark **characterizes** Monte Carlo behavior on RSA challenges without expecting factorization success.

## Integration with Existing Methods

Monte Carlo sampling is designed to **enhance** existing methods:

```python
# Example: Hybrid Z5D + Monte Carlo
from z5d_predictor import get_factor_candidates
from monte_carlo import FactorizationMonteCarloEnhancer

N = 77  # Small example
z5d_candidates = get_factor_candidates(N)
mc_candidates = FactorizationMonteCarloEnhancer(seed=42).biased_sampling_with_phi(N, 100)

# Combine and deduplicate
all_candidates = sorted(set([c for c, _, _ in z5d_candidates] + mc_candidates))

# Test candidates (this would find factors for N=77)
for c in all_candidates:
    if N % c == 0:
        print(f"Factor found: {c}")
```

## Running the Benchmark

### Quick Test (Small Semiprimes)

```bash
# Test on small numbers where success is expected
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 -c "
from scripts.benchmark_monte_carlo_rsa import benchmark_phi_biased_sampling, benchmark_standard_sampling, RSAChallenge

# Test N = 77 (7 × 11)
rsa = RSAChallenge(id='TEST-77', N=77, p=7, q=11, factored=True)

result_phi = benchmark_phi_biased_sampling(rsa, seed=42, max_tries=50, samples_per_try=100, timeout_seconds=10)
print(f'φ-biased: Factor found={result_phi.factor_found}, Tries={result_phi.tries_to_hit}')

result_std = benchmark_standard_sampling(rsa, seed=42, max_tries=50, samples_per_try=100, timeout_seconds=10)
print(f'Standard: Factor found={result_std.factor_found}, Tries={result_std.tries_to_hit}')
"
```

### Full RSA Characterization (No Factorization Expected)

```bash
# Characterize candidate distribution on RSA challenges
PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py \
  --rsa-ids RSA-100 RSA-129 \
  --seeds 42 \
  --output monte_carlo_rsa_characterization.csv
```

Expected output:
```
RSA-100:
  N digits: 100
  N bits: 330
  Seed 42:
    Running φ-biased sampling...
      Factor found: False
      Candidates tested: ~100,000
      Wall time: ~60s
    Running standard sampling...
      Factor found: False
      Candidates tested: ~100,000
      Wall time: ~60s
```

## Future Work

1. **Hybrid benchmarks**: Integrate with ZNeighborhood, ResidueFilter builders
2. **Variance reduction**: Add stratified/QMC benchmarks
3. **Parallelization**: Multi-core Monte Carlo with stream splitting
4. **GPU acceleration**: CUDA-based sampling for massive parallelism

## References

- Issue #47: Monte Carlo integration implementation
- MC-RNG-002: RNG policy documentation
- `docs/MONTE_CARLO_INTEGRATION.md`: Module overview

## License

MIT License (see repository root)
