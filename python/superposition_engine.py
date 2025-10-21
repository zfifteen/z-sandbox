#!/usr/bin/env python3
"""
Multi-Scale Geodesic Superposition Engine.
Combines multiple k-values for enhanced factorization paths.
"""

import math
from test_curved_geometry import curved_geometric_factorize, generate_balanced_semiprime
from z5d_predictor import z5d_predict, z5d_search_candidates

def geodesic_superpose(N, k_set):
    """
    Superpose multiple geodesic paths from different k starting points.
    Returns combined factor candidates.
    """
    path_candidates = set()

    for k in k_set:
        # Get Z5D prediction for this k
        pred = z5d_predict(k)

        # Search outward for candidates
        candidates = z5d_search_candidates(k, max_offset=100)

        # Add to combined set
        path_candidates.update(candidates)

        # Check if prediction itself is a factor
        if N % pred == 0:
            q = N // pred
            return pred, q  # Direct hit

    return list(path_candidates)

def adaptive_epsilon(N, k, base_epsilon=0.12):
    """
    Adaptive ε threshold based on local curvature.
    Shrinks threshold in high-density regions.
    """
    from z5d_predictor import theta_prime
    enhancement = theta_prime(N, k)
    curvature_factor = 1 + enhancement / 100  # Scale based on density
    return base_epsilon / curvature_factor

def multi_scale_factorize(N, k_set=[1, 2, 3, 4, 5], use_curved=True):
    """
    Multi-scale geodesic superposition factorization.
    Combines paths from multiple k-values.
    """
    print(f"Multi-scale factorization with k_set={k_set}")

    # Get superposed candidates
    superposed_candidates = geodesic_superpose(N, k_set)
    print(f"Superposed candidates: {len(superposed_candidates)}")

    if len(superposed_candidates) < 2:
        return None, None, {"error": "Insufficient candidates"}

    # Use adaptive epsilon for each k
    stages = []
    for k in k_set:
        eps = adaptive_epsilon(N, k)
        stages.append((k, eps))  # Use k as the "stage parameter"

    # For now, test with standard curved factorization on superposed set
    # In full implementation, this would use the superposition in distance calculations

    from test_curved_geometry import generate_balanced_semiprime
    # For demo, assume we know factors (in practice, this would be blind)
    # This is a placeholder for the full superposition logic

    return None, None, {"method": "multi_scale", "candidates": len(superposed_candidates), "stages": len(stages)}

def test_multi_scale():
    """Test multi-scale superposition on a known case."""
    print("=== Multi-Scale Geodesic Superposition Test ===\n")

    N, true_p, true_q = generate_balanced_semiprime(34, 42)
    print(f"Test Case: N={N}")
    print(f"True Factors: {true_p} × {true_q}")

    k_set = [1, 2, 3, 4, 5]
    result_p, result_q, metadata = multi_scale_factorize(N, k_set)

    print(f"Result: {metadata}")

    # In practice, this would integrate with the full factorization engine
    print("\nNote: Full integration requires combining superposition with Riemannian distances.")

if __name__ == "__main__":
    test_multi_scale()