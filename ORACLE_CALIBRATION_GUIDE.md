# Deterministic Oracle Calibration Guide

## Overview

The **Deterministic Oracle** provides RNG-free, high-precision ground truth targets for validating QMC (Quasi-Monte Carlo) methods and Z-Framework experiments. Using rapidly convergent hypergeometric series for 1/π (Ramanujan/Chudnovsky type), the oracle achieves ≈14 decimal digits per term and enables clean separation of algorithmic variance from stochastic noise.

## Key Features

1. **Deterministic Ground Truth**: No RNG noise in target values
2. **High Precision**: Uses mpmath with configurable decimal places (default: 100)
3. **Rapid Convergence**: Chudnovsky series achieves ~14.18 digits/term
4. **Clean Error Measurement**: Separates algorithmic variance from truth error
5. **Reproducible**: Same results every time, suitable for CI/CD gates

## Quick Start

### Basic Usage

```python
from oracle import DeterministicOracle

# Create oracle with 100 decimal places
oracle = DeterministicOracle(precision=100)

# Compute high-precision π
pi_val = oracle.get_pi(method='chudnovsky')
print(f"π = {pi_val}")

# Estimate error of an approximation
estimate = 3.14159
error = oracle.estimate_pi_error(estimate)
print(f"Error: {error:.6e}")
```

### Running the Benchmark

```bash
# Run oracle-based QMC benchmark
python3 python/benchmark_oracle_qmc.py

# Generate convergence visualizations
python3 python/visualize_oracle.py
```

This produces:
- `oracle_qmc_benchmark.csv` - Numerical results
- `oracle_convergence.png` - Main convergence comparison plot
- `oracle_methods.png` - Detailed method comparison

## Mathematical Foundation

### Chudnovsky Formula (1988)

The oracle uses the Chudnovsky brothers' formula for 1/π:

```
1/π = 12 Σ_{k=0}^∞ [(-1)^k (6k)! (13591409 + 545140134k)] / 
                    [(3k)! (k!)^3 (640320)^(3k+3/2)]
```

**Convergence rate**: Exponential, ~10^(-14) improvement per term

**Terms needed for P digits**: Roughly P/14

### Ramanujan Formula (1914)

Alternative formula with ~8 digits/term:

```
1/π = (2√2/9801) Σ [(4k)! (1103 + 26390k)] / [(k!)^4 396^(4k)]
```

## Convergence Validation

### Expected Theoretical Rates

| Method | Convergence Rate | Error Bound |
|--------|-----------------|-------------|
| Monte Carlo (Uniform) | O(1/√N) | C/√N |
| Stratified | O(1/√N) | C'/√N (smaller C') |
| QMC (Sobol/Halton) | O((log N)^s/N) | C(log N)^s/N |
| QMC-φ Hybrid | O((log N)^s/N) | C'(log N)^s/N |

where:
- N = sample count
- s = dimension (typically 2 for π estimation via circle)
- C, C' = implementation-dependent constants

### Empirical Validation

The oracle benchmark validates these rates empirically:

```python
from benchmark_oracle_qmc import OracleQMCBenchmark

benchmark = OracleQMCBenchmark(precision=100, seed=42)
sample_counts = [100, 1000, 10000, 100000]

results, pi_true = benchmark.run_convergence_test(sample_counts)
benchmark.analyze_convergence(results, pi_true)
```

Expected output shows:
- **Uniform MC**: Convergence rate ≈ N^(-0.5)
- **QMC**: Convergence rate ≈ N^(-1.0) (with log factor)
- **QMC improvement**: 3-10× better error at large N

## Integration with Z-Framework

### 1. Calibrating π-Dependent Constants

Many Z-Framework components use π-dependent constants:

```python
from oracle import DeterministicOracle

oracle = DeterministicOracle(precision=200)
pi_high_prec = oracle.get_pi()

# Use for geometric calculations
def geodesic_curvature(n):
    return 4 * log(n + 1) / (exp(2) * pi_high_prec)
```

### 2. QMC Parameter Validation

Validate QMC parameter choices:

```python
# Test different QMC configurations
def test_qmc_config(scramble=False, seed=42):
    benchmark = OracleQMCBenchmark(seed=seed)
    # ... configuration testing
    return error_at_N_10000

# Compare configurations
configs = [
    ('Sobol', False),
    ('Sobol-Owen', True),
]

for name, scramble in configs:
    error = test_qmc_config(scramble=scramble)
    print(f"{name}: error = {error:.6e}")
```

### 3. Regression Testing

Add oracle checks to CI/CD:

```python
# tests/test_qmc_regression.py
def test_qmc_convergence_rate():
    """Ensure QMC maintains expected convergence rate."""
    oracle = DeterministicOracle(precision=100)
    
    # Run small benchmark
    results = run_quick_benchmark(N_max=10000)
    
    # Check QMC is better than MC
    assert results['qmc']['error'] < results['uniform']['error']
    
    # Check approximate convergence rate
    rate = estimate_convergence_rate(results['qmc'])
    assert rate > 0.8  # Should be close to 1.0
```

## Best Practices

### 1. Precision Selection

Choose precision based on requirements:

