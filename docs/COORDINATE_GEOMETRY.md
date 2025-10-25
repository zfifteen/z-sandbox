# Coordinate Geometry Fundamentals

Foundational coordinate geometry module providing essential mathematical building blocks for geometric factorization techniques in the z-sandbox repository.

## Overview

The `coordinate_geometry` module implements fundamental plane and space geometry formulas that serve as building blocks for:
- **GVA (Geodesic Validation Assault)**: Torus embeddings and distance metrics
- **Z5D Axioms**: Discrete domain normalization and geometric transformations
- **QMC-φ Hybrid**: Variance-reduced Monte Carlo integration
- **Monte Carlo**: Stratified sampling and area-based variance reduction

## Features

### Distance Formulas
- **Euclidean distance**: 2D, 3D, n-dimensional
- **High-precision distance**: Using mpmath for < 1e-16 precision
- **Torus distance**: Wraparound metrics for [0,1) coordinates

**Application**: Computing initial geodesic proximities on d-dimensional torus before incorporating curvature κ in A* search refinements around √N.

### Midpoint and Section Division
- **Midpoint calculation**: 2D, 3D, n-dimensional
- **Section point**: Divide segments in ratio m:n

**Application**: Partitioning manifolds and generating candidate points in ZNeighborhood builders. Section formulas inform ratio-based divisions similar to Z5D axiom transformations Z = A(B/c).

### Centroid Calculations
- **Standard centroid**: 2D, 3D, n-dimensional
- **Weighted centroid**: Curvature-aware aggregation

**Application**: Aggregate flux-based positions in Riemannian metrics, validating factor clusters or balancing multi-dimensional embeddings in GVA.

### Area and Volume Computations
- **Triangle area**: Determinant method
- **Polygon area**: Shoelace formula
- **Tetrahedron volume**: 3D simplex

**Application**: Computing volumes or densities in higher-dimensional spaces, supporting prime-density mapping under Gauss-Prime Law or variance reduction in Monte Carlo integrations.

### Coordinate System Utilities
- **Quadrant determination**: 2D quadrants (I-IV)
- **Octant determination**: 3D octants (1-8)
- **Line equations**: Slope-intercept and general forms
- **Point-line distance**: Perpendicular distance

**Application**: Initializing coordinate frames in scripts like manifold_128bit.py, ensuring proper handling of fractional parts and modular constraints in residue filters.

## Installation

The module is part of the z-sandbox repository:

```bash
# Module location
python/coordinate_geometry.py

# Tests
tests/test_coordinate_geometry.py

# Demo
python/examples/coordinate_geometry_demo.py
```

## Quick Start

### Basic Usage

```python
from coordinate_geometry import (
    euclidean_distance_2d,
    midpoint_nd,
    centroid_nd,
    torus_distance_nd
)

# Distance calculation
d = euclidean_distance_2d(0, 0, 3, 4)  # 5.0

# Midpoint
m = midpoint_nd([0, 0], [4, 6])  # [2.0, 3.0]

# Centroid
c = centroid_nd([[0, 0], [3, 0], [0, 3]])  # [1.0, 1.0]

# Torus distance (with wraparound)
td = torus_distance_nd([0.1, 0.1], [0.9, 0.9])  # ~0.283
```

### Integration with GVA

```python
from coordinate_geometry import euclidean_distance_nd, torus_distance_nd

# Compute basic distance before curvature
emb_N = embed(N, dims=11)
emb_candidate = embed(candidate, dims=11)

# Base distance
base_dist = euclidean_distance_nd(emb_N, emb_candidate)

# Or use torus distance with wraparound
torus_dist = torus_distance_nd(emb_N, emb_candidate)

# Then apply Riemannian curvature
kappa = 4 * log(N+1) / exp(2)
riemannian_dist = base_dist * (1 + kappa * base_dist)
```

### Integration with Z5D

```python
from coordinate_geometry import section_point_nd, weighted_centroid_nd

# Section division for ratio-based transformations Z = A(B/c)
sqrt_N = math.sqrt(N)
search_range = [sqrt_N - 10, sqrt_N + 10]

# Divide in golden ratio φ:1
phi = (1 + math.sqrt(5)) / 2
section = section_point_nd([search_range[0]], [search_range[1]], phi, 1)

# Weighted centroid with curvature weights κ(n)
points = [embed(p) for p in candidate_factors]
weights = [curvature(p) for p in candidate_factors]
cluster_center = weighted_centroid_nd(points, weights)
```

### Integration with Monte Carlo

```python
from coordinate_geometry import polygon_area_2d, centroid_2d

# Stratified sampling with area-based allocation
strata = [
    [(25, 0), (27, 0), (27, 1), (25, 1)],
    [(27, 0), (29, 0), (29, 1), (27, 1)],
    [(29, 0), (31, 0), (31, 1), (29, 1)],
]

# Compute area for each stratum
areas = [polygon_area_2d(region) for region in strata]

# Sample proportionally to area for variance reduction
samples_per_stratum = [int(total_samples * a / sum(areas)) for a in areas]

# Compute centroids for initial sample points
centroids = [centroid_2d(region) for region in strata]
```

