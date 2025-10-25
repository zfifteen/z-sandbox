#!/usr/bin/env python3
"""
Barycentric Coordinates Module

Implements barycentric coordinate concepts for geometric factorization enhancement.
Barycentric coordinates express points in a simplex as weighted combinations of vertices,
with weights summing to 1. This provides a natural framework for:

1. Affine-invariant distance calculations
2. Convex interpolation in geometric spaces
3. Weighted averaging in higher-dimensional embeddings
4. Stratified sampling in simplicial decompositions

Mathematical Foundation:
- For a point P in a simplex with vertices V₀, V₁, ..., Vₙ
- P = λ₀V₀ + λ₁V₁ + ... + λₙVₙ where Σλᵢ = 1 and λᵢ ≥ 0
- The weights λᵢ are the barycentric coordinates

Integration with Z5D Axioms:
- Universal invariant: Z = A(B / c)
- Discrete domain: Z = n(Δ_n / Δ_max) 
- Curvature weighting: κ(n) = d(n)·ln(n+1)/e²
- Barycentric weights can be modulated by κ(n) for curvature-aware interpolation

References:
- Issue: "barycentric coordinates" enhancement proposal
- Existing framework: manifold_core.py, monte_carlo.py, z5d_axioms.py
"""

import math
from typing import List, Tuple, Optional, Callable
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt
import numpy as np

# Set high precision
mp.dps = 50

# Universal constants (from Z5D axioms)
PHI = mpf((1 + mpsqrt(5)) / 2)  # Golden ratio
E2 = exp(2)  # e² invariant


class BarycentricCoordinates:
    """
    Barycentric coordinate system for simplex-based geometric operations.
    
    A simplex in ℝⁿ is defined by n+1 vertices. Points within the simplex
    can be uniquely expressed as convex combinations (barycentric coords).
    """
    
    def __init__(self, vertices: List[np.ndarray]):
        """
        Initialize barycentric coordinate system with simplex vertices.
        
        Args:
            vertices: List of vertex positions (numpy arrays of same dimension)
            
        Raises:
            ValueError: If vertices are invalid or degenerate
        """
        if not vertices or len(vertices) < 2:
            raise ValueError("Need at least 2 vertices for a simplex")
        
        # Convert to numpy arrays and validate
        self.vertices = [np.array(v, dtype=float) for v in vertices]
        self.n_vertices = len(self.vertices)
        self.dimension = len(self.vertices[0])
        
        # Validate all vertices have same dimension
        for v in self.vertices:
            if len(v) != self.dimension:
                raise ValueError("All vertices must have the same dimension")
    
    def compute_barycentric_coords(self, point: np.ndarray) -> np.ndarray:
        """
        Compute barycentric coordinates of a point with respect to simplex vertices.
        
        For a point P and simplex vertices V₀, V₁, ..., Vₙ:
        P = λ₀V₀ + λ₁V₁ + ... + λₙVₙ where Σλᵢ = 1
        
        Args:
            point: Point position (numpy array)
            
        Returns:
            Barycentric coordinates λ = [λ₀, λ₁, ..., λₙ]
            
        Note:
            Uses least-squares solution for overdetermined systems (robust).
            For points outside simplex, some λᵢ may be negative.
        """
        point = np.array(point, dtype=float)
        
        if len(point) != self.dimension:
            raise ValueError(f"Point dimension {len(point)} doesn't match simplex dimension {self.dimension}")
        
        # Special case: 1D simplex (line segment)
        if self.n_vertices == 2:
            v0, v1 = self.vertices
            # Parametric form: P = (1-t)V₀ + tV₁
            diff = v1 - v0
            norm_sq = np.dot(diff, diff)
            if norm_sq < 1e-15:
                # Degenerate case: vertices coincide
                return np.array([1.0, 0.0])
            t = np.dot(point - v0, diff) / norm_sq
            return np.array([1 - t, t])
        
        # General case: Solve linear system
        # Construct matrix: [V₁-V₀ | V₂-V₀ | ... | Vₙ-V₀]
        v0 = self.vertices[0]
        A = np.column_stack([v - v0 for v in self.vertices[1:]])
        b = point - v0
        
        # Solve A·w = b where w = [λ₁, λ₂, ..., λₙ]
        try:
            # Use least squares for robustness
            w, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
            
            # Construct full barycentric coords
            lambdas = np.zeros(self.n_vertices)
            lambdas[1:] = w
            lambdas[0] = 1.0 - np.sum(w)
            
            return lambdas
        except np.linalg.LinAlgError:
            # Degenerate simplex - return equal weights
            return np.ones(self.n_vertices) / self.n_vertices
    
    def interpolate(self, lambdas: np.ndarray) -> np.ndarray:
        """
        Interpolate point from barycentric coordinates.
        
        Given λ = [λ₀, λ₁, ..., λₙ], compute:
        P = Σᵢ λᵢVᵢ
        
        Args:
            lambdas: Barycentric coordinates (should sum to 1)
            
        Returns:
            Interpolated point position
        """
        if len(lambdas) != self.n_vertices:
            raise ValueError(f"Expected {self.n_vertices} coordinates, got {len(lambdas)}")
        
        # Normalize to ensure sum = 1 (defensive)
        lambdas = np.array(lambdas)
        lambdas_sum = np.sum(lambdas)
        if abs(lambdas_sum) > 1e-15:
            lambdas = lambdas / lambdas_sum
        
        # Weighted sum: P = Σᵢ λᵢVᵢ
        point = np.zeros(self.dimension)
        for i, v in enumerate(self.vertices):
            point += lambdas[i] * v
        
        return point
    
    def is_inside_simplex(self, lambdas: np.ndarray, tolerance: float = 1e-10) -> bool:
        """
        Check if barycentric coordinates correspond to point inside simplex.
        
        Point is inside iff all λᵢ ≥ 0 and Σλᵢ = 1.
        
        Args:
            lambdas: Barycentric coordinates
            tolerance: Numerical tolerance for checks
            
        Returns:
            True if point is inside simplex
        """
        # Check sum = 1
        if abs(np.sum(lambdas) - 1.0) > tolerance:
            return False
        
        # Check all non-negative
        return np.all(lambdas >= -tolerance)
    
    def centroid(self) -> np.ndarray:
        """
        Compute centroid (center of mass) of simplex.
        
        Centroid has uniform barycentric coordinates: λᵢ = 1/n for all i.
        
        Returns:
            Centroid position
        """
        uniform_weights = np.ones(self.n_vertices) / self.n_vertices
        return self.interpolate(uniform_weights)


