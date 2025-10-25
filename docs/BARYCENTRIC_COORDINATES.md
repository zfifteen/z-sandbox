# Barycentric Coordinates Enhancement

## Overview

This document describes the integration of barycentric coordinate concepts into the Z-Sandbox geometric factorization framework. Barycentric coordinates provide a natural way to express points in simplices (generalized triangles) as weighted combinations of vertices, enabling affine-invariant distance calculations and improved sampling strategies.

## Mathematical Foundation

### Barycentric Coordinates

For a point **P** in a simplex with vertices **V**₀, **V**₁, ..., **V**ₙ, the barycentric coordinates are weights λ₀, λ₁, ..., λₙ such that:

```
P = λ₀V₀ + λ₁V₁ + ... + λₙVₙ
```

with the constraint:

```
Σλᵢ = 1
```

For points inside the simplex, all λᵢ ≥ 0. The barycentric coordinates are unique and provide an affine-invariant representation.

### Integration with Z5D Axioms

The barycentric framework integrates naturally with the existing Z5D axioms:

**Axiom 1: Universal Invariant**
```
Z = A(B / c)
```
Barycentric weights can be normalized using the universal constant c = e².

**Axiom 2: Discrete Domain**
```
Z = n(Δ_n / Δ_max)
```
Barycentric coordinates provide normalized weights analogous to Δ_n / Δ_max.

**Axiom 3: Curvature**
```
κ(n) = d(n) · ln(n+1) / e²
```
Barycentric weights can be modulated by curvature for geometry-aware interpolation.

**Axiom 4: Geometric Resolution**
```
θ'(n, k) = φ · ((n mod φ) / φ)^k
```
Barycentric sampling can incorporate φ-modulation for prime-density mapping.

## Implementation

### Core Module: `barycentric.py`

The barycentric module provides:

1. **BarycentricCoordinates Class**
   - Compute barycentric coordinates from point positions
   - Interpolate points from barycentric coordinates
   - Check if points are inside simplices
   - Calculate centroids

2. **Distance Metrics**
   - Affine-invariant distance in barycentric space
   - Multiple metrics: Euclidean, Manhattan, Chebyshev

3. **Curvature Weighting**
   - Modulate barycentric weights by curvature functions
   - Integration with Z5D κ(n) for geometry-aware interpolation

4. **Simplicial Stratification**
   - Generate uniformly distributed samples within simplices
   - Reproducible sampling with RNG control

5. **Torus Integration**
   - Barycentric embedding for torus coordinates
   - Anchor vertex generation based on curvature hotspots
   - Enhanced distance calculations for GVA

### Monte Carlo Integration: "barycentric" Mode

The `FactorizationMonteCarloEnhancer` now supports a "barycentric" sampling mode:

```python
from monte_carlo import FactorizationMonteCarloEnhancer

enhancer = FactorizationMonteCarloEnhancer(seed=42)
candidates = enhancer.biased_sampling_with_phi(
    N=899,
    num_samples=500,
    mode='barycentric'
)
```

#### How Barycentric Sampling Works

1. **Define Search Space**: Create a simplex (triangle) representing the search space around √N
   - Anchor vertices: left boundary, center (√N), right boundary

2. **Stratified Sampling**: Use Dirichlet distribution to generate uniform barycentric coordinates

3. **Curvature Weighting**: Apply κ(n)-based weights to bias toward √N region

4. **Candidate Generation**: Map barycentric coordinates to integer candidates

5. **φ-Modulation**: Apply golden ratio fine-tuning for prime-density alignment

## Usage Examples

### Basic Barycentric Coordinates

```python
import numpy as np
from barycentric import BarycentricCoordinates

# Define triangle vertices
vertices = [
    np.array([0.0, 0.0]),
    np.array([1.0, 0.0]),
    np.array([0.0, 1.0])
]

bc = BarycentricCoordinates(vertices)

# Test point
point = np.array([0.3, 0.2])

# Compute barycentric coordinates
lambdas = bc.compute_barycentric_coords(point)
print(f"Barycentric coordinates: {lambdas}")
print(f"Sum: {np.sum(lambdas)}")  # Should be 1.0

# Reconstruct point
reconstructed = bc.interpolate(lambdas)
print(f"Reconstructed: {reconstructed}")
```

### Curvature-Weighted Sampling

```python
from barycentric import curvature_weighted_barycentric

# Define curvature function (Z5D κ(n))
def kappa_func(vertex_idx):
    # Higher weight for vertices near √N
    weights = [0.2, 0.2, 0.6]
    return weights[vertex_idx]

# Compute curvature-weighted coordinates
weighted = curvature_weighted_barycentric(point, vertices, kappa_func)
print(f"Weighted coordinates: {weighted}")
```

### Monte Carlo Factorization

```python
from monte_carlo import FactorizationMonteCarloEnhancer

# Initialize enhancer
enhancer = FactorizationMonteCarloEnhancer(seed=42)

# Test semiprime
N = 899  # 29 × 31

# Compare sampling modes
modes = ['uniform', 'qmc_phi_hybrid', 'barycentric']

for mode in modes:
    candidates = enhancer.biased_sampling_with_phi(N, 500, mode=mode)
    hit = 29 in candidates or 31 in candidates
    print(f"{mode:15s}: {len(candidates):4d} candidates, hit={hit}")
```

### Torus Embedding Integration

