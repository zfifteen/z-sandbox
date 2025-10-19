# Quick Start Guide - Geometric Factorization

Get started with the Geometric Factorization algorithm in 5 minutes!

## Installation

No installation needed! Just Python 3.10+ standard library.

```bash
# Download the script
cd gists/
chmod +x geometric_factorization.py
```

## 30-Second Test

```bash
# Run unit tests to verify everything works
python geometric_factorization.py --test
```

Expected output:
```
✓ All unit tests passed!
```

## 2-Minute Demo

```bash
# Run a quick demonstration
python geometric_factorization.py --demo
```

This will factor several semiprimes of different sizes and show you:
- Success rates
- Candidate filtering statistics
- Timing information

## 5-Minute Exploration

Try the example usage script:

```bash
python example_usage.py
```

This runs 7 different examples showing all features of the algorithm.

## Basic Usage

### Factor a specific number

```bash
python geometric_factorization.py --factor 143
```

Output:
```
Factoring N = 143
SUCCESS: 11 × 13, 1 attempts
```

### Use in Python code

```python
from geometric_factorization import geometric_factor, FactorizationParams

# Factor a semiprime
N = 143
params = FactorizationParams()
result = geometric_factor(N, params)

if result.success:
    p, q = result.factors
    print(f"Factors: {p} × {q}")
    print(f"Attempts: {result.attempts}")
```

## Common Tasks

### Generate and factor a semiprime

```python
from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams

# Generate a 12-bit semiprime
N, p, q = generate_semiprime(bit_size=12, seed=42)
print(f"N = {N}, factors = {p} × {q}")

# Factor it
params = FactorizationParams()
result = geometric_factor(N, params)

if result.success:
    print(f"✓ Found: {result.factors[0]} × {result.factors[1]}")
```

### Custom parameters

```python
# Create custom parameters
params = FactorizationParams(
    k_list=[0.3, 0.5, 0.7],      # Try different k values
    eps_list=[0.02, 0.05],       # Use tighter tolerances
    search_window=2048,           # Wider search
    max_attempts=5000             # More attempts
)

result = geometric_factor(N, params)
```

### Access detailed diagnostics

```python
result = geometric_factor(N, params)

# Show filtering statistics
for log in result.logs:
    print(f"k={log['k']}, ε={log['epsilon']}: "
          f"{log['pre_filter']} → {log['post_filter']} candidates")

# Show timing
print(f"Total time: {result.timings['total']:.3f}s")
```

## Understanding the Output

When you run the demo, you'll see output like:

```
Sample 1/3 (seed=12042)
  N = 2623
  True factors: 43 × 61
  ✓ Found: 43 × 61
  Attempts: 9
  Best filtering: 180 → 5 (k=0.2, ε=0.02)
  Time: 0.004s
```

This means:
- **N = 2623**: The semiprime being factored
- **True factors**: The actual prime factors (for validation)
- **✓ Found**: Success! Algorithm found the factors
- **Attempts: 9**: Took 9 trial divisions to find the factor
- **Best filtering: 180 → 5**: Started with 180 candidates, filtered to just 5
- **k=0.2, ε=0.02**: Parameters that gave best filtering
- **Time: 0.004s**: Execution time

## Understanding Candidate Filtering

The key to this algorithm is geometric filtering:

```
180 → 5 means:
- Started with 180 prime candidates near √N
- Geometric filtering reduced them to just 5
- That's a 36:1 reduction ratio!
```

Better filtering = fewer candidates to test = faster factorization

## Tips for Success

1. **Start small**: Test on 10-15 bit semiprimes first
2. **Use defaults**: Default parameters work well for most cases
3. **Check logs**: Look at filtering ratios to see what's working
4. **Be patient**: Larger semiprimes (20+ bits) may take more attempts

## Common Use Cases

### Research and Education

```python
# Understand how theta function works
from geometric_factorization import theta, circular_distance

N = 143  # 11 × 13
k = 0.45

theta_N = theta(N, k)
theta_p = theta(11, k)
theta_q = theta(13, k)

print(f"θ(N) = {theta_N:.6f}")
print(f"θ(11) = {theta_p:.6f}, distance = {circular_distance(theta_p, theta_N):.6f}")
print(f"θ(13) = {theta_q:.6f}, distance = {circular_distance(theta_q, theta_N):.6f}")
```

### Batch Testing

```python
# Test multiple semiprimes
from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams

params = FactorizationParams()
successes = 0

for i in range(10):
    N, p, q = generate_semiprime(12, seed=1000 + i)
    result = geometric_factor(N, params)
    if result.success:
        successes += 1

print(f"Success rate: {successes}/10")
```

### Performance Testing

```python
import time
from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams

# Time a factorization
N, p, q = generate_semiprime(15, seed=999)
params = FactorizationParams()

start = time.time()
result = geometric_factor(N, params)
elapsed = time.time() - start

print(f"Factored in {elapsed:.3f}s with {result.attempts} attempts")
```

## Next Steps

1. **Read the README**: Full documentation in `README.md`
2. **Run examples**: Check out `example_usage.py` for more detailed examples
3. **Read validation report**: See `VALIDATION_REPORT.md` for test results
4. **Experiment**: Try different bit sizes and parameters!

## Troubleshooting

### "Failed to factor after X attempts"

This is normal, especially for larger semiprimes. Try:
- Increasing `max_attempts`
- Widening `search_window`
- Adding more k values
- Using looser epsilon values

### "Factors don't match"

This should never happen! If it does:
1. Check that you're comparing the right values
2. File a bug report - this would be a serious issue

### Slow performance

For faster results:
- Test smaller semiprimes (< 16 bits)
- Reduce `prime_limit` and `spiral_iters`
- Use fewer k and epsilon values

## Getting Help

- Check the README for detailed documentation
- Look at example_usage.py for practical examples
- Read the validation report for expected behavior
- Review the inline code documentation

## Useful Commands Cheat Sheet

```bash
# Test everything
python geometric_factorization.py --test

# Run demo
python geometric_factorization.py --demo

# Run validation experiments
python geometric_factorization.py --validate

# Factor a specific number
python geometric_factorization.py --factor 143

# Run examples
python example_usage.py

# Quick help
python geometric_factorization.py --help
```

## Key Concepts in 1 Minute

1. **Geometric Mapping**: Maps numbers to angles on a unit circle using golden ratio
2. **Circular Distance**: Measures how close two angles are (with wrap-around)
3. **Filtering**: Keeps only candidates whose angle is close to N's angle
4. **Multi-pass**: Tries different parameter combinations (k, ε) until success

That's it! You're ready to start using the Geometric Factorization algorithm.

---

**Happy Factoring!** 🎯
