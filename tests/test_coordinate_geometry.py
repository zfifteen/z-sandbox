#!/usr/bin/env python3
"""
Unit tests for coordinate_geometry module.

Tests all foundational coordinate geometry functions including:
- Distance formulas (2D, 3D, n-D, high-precision)
- Midpoint and section division
- Centroid calculations (standard and weighted)
- Area and volume computations
- Quadrant/octant determination
- Torus distance metrics
- Line equations and point-line distance
"""

import unittest
import math
import sys
sys.path.insert(0, 'python')

from coordinate_geometry import (
    # Distance formulas
    euclidean_distance_2d,
    euclidean_distance_3d,
    euclidean_distance_nd,
    euclidean_distance_nd_hp,
    # Midpoint and section
    midpoint_2d,
    midpoint_3d,
    midpoint_nd,
    section_point_2d,
    section_point_nd,
    # Centroid
    centroid_2d,
    centroid_3d,
    centroid_nd,
    weighted_centroid_nd,
    # Area and volume
    triangle_area_2d,
    triangle_area_vertices,
    polygon_area_2d,
    tetrahedron_volume,
    # Quadrants
    quadrant_2d,
    octant_3d,
    # Line equations
    line_equation_2d_slope_intercept,
    line_equation_2d_general,
    point_line_distance_2d,
    # Torus
    torus_distance_1d,
    torus_distance_nd,
)