def barycentric_distance(point1: np.ndarray, point2: np.ndarray, 
                         vertices: List[np.ndarray],
                         metric: str = 'euclidean') -> float:
    """
    Compute distance between two points using barycentric coordinate system.
    
    This provides an affine-invariant distance metric:
    1. Express both points in barycentric coordinates
    2. Compute distance in barycentric space
    3. Optionally apply curvature weighting
    
    Args:
        point1, point2: Points to measure distance between
        vertices: Simplex vertices defining barycentric system
        metric: Distance metric ('euclidean', 'manhattan', 'chebyshev')
        
    Returns:
        Distance value
    """
    bc = BarycentricCoordinates(vertices)
    
    # Get barycentric coordinates
    lambda1 = bc.compute_barycentric_coords(point1)
    lambda2 = bc.compute_barycentric_coords(point2)
    
    # Compute distance in barycentric space
    if metric == 'euclidean':
        return float(np.linalg.norm(lambda1 - lambda2))
    elif metric == 'manhattan':
        return float(np.sum(np.abs(lambda1 - lambda2)))
    elif metric == 'chebyshev':
        return float(np.max(np.abs(lambda1 - lambda2)))
    else:
        raise ValueError(f"Unknown metric: {metric}")


def curvature_weighted_barycentric(point: np.ndarray,
                                   vertices: List[np.ndarray],
                                   kappa_func: Optional[Callable] = None) -> np.ndarray:
    """
    Compute curvature-weighted barycentric coordinates.
    
    Integration with Z5D axioms:
    - Standard barycentric: λᵢ from geometric projection
    - Curvature weighting: λ'ᵢ = λᵢ · w(κᵢ) where w is weight function
    - Renormalization: λ'ᵢ / Σλ'ⱼ to maintain Σλ'ᵢ = 1
    
    Args:
        point: Point to compute coordinates for
        vertices: Simplex vertices
        kappa_func: Optional curvature function κ(vertex_idx) -> weight
        
    Returns:
        Curvature-weighted barycentric coordinates
    """
    bc = BarycentricCoordinates(vertices)
    lambdas = bc.compute_barycentric_coords(point)
    
    if kappa_func is None:
        return lambdas
    
    # Apply curvature weighting
    weighted = np.zeros_like(lambdas)
    for i in range(len(lambdas)):
        kappa_weight = kappa_func(i)
        weighted[i] = lambdas[i] * (1.0 + kappa_weight)
    
    # Renormalize
    weighted_sum = np.sum(weighted)
    if abs(weighted_sum) > 1e-15:
        weighted = weighted / weighted_sum
    
    return weighted


