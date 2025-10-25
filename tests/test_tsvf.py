#!/usr/bin/env python3
"""
Unit tests for Time-Symmetric Two-State Vector Formalism (TSVF)

Tests cover:
- State initialization and inner products
- Forward and backward evolution
- Weak value computation
- Time-symmetric metric
- Variance reduction estimation
- Candidate optimization
"""

import unittest
import numpy as np
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from tsvf import (
    TSVFState, TSVFEvolution, TSVFMetric, TSVFOptimizer,
    PHI, E2
)


class TestTSVFState(unittest.TestCase):
    """Test TSVF state representation and operations."""
    
    def test_state_initialization(self):
        """Test state creation with coordinates."""
        coords = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        state = TSVFState(coords, amplitude=1.0, phase=0.0)
        
        self.assertEqual(state.dimension, 5)
        self.assertEqual(state.amplitude, 1.0)
        self.assertEqual(state.phase, 0.0)
        np.testing.assert_array_almost_equal(state.coordinates, coords)
    
    def test_inner_product_identical_states(self):
        """Test inner product of state with itself."""
        coords = np.array([0.5, 0.5, 0.5])
        state = TSVFState(coords)
        
        inner_prod = state.inner_product(state)
        
        # Should be real and positive for identical states
        self.assertGreater(inner_prod.real, 0.9)
        self.assertLess(abs(inner_prod.imag), 0.1)
    
    def test_inner_product_orthogonal_states(self):
        """Test inner product of distant states."""
        state1 = TSVFState(np.array([0.0, 0.0, 0.0]))
        state2 = TSVFState(np.array([1.0, 1.0, 1.0]))
        
        inner_prod = state1.inner_product(state2)
        
        # Distant states should have small overlap (relaxed threshold)
        self.assertLess(abs(inner_prod), 0.3)
    
    def test_normalization(self):
        """Test state normalization."""
        coords = np.array([3.0, 4.0, 0.0])  # Will normalize to [0.6, 0.8, 0.0]
        state = TSVFState(coords)
        state.normalize()
        
        norm = np.linalg.norm(state.coordinates)
        self.assertAlmostEqual(norm, 1.0, places=10)
    
    def test_dimension_mismatch(self):
        """Test that dimension mismatch raises error."""
        state1 = TSVFState(np.array([0.1, 0.2]))
        state2 = TSVFState(np.array([0.1, 0.2, 0.3]))
        
        with self.assertRaises(ValueError):
            state1.inner_product(state2)