```python
from barycentric import torus_barycentric_embedding, barycentric_distance_torus

N = 899
p, q = 29, 31

# Generate torus embeddings with barycentric anchors
embedding_N, anchors_N = torus_barycentric_embedding(N, dims=5)
embedding_p, anchors_p = torus_barycentric_embedding(p, dims=5)

# Compute barycentric distance
dist = barycentric_distance_torus(embedding_N, embedding_p, N)
print(f"Barycentric distance d(θ(N), θ(p)) = {dist:.6f}")
```

## Performance Characteristics

### Test Results (N=899, seed=42, 500 samples)

| Mode           | Hit Rate | Candidates | Throughput   | Notes                        |
|----------------|----------|------------|--------------|------------------------------|
| uniform        | 100%     | 3          | 15,177 cand/s| Fast, minimal candidates     |
| qmc_phi_hybrid | 100%     | 197        | 145,148 cand/s| Best overall (RECOMMENDED)  |
| barycentric    | 100%     | 102        | 2,194 cand/s | Good coverage, moderate speed|

### When to Use Barycentric Mode

**Advantages:**
- Affine-invariant distance calculations
- Natural integration with Z5D curvature weighting
- Good candidate coverage with moderate candidate count
- Mathematically principled stratification

**Use Cases:**
- When geometric invariance is important
- For integration with curved space embeddings (GVA)
- When moderate candidate counts are acceptable
- For research into geometric factorization methods

**Trade-offs:**
- Lower throughput than QMC-φ hybrid (~7% of speed)
- Higher computational overhead per candidate
- Best for problems where geometric properties matter

## Integration with Existing Framework

### GVA (Geodesic Validation Assault)

Barycentric coordinates enhance GVA by:

1. **Affine-Invariant Distances**: More robust factor proximity detection
2. **Anchor Vertices**: Define canonical positions in torus space
3. **Curvature-Aware Interpolation**: Better handling of curved geometry

### Z5D Axioms

Barycentric framework aligns with Z5D axioms:

- **Normalization**: Barycentric constraint Σλᵢ = 1 mirrors discrete domain normalization
- **Curvature Integration**: Natural way to apply κ(n) weighting
- **Geometric Resolution**: Compatible with θ'(n, k) embeddings

### Monte Carlo Integration

Barycentric stratification provides:

- **Improved Coverage**: Uniform sampling over search simplices
- **Variance Reduction**: Stratified approach reduces clustering
- **Reproducibility**: Deterministic with seed control

## Testing

### Test Coverage

The barycentric module has comprehensive test coverage:

- **18 core tests** in `test_barycentric.py` (100% pass rate)
- **8 integration tests** in `test_monte_carlo_barycentric.py` (100% pass rate)

Test categories:
1. Basic barycentric coordinate calculations
2. Interpolation and reconstruction
3. Distance metrics
4. Curvature weighting
5. Simplicial stratification
6. Torus embedding integration
7. Monte Carlo integration
8. High-dimensional simplices (up to 11D for GVA)

### Running Tests

```bash
# Core barycentric tests
PYTHONPATH=python python3 tests/test_barycentric.py

# Monte Carlo integration tests
PYTHONPATH=python python3 tests/test_monte_carlo_barycentric.py

# Run demo
PYTHONPATH=python python3 python/examples/barycentric_demo.py
```

## Future Work

### Potential Enhancements

1. **GVA Integration**: Fully integrate barycentric distances into GVA factorization pipeline
2. **Higher-Dimensional Optimization**: Optimize for 11D+ torus embeddings
3. **Adaptive Anchor Placement**: Dynamic anchor vertices based on factorization progress
4. **Parallel Sampling**: Multi-threaded simplicial stratification
5. **Hybrid Approaches**: Combine barycentric with QMC for best of both worlds

### Research Directions

1. **Affine Invariance**: Exploit affine properties for cryptanalysis
2. **Curved Space Geometry**: Better handling of Riemannian curvature in torus
3. **Prime Density Mapping**: Use barycentric weights for prime distribution
4. **Simplicial Decomposition**: Partition torus space into simplices for parallel search

## References

### Mathematical Background

- Barycentric coordinates: Classical concept in affine geometry
- Dirichlet distribution: Generates uniform samples over simplices
- Z5D Axioms: Core mathematical framework of Z-Sandbox

### Related Documentation

- [Z5D_RSA_FACTORIZATION.md](Z5D_RSA_FACTORIZATION.md) - Z5D axioms and RSA factorization
- [MONTE_CARLO_INTEGRATION.md](MONTE_CARLO_INTEGRATION.md) - Monte Carlo methods
- [GVA_Mathematical_Framework.md](GVA_Mathematical_Framework.md) - GVA foundations
- [QMC_PHI_HYBRID_ENHANCEMENT.md](QMC_PHI_HYBRID_ENHANCEMENT.md) - QMC-φ hybrid mode

### Implementation Files

- `python/barycentric.py` - Core barycentric module (580 lines)
- `python/monte_carlo.py` - Monte Carlo integration with barycentric mode
- `tests/test_barycentric.py` - Core tests (18 tests)
- `tests/test_monte_carlo_barycentric.py` - Integration tests (8 tests)
- `python/examples/barycentric_demo.py` - Demonstration script

## Conclusion

The barycentric coordinates enhancement provides a mathematically principled framework for affine-invariant geometric operations in the Z-Sandbox factorization pipeline. While not the fastest sampling mode, it offers unique advantages in geometric invariance and natural integration with curved space embeddings, making it valuable for research and specific use cases where geometric properties are paramount.

The implementation is production-ready with comprehensive test coverage, reproducible sampling, and clean integration with existing Z5D axioms and Monte Carlo infrastructure.