| Application | Precision | Rationale |
|-------------|-----------|-----------|
| Quick tests | 50 digits | Fast, adequate for float64 |
| Standard benchmarks | 100 digits | Good balance |
| High-precision validation | 200+ digits | Extended precision needs |

### 2. Sample Count Selection

For meaningful convergence analysis:

```python
# Logarithmically spaced sample counts
sample_counts = [10**i for i in range(2, 7)]  # 100 to 1M
# Or: [100, 500, 1000, 5000, 10000, 50000, 100000]
```

### 3. Seed Management

For reproducible results:

```python
# Use consistent seed across tests
BENCHMARK_SEED = 42

oracle = DeterministicOracle(precision=100)
benchmark = OracleQMCBenchmark(seed=BENCHMARK_SEED)
```

### 4. Error Interpretation

The oracle measures **absolute error** against true π:

```python
error = |estimate - π_true|
rel_error = error / π_true
```

For convergence analysis, plot error on log-log scale to reveal power-law behavior.

## Example Workflows

### Workflow 1: Quick Validation

```bash
# Run basic oracle demo
python3 python/oracle.py

# Run benchmark with default settings
python3 python/benchmark_oracle_qmc.py
```

### Workflow 2: Comprehensive Analysis

```python
from benchmark_oracle_qmc import OracleQMCBenchmark
from visualize_oracle import plot_convergence_comparison

# Extended sample range
benchmark = OracleQMCBenchmark(precision=100, seed=42)
sample_counts = [10**i for i in range(2, 7)]

# Run all modes
results, pi_true = benchmark.run_convergence_test(
    sample_counts,
    modes=['uniform', 'stratified', 'qmc', 'qmc_phi_hybrid']
)

# Analyze
benchmark.analyze_convergence(results, pi_true)

# Visualize
plot_convergence_comparison(results, pi_true, 'custom_convergence.png')
```

### Workflow 3: Custom Integrand

Extend oracle to custom problems:

```python
from oracle import DeterministicOracle
from mpmath import mp

oracle = DeterministicOracle(precision=100)

# Define custom exact value (e.g., π²/6)
true_value = (oracle.get_pi() ** 2) / mp.mpf(6)

# Your estimator function
def my_estimator(N):
    # ... MC/QMC sampling logic
    return estimate

# Validate convergence
sample_counts = [1000, 10000, 100000]
results = oracle.convergence_oracle(
    sample_counts,
    my_estimator,
    true_value=true_value
)

# Check error scaling
for i, N in enumerate(sample_counts):
    print(f"N={N}: error={results['errors'][i]:.6e}")
```

## Troubleshooting

### Issue: High Initial Overhead

**Symptom**: First oracle call is slow

**Cause**: mpmath initialization and series computation

**Solution**: Use oracle caching:
```python
oracle = DeterministicOracle(precision=100)
pi_val = oracle.get_pi()  # Computes and caches
# Subsequent calls are instant
```

### Issue: QMC Not Beating MC

**Symptom**: QMC error ≥ MC error at large N

**Possible causes**:
1. Sample count not large enough (try N > 10000)
2. Implementation issue in QMC sampler
3. Dimension too high (curse of dimensionality)

**Debug**:
```python
# Check individual samples
print("MC error:", results['uniform']['errors'][-1])
print("QMC error:", results['qmc']['errors'][-1])
print("Improvement:", results['uniform']['errors'][-1] / results['qmc']['errors'][-1])
```

### Issue: Unexpected Convergence Rate

**Symptom**: Empirical rate doesn't match theory

**Check**:
1. Seed consistency: Same seed for reproducibility
2. Sample count range: Need wide enough range (3+ orders of magnitude)
3. Implementation bugs: Verify sampler correctness

## References

1. **Ramanujan (1914)**: *Modular Equations and Approximations to π*
2. **Chudnovsky & Chudnovsky (1988)**: *Approximations and Complex Multiplication*
3. **Bailey, Borwein & Plouffe (1997)**: *On the Rapid Computation of Various Polylogarithmic Constants*
4. **Cohen & Guillera**: Unified hypergeometric theory for 1/π formulas
5. **Owen (1995)**: Randomly permuted (t,m,s)-nets and (t,s)-sequences
6. **Joe & Kuo (2008)**: Constructing Sobol sequences with better projections

## Files Reference

| File | Purpose |
|------|---------|
| `python/oracle.py` | Core oracle implementation |
| `python/benchmark_oracle_qmc.py` | QMC benchmark using oracle |
| `python/visualize_oracle.py` | Visualization generator |
| `tests/test_oracle.py` | Comprehensive test suite |
| `oracle_qmc_benchmark.csv` | Benchmark results (generated) |
| `oracle_convergence.png` | Main convergence plot (generated) |
| `oracle_methods.png` | Detailed comparison plot (generated) |

## Summary

The Deterministic Oracle provides:
- ✅ RNG-free ground truth for QMC validation
- ✅ Clean separation of algorithmic vs stochastic variance
- ✅ Reproducible, high-precision error measurement
- ✅ CI/CD-ready regression testing
- ✅ Portable calibration for Z-Framework experiments

Use it to validate variance-reduction claims, debug QMC implementations, and establish deterministic baselines for geometric experiments.