def simplicial_stratification(vertices: List[np.ndarray], 
                              n_strata: int = 10) -> List[np.ndarray]:
    """
    Generate stratified sampling points within a simplex using barycentric coordinates.
    
    This provides uniform coverage of simplex interior for Monte Carlo sampling.
    Strategy: Generate uniform random barycentric coordinates that sum to 1.
    
    Args:
        vertices: Simplex vertices
        n_strata: Number of stratified sample points
        
    Returns:
        List of sample points uniformly distributed in simplex
    """
    bc = BarycentricCoordinates(vertices)
    n_vertices = len(vertices)
    
    samples = []
    for _ in range(n_strata):
        # Generate random barycentric coordinates using Dirichlet distribution
        # This ensures uniform sampling over simplex
        alphas = np.ones(n_vertices)  # Uniform prior
        lambdas = np.random.dirichlet(alphas)
        
        # Interpolate to get point
        point = bc.interpolate(lambdas)
        samples.append(point)
    
    return samples


def torus_barycentric_embedding(n: int, dims: int = 11, 
                                 anchor_scale: float = 0.1) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Create barycentric embedding for torus coordinates.
    
    Integration with existing torus embedding (manifold_core.py):
    1. Compute standard torus embedding θ(n) using φ-modulation
    2. Define anchor vertices based on prime-density hotspots
    3. Express θ(n) as barycentric combination of anchors
    
    This enables affine-invariant distance calculations for GVA.
    
    Args:
        n: Integer to embed
        dims: Embedding dimension (default 11 for GVA)
        anchor_scale: Scale factor for anchor vertex spread
        
    Returns:
        (embedding_coords, anchor_vertices)
    """
    from manifold_core import embed_5torus, curvature
    
    # Adjust dims to work with embed_5torus (which uses 5 dimensions)
    if dims > 5:
        # For higher dimensions, we'll extend by repeating the pattern
        base_dims = 5
        k = 0.5 / math.log2(math.log2(n + 1))
        base_embedding = embed_5torus(n, k)
        
        # Extend to full dimension
        embedding = list(base_embedding)
        for i in range(dims - base_dims):
            # Phase-shifted repetition with φ modulation
            phase = (i * PHI) % 1.0
            extended_coord = (embedding[i % base_dims] + phase) % 1.0
            embedding.append(extended_coord)
        
        embedding = np.array(embedding[:dims])
    else:
        k = 0.5 / math.log2(math.log2(n + 1))
        base_embedding = embed_5torus(n, k)
        embedding = np.array(base_embedding[:dims])
    
    # Define anchor vertices based on curvature hotspots
    # These represent canonical positions in torus space
    kappa = float(curvature(n))
    n_anchors = dims + 1  # Need d+1 vertices for d-dimensional simplex
    
    anchors = []
    for i in range(n_anchors):
        # Distribute anchors uniformly with curvature modulation
        anchor = np.zeros(dims)
        for d in range(dims):
            # Use φ-based spacing with curvature adjustment
            phase = (i / n_anchors + d * PHI) % 1.0
            anchor[d] = (phase * (1.0 + kappa * anchor_scale)) % 1.0
        anchors.append(anchor)
    
    return embedding, anchors


def barycentric_distance_torus(theta1: np.ndarray, theta2: np.ndarray,
                               n: int, anchor_scale: float = 0.1) -> float:
    """
    Compute Riemannian distance on torus using barycentric coordinates.
    
    Enhancement over standard torus distance (riemannian_distance_5d):
    - Express torus points as barycentric combinations
    - Use affine-invariant distance in barycentric space
    - Apply curvature weighting for improved factor detection
    
    Args:
        theta1, theta2: Torus coordinates to compare
        n: Reference integer for curvature calculation
        anchor_scale: Scale for anchor vertex generation
        
    Returns:
        Barycentric-weighted distance
    """
    dims = len(theta1)
    
    # Generate anchor vertices
    _, anchors = torus_barycentric_embedding(n, dims, anchor_scale)
    
    # Compute barycentric coordinates
    bc = BarycentricCoordinates(anchors)
    lambda1 = bc.compute_barycentric_coords(theta1)
    lambda2 = bc.compute_barycentric_coords(theta2)
    
    # Apply curvature weighting
    from manifold_core import curvature
    kappa = float(curvature(n))
    
    # Weighted distance with curvature modulation
    diff = lambda1 - lambda2
    weighted_diff = diff * (1.0 + kappa * np.abs(diff))
    
    return float(np.linalg.norm(weighted_diff))


# Test/validation functions
def validate_barycentric_properties():
    """
    Validate fundamental barycentric coordinate properties.
    
    Tests:
    1. Centroid has uniform coordinates
    2. Vertices have unit coordinates
    3. Interpolation is exact
    4. Sum constraint Σλᵢ = 1
    """
    # 2D triangle
    vertices_2d = [
        np.array([0.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([0.0, 1.0])
    ]
    
    bc = BarycentricCoordinates(vertices_2d)
    
    # Test 1: Centroid
    centroid = bc.centroid()
    expected_centroid = np.array([1/3, 1/3])
    assert np.allclose(centroid, expected_centroid, atol=1e-10), \
        f"Centroid test failed: {centroid} != {expected_centroid}"
    
    # Test 2: Vertex coordinates
    for i, v in enumerate(vertices_2d):
        lambdas = bc.compute_barycentric_coords(v)
        expected = np.zeros(3)
        expected[i] = 1.0
        assert np.allclose(lambdas, expected, atol=1e-10), \
            f"Vertex {i} coords test failed: {lambdas} != {expected}"
    
    # Test 3: Interpolation
    test_lambdas = np.array([0.2, 0.3, 0.5])
    point = bc.interpolate(test_lambdas)
    recovered_lambdas = bc.compute_barycentric_coords(point)
    assert np.allclose(recovered_lambdas, test_lambdas, atol=1e-10), \
        f"Interpolation test failed: {recovered_lambdas} != {test_lambdas}"
    
    # Test 4: Sum constraint
    assert np.allclose(np.sum(recovered_lambdas), 1.0, atol=1e-10), \
        f"Sum constraint failed: {np.sum(recovered_lambdas)} != 1.0"
    
    print("✓ All barycentric property tests passed")
    return True


if __name__ == "__main__":
    print("Barycentric Coordinates Module")
    print("=" * 60)
    print("Running validation tests...")
    print()
    
    validate_barycentric_properties()
    
    print()
    print("Example: 3D tetrahedron")
    print("-" * 60)
    
    # 3D tetrahedron
    vertices_3d = [
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0])
    ]
    
    bc_3d = BarycentricCoordinates(vertices_3d)
    centroid_3d = bc_3d.centroid()
    print(f"Centroid: {centroid_3d}")
    print(f"Expected: [0.25, 0.25, 0.25]")
    
    # Test point
    test_point = np.array([0.25, 0.25, 0.25])
    lambdas_3d = bc_3d.compute_barycentric_coords(test_point)
    print(f"Barycentric coords of centroid: {lambdas_3d}")
    print(f"Expected: [0.25, 0.25, 0.25, 0.25]")
    print(f"Inside simplex: {bc_3d.is_inside_simplex(lambdas_3d)}")
    
    print()
    print("Module ready for integration with Z-Sandbox framework")