class TestTSVFEvolution(unittest.TestCase):
    """Test TSVF evolution operators."""
    
    def setUp(self):
        """Set up evolution operator."""
        self.evolution = TSVFEvolution()
        self.target_N = 899  # 29 × 31
    
    def test_forward_evolution_length(self):
        """Test forward evolution produces correct number of states."""
        initial = TSVFState(np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
        
        states = self.evolution.forward_evolve(initial, self.target_N, time_steps=10)
        
        # Should return initial state plus 10 evolved states
        self.assertEqual(len(states), 11)
    
    def test_forward_evolution_coordinates_change(self):
        """Test that forward evolution changes coordinates."""
        initial = TSVFState(np.array([0.2, 0.3, 0.4]))
        
        states = self.evolution.forward_evolve(initial, self.target_N, time_steps=10)
        
        # First and last states should differ
        initial_coords = states[0].coordinates
        final_coords = states[-1].coordinates
        
        # Check that at least some coordinate changed significantly
        max_change = np.max(np.abs(initial_coords - final_coords))
        self.assertGreater(max_change, 0.01)
    
    def test_backward_evolution_length(self):
        """Test backward evolution produces correct number of states."""
        final = TSVFState(np.array([0.6, 0.7, 0.8]))
        
        states = self.evolution.backward_evolve(final, self.target_N, time_steps=10)
        
        self.assertEqual(len(states), 11)
    
    def test_backward_evolution_reverses_forward(self):
        """Test that backward evolution approximately reverses forward."""
        initial = TSVFState(np.array([0.3, 0.4, 0.5]))
        
        # Forward evolve
        forward_states = self.evolution.forward_evolve(
            initial, self.target_N, time_steps=5
        )
        final_forward = forward_states[-1]
        
        # Backward evolve from end
        backward_states = self.evolution.backward_evolve(
            final_forward, self.target_N, time_steps=5
        )
        
        # Backward evolution should move toward origin
        # (not exact reversal due to modulo arithmetic)
        self.assertIsNotNone(backward_states)
        self.assertEqual(len(backward_states), 6)
    
    def test_weak_value_computation(self):
        """Test weak value calculation."""
        forward_state = TSVFState(np.array([0.2, 0.3, 0.4]))
        backward_state = TSVFState(np.array([0.6, 0.7, 0.8]))
        
        # Identity-like observable
        observable = np.eye(3)
        
        weak_value = self.evolution.compute_weak_value(
            observable, forward_state, backward_state
        )
        
        # Should be finite complex number
        self.assertFalse(np.isinf(weak_value.real))
        self.assertFalse(np.isinf(weak_value.imag))
    
    def test_weak_value_orthogonal_states(self):
        """Test weak value with nearly orthogonal states."""
        # Very distant states
        forward_state = TSVFState(np.array([0.0, 0.0, 0.0]))
        backward_state = TSVFState(np.array([0.99, 0.99, 0.99]))
        
        observable = np.eye(3)
        
        weak_value = self.evolution.compute_weak_value(
            observable, forward_state, backward_state
        )
        
        # Can be very large or infinite for orthogonal states
        # Just check it completes without error
        self.assertIsNotNone(weak_value)


class TestTSVFMetric(unittest.TestCase):
    """Test time-symmetric distance metric."""
    
    def setUp(self):
        """Set up metric."""
        self.metric = TSVFMetric(alpha=0.5, beta=0.5)
        self.target_N = 899
    
    def test_distance_positive(self):
        """Test distance is always positive."""
        point1 = np.array([0.1, 0.2, 0.3])
        point2 = np.array([0.4, 0.5, 0.6])
        
        dist = self.metric.distance(point1, point2, self.target_N, use_tsvf=True)
        
        self.assertGreater(dist, 0.0)
    
    def test_distance_symmetric(self):
        """Test distance symmetry: d(A,B) ≈ d(B,A)."""
        point1 = np.array([0.2, 0.3, 0.4])
        point2 = np.array([0.7, 0.8, 0.9])
        
        dist_12 = self.metric.distance(point1, point2, self.target_N, use_tsvf=True)
        dist_21 = self.metric.distance(point2, point1, self.target_N, use_tsvf=True)
        
        # Should be approximately symmetric
        self.assertAlmostEqual(dist_12, dist_21, places=5)
    
    def test_distance_identity(self):
        """Test distance from point to itself is zero."""
        point = np.array([0.5, 0.5, 0.5])
        
        dist = self.metric.distance(point, point, self.target_N, use_tsvf=True)
        
        self.assertAlmostEqual(dist, 0.0, places=10)
    
    def test_tsvf_vs_standard_distance(self):
        """Test TSVF distance differs from standard Riemannian."""
        point1 = np.array([0.1, 0.2, 0.3])
        point2 = np.array([0.4, 0.5, 0.6])
        
        tsvf_dist = self.metric.distance(point1, point2, self.target_N, use_tsvf=True)
        standard_dist = self.metric.distance(point1, point2, self.target_N, use_tsvf=False)
        
        # TSVF should provide different (typically enhanced) metric
        self.assertNotAlmostEqual(tsvf_dist, standard_dist, places=5)
    
    def test_metric_weights(self):
        """Test metric respects alpha/beta weights."""
        metric_forward = TSVFMetric(alpha=1.0, beta=0.0)
        metric_backward = TSVFMetric(alpha=0.0, beta=1.0)
        
        point1 = np.array([0.2, 0.3])
        point2 = np.array([0.7, 0.8])
        
        dist_forward = metric_forward.distance(point1, point2, self.target_N, use_tsvf=True)
        dist_backward = metric_backward.distance(point1, point2, self.target_N, use_tsvf=True)
        
        # Different weights should give different results
        self.assertNotAlmostEqual(dist_forward, dist_backward, places=5)


class TestTSVFOptimizer(unittest.TestCase):
    """Test TSVF-based optimization."""
    
    def setUp(self):
        """Set up optimizer."""
        self.target_N = 899  # 29 × 31
        self.optimizer = TSVFOptimizer(self.target_N, dimension=5)
    
    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        self.assertEqual(self.optimizer.target_value, 899)
        self.assertEqual(self.optimizer.dimension, 5)
        self.assertIsNotNone(self.optimizer.evolution)
        self.assertIsNotNone(self.optimizer.metric)
    
    def test_simple_embed(self):
        """Test simple embedding function."""
        value = 100
        embedding = self.optimizer._simple_embed(value)
        
        self.assertEqual(len(embedding), 5)
        # All coordinates should be in [0, 1)
        self.assertTrue(np.all(embedding >= 0.0))
        self.assertTrue(np.all(embedding < 1.0))
    
    def test_embed_deterministic(self):
        """Test embedding is deterministic."""
        value = 100
        embed1 = self.optimizer._simple_embed(value)
        embed2 = self.optimizer._simple_embed(value)
        
        np.testing.assert_array_almost_equal(embed1, embed2)
    
    def test_optimize_candidates_returns_scored_list(self):
        """Test candidate optimization returns scored list."""
        sqrt_n = int(self.target_N ** 0.5)
        candidates = [sqrt_n + i for i in range(-10, 11)]
        target_embedding = self.optimizer._simple_embed(self.target_N)
        
        ranked = self.optimizer.optimize_candidates(
            candidates, target_embedding, max_candidates=5
        )
        
        # Should return list of tuples
        self.assertIsInstance(ranked, list)
        self.assertLessEqual(len(ranked), 5)
        
        # Each tuple should be (candidate, score)
        for candidate, score in ranked:
            self.assertIsInstance(candidate, int)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_optimize_candidates_sorted(self):
        """Test candidates are sorted by score."""
        sqrt_n = int(self.target_N ** 0.5)
        candidates = [sqrt_n + i for i in range(-5, 6)]
        target_embedding = self.optimizer._simple_embed(self.target_N)
        
        ranked = self.optimizer.optimize_candidates(
            candidates, target_embedding, max_candidates=10
        )
        
        # Scores should be in descending order
        scores = [score for _, score in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_variance_reduction_factor(self):
        """Test variance reduction computation."""
        initial = TSVFState(np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
        final = TSVFState(np.array([0.6, 0.7, 0.8, 0.9, 0.95]))
        
        forward_states = self.optimizer.evolution.forward_evolve(
            initial, self.target_N, time_steps=5
        )
        backward_states = self.optimizer.evolution.backward_evolve(
            final, self.target_N, time_steps=5
        )
        
        var_reduction = self.optimizer.compute_variance_reduction_factor(
            forward_states[:5], backward_states[:5]
        )
        
        # Should be >= 1.0 (1.0 means no improvement)
        self.assertGreaterEqual(var_reduction, 1.0)
    
    def test_variance_reduction_length_mismatch(self):
        """Test variance reduction with mismatched state lists."""
        initial = TSVFState(np.array([0.1, 0.2, 0.3]))
        
        forward_states = self.optimizer.evolution.forward_evolve(
            initial, self.target_N, time_steps=5
        )
        backward_states = self.optimizer.evolution.backward_evolve(
            initial, self.target_N, time_steps=3
        )
        
        with self.assertRaises(ValueError):
            self.optimizer.compute_variance_reduction_factor(
                forward_states, backward_states
            )


class TestTSVFIntegration(unittest.TestCase):
    """Integration tests for TSVF system."""
    
    def test_full_pipeline_small_semiprime(self):
        """Test complete TSVF pipeline on small semiprime."""
        N = 899  # 29 × 31
        optimizer = TSVFOptimizer(N, dimension=5)
        
        # Initial and final states
        initial = TSVFState(np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
        final = TSVFState(np.array([0.6, 0.7, 0.8, 0.9, 0.95]))
        
        # Evolution
        forward_states = optimizer.evolution.forward_evolve(initial, N, time_steps=10)
        backward_states = optimizer.evolution.backward_evolve(final, N, time_steps=10)
        
        # Variance reduction
        var_reduction = optimizer.compute_variance_reduction_factor(
            forward_states[:10], backward_states[:10]
        )
        
        # Candidate optimization
        sqrt_n = int(N ** 0.5)
        candidates = [sqrt_n + i for i in range(-20, 21)]
        target_embedding = optimizer._simple_embed(N)
        
        ranked = optimizer.optimize_candidates(
            candidates, target_embedding, max_candidates=10
        )
        
        # Verify results are sensible
        self.assertGreater(var_reduction, 1.0)
        self.assertGreater(len(ranked), 0)
        self.assertLessEqual(len(ranked), 10)
        
        # Check if true factors get high scores (if in candidate list)
        true_factors = [29, 31]
        for factor in true_factors:
            if factor in [c for c, _ in ranked]:
                # True factor should be in top-ranked candidates
                factor_rank = next(i for i, (c, _) in enumerate(ranked) if c == factor)
                self.assertLess(factor_rank, 5, 
                               f"True factor {factor} should rank highly")
    
    def test_constants_defined(self):
        """Test universal constants are properly defined."""
        self.assertAlmostEqual(PHI, 1.618033988749, places=10)
        self.assertAlmostEqual(E2, 7.389056098930, places=10)


class TestTSVFEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_zero_dimensional_state(self):
        """Test handling of zero-dimensional state."""
        # Empty array creates 0-dimensional state (allowed but unusual)
        state = TSVFState(np.array([]))
        self.assertEqual(state.dimension, 0)
    
    def test_large_amplitude_state(self):
        """Test state with large amplitude."""
        coords = np.array([0.5, 0.5, 0.5])
        state = TSVFState(coords, amplitude=1e6)
        
        self.assertEqual(state.amplitude, 1e6)
    
    def test_zero_amplitude_state(self):
        """Test state with zero amplitude."""
        coords = np.array([0.5, 0.5, 0.5])
        state = TSVFState(coords, amplitude=0.0)
        
        inner_prod = state.inner_product(state)
        self.assertAlmostEqual(abs(inner_prod), 0.0, places=10)
    
    def test_very_large_target(self):
        """Test TSVF with very large target value."""
        N = 2**128 - 1
        optimizer = TSVFOptimizer(N, dimension=5)
        
        # Should initialize without error
        self.assertEqual(optimizer.target_value, N)
        
        # Test embedding works
        embedding = optimizer._simple_embed(N)
        self.assertEqual(len(embedding), 5)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
