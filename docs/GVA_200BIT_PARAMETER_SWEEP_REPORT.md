# GVA 200-bit Factorization Scaling Experiment: Parameter Sweep Report

**Date**: October 23, 2025
**Objective**: Systematically test GVA factorization method on 200-bit semiprimes across multiple parameter configurations to establish scaling feasibility.

## Executive Summary

The GVA (Geometric Vector Approximation) method, which successfully factorizes 64-128 bit semiprimes, was tested on 200-bit numbers across 9 parameter combinations. **Result: 0% success rate (0/900 trials)**. The method does not scale to 200-bit factorization with current implementation and tested parameter ranges.

## Experimental Setup

### GVA Method Overview
- **Core Algorithm**: Embeds numbers into d-dimensional torus using golden ratio modulation
- **Distance Metric**: Riemannian distance with curvature correction
- **Candidate Ranking**: Sorts factors by geometric proximity to target embedding
- **Search Strategy**: Tests top-K candidates around √N

### Parameter Configurations Tested
- **Dimensions (d)**: 13, 15, 17
- **Search Ranges (R)**: 5000, 10000, 50000
- **Total Combinations**: 9 (3 × 3)
- **Trials per Configuration**: 100
- **Total Trials**: 900

### Test Data Generation
- **Semiprime Generation**: Balanced 200-bit semiprimes (p,q ≈ 100 bits each)
- **Prime Generation**: Uses sympy.nextprime() with random offsets
- **RNG Seed**: Fixed seed (12345 + trial_number) for reproducibility
- **Bit Length Verification**: All semiprimes confirmed 199-200 bits

## Implementation Details

### Core Functions

```python
def embed(n, dims=11, k=None):
    """Embed number into d-dimensional torus using golden ratio modulation."""
    phi = (1 + math.sqrt(5)) / 2
    if k is None:
        k = 0.3 / (math.log(math.log(n + 1)) / math.log(2))
    x = n / math.exp(2)
    frac = (x / phi) % 1
    return [(phi * frac ** k) % 1 for _ in range(dims)]

def riemann_dist(c1, c2, N):
    """Calculate Riemannian distance with curvature correction."""
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return math.sqrt(sum((min(abs(a - b), 1 - abs(a - b)) * (1 + kappa * 0.01))**2 for a, b in zip(c1, c2)))

def generate_200bit_semiprime(seed=None):
    """Generate a balanced 200-bit semiprime."""
    if seed:
        random.seed(seed)

    # Generate two ~100-bit primes using nextprime for better distribution
    base = 2**99  # Each prime ~100 bits, product ~200 bits
    offset = random.randint(0, 10**8)  # Large offset range
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10**6))  # More spread
    N = int(p) * int(q)

    return N, int(p), int(q)

def gva_factorize_200bit(N, max_candidates=1000, dims=11, search_range=1000):
    """Attempt GVA factorization on 200-bit semiprime."""
    start_time = time.time()

    # Embed N
    theta_N = embed(N, dims)

    # Search around sqrt(N)
    sqrtN = int(math.sqrt(N))
    R = search_range
    candidates = range(max(2, sqrtN - R), sqrtN + R + 1)

    # Rank candidates by Riemannian distance
    ranked_candidates = sorted(candidates, key=lambda c: riemann_dist(embed(c, dims), theta_N, N))

    # Test top candidates
    for cand in ranked_candidates[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed

    elapsed = time.time() - start_time
    return None, elapsed
```

### Experiment Script

The main experiment script (`python/gva_200bit_experiment.py`) accepts command-line parameters:

```bash
python3 python/gva_200bit_experiment.py [num_trials] [dims] [search_range]
```

Example usage:
```bash
python3 python/gva_200bit_experiment.py 100 13 5000
```

## Results Summary

### Overall Statistics
- **Total Trials**: 900
- **Successful Factorizations**: 0
- **Success Rate**: 0.0%
- **Average Time per Trial**: 0.045s - 0.523s (scales with search range)
- **Total Runtime**: ~7.5 minutes

### Per-Configuration Results

| Configuration | Dimensions | Search Range | Trials | Successes | Success Rate | Avg Time (s) | Total Time (s) |
|---------------|------------|--------------|--------|-----------|--------------|--------------|----------------|
| d13_r5000    | 13        | 5000        | 100   | 0        | 0.0%        | 0.045       | 4.5           |
| d13_r10000   | 13        | 10000       | 100   | 0        | 0.0%        | 0.088       | 8.8           |
| d13_r50000   | 13        | 50000       | 100   | 0        | 0.0%        | 0.425       | 42.5          |
| d15_r5000    | 15        | 5000        | 100   | 0        | 0.0%        | 0.052       | 5.2           |
| d15_r10000   | 15        | 10000       | 100   | 0        | 0.0%        | 0.098       | 9.8           |
| d15_r50000   | 15        | 50000       | 100   | 0        | 0.0%        | 0.474       | 47.4          |
| d17_r5000    | 17        | 5000        | 100   | 0        | 0.0%        | 0.059       | 5.9           |
| d17_r10000   | 17        | 10000       | 100   | 0        | 0.0%        | 0.108       | 10.8          |
| d17_r50000   | 17        | 50000       | 100   | 0        | 0.0%        | 0.523       | 52.3          |

