#!/usr/bin/env python3
"""
Coordinate Geometry Fundamentals Module

Provides foundational coordinate geometry formulas for geometric factorization techniques,
particularly in torus embeddings, distance metrics, and geometric validation approaches.

This module serves as a quick reference and building block for:
- Distance calculations in Euclidean and toroidal spaces
- Midpoint and section division for manifold partitioning
- Centroid calculations for flux-based position aggregation
- Area/volume computations via determinants for density mapping
- Coordinate frame initialization and quadrant handling

Mathematical Foundation:
These basic plane geometry principles ground advanced techniques like:
- GVA (Geodesic Validation Assault) with torus embeddings
- Z5D axioms with discrete domain normalization
- QMC-φ hybrid sampling with geometric coverage
- Monte Carlo integration with variance reduction
- Riemannian distance metrics with curvature

References:
- Issue: "coordinate geometry fundamentals" enhancement proposal
- Integration: manifold_128bit.py, demo_z5d_rsa.py, qmc_phi_hybrid_demo.py
- Z5D axioms: Z = A(B/c), κ(n), θ'(n,k)
"""

import math
from typing import List, Tuple, Union, Sequence
from mpmath import mp, mpf, sqrt as mpsqrt, log, exp
import numpy as np

# Set high precision for consistency with repository
mp.dps = 50

# Universal constants (from Z5D axioms)
PHI = mpf((1 + mpsqrt(5)) / 2)  # Golden ratio
E2 = exp(2)  # e² invariant


# =============================================================================
# Distance Formulas
# =============================================================================

