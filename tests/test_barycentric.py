#!/usr/bin/env python3
"""
Test suite for barycentric coordinates module.

Validates:
1. Core barycentric coordinate calculations
2. Interpolation and reconstruction
3. Distance metrics
4. Curvature weighting
5. Integration with torus embeddings
6. Simplicial stratification for sampling
"""

import unittest
import sys
import os
import numpy as np
import math

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from barycentric import (
    BarycentricCoordinates,
    barycentric_distance,
    curvature_weighted_barycentric,
    simplicial_stratification,
    torus_barycentric_embedding,
    barycentric_distance_torus,
    validate_barycentric_properties
)


class TestBarycentricBasics(unittest.TestCase):
    """Test fundamental barycentric coordinate operations."""
    
    def test_2d_triangle_vertices(self):
        """Test that vertices have unit barycentric coordinates."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        # Each vertex should have λᵢ = 1, others = 0
        for i, v in enumerate(vertices):
            lambdas = bc.compute_barycentric_coords(v)
            expected = np.zeros(3)
            expected[i] = 1.0
            np.testing.assert_allclose(lambdas, expected, atol=1e-10,
                                      err_msg=f"Vertex {i} coords incorrect")
    
    def test_2d_triangle_centroid(self):
        """Test centroid has uniform coordinates (1/3, 1/3, 1/3)."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        centroid = bc.centroid()
        expected_centroid = np.array([1/3, 1/3])
        np.testing.assert_allclose(centroid, expected_centroid, atol=1e-10)
        
        # Centroid's barycentric coords should be uniform
        lambdas = bc.compute_barycentric_coords(centroid)
        expected_lambdas = np.array([1/3, 1/3, 1/3])
        np.testing.assert_allclose(lambdas, expected_lambdas, atol=1e-10)
    
    def test_interpolation_consistency(self):
        """Test that interpolation and coordinate computation are inverses."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.5, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        # Random barycentric coordinates
        test_lambdas = np.array([0.2, 0.3, 0.5])
        
        # Interpolate to get point
        point = bc.interpolate(test_lambdas)
        
        # Compute coordinates back
        recovered_lambdas = bc.compute_barycentric_coords(point)
        
        np.testing.assert_allclose(recovered_lambdas, test_lambdas, atol=1e-10)
    
    def test_sum_constraint(self):
        """Test that barycentric coordinates sum to 1."""
        vertices = [
            np.array([1.0, 2.0]),
            np.array([3.0, 1.0]),
            np.array([2.0, 4.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        # Test multiple points
        test_points = [
            np.array([2.0, 2.0]),
            np.array([1.5, 2.5]),
            np.array([2.5, 2.0])
        ]
        
        for point in test_points:
            lambdas = bc.compute_barycentric_coords(point)
            self.assertAlmostEqual(np.sum(lambdas), 1.0, places=10,
                                  msg=f"Sum constraint violated for {point}")
    
    def test_inside_simplex(self):
        """Test is_inside_simplex detection."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        # Inside point
        inside_lambdas = np.array([0.3, 0.4, 0.3])
        self.assertTrue(bc.is_inside_simplex(inside_lambdas))
        
        # Outside point (negative coordinate)
        outside_lambdas = np.array([1.5, -0.3, -0.2])
        self.assertFalse(bc.is_inside_simplex(outside_lambdas))


class TestBarycentricDistance(unittest.TestCase):
    """Test barycentric distance metrics."""
    
    def test_euclidean_distance(self):
        """Test Euclidean distance in barycentric space."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        point1 = np.array([0.25, 0.25])
        point2 = np.array([0.5, 0.5])
        
        dist = barycentric_distance(point1, point2, vertices, metric='euclidean')
        
        # Distance should be positive
        self.assertGreater(dist, 0)
        
        # Distance to itself should be zero
        dist_self = barycentric_distance(point1, point1, vertices, metric='euclidean')
        self.assertAlmostEqual(dist_self, 0.0, places=10)
    
    def test_manhattan_distance(self):
        """Test Manhattan distance in barycentric space."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        point1 = np.array([0.2, 0.2])
        point2 = np.array([0.6, 0.2])
        
        dist = barycentric_distance(point1, point2, vertices, metric='manhattan')
        self.assertGreater(dist, 0)


class TestCurvatureWeighting(unittest.TestCase):
    """Test curvature-weighted barycentric coordinates."""
    
    def test_curvature_weighting_normalization(self):
        """Test that curvature weighting maintains sum = 1."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        point = np.array([0.3, 0.3])
        
        # Simple curvature function
        def kappa_func(i):
            return 0.1 * i  # Increasing weight by vertex index
        
        weighted = curvature_weighted_barycentric(point, vertices, kappa_func)
        
        # Should still sum to 1
        self.assertAlmostEqual(np.sum(weighted), 1.0, places=10)
    
    def test_curvature_weighting_effect(self):
        """Test that curvature weighting modifies coordinates."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        point = np.array([0.5, 0.0])  # On edge between v0 and v1
        
        # No curvature
        bc = BarycentricCoordinates(vertices)
        unweighted = bc.compute_barycentric_coords(point)
        
        # With curvature
        def kappa_func(i):
            return 0.5 if i == 0 else 0.0
        
        weighted = curvature_weighted_barycentric(point, vertices, kappa_func)
        
        # Curvature should modify the coordinates
        self.assertFalse(np.allclose(weighted, unweighted, atol=1e-10))
        
        # But sum should still be 1
        self.assertAlmostEqual(np.sum(weighted), 1.0, places=10)


