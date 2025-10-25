#!/usr/bin/env python3
"""
Coordinate Geometry Fundamentals Demo

Comprehensive demonstration of coordinate geometry functions integrated
with the geometric factorization framework, showing practical applications
in GVA, Z5D, QMC, and Monte Carlo contexts.
"""

import sys
sys.path.insert(0, 'python')

from coordinate_geometry import (
    # Distance formulas
    euclidean_distance_2d, euclidean_distance_3d, euclidean_distance_nd, euclidean_distance_nd_hp,
    # Midpoint and section
    midpoint_2d, midpoint_3d, midpoint_nd, section_point_2d, section_point_nd,
    # Centroid
    centroid_2d, centroid_3d, centroid_nd, weighted_centroid_nd,
    # Area and volume
    triangle_area_2d, triangle_area_vertices, polygon_area_2d, tetrahedron_volume,
    # Quadrants
    quadrant_2d, octant_3d,
    # Line equations
    line_equation_2d_slope_intercept, line_equation_2d_general, point_line_distance_2d,
    # Torus
    torus_distance_1d, torus_distance_nd,
    PHI, E2
)

import math


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)


def demo_distance_formulas():
    """Demonstrate distance formulas with factorization context."""
    print_header("Distance Formulas - Geodesic Calculations on Torus")
    
    print("\n1. Basic Euclidean Distance (2D)")
    print("-" * 75)
    print("   Application: Prototype basic geodesic calculations before curvature")
    d = euclidean_distance_2d(0, 0, 3, 4)
    print(f"   Distance from (0,0) to (3,4): {d}")
    print(f"   Classic 3-4-5 triangle: √(3² + 4²) = {d}")
    
    print("\n2. Extended to Higher Dimensions (n-D)")
    print("-" * 75)
    print("   Application: Computing proximities in 5D/11D torus embeddings for GVA")
    
    # Simulate 5D torus embedding near √N for semiprime N=899
    sqrt_899 = math.sqrt(899)
    print(f"\n   Example: Semiprime N = 899 = 29 × 31, √N ≈ {sqrt_899:.2f}")
    
    # Simulate embeddings for candidate factors
    coords_29 = [0.234, 0.567, 0.123, 0.789, 0.456]  # Simulated embedding
    coords_31 = [0.245, 0.578, 0.134, 0.801, 0.467]  # Close to first
    
    d_5d = euclidean_distance_nd(coords_29, coords_31)
    print(f"   Distance between factor embeddings: {d_5d:.6f}")
    print(f"   (Before curvature κ adjustment in Riemannian metric)")
    
    print("\n3. High-Precision Distance (mpmath)")
    print("-" * 75)
    print("   Application: Z5D axiom validation with precision < 1e-16")
    d_hp = euclidean_distance_nd_hp([0, 0], [1, 1])
    print(f"   High-precision √2: {float(d_hp):.16f}")
    print(f"   Standard math.sqrt(2): {math.sqrt(2):.16f}")


def demo_midpoint_section():
    """Demonstrate midpoint and section division for manifold partitioning."""
    print_header("Midpoint & Section - Manifold Partitioning & Candidate Generation")
    
    print("\n1. Midpoint for ZNeighborhood Builders")
    print("-" * 75)
    print("   Application: Generating candidate points around √N")
    
    N = 899
    sqrt_N = math.sqrt(N)
    lower_bound = sqrt_N - 10
    upper_bound = sqrt_N + 10
    
    print(f"   Semiprime N = {N}, √N ≈ {sqrt_N:.2f}")
    print(f"   Search range: [{lower_bound:.2f}, {upper_bound:.2f}]")
    
    midpoint = (lower_bound + upper_bound) / 2
    print(f"   Midpoint of search range: {midpoint:.2f}")
    
    # Midpoint in 2D coordinate space
    p1 = (lower_bound, 0)
    p2 = (upper_bound, 0)
    mid_2d = midpoint_2d(*p1, *p2)
    print(f"   Midpoint in 2D: {mid_2d}")
    
    print("\n2. Section Division for Ratio-Based Offsets")
    print("-" * 75)
    print("   Application: Similar to Z5D transformations Z = A(B/c)")
    
    # Divide search range in golden ratio
    phi = float(PHI)
    print(f"   Golden ratio φ ≈ {phi:.6f}")
    
    # Section point dividing in φ:1 ratio
    section = section_point_2d(lower_bound, 0, upper_bound, 0, phi, 1)
    print(f"   Section point at φ:1 ratio: ({section[0]:.2f}, {section[1]:.2f})")
    print(f"   (Simulates dilation in theta-gating for ECM guidance)")