class TestDistanceFormulas(unittest.TestCase):
    """Test distance calculation functions."""
    
    def test_euclidean_distance_2d_basic(self):
        """Test 2D distance with standard 3-4-5 triangle."""
        d = euclidean_distance_2d(0, 0, 3, 4)
        self.assertAlmostEqual(d, 5.0)
    
    def test_euclidean_distance_2d_same_point(self):
        """Test distance from point to itself."""
        d = euclidean_distance_2d(1, 1, 1, 1)
        self.assertAlmostEqual(d, 0.0)
    
    def test_euclidean_distance_3d_basic(self):
        """Test 3D distance."""
        d = euclidean_distance_3d(0, 0, 0, 1, 1, 1)
        self.assertAlmostEqual(d, math.sqrt(3))
    
    def test_euclidean_distance_3d_unit_cube(self):
        """Test distance across unit cube diagonal."""
        d = euclidean_distance_3d(0, 0, 0, 1, 0, 0)
        self.assertAlmostEqual(d, 1.0)
    
    def test_euclidean_distance_nd_2d(self):
        """Test n-D distance with 2D case."""
        d = euclidean_distance_nd([0, 0], [3, 4])
        self.assertAlmostEqual(d, 5.0)
    
    def test_euclidean_distance_nd_5d(self):
        """Test n-D distance with 5D case."""
        d = euclidean_distance_nd([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
        # Distance = sqrt(16 + 4 + 0 + 4 + 16) = sqrt(40)
        self.assertAlmostEqual(d, math.sqrt(40))
    
    def test_euclidean_distance_nd_dimension_mismatch(self):
        """Test error on dimension mismatch."""
        with self.assertRaises(ValueError):
            euclidean_distance_nd([1, 2], [1, 2, 3])
    
    def test_euclidean_distance_nd_hp_precision(self):
        """Test high-precision distance."""
        d = euclidean_distance_nd_hp([0, 0], [1, 1])
        # Should be sqrt(2) with high precision
        self.assertAlmostEqual(float(d), math.sqrt(2), places=10)


class TestMidpointAndSection(unittest.TestCase):
    """Test midpoint and section division functions."""
    
    def test_midpoint_2d_basic(self):
        """Test 2D midpoint calculation."""
        mx, my = midpoint_2d(0, 0, 4, 6)
        self.assertAlmostEqual(mx, 2.0)
        self.assertAlmostEqual(my, 3.0)
    
    def test_midpoint_2d_negative_coords(self):
        """Test midpoint with negative coordinates."""
        mx, my = midpoint_2d(-2, -4, 2, 4)
        self.assertAlmostEqual(mx, 0.0)
        self.assertAlmostEqual(my, 0.0)
    
    def test_midpoint_3d_basic(self):
        """Test 3D midpoint calculation."""
        mx, my, mz = midpoint_3d(0, 0, 0, 2, 4, 6)
        self.assertAlmostEqual(mx, 1.0)
        self.assertAlmostEqual(my, 2.0)
        self.assertAlmostEqual(mz, 3.0)
    
    def test_midpoint_nd_2d(self):
        """Test n-D midpoint with 2D case."""
        m = midpoint_nd([0, 0], [4, 6])
        self.assertEqual(len(m), 2)
        self.assertAlmostEqual(m[0], 2.0)
        self.assertAlmostEqual(m[1], 3.0)
    
    def test_midpoint_nd_5d(self):
        """Test n-D midpoint with 5D case."""
        m = midpoint_nd([0, 0, 0, 0, 0], [2, 4, 6, 8, 10])
        self.assertEqual(len(m), 5)
        for i, expected in enumerate([1, 2, 3, 4, 5]):
            self.assertAlmostEqual(m[i], expected)
    
    def test_section_point_2d_1_to_2(self):
        """Test section point dividing in 1:2 ratio."""
        px, py = section_point_2d(0, 0, 6, 6, 1, 2)
        # Point should be 1/3 of the way from (0,0) to (6,6)
        self.assertAlmostEqual(px, 2.0)
        self.assertAlmostEqual(py, 2.0)
    
    def test_section_point_2d_2_to_1(self):
        """Test section point dividing in 2:1 ratio."""
        px, py = section_point_2d(0, 0, 6, 6, 2, 1)
        # Point should be 2/3 of the way from (0,0) to (6,6)
        self.assertAlmostEqual(px, 4.0)
        self.assertAlmostEqual(py, 4.0)
    
    def test_section_point_2d_midpoint(self):
        """Test that 1:1 ratio gives midpoint."""
        px, py = section_point_2d(0, 0, 4, 6, 1, 1)
        self.assertAlmostEqual(px, 2.0)
        self.assertAlmostEqual(py, 3.0)
    
    def test_section_point_nd_basic(self):
        """Test n-D section point."""
        p = section_point_nd([0, 0, 0], [6, 6, 6], 1, 2)
        self.assertEqual(len(p), 3)
        for coord in p:
            self.assertAlmostEqual(coord, 2.0)


class TestCentroid(unittest.TestCase):
    """Test centroid calculation functions."""
    
    def test_centroid_2d_triangle(self):
        """Test centroid of right triangle."""
        cx, cy = centroid_2d([(0, 0), (3, 0), (0, 3)])
        self.assertAlmostEqual(cx, 1.0)
        self.assertAlmostEqual(cy, 1.0)
    
    def test_centroid_2d_square(self):
        """Test centroid of square."""
        cx, cy = centroid_2d([(0, 0), (2, 0), (2, 2), (0, 2)])
        self.assertAlmostEqual(cx, 1.0)
        self.assertAlmostEqual(cy, 1.0)
    
    def test_centroid_2d_single_point(self):
        """Test centroid of single point."""
        cx, cy = centroid_2d([(5, 7)])
        self.assertAlmostEqual(cx, 5.0)
        self.assertAlmostEqual(cy, 7.0)
    
    def test_centroid_3d_tetrahedron(self):
        """Test centroid of tetrahedron."""
        cx, cy, cz = centroid_3d([(0, 0, 0), (3, 0, 0), (0, 3, 0), (0, 0, 3)])
        self.assertAlmostEqual(cx, 0.75)
        self.assertAlmostEqual(cy, 0.75)
        self.assertAlmostEqual(cz, 0.75)
    
    def test_centroid_nd_2d(self):
        """Test n-D centroid with 2D case."""
        c = centroid_nd([[0, 0], [2, 0], [2, 2], [0, 2]])
        self.assertEqual(len(c), 2)
        self.assertAlmostEqual(c[0], 1.0)
        self.assertAlmostEqual(c[1], 1.0)
    
    def test_centroid_nd_5d(self):
        """Test n-D centroid with 5D case."""
        c = centroid_nd([[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]])
        self.assertEqual(len(c), 5)
        for coord in c:
            self.assertAlmostEqual(coord, 3.0)
    
    def test_weighted_centroid_nd_uniform_weights(self):
        """Test weighted centroid with uniform weights (should equal regular centroid)."""
        c_weighted = weighted_centroid_nd([[0, 0], [2, 0], [2, 2], [0, 2]], [1, 1, 1, 1])
        c_regular = centroid_nd([[0, 0], [2, 0], [2, 2], [0, 2]])
        self.assertEqual(len(c_weighted), len(c_regular))
        for cw, cr in zip(c_weighted, c_regular):
            self.assertAlmostEqual(cw, cr)
    
    def test_weighted_centroid_nd_custom_weights(self):
        """Test weighted centroid with custom weights."""
        # With weights [1, 2, 1], middle point should dominate
        c = weighted_centroid_nd([[0, 0], [1, 1], [2, 2]], [1, 2, 1])
        self.assertEqual(len(c), 2)
        self.assertAlmostEqual(c[0], 1.0)
        self.assertAlmostEqual(c[1], 1.0)


class TestAreaVolume(unittest.TestCase):
    """Test area and volume calculation functions."""
    
    def test_triangle_area_2d_right_triangle(self):
        """Test area of right triangle."""
        area = triangle_area_2d(0, 0, 4, 0, 0, 3)
        self.assertAlmostEqual(area, 6.0)
    
    def test_triangle_area_2d_arbitrary(self):
        """Test area of arbitrary triangle."""
        area = triangle_area_2d(1, 1, 4, 2, 2, 5)
        self.assertAlmostEqual(area, 5.5)
    
    def test_triangle_area_vertices(self):
        """Test triangle area using vertex list."""
        area = triangle_area_vertices([(0, 0), (4, 0), (0, 3)])
        self.assertAlmostEqual(area, 6.0)
    
    def test_triangle_area_vertices_wrong_count(self):
        """Test error with wrong number of vertices."""
        with self.assertRaises(ValueError):
            triangle_area_vertices([(0, 0), (4, 0)])
    
    def test_polygon_area_2d_rectangle(self):
        """Test area of rectangle."""
        area = polygon_area_2d([(0, 0), (4, 0), (4, 3), (0, 3)])
        self.assertAlmostEqual(area, 12.0)
    
    def test_polygon_area_2d_quadrilateral(self):
        """Test area of quadrilateral."""
        area = polygon_area_2d([(0, 0), (2, 0), (3, 2), (1, 3)])
        self.assertAlmostEqual(area, 5.5)
    
    def test_polygon_area_2d_triangle(self):
        """Test polygon area with triangle (should match triangle_area_2d)."""
        area_poly = polygon_area_2d([(0, 0), (4, 0), (0, 3)])
        area_tri = triangle_area_2d(0, 0, 4, 0, 0, 3)
        self.assertAlmostEqual(area_poly, area_tri)
    
    def test_tetrahedron_volume_unit(self):
        """Test volume of unit tetrahedron."""
        vol = tetrahedron_volume([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
        # Volume of unit tetrahedron is 1/6
        self.assertAlmostEqual(vol, 1.0 / 6.0)
    
    def test_tetrahedron_volume_scaled(self):
        """Test volume of scaled tetrahedron."""
        vol = tetrahedron_volume([0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 2])
        # Volume should scale by cube of factor: (2^3) * (1/6) = 8/6 = 4/3
        self.assertAlmostEqual(vol, 4.0 / 3.0)


class TestQuadrantsOctants(unittest.TestCase):
    """Test quadrant and octant determination functions."""
    
    def test_quadrant_2d_all_quadrants(self):
        """Test all four quadrants."""
        self.assertEqual(quadrant_2d(1, 1), 1)
        self.assertEqual(quadrant_2d(-1, 1), 2)
        self.assertEqual(quadrant_2d(-1, -1), 3)
        self.assertEqual(quadrant_2d(1, -1), 4)
    
    def test_quadrant_2d_on_axes(self):
        """Test points on axes."""
        self.assertEqual(quadrant_2d(0, 1), 0)
        self.assertEqual(quadrant_2d(1, 0), 0)
        self.assertEqual(quadrant_2d(0, 0), 0)
        self.assertEqual(quadrant_2d(0, -1), 0)
    
    def test_octant_3d_all_octants(self):
        """Test all eight octants."""
        self.assertEqual(octant_3d(1, 1, 1), 1)
        self.assertEqual(octant_3d(-1, 1, 1), 2)
        self.assertEqual(octant_3d(-1, -1, 1), 3)
        self.assertEqual(octant_3d(1, -1, 1), 4)
        self.assertEqual(octant_3d(1, 1, -1), 5)
        self.assertEqual(octant_3d(-1, 1, -1), 6)
        self.assertEqual(octant_3d(-1, -1, -1), 7)
        self.assertEqual(octant_3d(1, -1, -1), 8)
    
    def test_octant_3d_on_planes(self):
        """Test points on coordinate planes."""
        self.assertEqual(octant_3d(0, 1, 1), 0)
        self.assertEqual(octant_3d(1, 0, 1), 0)
        self.assertEqual(octant_3d(1, 1, 0), 0)


class TestLineEquations(unittest.TestCase):
    """Test line equation functions."""
    
    def test_line_equation_2d_slope_intercept_diagonal(self):
        """Test slope-intercept form for diagonal line."""
        m, b = line_equation_2d_slope_intercept(0, 0, 2, 4)
        self.assertAlmostEqual(m, 2.0)
        self.assertAlmostEqual(b, 0.0)
    
    def test_line_equation_2d_slope_intercept_horizontal(self):
        """Test slope-intercept form for horizontal line."""
        m, b = line_equation_2d_slope_intercept(0, 5, 3, 5)
        self.assertAlmostEqual(m, 0.0)
        self.assertAlmostEqual(b, 5.0)
    
    def test_line_equation_2d_slope_intercept_vertical_error(self):
        """Test error for vertical line."""
        with self.assertRaises(ValueError):
            line_equation_2d_slope_intercept(2, 0, 2, 5)
    
    def test_line_equation_2d_general_diagonal(self):
        """Test general form for diagonal line."""
        A, B, C = line_equation_2d_general(0, 0, 1, 1)
        # Line y = x has form -x + y = 0 or x - y = 0
        # Verify point lies on line
        self.assertAlmostEqual(A * 0.5 + B * 0.5 + C, 0.0)
        self.assertAlmostEqual(A * 1 + B * 1 + C, 0.0)
    
    def test_line_equation_2d_general_horizontal(self):
        """Test general form for horizontal line."""
        A, B, C = line_equation_2d_general(0, 1, 2, 1)
        # Horizontal line y = 1 has form 0x + 1y - 1 = 0
        # A should be 0, and By + C = 0 should hold for y = 1
        self.assertAlmostEqual(A, 0.0)
        self.assertAlmostEqual(B * 1 + C, 0.0)
    
    def test_point_line_distance_2d_basic(self):
        """Test point-to-line distance."""
        # Line x + y - 2 = 0 (or x + y = 2)
        # Distance from origin should be 2/sqrt(2) = sqrt(2)
        d = point_line_distance_2d(0, 0, 1, 1, -2)
        self.assertAlmostEqual(d, math.sqrt(2))
    
    def test_point_line_distance_2d_point_on_line(self):
        """Test distance when point is on line."""
        # Point (1, 1) on line x + y - 2 = 0
        d = point_line_distance_2d(1, 1, 1, 1, -2)
        self.assertAlmostEqual(d, 0.0)


class TestTorusDistance(unittest.TestCase):
    """Test torus distance functions."""
    
    def test_torus_distance_1d_short_path(self):
        """Test 1D torus distance with short path."""
        d = torus_distance_1d(0.0, 0.5)
        self.assertAlmostEqual(d, 0.5)
    
    def test_torus_distance_1d_wraparound(self):
        """Test 1D torus distance with wraparound."""
        d = torus_distance_1d(0.1, 0.9)
        # Wraparound distance: 0.2 (shorter than 0.8)
        self.assertAlmostEqual(d, 0.2)
    
    def test_torus_distance_1d_same_point(self):
        """Test 1D torus distance for same point."""
        d = torus_distance_1d(0.5, 0.5)
        self.assertAlmostEqual(d, 0.0)
    
    def test_torus_distance_nd_2d_no_wraparound(self):
        """Test 2D torus distance without wraparound."""
        d = torus_distance_nd([0.0, 0.0], [0.3, 0.4])
        self.assertAlmostEqual(d, 0.5)
    
    def test_torus_distance_nd_2d_with_wraparound(self):
        """Test 2D torus distance with wraparound."""
        d = torus_distance_nd([0.1, 0.1], [0.9, 0.9])
        # Each dimension: min(0.8, 0.2) = 0.2
        # Distance: sqrt(0.2^2 + 0.2^2) = sqrt(0.08) ≈ 0.283
        self.assertAlmostEqual(d, math.sqrt(0.08), places=5)
    
    def test_torus_distance_nd_dimension_mismatch(self):
        """Test error on dimension mismatch."""
        with self.assertRaises(ValueError):
            torus_distance_nd([0.1, 0.2], [0.3, 0.4, 0.5])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_points_centroid(self):
        """Test error on empty points list for centroid."""
        with self.assertRaises(ValueError):
            centroid_2d([])
        with self.assertRaises(ValueError):
            centroid_nd([])
        with self.assertRaises(ValueError):
            weighted_centroid_nd([], [])
    
    def test_inconsistent_dimensions_centroid_nd(self):
        """Test error on inconsistent dimensions."""
        with self.assertRaises(ValueError):
            centroid_nd([[0, 0], [1, 1, 1]])
    
    def test_section_point_zero_sum(self):
        """Test error when m + n = 0."""
        with self.assertRaises(ValueError):
            section_point_2d(0, 0, 1, 1, 1, -1)
    
    def test_weighted_centroid_weights_mismatch(self):
        """Test error when weights count doesn't match points."""
        with self.assertRaises(ValueError):
            weighted_centroid_nd([[0, 0], [1, 1]], [1, 2, 3])
    
    def test_weighted_centroid_zero_weight_sum(self):
        """Test error when sum of weights is zero."""
        with self.assertRaises(ValueError):
            weighted_centroid_nd([[0, 0], [1, 1]], [1, -1])
    
    def test_polygon_area_too_few_vertices(self):
        """Test error with too few vertices."""
        with self.assertRaises(ValueError):
            polygon_area_2d([(0, 0), (1, 1)])


class TestIntegrationWithRepository(unittest.TestCase):
    """Test integration with repository concepts (GVA, Z5D, etc.)."""
    
    def test_torus_distance_for_gva_embedding(self):
        """Test torus distance suitable for GVA torus embeddings."""
        # Simulate 5D torus embedding coordinates (all in [0, 1))
        coords1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        coords2 = [0.15, 0.25, 0.35, 0.45, 0.55]
        
        d = torus_distance_nd(coords1, coords2)
        self.assertGreater(d, 0.0)
        self.assertLess(d, 1.0)  # Max distance on unit torus
    
    def test_high_precision_distance(self):
        """Test high-precision distance for Z5D validation."""
        # Requires precision < 1e-16
        d = euclidean_distance_nd_hp([0, 0], [1, 1])
        d_float = float(d)
        
        # Should be very close to sqrt(2)
        expected = math.sqrt(2)
        error = abs(d_float - expected)
        self.assertLess(error, 1e-15)
    
    def test_weighted_centroid_with_curvature_weights(self):
        """Test weighted centroid with simulated κ(n) weights."""
        # Simulate curvature-weighted aggregation
        points = [[0, 0], [1, 0], [0, 1]]
        
        # Simple increasing weights (simulating curvature)
        weights = [1.0, 1.5, 2.0]
        
        c = weighted_centroid_nd(points, weights)
        self.assertEqual(len(c), 2)
        
        # Weighted toward higher-weight points
        self.assertGreater(c[0], 0.3)  # Weighted toward [1, 0]
        self.assertGreater(c[1], 0.3)  # Weighted toward [0, 1]


def run_tests():
    """Run all tests with verbose output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDistanceFormulas))
    suite.addTests(loader.loadTestsFromTestCase(TestMidpointAndSection))
    suite.addTests(loader.loadTestsFromTestCase(TestCentroid))
    suite.addTests(loader.loadTestsFromTestCase(TestAreaVolume))
    suite.addTests(loader.loadTestsFromTestCase(TestQuadrantsOctants))
    suite.addTests(loader.loadTestsFromTestCase(TestLineEquations))
    suite.addTests(loader.loadTestsFromTestCase(TestTorusDistance))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithRepository))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