## Running Examples

### Module Demo
```bash
cd /home/runner/work/z-sandbox/z-sandbox
python3 python/coordinate_geometry.py
```

### Comprehensive Demo
```bash
PYTHONPATH=python python3 python/examples/coordinate_geometry_demo.py
```

### Run Tests
```bash
python3 tests/test_coordinate_geometry.py
# or
python3 -m pytest tests/test_coordinate_geometry.py -v
```

## Test Coverage

The module includes 60 comprehensive unit tests covering:
- ✅ Distance formulas (8 tests)
- ✅ Midpoint and section division (9 tests)
- ✅ Centroid calculations (7 tests)
- ✅ Area and volume computations (8 tests)
- ✅ Quadrants and octants (5 tests)
- ✅ Line equations (6 tests)
- ✅ Torus distance (5 tests)
- ✅ Edge cases and error handling (9 tests)
- ✅ Repository integration (3 tests)

All tests passing (100% success rate).

## API Reference

### Distance Functions
- `euclidean_distance_2d(x1, y1, x2, y2)` → float
- `euclidean_distance_3d(x1, y1, z1, x2, y2, z2)` → float
- `euclidean_distance_nd(p1, p2)` → float
- `euclidean_distance_nd_hp(p1, p2)` → mpf (high-precision)
- `torus_distance_1d(coord1, coord2)` → float
- `torus_distance_nd(coords1, coords2)` → float

### Midpoint and Section
- `midpoint_2d(x1, y1, x2, y2)` → (float, float)
- `midpoint_3d(x1, y1, z1, x2, y2, z2)` → (float, float, float)
- `midpoint_nd(p1, p2)` → List[float]
- `section_point_2d(x1, y1, x2, y2, m, n)` → (float, float)
- `section_point_nd(p1, p2, m, n)` → List[float]

### Centroid
- `centroid_2d(points)` → (float, float)
- `centroid_3d(points)` → (float, float, float)
- `centroid_nd(points)` → List[float]
- `weighted_centroid_nd(points, weights)` → List[float]

### Area and Volume
- `triangle_area_2d(x1, y1, x2, y2, x3, y3)` → float
- `triangle_area_vertices(vertices)` → float
- `polygon_area_2d(vertices)` → float
- `tetrahedron_volume(p1, p2, p3, p4)` → float

### Coordinate System
- `quadrant_2d(x, y)` → int (0-4)
- `octant_3d(x, y, z)` → int (0-8)
- `line_equation_2d_slope_intercept(x1, y1, x2, y2)` → (m, b)
- `line_equation_2d_general(x1, y1, x2, y2)` → (A, B, C)
- `point_line_distance_2d(px, py, A, B, C)` → float

## Integration with Repository

The coordinate geometry module is referenced in:
- **demo_z5d_rsa.py**: Z5D axiom demonstrations
- **qmc_phi_hybrid_demo.py**: QMC-φ variance reduction
- **manifold_128bit.py**: GVA torus embeddings (potential)
- **monte_carlo.py**: Stratified sampling (potential)

## Mathematical Foundation

These formulas provide foundational building blocks grounded in:
- **Euclidean geometry**: Standard distance metrics in ℝⁿ
- **Toroidal geometry**: Wraparound distance on [0,1)ⁿ torus
- **Affine geometry**: Ratio-based divisions and weighted centroids
- **Determinant methods**: Area/volume via cross products

They support advanced techniques:
- **Z5D axioms**: Z = A(B/c), κ(n) curvature, θ'(n,k) geometric resolution
- **Riemannian metrics**: Base distance before curvature incorporation
- **Variance reduction**: Stratified sampling with area-weighted allocation
- **Geometric validation**: Factor proximity detection in embedding space

## Performance

- Distance calculations: O(n) for n-dimensional points
- Centroid calculations: O(mn) for m points in n dimensions
- Area calculations: O(k) for k vertices
- High-precision: Uses mpmath for < 1e-16 accuracy

Suitable for real-time use in factorization algorithms with thousands of candidates.

## Related Documentation

- [Z5D RSA Factorization](../docs/Z5D_RSA_FACTORIZATION.md)
- [QMC-φ Hybrid Enhancement](../docs/QMC_PHI_HYBRID_ENHANCEMENT.md)
- [GVA Mathematical Framework](../docs/GVA_Mathematical_Framework.md)
- [Monte Carlo Integration](../docs/MONTE_CARLO_INTEGRATION.md)
- [Barycentric Coordinates](../docs/BARYCENTRIC_COORDINATES.md)

## License

Part of the z-sandbox repository (MIT License).

---

*Last updated: 2025-10-25*