def demo_centroid():
    """Demonstrate centroid calculations for flux-based aggregation."""
    print_header("Centroid - Flux-Based Position Aggregation in Riemannian Metrics")
    
    print("\n1. Basic Centroid (Triangle)")
    print("-" * 75)
    print("   Application: Validating factor clusters in GVA")
    
    # Three candidate factors near √899
    candidates = [(29, 0), (30, 0), (31, 0)]
    c = centroid_2d(candidates)
    print(f"   Candidate factors: {candidates}")
    print(f"   Centroid: {c}")
    print(f"   (Expected near √899 ≈ {math.sqrt(899):.2f})")
    
    print("\n2. Weighted Centroid with Curvature")
    print("-" * 75)
    print("   Application: Curvature-weighted aggregation with κ(n)")
    
    # Simulate torus embedding coordinates
    points_5d = [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.15, 0.25, 0.35, 0.45, 0.55],
        [0.2, 0.3, 0.4, 0.5, 0.6]
    ]
    
    # Simulate curvature weights (increasing with distance from √N)
    weights = [1.0, 1.5, 2.0]
    
    c_weighted = weighted_centroid_nd(points_5d, weights)
    print(f"   Points: {len(points_5d)} 5D embeddings")
    print(f"   Weights (κ-based): {weights}")
    print(f"   Weighted centroid: [{', '.join(f'{x:.3f}' for x in c_weighted)}]")
    print(f"   (Weighted toward higher-curvature regions)")


