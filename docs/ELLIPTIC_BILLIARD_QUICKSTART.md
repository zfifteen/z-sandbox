# Elliptical Billiard Model - Quick Start Guide

## What is it?

A novel approach to integer factorization based on **wavefront propagation on a curved manifold**. In log-space, factor pairs satisfy x + y = log N (a line). We use an ellipse-like manifold as a heuristic embedding; the native integer geometry is xy = N, and the product-faithful two-foci analogue is the Cassini oval.

## Quick Start

### 1. Basic Usage

```python
from python.manifold_elliptic import embedTorusGeodesic_with_elliptic_refinement

# Factor a semiprime
N = 143  # 11 × 13

# Get candidate factor seeds
coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)

# Examine top candidates
for seed in seeds[:5]:
    p, q = seed['p'], seed['q']
    print(f"{p} × {q} = {p*q} (confidence: {seed['confidence']:.3f})")
```

### 2. Run Tests

```bash
# Run comprehensive test suite (7 tests)
python3 tests/test_elliptic_billiard.py

# Expected output: ✓ ALL TESTS PASSED!
```

### 3. Run Demo

```bash
# See the model in action
python3 python/examples/elliptic_billiard_demo.py

# See integration with GVA
python3 python/examples/elliptic_integration_example.py
```

## Mathematical Foundation

### The Core Insight

For semiprime N = p × q:
```
N = p × q  (product relationship)
log(N) = log(p) + log(q)  (log-sum identity)
```

In log-coordinates (x,y) = (log p, log q), valid factors lie on the **line** x + y = log(N), not an ellipse.

The product relationship p × q = N defines a **rectangular hyperbola** in the (p,q) plane, or equivalently, a **Cassini oval** (constant product of distances to foci) in transformed coordinates.

### Geometric Model

This implementation uses a **heuristic approximation** inspired by hyperbola/Cassini geometry:
- Respects the multiplicative structure (product, not sum)
- Generates approximate seed candidates, not exact factors
- Requires downstream refinement (GVA, trial division)

### Wavefront Convergence

1. Embed N in 17-dimensional torus with product-respecting metric
2. Propagate wavefront using simplified harmonic model
3. Detect convergence peaks (heuristic guidance)
4. Extract approximate factor seed candidates from peaks

## API Reference

### Main Functions

**`embed_elliptical_billiard(N, dims=17)`**
- Embeds N in high-dimensional torus
- Returns ellipse parameters and foci coordinates

**`propagate_wavefront_sympy(ellipse_data, N)`**
- Solves wave equation on manifold
- Returns wavefront solution parameters

**`detect_convergence_peaks(wavefront_solution, ellipse_data, dims=17)`**
- Finds peaks in wavefront amplitude
- Returns list of peak times and amplitudes

**`extract_factor_seeds(peaks, ellipse_data, N)`**
- Converts peaks to factor candidates
- Returns list of (p, q) pairs with confidence scores

**`embedTorusGeodesic_with_elliptic_refinement(N, k, dims=17)`**
- **Main integration function**
- Returns (coords, factor_seeds)
- Use this for most applications

## Example Results

### Test Case: N = 143 (11 × 13)

```
Log-sum relation: ✓ Verified (x + y = log N holds)
Generated 10 approximate seed candidates
Top seeds (for refinement):
  1. 15 × 9 = 135   (error: 5.6%, confidence: 1.500)
  2. 13 × 10 = 130  (error: 9.1%, confidence: 1.155)
  3. 12 × 11 = 132  (error: 7.7%, confidence: 1.155)
```

### Test Case: N = 10403 (101 × 103)

```
Top candidates:
  1. 161 × 64 = 10304  (error: 0.95%, confidence: 1.500)
  2. 130 × 79 = 10270  (error: 1.28%, confidence: 1.500)
  3. 114 × 90 = 10260  (error: 1.37%, confidence: 1.145)
```

## Integration with GVA

The elliptical billiard model generates **candidate seeds** that can initialize other factorization methods:

```python
# 1. Get seeds from elliptical billiard
coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)

# 2. Use seeds to guide GVA search
for seed in seeds[:10]:
    p_estimate = seed['p']
    # Run GVA geodesic search around p_estimate
    # Refine with Z5D predictions
    # Validate with trial division
```

## When to Use

### Best For:
- Balanced semiprimes (p ≈ q)
- Generating initial candidate guesses
- Multi-stage factorization pipelines
- Research and experimentation

### Limitations:
- Generates approximations, not exact factors
- Requires additional refinement/validation
- Best combined with other methods

## Performance

- **Embedding**: O(dims) = O(17) operations
- **Wavefront surrogate (1-D oscillator): O(1) per evaluation**; full 2-D PDE/eikonal solvers are **not O(1)** and are out of scope here.
- **Peak detection**: O(peaks) = O(20) samples
- **Extraction**: O(peaks) = O(10) candidates

Total: Very fast - milliseconds for small N (note: complexity for full ND eikonal would be O(M log M) with Fast Marching)

## Files

```
python/
  manifold_elliptic.py              # Core implementation
  examples/
    elliptic_billiard_demo.py       # Usage demonstration
    elliptic_integration_example.py # GVA integration

tests/
  test_elliptic_billiard.py         # Test suite (7 tests)

docs/
  elliptical_billiard_model.md      # Full documentation
  ELLIPTIC_BILLIARD_QUICKSTART.md   # This file
```

## Testing Status

✅ **7/7 Python tests passing**
✅ **All Java tests passing**
✅ **Module imports correctly**
✅ **Examples run successfully**

## Next Steps

1. **Try it**: Run `python3 tests/test_elliptic_billiard.py`
2. **Learn more**: Read `docs/elliptical_billiard_model.md`
3. **Experiment**: Modify `python/examples/elliptic_billiard_demo.py`
4. **Integrate**: Use with existing GVA/Z5D methods

## Theoretical Background

This implementation is based on modeling factorization as a **wave propagation problem on a curved manifold**, where:

- Factor locations emerge as **approximate convergence regions** of wavefront patterns
- Heuristic patterns reveal **geometric structure** of the product relationship
- Log-sum identity (log p + log q = log N) defines a **line** in log-coordinates
- Product structure (p × q = N) defines a **hyperbola** in integer space
- 17-dimensional torus provides embedding space (prime dimension avoids symmetry artifacts)

## Citation

Part of the z-sandbox RSA factorization framework.
Grounded in the hyperbola xy = N (integer space) with the log-sum relation used as a heuristic embedding (ellipse-like manifold is heuristic; Cassini ovals are the product analogue).

## Support

For issues or questions:
1. Check `docs/elliptical_billiard_model.md` for details
2. Run tests to verify installation
3. Review examples for usage patterns

---

**Status**: ✅ Fully Implemented and Tested
**Version**: 1.0
**Last Updated**: 2025-10-22
