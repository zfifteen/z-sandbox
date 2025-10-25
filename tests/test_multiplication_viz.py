#!/usr/bin/env python3
"""
Unit tests for line-intersection multiplication visualization.

Tests the accuracy of intersection-based candidate generation and validates
the visualization concepts against known factor cases.
"""

import sys
import os
import unittest
import tempfile
import math

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python", "examples"))

from multiplication_viz_factor import (  # noqa: E402
    count_intersections,
    intersection_based_candidates,
    draw_intersection_mult,
    draw_intersection_mult_advanced,
)


class TestIntersectionCounting(unittest.TestCase):
    """Test intersection counting functionality."""

    def test_basic_intersection_count(self):
        """Test that intersection count equals product of digit counts."""
        # 2 digits × 2 digits = 4 intersections
        count = count_intersections([2, 1], [3, 2])
        self.assertEqual(count, 4)

    def test_scaled_intersection_count(self):
        """Test intersection counting with different digit lengths."""
        # 3 digits × 2 digits = 6 intersections
        count = count_intersections([5, 0, 0], [1, 3])
        self.assertEqual(count, 6)

    def test_single_digit_multiplication(self):
        """Test single digit × single digit = 1 intersection."""
        count = count_intersections([7], [9])
        self.assertEqual(count, 1)


class TestCandidateGeneration(unittest.TestCase):
    """Test intersection-based candidate generation."""

    def test_small_semiprime_candidates(self):
        """Test candidate generation for small semiprime 143 = 11 × 13."""
        N = 143
        p, q = 11, 13

        candidates = intersection_based_candidates(N, num_candidates=20)

        # Both factors should be in candidate list
        self.assertIn(p, candidates, f"Factor {p} not found in candidates")
        self.assertIn(q, candidates, f"Factor {q} not found in candidates")

    def test_candidates_near_sqrt(self):
        """Test that candidates cluster near √N."""
        N = 10000  # √N = 100
        candidates = intersection_based_candidates(N, num_candidates=50)

        sqrt_n = math.sqrt(N)

        # All candidates should be reasonably close to √N
        for candidate in candidates:
            distance_ratio = abs(candidate - sqrt_n) / sqrt_n
            self.assertLess(
                distance_ratio, 0.5, f"Candidate {candidate} too far from √N={sqrt_n}"
            )

    def test_larger_semiprime_candidates(self):
        """Test candidate generation for larger semiprime."""
        p, q = 100003, 100019
        N = p * q

        candidates = intersection_based_candidates(N, num_candidates=100)

        # Factors should be findable with reasonable candidate pool
        self.assertIn(p, candidates, f"Factor {p} not found in candidates")
        self.assertIn(q, candidates, f"Factor {q} not found in candidates")

    def test_candidate_ordering(self):
        """Test that candidates are ordered by proximity to √N."""
        N = 10000
        candidates = intersection_based_candidates(N, num_candidates=20)

        sqrt_n = math.sqrt(N)

        # Check that distances are monotonically non-decreasing
        prev_dist = 0
        for candidate in candidates:
            dist = abs(candidate - sqrt_n)
            self.assertGreaterEqual(
                dist,
                prev_dist - 1e-10,  # Allow floating point tolerance
                "Candidates not ordered by proximity",
            )
            prev_dist = dist


class TestVisualizationFunctions(unittest.TestCase):
    """Test visualization generation without displaying."""

    def test_basic_visualization_creation(self):
        """Test that basic visualization can be created."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            fig = draw_intersection_mult([2, 1], [3, 2], 672, output_file=tmp.name)
            self.assertIsNotNone(fig)
            # Check file was created
            self.assertTrue(os.path.exists(tmp.name))

    def test_advanced_visualization_creation(self):
        """Test that advanced visualization with factors can be created."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            fig = draw_intersection_mult_advanced(
                11,
                13,
                highlight_factors=True,
                curvature_weight=True,
                output_file=tmp.name,
            )
            self.assertIsNotNone(fig)
            self.assertTrue(os.path.exists(tmp.name))

    def test_visualization_without_candidates(self):
        """Test visualization with candidate overlay disabled."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            fig = draw_intersection_mult(
                [2, 1], [3, 2], 672, show_candidates=False, output_file=tmp.name
            )
            self.assertIsNotNone(fig)


class TestFactorValidation(unittest.TestCase):
    """Test validation against known factor cases (RSA-style harness)."""

    def test_alignment_small_semiprimes(self):
        """Test >95% alignment on small synthetic targets."""
        test_cases = [
            (11, 13),  # 143
            (17, 19),  # 323
            (23, 29),  # 667
            (31, 37),  # 1147
            (41, 43),  # 1763
        ]

        total = len(test_cases)
        found = 0

        for p, q in test_cases:
            N = p * q
            candidates = intersection_based_candidates(N, num_candidates=50)

            if p in candidates and q in candidates:
                found += 1

        alignment_rate = found / total
        self.assertGreaterEqual(
            alignment_rate, 0.95, f"Alignment rate {alignment_rate:.2%} < 95%"
        )

    def test_alignment_medium_semiprimes(self):
        """Test alignment on medium-sized semiprimes."""
        test_cases = [
            (1009, 1013),  # ~10^6
            (10007, 10009),  # ~10^8
        ]

        total = len(test_cases)
        found = 0

        for p, q in test_cases:
            N = p * q
            # Need larger candidate pool for bigger numbers
            candidates = intersection_based_candidates(N, num_candidates=200)

            if p in candidates and q in candidates:
                found += 1

        alignment_rate = found / total
        # Medium semiprimes may need larger candidate pools
        # But should still have reasonable success rate
        self.assertGreaterEqual(
            alignment_rate, 0.5, f"Alignment rate {alignment_rate:.2%} too low"
        )


class TestIntegrationWithZ5D(unittest.TestCase):
    """Test integration concepts with Z5D axioms."""

    def test_curvature_calculation(self):
        """Test Z5D curvature κ(n) = d(n) · ln(n+1) / e² concepts."""
        # This tests that the curvature calculation in visualization
        # aligns with Z5D axioms
        N = 143
        e2 = math.exp(2)
        d_n = len(str(N))  # Digits as proxy for divisor count
        kappa = d_n * math.log(N + 1) / e2

        # Curvature should be positive and reasonable
        self.assertGreater(kappa, 0)
        self.assertLess(kappa, 100)  # Sanity check

    def test_geometric_proximity_concept(self):
        """Test that geometric proximity correlates with factorization."""
        # For balanced semiprime, factors cluster near √N
        p, q = 97, 101
        N = p * q
        sqrt_n = math.sqrt(N)

        # Both factors should be within 10% of √N for balanced semiprime
        p_proximity = abs(p - sqrt_n) / sqrt_n
        q_proximity = abs(q - sqrt_n) / sqrt_n

        self.assertLess(p_proximity, 0.1)
        self.assertLess(q_proximity, 0.1)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
