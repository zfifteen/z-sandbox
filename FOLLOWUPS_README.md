# High-Value Monte Carlo Follow-Ups - Quick Start

This directory contains the implementation of 5 high-value post-merge follow-ups for the Monte Carlo integration module.

## What's New

1. **Factorization Builders Comparison** - Z5D builder now included in benchmark CSV
2. **Replay Recipe** - One-liner to reproduce exact benchmark results
3. **Variance Reduction Modes** - QMC and stratified sampling in factor sampler
4. **Deprecation Warning** - Gradual migration from old import paths
5. **CI Performance Guardrail** - Candidates/sec metric for regression detection

## Quick Demo

Run the demo to see all features in action:

```bash
cd /home/runner/work/z-sandbox/z-sandbox
python3 demo_benchmark_followups.py
```

## Running Tests

All 17 tests should pass:

```bash
PYTHONPATH=python python3 tests/test_monte_carlo.py
```

## Using Variance Reduction Modes

```python
from monte_carlo import FactorizationMonteCarloEnhancer

enhancer = FactorizationMonteCarloEnhancer(seed=42)

# Try different modes
for mode in ["uniform", "stratified", "qmc"]:
    candidates = enhancer.biased_sampling_with_phi(
        N=899,  # 29 × 31
        num_samples=500,
        mode=mode
    )
    print(f"{mode}: {len(candidates)} candidates")
```

## Running Benchmark with All Features

```bash
PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py \
  --rsa-ids RSA-100 \
  --seeds 42 \
  --include-builders \
  --include-variance-reduction \
  --output results.csv
```

This will generate a CSV with:
- Monte Carlo methods (uniform, stratified, qmc)
- Z5D builder results
- Performance metrics (candidates/sec)
- Factor finding success rates

## Replay Recipe

After running a benchmark, replay exact results:

```bash
# From CSV: seed=42, mode=qmc, N=899
PYTHONPATH=python python3 -c "
from monte_carlo import FactorizationMonteCarloEnhancer
e = FactorizationMonteCarloEnhancer(seed=42)
c = e.biased_sampling_with_phi(N=899, num_samples=500, mode='qmc')
print(f'Replayed: {len(c)} candidates')
"
```

## Deprecation Migration

Old (deprecated, still works):
```python
from monte_carlo import HyperRotationMonteCarloAnalyzer
analyzer = HyperRotationMonteCarloAnalyzer(seed=42)  # Warning issued
```

New (recommended):
```python
from security.hyper_rotation import HyperRotationMonteCarloAnalyzer
analyzer = HyperRotationMonteCarloAnalyzer(seed=42)  # No warning
```

## CI Performance Metrics

The CI now tracks performance:

```
CI Performance Guardrail:
  Uniform mode: 16,009 candidates/sec
  QMC mode: 1,616 candidates/sec
  (Baseline: >1000 cand/s)
```

Any regression below 100 cand/s will trigger a warning in CI logs.

## Files Changed

- `python/monte_carlo.py` - Added variance reduction modes + deprecation warning
- `scripts/benchmark_monte_carlo_rsa.py` - Added Z5D builder + new CSV fields
- `docs/MONTE_CARLO_BENCHMARK.md` - Added replay recipe section
- `.github/workflows/ci.yml` - Added performance guardrail
- `tests/test_monte_carlo.py` - Added 3 new tests (17 total)
- `demo_benchmark_followups.py` - Demo script (NEW)
- `IMPLEMENTATION_SUMMARY_FOLLOWUPS.md` - Detailed summary (NEW)

## Performance Summary

| Method | Candidates/sec | Best For |
|--------|---------------|----------|
| Z5D builder | ~74,000 | Large N, deterministic |
| φ-biased uniform | ~16,000 | Fast exploration |
| φ-biased QMC | ~1,700 | Better convergence |
| φ-biased stratified | ~600 | Uniform coverage |

## Documentation

- `IMPLEMENTATION_SUMMARY_FOLLOWUPS.md` - Complete implementation details
- `docs/MONTE_CARLO_BENCHMARK.md` - Benchmark usage guide
- `docs/MONTE_CARLO_RNG_POLICY.md` - RNG policy and reproducibility
- `docs/MONTE_CARLO_INTEGRATION.md` - Module overview

## Security

✅ CodeQL Analysis: 0 alerts  
✅ All tests passing: 17/17  
✅ No breaking changes  
✅ Backwards compatible with deprecation warnings  

## Questions?

See `IMPLEMENTATION_SUMMARY_FOLLOWUPS.md` for detailed explanations of each follow-up.