def demo_area_volume():
    """Demonstrate area/volume for density mapping."""
    print_header("Area & Volume - Prime-Density Mapping via Determinants")
    
    print("\n1. Triangle Area (Determinant Method)")
    print("-" * 75)
    print("   Formula: Area = ½|x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|")
    print("   Application: Extend to volumes/densities in higher dimensions")
    
    area = triangle_area_2d(0, 0, 4, 0, 0, 3)
    print(f"   Right triangle (0,0), (4,0), (0,3): Area = {area}")
    
    print("\n2. Polygon Area (Shoelace Formula)")
    print("-" * 75)
    print("   Application: Computing regions in manifold partitioning")
    
    # Rectangle representing search space
    vertices = [(20, 0), (40, 0), (40, 10), (20, 10)]
    poly_area = polygon_area_2d(vertices)
    print(f"   Search rectangle vertices: {vertices}")
    print(f"   Area: {poly_area}")
    
    print("\n3. Tetrahedron Volume")
    print("-" * 75)
    print("   Application: 3D simplex volumes for stratified sampling")
    
    vol = tetrahedron_volume([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
    print(f"   Unit tetrahedron volume: {vol:.6f}")
    print(f"   (Foundation for barycentric stratification in Monte Carlo)")


def demo_torus_distance():
    """Demonstrate torus distance for GVA embeddings."""
    print_header("Torus Distance - GVA Torus Embeddings with Wraparound")
    
    print("\n1. 1D Torus Distance (Circular)")
    print("-" * 75)
    print("   Formula: min(|c1 - c2|, 1 - |c1 - c2|)")
    print("   Application: Component distance for fractional coordinates [0, 1)")
    
    d1 = torus_distance_1d(0.1, 0.9)
    d2 = torus_distance_1d(0.0, 0.5)
    print(f"   Distance 0.1 to 0.9: {d1:.2f} (wraparound)")
    print(f"   Distance 0.0 to 0.5: {d2:.2f} (direct)")
    
    print("\n2. n-D Torus Distance")
    print("-" * 75)
    print("   Application: Basic metric before Riemannian curvature in GVA")
    
    # Simulate 5D torus embeddings for factors
    # Using iterative frac(φ * frac(n / e²)^k) pattern
    N = 899
    e2 = float(E2)
    phi = float(PHI)
    k = 0.5 / math.log2(math.log2(N + 1))
    
    def simple_embed(n, dims=5):
        """Simplified embedding simulation."""
        x = n / e2
        coords = []
        for _ in range(dims):
            x_mod = x % phi
            ratio = x_mod / phi if x_mod > 0 else 1e-50
            x = phi * (ratio ** k)
            coords.append(x % 1)  # Fractional part
        return coords
    
    emb_29 = simple_embed(29)
    emb_31 = simple_embed(31)
    
    d_torus = torus_distance_nd(emb_29, emb_31)
    print(f"   Embedding for factor 29: [{', '.join(f'{x:.3f}' for x in emb_29)}]")
    print(f"   Embedding for factor 31: [{', '.join(f'{x:.3f}' for x in emb_31)}]")
    print(f"   Torus distance: {d_torus:.6f}")
    print(f"   (Foundation for Riemannian distance with κ(n) curvature)")


def demo_integration_examples():
    """Demonstrate integration with repository concepts."""
    print_header("Integration Examples - GVA, Z5D, QMC Applications")
    
    print("\n1. A* Search Refinement Around √N")
    print("-" * 75)
    print("   Using distance formulas for initial proximity before curvature")
    
    N = 899
    sqrt_N = math.sqrt(N)
    candidates = [29, 30, 31]
    
    print(f"   Target N = {N}, √N ≈ {sqrt_N:.2f}")
    print(f"   Candidates: {candidates}")
    
    for c in candidates:
        dist = abs(c - sqrt_N)
        print(f"   Distance from √N to {c}: {dist:.2f}")
    
    print("\n2. Variance Reduction in Monte Carlo")
    print("-" * 75)
    print("   Area calculations for stratified sampling regions")
    
    # Divide search space into strata
    regions = [
        [(25, 0), (27, 0), (27, 1), (25, 1)],
        [(27, 0), (29, 0), (29, 1), (27, 1)],
        [(29, 0), (31, 0), (31, 1), (29, 1)],
    ]
    
    print(f"   Stratified search space: {len(regions)} regions")
    for i, region in enumerate(regions, 1):
        area = polygon_area_2d(region)
        print(f"   Region {i} area: {area}")
    
    print("\n3. Residue Filter Initialization")
    print("-" * 75)
    print("   Quadrant-based coordinate frame handling")
    
    # Check quadrants for modular constraints
    test_points = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for p in test_points:
        q = quadrant_2d(*p)
        print(f"   Point {p} → Quadrant {q}")


def demo_practical_usage():
    """Show practical usage patterns from the issue."""
    print_header("Practical Usage - From Issue Examples")
    
    print("\n1. Distance in manifold_128bit.py")
    print("-" * 75)
    print("   Computing initial proximities before κ incorporation")
    
    code = '''
    # In manifold_128bit.py context:
    from coordinate_geometry import euclidean_distance_nd
    
    emb_N = embed(N, dims=11)
    emb_candidate = embed(candidate, dims=11)
    base_dist = euclidean_distance_nd(emb_N, emb_candidate)
    # Then apply: riemannian_dist = base_dist * (1 + kappa * base_dist)
    '''
    print(code)
    
    print("\n2. Centroid in GVA Validation")
    print("-" * 75)
    print("   Aggregating flux-based positions for cluster validation")
    
    code = '''
    # In GVA context:
    from coordinate_geometry import centroid_nd
    
    factor_embeddings = [embed(p) for p in candidate_factors]
    cluster_center = centroid_nd(factor_embeddings)
    # Verify if cluster_center aligns with embed(N)
    '''
    print(code)
    
    print("\n3. Midpoint in QMC Sampling")
    print("-" * 75)
    print("   Generating stratified sample points")
    
    code = '''
    # In qmc_phi_hybrid_demo.py:
    from coordinate_geometry import midpoint_nd
    
    strata_start = [0.0, 0.0, 0.0]
    strata_end = [0.5, 0.5, 0.5]
    sample_point = midpoint_nd(strata_start, strata_end)
    '''
    print(code)


def main():
    """Run all demonstrations."""
    print("=" * 75)
    print("  COORDINATE GEOMETRY FUNDAMENTALS DEMONSTRATION")
    print("  Foundational Building Blocks for Geometric Factorization")
    print("=" * 75)
    
    # Run demonstrations
    demo_distance_formulas()
    demo_midpoint_section()
    demo_centroid()
    demo_area_volume()
    demo_torus_distance()
    demo_integration_examples()
    demo_practical_usage()
    
    # Summary
    print_header("Summary")
    print("""
    Coordinate geometry fundamentals provide essential building blocks for:
    
    ✓ Distance Formulas: Euclidean distances for geodesic calculations on torus
      → Before incorporating curvature κ in A* search refinements
      → Supporting GVA proximity detection and validation
    
    ✓ Midpoint & Section: Partitioning manifolds and candidate generation
      → ZNeighborhood builders around √N
      → Ratio-based divisions similar to Z5D transformations Z = A(B/c)
    
    ✓ Centroid Calculations: Flux-based position aggregation
      → Validating factor clusters in GVA
      → Curvature-weighted with κ(n) for Riemannian metrics
    
    ✓ Area & Volume: Determinant-based density computations
      → Prime-density mapping under Gauss-Prime Law
      → Variance reduction in Monte Carlo stratification
    
    ✓ Torus Distance: Wraparound metrics for embeddings
      → Foundation for Riemannian distance in GVA
      → Handling fractional parts and modular constraints
    
    These formulas streamline testing and enhance geometric intuition during
    benchmarks, potentially improving success rates on 256-bit targets by
    grounding advanced curvatures in basic plane principles.
    """)
    
    print("=" * 75)
    print("  Demonstration Complete!")
    print("=" * 75)


if __name__ == "__main__":
    main()