class TestSimplicialStratification(unittest.TestCase):
    """Test simplicial stratification for sampling."""
    
    def test_stratification_count(self):
        """Test that correct number of samples are generated."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        n_strata = 20
        samples = simplicial_stratification(vertices, n_strata)
        
        self.assertEqual(len(samples), n_strata)
    
    def test_stratification_inside(self):
        """Test that all samples are inside simplex."""
        vertices = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0])
        ]
        
        samples = simplicial_stratification(vertices, 10)
        bc = BarycentricCoordinates(vertices)
        
        for sample in samples:
            lambdas = bc.compute_barycentric_coords(sample)
            # Allow small numerical tolerance
            self.assertTrue(bc.is_inside_simplex(lambdas, tolerance=1e-8),
                          msg=f"Sample {sample} outside simplex: lambdas={lambdas}")


class TestTorusIntegration(unittest.TestCase):
    """Test integration with torus embeddings."""
    
    def test_torus_embedding_dimensions(self):
        """Test that torus embedding produces correct dimensions."""
        n = 899  # Example semiprime (29 × 31)
        dims = 11
        
        embedding, anchors = torus_barycentric_embedding(n, dims)
        
        # Check dimensions
        self.assertEqual(len(embedding), dims)
        self.assertEqual(len(anchors), dims + 1)  # Need d+1 anchors
        
        for anchor in anchors:
            self.assertEqual(len(anchor), dims)
    
    def test_torus_embedding_coordinates(self):
        """Test that torus embedding produces valid coordinates."""
        n = 1000
        dims = 5
        
        embedding, anchors = torus_barycentric_embedding(n, dims)
        
        # All coordinates should be in [0, 1] (torus space)
        self.assertTrue(np.all(embedding >= 0.0))
        self.assertTrue(np.all(embedding <= 1.0))
        
        for anchor in anchors:
            self.assertTrue(np.all(anchor >= 0.0))
            self.assertTrue(np.all(anchor <= 1.0))
    
    def test_barycentric_distance_torus_properties(self):
        """Test barycentric distance on torus."""
        n = 899
        
        # Create two torus coordinates
        _, anchors = torus_barycentric_embedding(n, dims=5)
        theta1 = anchors[0]  # Use first anchor
        theta2 = anchors[1]  # Use second anchor
        
        # Distance should be positive
        dist = barycentric_distance_torus(theta1, theta2, n)
        self.assertGreater(dist, 0)
        
        # Distance to itself should be small (near zero)
        dist_self = barycentric_distance_torus(theta1, theta1, n)
        self.assertLess(dist_self, 1e-6)


class Test3DTetrahedron(unittest.TestCase):
    """Test barycentric coordinates in 3D."""
    
    def test_3d_tetrahedron_centroid(self):
        """Test 3D tetrahedron centroid."""
        vertices = [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        centroid = bc.centroid()
        expected = np.array([0.25, 0.25, 0.25])
        np.testing.assert_allclose(centroid, expected, atol=1e-10)
    
    def test_3d_tetrahedron_vertices(self):
        """Test 3D tetrahedron vertex coordinates."""
        vertices = [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0])
        ]
        bc = BarycentricCoordinates(vertices)
        
        for i, v in enumerate(vertices):
            lambdas = bc.compute_barycentric_coords(v)
            expected = np.zeros(4)
            expected[i] = 1.0
            np.testing.assert_allclose(lambdas, expected, atol=1e-10)


class TestHighDimensional(unittest.TestCase):
    """Test barycentric coordinates in high dimensions."""
    
    def test_11d_simplex(self):
        """Test 11-dimensional simplex (for GVA integration)."""
        dims = 11
        n_vertices = dims + 1  # 12 vertices
        
        # Create simplex vertices (standard basis + origin)
        vertices = [np.zeros(dims)]  # Origin
        for i in range(dims):
            v = np.zeros(dims)
            v[i] = 1.0
            vertices.append(v)
        
        bc = BarycentricCoordinates(vertices)
        
        # Test centroid
        centroid = bc.centroid()
        expected_centroid = np.ones(dims) / n_vertices
        np.testing.assert_allclose(centroid, expected_centroid, atol=1e-10)
        
        # Test that centroid has uniform barycentric coords
        lambdas = bc.compute_barycentric_coords(centroid)
        expected_lambdas = np.ones(n_vertices) / n_vertices
        np.testing.assert_allclose(lambdas, expected_lambdas, atol=1e-10)


class TestValidation(unittest.TestCase):
    """Test validation functions."""
    
    def test_validate_properties(self):
        """Test that validation function passes."""
        result = validate_barycentric_properties()
        self.assertTrue(result)


def run_comprehensive_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("Barycentric Coordinates Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBarycentricBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestBarycentricDistance))
    suite.addTests(loader.loadTestsFromTestCase(TestCurvatureWeighting))
    suite.addTests(loader.loadTestsFromTestCase(TestSimplicialStratification))
    suite.addTests(loader.loadTestsFromTestCase(TestTorusIntegration))
    suite.addTests(loader.loadTestsFromTestCase(Test3DTetrahedron))
    suite.addTests(loader.loadTestsFromTestCase(TestHighDimensional))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
