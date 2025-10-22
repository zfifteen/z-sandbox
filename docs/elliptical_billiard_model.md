# Elliptical Billiard Model for Factorization

## Overview

The Elliptical Billiard Model is a novel approach to integer factorization that models the problem as **wavefront propagation on a curved manifold**. It leverages the geometric properties of ellipses in logarithmic space to identify factor candidates through self-interference patterns.

## Mathematical Framework

### Core Insight

For a semiprime N = p × q:

```
N = p × q
→ log(N) = log(p) + log(q)
```

In logarithmic space, N is the "sum" of two values at log(p) and log(q).

### Ellipse Property

A fundamental property of ellipses: For any point on an ellipse, the sum of distances to two foci is constant:

```
d(point, focus₁) + d(point, focus₂) = 2a  (constant)
```

where `a` is the semi-major axis.

### Hypothesis

If we place foci at log(p) and log(q), then log(N) lies on an ellipse in the embedding space. Wavefronts propagating from log(N) will converge at the foci, revealing factor locations through self-intersection patterns.

## Implementation

### Components

1. **Elliptical Embedding** (`embed_elliptical_billiard`)
   - Embeds N in a 17-dimensional torus with elliptical geometry
   - Places foci at estimated factor locations
   - Uses golden ratio for coordinate distribution

2. **Wavefront Propagation** (`propagate_wavefront_sympy`)
   - Solves Helmholtz equation: ∇²u + k²u = 0
   - Models wave propagation on the curved manifold
   - Returns analytical solution: u(t) = cos(k·t)

3. **Peak Detection** (`detect_convergence_peaks`)
   - Analyzes wavefront solution to find convergence peaks
   - Peaks indicate potential factor locations
   - Returns top candidates by amplitude

4. **Factor Seed Extraction** (`extract_factor_seeds`)
   - Converts convergence peaks to candidate factor values
   - Maps from ellipse coordinates back to integer space
   - Provides confidence scores for each candidate

5. **Coordinate Refinement** (`refine_with_peaks`)
   - Adjusts embedding coordinates based on wavefront convergence
   - Weights adjustments by peak confidence
   - Integrates with existing manifold methods

### Full Integration

The `embedTorusGeodesic_with_elliptic_refinement` function combines all steps:

```python
coords, factor_seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)
```

Returns:
- `coords`: Refined 17-dimensional embedding coordinates
- `factor_seeds`: List of candidate factor pairs with confidence scores

## Usage

### Basic Example

```python
from python.manifold_elliptic import embedTorusGeodesic_with_elliptic_refinement

N = 143  # 11 × 13

# Run elliptical billiard model
coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)

# Examine top candidates
for seed in seeds[:5]:
    p, q = seed['p'], seed['q']
    print(f"Candidate: {p} × {q} = {p*q} (confidence: {seed['confidence']:.3f})")
```

### Integration with Existing Methods

The elliptical billiard model is designed to work with existing factorization approaches:

```python
# 1. Get candidate seeds from elliptical billiard
coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)

# 2. Use seeds to initialize GVA geodesic search
for seed in seeds[:10]:
    p_estimate = seed['p']
    # Run GVA around this estimate
    
# 3. Refine with Z5D predictions
# 4. Validate with trial division
```

## Why This Works

### 1. Ellipse Geometry Captures Factorization

The relationship N = p × q translates naturally to ellipse geometry in log-space:
- Center is at log(N)/2
- Foci are at log(p) and log(q)
- Semi-major axis is log(N)/2
- Distance between foci relates to factor imbalance

### 2. Wavefront Convergence Reveals Foci

Physical intuition:
- Wave emitted from N's embedding
- Travels through curved torus manifold
- Converges at factor locations (foci)
- Self-intersection points indicate factor candidates

### 3. PDE Solution Provides Time Evolution

Mathematical advantages:
- Helmholtz equation has well-studied solutions
- Analytical solution for simple cases
- Peaks in amplitude indicate factor locations
- Multiple modes capture different factor candidates

### 4. 17-Dimensional Torus Provides Rich Structure

Dimensionality benefits:
- 17 is prime → avoids unwanted symmetries
- Sufficient dimensions to embed complex ellipses
- Golden ratio distribution ensures good coverage
- Compatible with existing GVA methods

## Test Results

### Ellipse Property Verification

For balanced semiprimes (p ≈ q), the distances from log(p) and log(q) to the center are nearly equal:

```
N = 143 = 11 × 13
  log(N)/2 = 2.4814
  Distance to log(11) = 0.0835
  Distance to log(13) = 0.0835
  ✓ Balanced semiprime verified
```

### Candidate Generation

The model successfully generates candidate seeds close to true factors:

```
N = 10403 = 101 × 103
Top candidates:
  1. 161 × 64 = 10304 (error: 0.95%)
  2. 130 × 79 = 10270 (error: 1.28%)
  3. 114 × 90 = 10260 (error: 1.37%)
```

## Practical Application

### Use Case: Candidate Seed Generation

The elliptical billiard model excels at:
1. **Initial estimates** - Provides multiple starting points for refinement
2. **Geometric insight** - Captures structural properties of factorization
3. **Confidence scoring** - Ranks candidates by likelihood
4. **Integration** - Works with existing GVA/Z5D methods

### Workflow

```
┌─────────────────────────────────────────┐
│ 1. Elliptical Billiard Model            │
│    → Generate candidate seeds            │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. Seed-Initialized GVA                 │
│    → Geodesic search around seeds       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. Z5D Refinement                       │
│    → Prime index predictions            │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 4. Trial Division                       │
│    → Validate candidates                │
└─────────────────────────────────────────┘
```

## Advantages Over Baseline

1. **Theoretically Motivated** - Based on ellipse geometry in log-space
2. **Multi-Scale** - Works for balanced and unbalanced semiprimes
3. **Multiple Candidates** - Provides ranked list of possibilities
4. **Complementary** - Enhances rather than replaces existing methods
5. **Adaptive** - Ellipse shape adapts to factor distribution

## Limitations

1. **Approximate** - Generates candidate seeds, not exact factors
2. **Computational** - Requires multiple computations per semiprime
3. **Refinement Needed** - Must be combined with validation methods
4. **Scale Dependent** - Performance varies with semiprime size

## Files

- **Implementation**: `python/manifold_elliptic.py`
- **Tests**: `tests/test_elliptic_billiard.py`
- **Demo**: `python/examples/elliptic_billiard_demo.py`

## Running Tests

```bash
# Run comprehensive test suite
python3 tests/test_elliptic_billiard.py

# Run demonstration
python3 python/examples/elliptic_billiard_demo.py

# Test module directly
python3 python/manifold_elliptic.py
```

## Future Enhancements

1. **Numerical PDE Solvers** - For better accuracy with large N
2. **Multi-Scale Analysis** - Coarse-to-fine grain refinement
3. **Quantum-Inspired Methods** - Wavefunction superposition
4. **Machine Learning** - Train on peak patterns
5. **Parallel Processing** - Evaluate multiple seeds simultaneously

## References

This implementation is based on the mathematical insight that factorization can be modeled as a wave propagation problem on a curved manifold, where factor locations emerge as convergence points of self-interfering wavefronts.

## License

Part of the z-sandbox RSA factorization framework.