def euclidean_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Euclidean distance between two points in 2D space.
    
    Formula: d = √[(x2 - x1)² + (y2 - y1)²]
    
    Application: Basic geodesic calculations on d-dimensional torus for initial
    proximities before incorporating curvature κ in A* search refinements around √N.
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Distance between the points
        
    Example:
        >>> euclidean_distance_2d(0, 0, 3, 4)
        5.0
    """
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def euclidean_distance_3d(x1: float, y1: float, z1: float, 
                          x2: float, y2: float, z2: float) -> float:
    """
    Calculate Euclidean distance between two points in 3D space.
    
    Formula: d = √[(x2 - x1)² + (y2 - y1)² + (z2 - z1)²]
    
    Args:
        x1, y1, z1: Coordinates of first point
        x2, y2, z2: Coordinates of second point
        
    Returns:
        Distance between the points
        
    Example:
        >>> euclidean_distance_3d(0, 0, 0, 1, 1, 1)
        1.7320508075688772
    """
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def euclidean_distance_nd(p1: Sequence[float], p2: Sequence[float]) -> float:
    """
    Calculate Euclidean distance between two points in n-dimensional space.
    
    Formula: d = √[Σ(pi - qi)²] for all dimensions i
    
    Application: Extended to higher dimensions for computing proximities in
    multi-dimensional torus embeddings like those in manifold_128bit.py with
    dims=5 or dims=11 for GVA factorization.
    
    Args:
        p1: Coordinates of first point (list/tuple/array)
        p2: Coordinates of second point (same length as p1)
        
    Returns:
        Distance between the points
        
    Raises:
        ValueError: If points have different dimensions
        
    Example:
        >>> euclidean_distance_nd([0, 0, 0], [1, 1, 1])
        1.7320508075688772
        >>> euclidean_distance_nd([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
        6.324555320336759
    """
    if len(p1) != len(p2):
        raise ValueError(f"Points must have same dimension: {len(p1)} vs {len(p2)}")
    
    sum_sq = sum((a - b) ** 2 for a, b in zip(p1, p2))
    return math.sqrt(sum_sq)


def euclidean_distance_nd_hp(p1: Sequence[float], p2: Sequence[float]) -> mpf:
    """
    High-precision Euclidean distance in n-dimensional space using mpmath.
    
    Application: For computing distances with precision < 1e-16 required in
    Z5D axiom validation and GVA proximity detection near factor candidates.
    
    Args:
        p1: Coordinates of first point
        p2: Coordinates of second point
        
    Returns:
        High-precision distance (mpmath.mpf)
        
    Example:
        >>> float(euclidean_distance_nd_hp([0, 0], [1, 1]))
        1.4142135623730951
    """
    if len(p1) != len(p2):
        raise ValueError(f"Points must have same dimension: {len(p1)} vs {len(p2)}")
    
    sum_sq = sum((mpf(a) - mpf(b)) ** 2 for a, b in zip(p1, p2))
    return mpsqrt(sum_sq)


# =============================================================================
# Midpoint and Section Division
# =============================================================================

def midpoint_2d(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float]:
    """
    Calculate midpoint between two points in 2D space.
    
    Formula: M = ((x1 + x2)/2, (y1 + y2)/2)
    
    Application: Leverage for partitioning manifolds or generating candidate
    points in ZNeighborhood builders for factorization around √N.
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Tuple (mx, my) representing midpoint coordinates
        
    Example:
        >>> midpoint_2d(0, 0, 4, 6)
        (2.0, 3.0)
    """
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def midpoint_3d(x1: float, y1: float, z1: float,
                x2: float, y2: float, z2: float) -> Tuple[float, float, float]:
    """
    Calculate midpoint between two points in 3D space.
    
    Formula: M = ((x1 + x2)/2, (y1 + y2)/2, (z1 + z2)/2)
    
    Args:
        x1, y1, z1: Coordinates of first point
        x2, y2, z2: Coordinates of second point
        
    Returns:
        Tuple (mx, my, mz) representing midpoint coordinates
        
    Example:
        >>> midpoint_3d(0, 0, 0, 2, 4, 6)
        (1.0, 2.0, 3.0)
    """
    return ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)


def midpoint_nd(p1: Sequence[float], p2: Sequence[float]) -> List[float]:
    """
    Calculate midpoint between two points in n-dimensional space.
    
    Formula: M = ((p1[i] + p2[i])/2) for all dimensions i
    
    Args:
        p1: Coordinates of first point
        p2: Coordinates of second point
        
    Returns:
        List of midpoint coordinates
        
    Raises:
        ValueError: If points have different dimensions
        
    Example:
        >>> midpoint_nd([0, 0, 0], [2, 4, 6])
        [1.0, 2.0, 3.0]
    """
    if len(p1) != len(p2):
        raise ValueError(f"Points must have same dimension: {len(p1)} vs {len(p2)}")
    
    return [(a + b) / 2 for a, b in zip(p1, p2)]


def section_point_2d(x1: float, y1: float, x2: float, y2: float, 
                     m: float, n: float) -> Tuple[float, float]:
    """
    Calculate point dividing line segment in ratio m:n (internal division).
    
    Formula: P = ((mx2 + nx1)/(m+n), (my2 + ny1)/(m+n))
    
    Application: Section formulas inform ratio-based divisions similar to
    Z5D axiom transformations Z = A(B/c), simulating dilations or offsets
    in theta-gating for ECM guidance.
    
    Args:
        x1, y1: Coordinates of first endpoint
        x2, y2: Coordinates of second endpoint
        m, n: Ratio values (m:n division)
        
    Returns:
        Tuple (px, py) representing the section point
        
    Raises:
        ValueError: If m + n = 0
        
    Example:
        >>> section_point_2d(0, 0, 3, 3, 1, 2)  # Divides in 1:2 ratio
        (1.0, 1.0)
        >>> section_point_2d(0, 0, 6, 6, 2, 1)  # Divides in 2:1 ratio
        (4.0, 4.0)
    """
    if m + n == 0:
        raise ValueError("m + n cannot be zero")
    
    px = (m * x2 + n * x1) / (m + n)
    py = (m * y2 + n * y1) / (m + n)
    return (px, py)


def section_point_nd(p1: Sequence[float], p2: Sequence[float],
                     m: float, n: float) -> List[float]:
    """
    Calculate point dividing line segment in ratio m:n in n-dimensional space.
    
    Formula: P[i] = (m*p2[i] + n*p1[i])/(m+n) for all dimensions i
    
    Args:
        p1: Coordinates of first endpoint
        p2: Coordinates of second endpoint
        m, n: Ratio values (m:n division)
        
    Returns:
        List of section point coordinates
        
    Raises:
        ValueError: If points have different dimensions or m + n = 0
        
    Example:
        >>> section_point_nd([0, 0], [6, 6], 1, 2)
        [2.0, 2.0]
    """
    if len(p1) != len(p2):
        raise ValueError(f"Points must have same dimension: {len(p1)} vs {len(p2)}")
    if m + n == 0:
        raise ValueError("m + n cannot be zero")
    
    return [(m * b + n * a) / (m + n) for a, b in zip(p1, p2)]


# =============================================================================
# Centroid Calculations
# =============================================================================

def centroid_2d(points: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate centroid (center of mass) of multiple points in 2D space.
    
    Formula for triangle: C = ((x1+x2+x3)/3, (y1+y2+y3)/3)
    Formula for n points: C = (Σxi/n, Σyi/n)
    
    Application: Apply to aggregate flux-based positions in Riemannian metrics,
    helping validate factor clusters or balance multi-dimensional embeddings in
    GVA, where midpoints might coincide in parallelogram-like structures.
    
    Args:
        points: Sequence of (x, y) coordinate tuples
        
    Returns:
        Tuple (cx, cy) representing centroid coordinates
        
    Raises:
        ValueError: If points list is empty
        
    Example:
        >>> centroid_2d([(0, 0), (3, 0), (0, 3)])  # Right triangle
        (1.0, 1.0)
        >>> centroid_2d([(0, 0), (2, 0), (2, 2), (0, 2)])  # Square
        (1.0, 1.0)
    """
    if not points:
        raise ValueError("Points list cannot be empty")
    
    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    return (cx, cy)


def centroid_3d(points: Sequence[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    """
    Calculate centroid of multiple points in 3D space.
    
    Formula: C = (Σxi/n, Σyi/n, Σzi/n)
    
    Args:
        points: Sequence of (x, y, z) coordinate tuples
        
    Returns:
        Tuple (cx, cy, cz) representing centroid coordinates
        
    Raises:
        ValueError: If points list is empty
        
    Example:
        >>> centroid_3d([(0, 0, 0), (3, 0, 0), (0, 3, 0), (0, 0, 3)])
        (0.75, 0.75, 0.75)
    """
    if not points:
        raise ValueError("Points list cannot be empty")
    
    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    cz = sum(p[2] for p in points) / n
    return (cx, cy, cz)


def centroid_nd(points: Sequence[Sequence[float]]) -> List[float]:
    """
    Calculate centroid of multiple points in n-dimensional space.
    
    Formula: C[i] = Σ(points[j][i])/n for all dimensions i
    
    Args:
        points: Sequence of points, each a sequence of coordinates
        
    Returns:
        List of centroid coordinates
        
    Raises:
        ValueError: If points list is empty or points have inconsistent dimensions
        
    Example:
        >>> centroid_nd([[0, 0], [2, 0], [2, 2], [0, 2]])
        [1.0, 1.0]
        >>> centroid_nd([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [4.0, 5.0, 6.0]
    """
    if not points:
        raise ValueError("Points list cannot be empty")
    
    n = len(points)
    dimensions = len(points[0])
    
    # Validate all points have same dimension
    for i, p in enumerate(points):
        if len(p) != dimensions:
            raise ValueError(f"Inconsistent dimensions: point {i} has {len(p)}, expected {dimensions}")
    
    # Calculate centroid for each dimension
    centroid = []
    for dim in range(dimensions):
        coord_sum = sum(p[dim] for p in points)
        centroid.append(coord_sum / n)
    
    return centroid


# =============================================================================
# Area and Volume Calculations
# =============================================================================

def triangle_area_2d(x1: float, y1: float, x2: float, y2: float, 
                     x3: float, y3: float) -> float:
    """
    Calculate area of a triangle using determinant method.
    
    Formula: Area = ½|x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|
    
    Application: Extend determinant method to compute volumes or densities in
    higher-dimensional spaces, supporting prime-density mapping under Gauss-Prime
    Law or variance reduction in Monte Carlo integrations.
    
    Args:
        x1, y1: Coordinates of first vertex
        x2, y2: Coordinates of second vertex
        x3, y3: Coordinates of third vertex
        
    Returns:
        Area of the triangle (always positive)
        
    Example:
        >>> triangle_area_2d(0, 0, 4, 0, 0, 3)
        6.0
        >>> triangle_area_2d(1, 1, 4, 2, 2, 5)
        4.5
    """
    area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    return area


def triangle_area_vertices(vertices: Sequence[Tuple[float, float]]) -> float:
    """
    Calculate area of a triangle given vertices as sequence.
    
    Args:
        vertices: Sequence of 3 (x, y) tuples
        
    Returns:
        Area of the triangle
        
    Raises:
        ValueError: If not exactly 3 vertices provided
        
    Example:
        >>> triangle_area_vertices([(0, 0), (4, 0), (0, 3)])
        6.0
    """
    if len(vertices) != 3:
        raise ValueError(f"Expected 3 vertices, got {len(vertices)}")
    
    (x1, y1), (x2, y2), (x3, y3) = vertices
    return triangle_area_2d(x1, y1, x2, y2, x3, y3)


def polygon_area_2d(vertices: Sequence[Tuple[float, float]]) -> float:
    """
    Calculate area of a polygon using the shoelace formula (surveyor's formula).
    
    Formula: Area = ½|Σ(xi*yi+1 - xi+1*yi)| for i = 0 to n-1 (with wraparound)
    
    Application: Generalization of triangle area for complex geometric regions
    in manifold partitioning and variance-reduced stratification.
    
    Args:
        vertices: Sequence of (x, y) tuples in order (clockwise or counterclockwise)
        
    Returns:
        Area of the polygon (always positive)
        
    Raises:
        ValueError: If fewer than 3 vertices provided
        
    Example:
        >>> polygon_area_2d([(0, 0), (4, 0), (4, 3), (0, 3)])  # Rectangle
        12.0
        >>> polygon_area_2d([(0, 0), (2, 0), (3, 2), (1, 3)])  # Quadrilateral
        5.5
    """
    if len(vertices) < 3:
        raise ValueError(f"Need at least 3 vertices, got {len(vertices)}")
    
    n = len(vertices)
    area = 0.0
    
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]  # Wraparound to first vertex
        area += x1 * y2 - x2 * y1
    
    return abs(area) / 2.0


def tetrahedron_volume(p1: Sequence[float], p2: Sequence[float],
                       p3: Sequence[float], p4: Sequence[float]) -> float:
    """
    Calculate volume of a tetrahedron (3D simplex) using determinant method.
    
    Formula: V = |det([p2-p1, p3-p1, p4-p1])| / 6
    
    Application: Extension to 3D for computing volumetric densities in
    higher-dimensional embeddings and simplex-based stratification.
    
    Args:
        p1, p2, p3, p4: Vertices as sequences of 3 coordinates each
        
    Returns:
        Volume of the tetrahedron
        
    Raises:
        ValueError: If points don't have exactly 3 dimensions
        
    Example:
        >>> tetrahedron_volume([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
        0.16666666666666666
    """
    for p in [p1, p2, p3, p4]:
        if len(p) != 3:
            raise ValueError(f"Points must be 3-dimensional, got {len(p)}")
    
    # Convert to numpy for determinant calculation
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    v3 = np.array(p4) - np.array(p1)
    
    matrix = np.stack([v1, v2, v3], axis=1)
    det = np.linalg.det(matrix)
    
    return abs(det) / 6.0


# =============================================================================
# Quadrants and Coordinate System Utilities
# =============================================================================

def quadrant_2d(x: float, y: float) -> int:
    """
    Determine quadrant of a point in 2D Cartesian coordinate system.
    
    Quadrant numbering:
    - Quadrant I:   x > 0, y > 0
    - Quadrant II:  x < 0, y > 0
    - Quadrant III: x < 0, y < 0
    - Quadrant IV:  x > 0, y < 0
    - 0: Point on an axis or origin
    
    Application: Reference for initializing coordinate frames in scripts like
    manifold_128bit.py, ensuring proper handling of fractional parts and modular
    constraints in residue filters.
    
    Args:
        x: x-coordinate
        y: y-coordinate
        
    Returns:
        Quadrant number (1-4) or 0 if on axis/origin
        
    Example:
        >>> quadrant_2d(1, 1)
        1
        >>> quadrant_2d(-1, 1)
        2
        >>> quadrant_2d(-1, -1)
        3
        >>> quadrant_2d(1, -1)
        4
        >>> quadrant_2d(0, 1)
        0
    """
    if x == 0 or y == 0:
        return 0
    elif x > 0 and y > 0:
        return 1
    elif x < 0 and y > 0:
        return 2
    elif x < 0 and y < 0:
        return 3
    else:  # x > 0 and y < 0
        return 4


def octant_3d(x: float, y: float, z: float) -> int:
    """
    Determine octant of a point in 3D Cartesian coordinate system.
    
    Octant numbering (standard convention):
    - Octant 1: (+, +, +)
    - Octant 2: (-, +, +)
    - Octant 3: (-, -, +)
    - Octant 4: (+, -, +)
    - Octant 5: (+, +, -)
    - Octant 6: (-, +, -)
    - Octant 7: (-, -, -)
    - Octant 8: (+, -, -)
    - 0: Point on a plane/axis or origin
    
    Args:
        x: x-coordinate
        y: y-coordinate
        z: z-coordinate
        
    Returns:
        Octant number (1-8) or 0 if on plane/axis/origin
        
    Example:
        >>> octant_3d(1, 1, 1)
        1
        >>> octant_3d(-1, -1, -1)
        7
        >>> octant_3d(1, 0, 1)
        0
    """
    if x == 0 or y == 0 or z == 0:
        return 0
    
    if x > 0:
        if y > 0:
            return 1 if z > 0 else 5
        else:  # y < 0
            return 4 if z > 0 else 8
    else:  # x < 0
        if y > 0:
            return 2 if z > 0 else 6
        else:  # y < 0
            return 3 if z > 0 else 7


def line_equation_2d_slope_intercept(x1: float, y1: float, 
                                     x2: float, y2: float) -> Tuple[float, float]:
    """
    Calculate slope-intercept form (y = mx + b) of a line through two points.
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Tuple (m, b) where m is slope and b is y-intercept
        
    Raises:
        ValueError: If line is vertical (undefined slope)
        
    Example:
        >>> line_equation_2d_slope_intercept(0, 0, 2, 4)
        (2.0, 0.0)
        >>> line_equation_2d_slope_intercept(1, 2, 3, 6)
        (2.0, 0.0)
    """
    if x2 == x1:
        raise ValueError("Vertical line has undefined slope (use general form instead)")
    
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return (m, b)


def line_equation_2d_general(x1: float, y1: float, 
                             x2: float, y2: float) -> Tuple[float, float, float]:
    """
    Calculate general form (Ax + By + C = 0) of a line through two points.
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Tuple (A, B, C) representing line equation Ax + By + C = 0
        
    Example:
        >>> line_equation_2d_general(0, 0, 1, 1)
        (-1.0, 1.0, 0.0)
        >>> line_equation_2d_general(0, 1, 2, 1)  # Horizontal line
        (0.0, 1.0, -1.0)
    """
    # Direction vector
    dx = x2 - x1
    dy = y2 - y1
    
    # Normal vector (perpendicular): (-dy, dx)
    A = -dy
    B = dx
    C = -(A * x1 + B * y1)
    
    return (A, B, C)


def point_line_distance_2d(px: float, py: float,
                           A: float, B: float, C: float) -> float:
    """
    Calculate perpendicular distance from a point to a line in 2D.
    
    Formula: distance = |Ax + By + C| / √(A² + B²)
    
    Args:
        px, py: Coordinates of the point
        A, B, C: Coefficients of line equation Ax + By + C = 0
        
    Returns:
        Perpendicular distance from point to line
        
    Raises:
        ValueError: If A = B = 0 (degenerate line)
        
    Example:
        >>> point_line_distance_2d(0, 0, 1, 1, -2)  # Line x + y = 2
        1.4142135623730951
    """
    if A == 0 and B == 0:
        raise ValueError("Degenerate line (A = B = 0)")
    
    numerator = abs(A * px + B * py + C)
    denominator = math.sqrt(A * A + B * B)
    return numerator / denominator


# =============================================================================
# Integration with Repository Concepts
# =============================================================================

def torus_distance_1d(coord1: float, coord2: float) -> float:
    """
    Calculate circular (toroidal) distance in 1D, accounting for wraparound.
    
    Formula: min(|c1 - c2|, 1 - |c1 - c2|)
    
    Application: Component distance for torus embeddings in GVA, where
    coordinates wrap around at boundaries [0, 1).
    
    Args:
        coord1: First coordinate (typically in [0, 1))
        coord2: Second coordinate (typically in [0, 1))
        
    Returns:
        Minimum distance accounting for wraparound
        
    Example:
        >>> torus_distance_1d(0.1, 0.9)
        0.2
        >>> torus_distance_1d(0.0, 0.5)
        0.5
    """
    diff = abs(coord1 - coord2)
    return min(diff, 1 - diff)


def torus_distance_nd(coords1: Sequence[float], coords2: Sequence[float]) -> float:
    """
    Calculate Euclidean distance on n-dimensional torus with wraparound.
    
    Formula: √[Σ(min(|ci1 - ci2|, 1 - |ci1 - ci2|))²]
    
    Application: Basic distance metric for torus embeddings before applying
    curvature corrections. Used as foundation for Riemannian distance in GVA.
    
    Args:
        coords1: First point coordinates (each in [0, 1))
        coords2: Second point coordinates
        
    Returns:
        Toroidal distance between points
        
    Raises:
        ValueError: If coordinate sequences have different lengths
        
    Example:
        >>> torus_distance_nd([0.1, 0.1], [0.9, 0.9])
        0.28284271247461906
    """
    if len(coords1) != len(coords2):
        raise ValueError(f"Coordinate sequences must have same length: {len(coords1)} vs {len(coords2)}")
    
    sum_sq = sum(torus_distance_1d(c1, c2) ** 2 for c1, c2 in zip(coords1, coords2))
    return math.sqrt(sum_sq)


def weighted_centroid_nd(points: Sequence[Sequence[float]], 
                        weights: Sequence[float]) -> List[float]:
    """
    Calculate weighted centroid of points in n-dimensional space.
    
    Formula: C[i] = Σ(weights[j] * points[j][i]) / Σweights
    
    Application: Curvature-weighted aggregation for flux-based positions in
    Riemannian metrics, where weights can be modulated by κ(n) for geometric
    factorization validations.
    
    Args:
        points: Sequence of points, each a sequence of coordinates
        weights: Sequence of weights (must have same length as points)
        
    Returns:
        List of weighted centroid coordinates
        
    Raises:
        ValueError: If points and weights have different lengths,
                   if points list is empty, or if sum of weights is zero
        
    Example:
        >>> weighted_centroid_nd([[0, 0], [1, 1], [2, 2]], [1, 2, 1])
        [1.0, 1.0]
        >>> weighted_centroid_nd([[0, 0, 0], [1, 0, 0]], [1, 3])
        [0.75, 0.0, 0.0]
    """
    if not points:
        raise ValueError("Points list cannot be empty")
    if len(points) != len(weights):
        raise ValueError(f"Points and weights must have same length: {len(points)} vs {len(weights)}")
    
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise ValueError("Sum of weights cannot be zero")
    
    dimensions = len(points[0])
    
    # Validate all points have same dimension
    for i, p in enumerate(points):
        if len(p) != dimensions:
            raise ValueError(f"Inconsistent dimensions: point {i} has {len(p)}, expected {dimensions}")
    
    # Calculate weighted centroid for each dimension
    centroid = []
    for dim in range(dimensions):
        weighted_sum = sum(w * p[dim] for w, p in zip(weights, points))
        centroid.append(weighted_sum / weight_sum)
    
    return centroid


# =============================================================================
# Main - Demonstration and Testing
# =============================================================================

def main():
    """
    Demonstrate coordinate geometry fundamentals with examples.
    """
    print("=" * 70)
    print(" Coordinate Geometry Fundamentals - Quick Reference")
    print("=" * 70)
    
    # Distance formulas
    print("\n1. Distance Formulas")
    print("-" * 70)
    d = euclidean_distance_2d(0, 0, 3, 4)
    print(f"   2D Euclidean distance (0,0) to (3,4): {d}")
    
    d3d = euclidean_distance_3d(0, 0, 0, 1, 1, 1)
    print(f"   3D Euclidean distance (0,0,0) to (1,1,1): {d3d:.6f}")
    
    dnd = euclidean_distance_nd([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    print(f"   5D Euclidean distance: {dnd:.6f}")
    
    # Midpoint
    print("\n2. Midpoint Calculations")
    print("-" * 70)
    m = midpoint_2d(0, 0, 4, 6)
    print(f"   Midpoint of (0,0) and (4,6): {m}")
    
    m3d = midpoint_3d(0, 0, 0, 2, 4, 6)
    print(f"   Midpoint of (0,0,0) and (2,4,6): {m3d}")
    
    # Section division
    print("\n3. Section Division")
    print("-" * 70)
    s = section_point_2d(0, 0, 6, 6, 1, 2)
    print(f"   Point dividing (0,0)-(6,6) in 1:2 ratio: {s}")
    
    # Centroid
    print("\n4. Centroid Calculations")
    print("-" * 70)
    c = centroid_2d([(0, 0), (3, 0), (0, 3)])
    print(f"   Centroid of triangle (0,0), (3,0), (0,3): {c}")
    
    c_weighted = weighted_centroid_nd([[0, 0], [1, 1], [2, 2]], [1, 2, 1])
    print(f"   Weighted centroid with weights [1,2,1]: {c_weighted}")
    
    # Area
    print("\n5. Area Calculations")
    print("-" * 70)
    area = triangle_area_2d(0, 0, 4, 0, 0, 3)
    print(f"   Triangle area (0,0), (4,0), (0,3): {area}")
    
    poly_area = polygon_area_2d([(0, 0), (4, 0), (4, 3), (0, 3)])
    print(f"   Rectangle area (0,0)-(4,3): {poly_area}")
    
    # Volume
    print("\n6. Volume Calculations")
    print("-" * 70)
    vol = tetrahedron_volume([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
    print(f"   Tetrahedron volume (unit simplex): {vol:.6f}")
    
    # Quadrants
    print("\n7. Quadrants and Octants")
    print("-" * 70)
    q = quadrant_2d(1, 1)
    print(f"   Quadrant of (1, 1): {q}")
    
    oct = octant_3d(-1, 1, -1)
    print(f"   Octant of (-1, 1, -1): {oct}")
    
    # Torus distance
    print("\n8. Torus Distance (for GVA/manifold embeddings)")
    print("-" * 70)
    td = torus_distance_1d(0.1, 0.9)
    print(f"   1D torus distance 0.1 to 0.9: {td}")
    
    tnd = torus_distance_nd([0.1, 0.1], [0.9, 0.9])
    print(f"   2D torus distance (0.1,0.1) to (0.9,0.9): {tnd:.6f}")
    
    print("\n" + "=" * 70)
    print(" All functions demonstrated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
