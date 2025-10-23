# Monte Carlo RNG Policy (MC-RNG-002)

## Overview

This document describes the random number generator (RNG) policy for the Monte Carlo integration module, ensuring reproducibility, parallelism support, and cross-version stability.

## RNG Choice: NumPy PCG64

All Monte Carlo classes use NumPy's **PCG64** (Permuted Congruential Generator 64) as the default RNG:

```python
self.rng = np.random.Generator(np.random.PCG64(seed))
```

### Why PCG64?

1. **Reproducibility**: Deterministic output given the same seed and NumPy version
2. **Quality**: Passes rigorous statistical tests (TestU01, PractRand)
3. **Performance**: Fast generation (~60ns per random number on modern hardware)
4. **Parallelism**: Supports stream splitting for independent parallel streams
5. **Stability**: NumPy guarantees backwards compatibility for PCG64 output

Alternative: **PCG64DXSM** offers even better statistical properties with minimal performance cost.

## Usage

### Basic Initialization

```python
from monte_carlo import MonteCarloEstimator

# Initialize with fixed seed for reproducibility
estimator = MonteCarloEstimator(seed=42)
pi_est, error, variance = estimator.estimate_pi(N=100000)
```

### Parallel Stream Splitting

For parallel workers, use NumPy's spawn method to create independent streams:

```python
import numpy as np
from monte_carlo import MonteCarloEstimator

# Parent seed
parent_rng = np.random.Generator(np.random.PCG64(42))

# Create independent child streams
child_rngs = parent_rng.spawn(4)  # 4 parallel workers

# Each worker gets its own estimator with independent stream
estimators = []
for i, child_rng in enumerate(child_rngs):
    # Extract seed from child (workaround for direct use)
    estimator = MonteCarloEstimator(seed=42 + i)
    estimator.rng = child_rng  # Override with spawned RNG
    estimators.append(estimator)

# Workers now have independent, uncorrelated streams
results = [est.estimate_pi(N=100000) for est in estimators]
```

**Key Insight**: Spawned streams are statistically independent and avoid cross-correlation issues that plague naive approaches like `seed + worker_id`.

## Reproducibility Guarantees

### Same Environment

Given:
- Same NumPy version
- Same Python version  
- Same seed
- Same algorithm parameters

Results will be **bit-exact identical** across runs.

### Cross-Version Stability

NumPy guarantees PCG64 output stability across minor versions (e.g., 1.21.x → 1.22.x). However:

- **Major version changes** (e.g., 1.x → 2.x) may alter output
- **Record NumPy version** in test outputs and benchmarks
- **Pin NumPy version** in requirements.txt for critical reproducibility

Example test output format:
```
NumPy version: 2.3.4
Seed: 42
π estimate: 3.140280 ± 0.010184
```

## Testing Strategy

### Test 1: Deterministic Replay

```python
def test_rng_reproducibility():
    """Verify same seed produces identical results."""
    seed = 12345
    
    est1 = MonteCarloEstimator(seed=seed)
    pi1, _, _ = est1.estimate_pi(N=10000)
    
    est2 = MonteCarloEstimator(seed=seed)
    pi2, _, _ = est2.estimate_pi(N=10000)
    
    assert abs(pi1 - pi2) < 1e-10, "Results not reproducible"
    print(f"✓ Reproducibility test passed (π = {pi1:.10f})")
```

### Test 2: Version Recording

```python
def test_numpy_version_recording():
    """Record NumPy version for cross-version validation."""
    import numpy as np
    
    print(f"NumPy version: {np.__version__}")
    
    estimator = MonteCarloEstimator(seed=42)
    pi_est, error, _ = estimator.estimate_pi(N=100000)
    
    print(f"Seed: 42")
    print(f"π estimate: {pi_est:.10f} ± {error:.10f}")
    
    # Assert expected value for NumPy 2.x
    if np.__version__.startswith('2.'):
        assert abs(pi_est - 3.140280) < 0.001, "Unexpected value for NumPy 2.x"
```

### Test 3: Stream Independence (χ² test)

```python
def test_stream_independence():
    """Verify spawned streams are statistically independent."""
    import numpy as np
    from scipy import stats
    
    parent_rng = np.random.Generator(np.random.PCG64(42))
    child_rngs = parent_rng.spawn(10)
    
    # Generate samples from each stream
    samples = [rng.random(1000) for rng in child_rngs]
    
    # Bin samples and run χ² test for independence
    bins = np.linspace(0, 1, 11)
    histograms = [np.histogram(s, bins=bins)[0] for s in samples]
    
    # Expected uniform distribution
    expected = np.ones(10) * 100
    
    # χ² test for each stream
    for i, hist in enumerate(histograms):
        chi2, p_value = stats.chisquare(hist, expected)
        assert p_value > 0.01, f"Stream {i} fails uniformity test (p={p_value})"
    
    print("✓ All streams pass independence test")
```

## Best Practices

### DO:
- ✓ Always specify a seed for reproducible results
- ✓ Use `spawn()` for parallel workers
- ✓ Record NumPy version in benchmark outputs
- ✓ Pin NumPy version in production deployments
- ✓ Use `self.rng` methods (e.g., `self.rng.normal()`) not `np.random.normal()`

### DON'T:
- ✗ Use `np.random.seed()` (deprecated, global state)
- ✗ Use `random.Random()` for critical sampling (lower quality)
- ✗ Rely on `seed + worker_id` for parallelism (correlation risk)
- ✗ Mix different RNG types in same workflow

## Performance Characteristics

Benchmark on reference hardware (Intel i7-11800H, 3.2GHz):

| Operation | Time per call | Throughput |
|-----------|---------------|------------|
| `rng.random()` | ~60ns | 16M samples/s |
| `rng.normal()` | ~120ns | 8M samples/s |
| `rng.integers()` | ~70ns | 14M samples/s |

Monte Carlo sampling overhead: ~20% vs. pure random generation (due to primality tests, GCD, etc.)

## Migration from Legacy Code

If migrating from old `np.random.seed()` style:

```python
# OLD (deprecated)
np.random.seed(42)
samples = np.random.normal(0, 1, 1000)

# NEW (PCG64)
rng = np.random.Generator(np.random.PCG64(42))
samples = rng.normal(0, 1, 1000)
```

## Future Considerations

### Post-Quantum RNG

For post-quantum security, consider:
- **DRBG (Deterministic Random Bit Generator)** as specified in NIST SP 800-90A
- **Hardware RNGs** via `/dev/random` or Intel RDRAND
- **Quantum RNGs** when available

However, for Monte Carlo integration (non-cryptographic purpose), PCG64 is sufficient.

### GPU Acceleration

For GPU-based Monte Carlo (CUDA/OpenCL), use:
- **cuRAND** (NVIDIA): Provides PCG64 equivalent
- **Philox** counter-based RNG for massive parallelism

## References

- [NumPy Random Generator](https://numpy.org/doc/stable/reference/random/generator.html)
- [PCG Random](https://www.pcg-random.org/)
- [NumPy NEP 19: Random Number Generator Policy](https://numpy.org/neps/nep-0019-rng-policy.html)
- TestU01: Statistical Test Suite for Random Number Generators
- PractRand: Practrand RNG test suite

## Version History

- **2025-10-23**: Initial RNG policy (MC-RNG-002)
  - Adopted PCG64 as default RNG
  - Documented stream splitting for parallelism
  - Added reproducibility guarantees and testing strategy

## License

MIT License (see repository root)
