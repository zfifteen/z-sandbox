# GVA 200-bit Factorization Parameter Sweep: Complete Reproduction Guide

**For another LLM to reproduce this experiment from scratch**

## Overview

This guide enables complete reproduction of the GVA 200-bit factorization scaling experiment. The experiment tested whether the Geometric Vector Approximation (GVA) method, which successfully factorizes 64-128 bit semiprimes, can scale to 200-bit numbers.

**Key Result**: 0% success rate across 900 trials and 9 parameter combinations.

## Quick Start

```bash
# 1. Run the full parameter sweep (900 trials, ~7.5 minutes)
bash scripts/run_gva_parameter_sweep.sh

# 2. Verify results
python3 scripts/verify_gva_results.py

# 3. Read detailed report
cat docs/GVA_200BIT_PARAMETER_SWEEP_REPORT.md
```

## Prerequisites

```bash
# Install required Python packages
pip install sympy

# Verify installation
python3 -c "import sympy; print('SymPy version:', sympy.__version__)"
```

## File Structure

```
z-sandbox/
├── python/gva_200bit_experiment.py      # Main experiment script
├── scripts/
│   ├── run_gva_parameter_sweep.sh       # Automated sweep runner
│   └── verify_gva_results.py            # Results analysis script
├── docs/
│   ├── GVA_200BIT_PARAMETER_SWEEP_REPORT.md    # Detailed technical report
│   └── GVA_200BIT_REPRODUCTION_GUIDE.md        # This guide
├── TODO.md                              # Updated research roadmap
└── gva_200bit_*_results.csv             # Generated result files (9 total)
```

## Step-by-Step Reproduction

### Step 1: Run Individual Experiments

Each experiment tests one parameter combination:

```bash
# Example: Test dims=13, search_range=5000, 100 trials
python3 python/gva_200bit_experiment.py 100 13 5000

# Output: gva_200bit_d13_r5000_results.csv
```

### Step 2: Run Full Parameter Sweep

The automated script runs all 9 combinations:

```bash
bash scripts/run_gva_parameter_sweep.sh
```

This executes:
- Dimensions: 13, 15, 17
- Search ranges: 5000, 10000, 50000
- 100 trials each = 900 total trials

### Step 3: Verify Results

```bash
python3 scripts/verify_gva_results.py
```

Expected output shows 0 successes across all configurations.

## Expected Results

### Performance Metrics
- **Total Trials**: 900
- **Success Rate**: 0.0%
- **Time Range**: 0.040s - 0.600s per trial
- **Total Runtime**: ~7.5 minutes

### Per-Configuration Results
| Config | Trials | Successes | Avg Time |
|--------|--------|-----------|----------|
| d13_r5000 | 100 | 0 | 0.045s |
| d13_r10000 | 100 | 0 | 0.088s |
| d13_r50000 | 100 | 0 | 0.425s |
| d15_r5000 | 100 | 0 | 0.052s |
| d15_r10000 | 100 | 0 | 0.098s |
| d15_r50000 | 100 | 0 | 0.474s |
| d17_r5000 | 100 | 0 | 0.059s |
| d17_r10000 | 100 | 0 | 0.108s |
| d17_r50000 | 100 | 0 | 0.523s |

## Key Code Components

### Main Experiment Function

```python
def gva_factorize_200bit(N, max_candidates=1000, dims=11, search_range=1000):
    # Embed target number
    theta_N = embed(N, dims)

    # Generate and rank candidates around sqrt(N)
    sqrtN = int(math.sqrt(N))
    candidates = range(max(2, sqrtN - search_range), sqrtN + search_range + 1)
    ranked_candidates = sorted(candidates,
        key=lambda c: riemann_dist(embed(c, dims), theta_N, N))

    # Test top candidates
    for cand in ranked_candidates[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            return cand, elapsed_time

    return None, elapsed_time
```

### Embedding Function

```python
def embed(n, dims=11, k=None):
    phi = (1 + math.sqrt(5)) / 2
    if k is None:
        k = 0.3 / (math.log(math.log(n + 1)) / math.log(2))
    x = n / math.exp(2)
    frac = (x / phi) % 1
    return [(phi * frac ** k) % 1 for _ in range(dims)]
```

### Distance Metric

```python
def riemann_dist(c1, c2, N):
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return math.sqrt(sum((min(abs(a - b), 1 - abs(a - b)) *
        (1 + kappa * 0.01))**2 for a, b in zip(c1, c2)))
```

## Understanding the Results

### Why 0% Success?

1. **Mathematical Limitations**: Current GVA formulation may not generalize to 200-bit numbers
2. **Embedding Quality**: Golden ratio modulation loses effectiveness at larger scales
3. **Distance Metric**: Riemannian correction insufficient for high-dimensional manifolds
4. **Search Space**: Even 50,000 candidate range insufficient for 200-bit factors

### Performance Scaling

- **Time Complexity**: O(dims × search_range × max_candidates)
- **Memory Usage**: Minimal - only stores embeddings during ranking
- **Bottleneck**: Distance calculations dominate for large search ranges

## Validation and Debugging

### Reproducibility Checks

```bash
# Verify RNG seed consistency
grep "seed=12345" python/gva_200bit_experiment.py

# Check bit length distribution
python3 -c "
import csv
for f in glob.glob('gva_200bit_*_results.csv'):
    with open(f) as file:
        bits = [int(row['N_bits']) for row in csv.DictReader(file)]
        print(f'{f}: bits {min(bits)}-{max(bits)}')
"
```

### Expected Data Characteristics

- **Bit Lengths**: All semiprimes should be 199-200 bits
- **Prime Factors**: Each semiprime has two ~100-bit prime factors
- **Timing**: Should scale linearly with search_range and dims
- **Success Pattern**: Should be 0 across all configurations

## Next Steps for Another LLM

If reproducing this experiment, consider these research directions:

### Immediate Investigations
1. **Scale Back Testing**: Test on 150-180 bit numbers to find working boundary
2. **Algorithm Analysis**: Debug why GVA fails on larger numbers
3. **Parameter Exploration**: Try different k values, embedding functions, distance metrics

### Alternative Approaches
1. **Hybrid Methods**: Combine GVA with ResidueFilter or other complementary techniques
2. **Z5D Integration**: Use Z5D predictor to generate better initial candidates
3. **Multi-Stage Filtering**: Apply GVA as one stage in a pipeline

### Technical Improvements
1. **Precision**: Investigate mpmath high-precision arithmetic
2. **Optimization**: Profile and optimize distance calculations
3. **Parallelization**: Distribute trials across multiple cores/processes

## Files to Examine

### Code Files
- `python/gva_200bit_experiment.py` - Complete implementation
- `scripts/run_gva_parameter_sweep.sh` - Automation script
- `scripts/verify_gva_results.py` - Analysis tool

### Documentation
- `docs/GVA_200BIT_PARAMETER_SWEEP_REPORT.md` - Technical details
- `TODO.md` - Updated research roadmap

### Data Files
- 9 CSV files with detailed trial-by-trial results
- Each contains 100 rows with timing, success, and parameter data

## Conclusion

This reproduction guide provides everything needed to independently verify that GVA factorization does not scale to 200-bit numbers with current parameters. The systematic approach and comprehensive documentation ensure the findings are reproducible and the methodology is transparent.

**Key Takeaway**: While GVA works well for smaller numbers (64-128 bits), fundamental changes are needed for 200-bit factorization.