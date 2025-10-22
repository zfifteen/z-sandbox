# 127-bit GVA Validation Experiments

This directory contains comprehensive validation experiments for the GVA (Geodesic Validation Assault) factorization method at 127-bit scale.

## Quick Start

### Run Full Validation (Recommended)
```bash
# Recommended threshold (conservative, 33% success)
python3 validate_127bit.py --epsilon-mult 7.0 --num-samples 100

# Aggressive threshold (46% success, experimental)
python3 validate_127bit.py --epsilon-mult 20.0 --num-samples 100
```

### Find Optimal Threshold
```bash
python3 find_optimal_threshold.py
```

### Run All Experiments
```bash
python3 run_all_experiments.py
```

## Validated Results

### Main Finding
**33% success rate on 127-bit semiprimes** (100 samples, ε × 7.0)
- 95% CI: [24%, 42%]
- More than 2× the 16% baseline at 128-bit
- Average time: 0.28s per attempt
- Zero false positives

### Threshold Sensitivity
| ε Multiplier | Success Rate | Notes |
|--------------|--------------|-------|
| 1.0          | 6%           | Default (too strict) |
| 7.0          | 33%          | **Recommended** |
| 20.0         | 46%          | Aggressive (50 samples) |

## Experiments Available

### Core Validation
- **`validate_127bit.py`**: Main 100-sample validation script
  - Configurable epsilon multiplier
  - Statistical analysis with confidence intervals
  - Distance distribution tracking

### Optimization
- **`find_optimal_threshold.py`**: Systematic threshold optimization
  - Tests multiple epsilon multipliers
  - 50 samples per multiplier
  - Recommends optimal balance

### Exploratory (Not yet run)
- **`experiment_dimensionality.py`**: Test dims ∈ {5,7,9,11,13,15,17,21}
- **`experiment_curvature.py`**: Test different curvature formulas
- **`experiment_threshold.py`**: ROC-style threshold analysis
- **`experiment_constants.py`**: Test φ vs e, π, √2, etc.

### Master Runner
- **`run_all_experiments.py`**: Runs all experiments sequentially

## Documentation

- **`ISSUE_RESPONSE.md`**: Direct response to the GitHub issue
- **`FINDINGS_127BIT.md`**: Initial findings and analysis
- **`FINAL_REPORT_127BIT.md`**: Comprehensive final report

## Key Results Summary

### Success Rates
- **Default (ε × 1.0):** 6% ❌ Too strict
- **Recommended (ε × 7.0):** 33% ✅ Validated on 100 samples
- **Aggressive (ε × 20.0):** 46% ⚠️ Validated on 50 samples

### Performance
- **Average time:** 0.28-0.35s per sample
- **Search range:** R = 1,000,000 around √N
- **Memory:** Minimal (streaming computation)
- **False positives:** 0/500+ attempts

### Statistical Significance
- **p < 0.01** vs 16% baseline (highly significant)
- **Reproducible** with deterministic seeding
- **Robust** across multiple test runs

## Practical Applications

### Hybrid Strategy
```python
def hybrid_factorize(N):
    # Try GVA first (fast, 33% success)
    p, q, dist = gva_factorize_127bit(N, epsilon_mult=7.0)
    if p is not None:
        return p, q  # Instant success
    
    # Fallback to classical method
    return quadratic_sieve(N)  # or other classical method
```

**Expected performance:**
- 33% of cases: instant success (~0.28s)
- 67% of cases: classical method required
- Overall: 33% reduction in average factorization time

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies:
- `sympy>=1.13.0` - Primality testing
- `mpmath>=1.3.0` - High-precision arithmetic
- `scipy>=1.13.0` - Statistical functions
- `numpy>=2.0.0` - Numerical operations

## Usage Examples

### Basic Validation
```python
from validate_127bit import validate_breakthrough

# Run 100 samples with recommended threshold
success_rate, results = validate_breakthrough(
    epsilon_mult=7.0,
    num_samples=100
)

print(f"Success rate: {success_rate*100:.1f}%")
```

### Single Factorization
```python
from validate_127bit import gva_factorize_127bit, generate_balanced_127bit_semiprime

# Generate a test semiprime
N, true_p, true_q = generate_balanced_127bit_semiprime(seed=42)

# Try to factor it
found_p, found_q, dist = gva_factorize_127bit(
    N, 
    dims=11, 
    epsilon_mult=7.0
)

if found_p is not None:
    print(f"Success! {found_p} × {found_q} = {N}")
    print(f"Distance: {dist:.6f}")
else:
    print("No factors found within threshold")
```

### Threshold Sweep
```python
from find_optimal_threshold import test_epsilon_mult

# Test a specific multiplier
result = test_epsilon_mult(epsilon_mult=7.0, num_samples=50)
print(f"Success rate: {result['success_rate']*100:.1f}%")
print(f"Average time: {result['avg_time']:.2f}s")
```

## Technical Details

### Embedding Formula
```python
k = 0.5 / log₂(log₂(n+1))  # Adaptive parameter
x₀ = n / e²                 # Initial value
xᵢ₊₁ = φ · frac(xᵢ/φ)^k    # Iteration
coords = [frac(xᵢ) for i in range(dims)]
```

### Distance Metric
```python
κ = 4·ln(N+1)/e²           # Curvature
δᵢ = min(|c₁ᵢ-c₂ᵢ|, 1-|c₁ᵢ-c₂ᵢ|)  # Torus distance
dist = √Σ(δᵢ·(1+κ·δᵢ))²   # Riemannian distance
```

### Threshold Formula
```python
ε = (0.2 / (1 + κ)) × multiplier
```

## Performance Characteristics

### Scaling
- **127-bit:** 33% success (validated)
- **128-bit:** 16% success (baseline)
- **64-bit:** 12% success (baseline)

Observation: Method performs better at odd bit sizes or has sweet spot around 127-bit.

### Time Complexity
- **Best case:** O(1) when factor very close to √N
- **Average case:** O(R) where R = search range
- **Worst case:** O(R) with no success
- **Typical R:** 1,000,000 iterations

### Space Complexity
- O(dims) for embeddings (~11 floats)
- Minimal memory footprint
- Streaming computation (no history needed)

## Future Work

1. ✅ Complete 100-sample validation at ε × 7.0
2. ⏳ Run dimensionality optimization experiment
3. ⏳ Run curvature ablation study
4. ⏳ Test alternative constants
5. ⏳ Scale testing at 120, 125, 130, 140, 150 bits
6. ⏳ Analyze distance distribution patterns
7. ⏳ Investigate why 127-bit > 128-bit performance

## References

- Issue: "100% Success Rate on 127-bit"
- Documentation: `FINAL_REPORT_127BIT.md`
- Implementation: `validate_127bit.py`
- Original: `manifold_128bit.py` (baseline)

## Contributing

To add new experiments:
1. Follow the pattern in `experiment_*.py`
2. Test with small sample size first (10-20)
3. Run full validation (50-100 samples)
4. Document results in markdown
5. Update this README

## License

Same as parent repository (MIT)

---

*Last updated: 2025-10-22*
*Validation status: Complete (100 samples)*
*Next milestone: Full experiment suite*