### Performance Scaling Analysis
- **Time Complexity**: O(d × R × max_candidates) where d=dimensions, R=search_range
- **Memory Usage**: Minimal - stores only candidate embeddings during ranking
- **Bottleneck**: Distance calculations scale linearly with dimensions and search range

## Data Files Generated

All result files are CSV format with columns:
- `trial`: Trial number (1-100)
- `N_bits`: Bit length of semiprime
- `success`: Boolean success flag
- `factor_found`: Found factor (null if unsuccessful)
- `time_seconds`: Time taken for trial
- `dims`: Dimensions used
- `search_range`: Search range used
- `timestamp`: ISO timestamp

### File List
```
gva_200bit_d13_r5000_results.csv
gva_200bit_d13_r10000_results.csv
gva_200bit_d13_r50000_results.csv
gva_200bit_d15_r5000_results.csv
gva_200bit_d15_r10000_results.csv
gva_200bit_d15_r50000_results.csv
gva_200bit_d17_r5000_results.csv
gva_200bit_d17_r10000_results.csv
gva_200bit_d17_r50000_results.csv
```

## Analysis and Conclusions

### Key Findings
1. **No Scaling Success**: GVA method fails completely on 200-bit numbers across all tested parameters
2. **Parameter Insensitivity**: Neither increasing dimensions nor search range improved results
3. **Performance Scaling**: Times increase predictably with search range but success remains zero
4. **Known Working Range**: Method succeeds on 64-128 bit numbers but breaks at 200 bits

### Technical Insights
- **Embedding Quality**: Golden ratio modulation may lose effectiveness at larger scales
- **Distance Metric**: Riemannian correction may be insufficient for 200-bit manifolds
- **Candidate Space**: Even with 50,000 candidate range, no prime factors found in top 1000 ranked positions
- **Parameter k**: Adaptive k calculation may not be optimal for large numbers

### Limitations Identified
1. **Mathematical Foundations**: Current embedding/distance formulation may not generalize to 200+ bits
2. **Search Space Coverage**: Even maximum tested range (50,000) may be insufficient
3. **Precision Issues**: Floating-point arithmetic may introduce errors at large scales
4. **Algorithm Convergence**: Method may require fundamental redesign for large numbers

## Reproduction Instructions

### Prerequisites
```bash
pip install sympy
```

### Run Individual Experiments
```bash
# Test specific configuration
python3 python/gva_200bit_experiment.py 100 13 5000

# Output: gva_200bit_d13_r5000_results.csv
```

### Run Full Parameter Sweep
```bash
# Run all 9 configurations (can be parallelized)
for dims in 13 15 17; do
    for range in 5000 10000 50000; do
        python3 python/gva_200bit_experiment.py 100 $dims $range &
    done
done
wait
```

### Verify Results
```bash
# Check success rates across all files
grep -l "True" gva_200bit_*.csv || echo "No successes found"

# Count total trials
wc -l gva_200bit_*_results.csv
```

## Next Steps and Recommendations

### Immediate Actions
1. **Scale Back Testing**: Test on 150-180 bit numbers to find working range boundary
2. **Algorithm Review**: Analyze mathematical foundations and identify scaling limitations
3. **Hybrid Approaches**: Combine GVA with ResidueFilter or other complementary methods

### Research Directions
1. **Embedding Functions**: Investigate alternative torus embeddings for large numbers
2. **Distance Metrics**: Test different Riemannian formulations or manifold types
3. **Parameter Optimization**: Implement adaptive parameter selection based on number properties
4. **Multi-Stage Methods**: Use GVA as one stage in a multi-filter pipeline

### Validation Framework
1. **Reproducibility**: All experiments use fixed RNG seeds
2. **Statistical Power**: Run 1000+ trials for meaningful success rate estimates
3. **Performance Metrics**: Track candidate reduction efficiency, not just success rate

## Files Modified/Created

### Code Files
- `python/gva_200bit_experiment.py` - Main experiment script (parameterized)

### Documentation
- `docs/GVA_200BIT_PARAMETER_SWEEP_REPORT.md` - This report
- `TODO.md` - Updated with findings and next steps

### Data Files
- 9 CSV result files (see File List above)

This comprehensive parameter sweep establishes that current GVA implementation does not scale to 200-bit factorization, providing a clear baseline for future algorithm improvements.