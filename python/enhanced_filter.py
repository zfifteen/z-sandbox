#!/usr/bin/env python3
"""
Enhanced geometric filtering with distance-weighted prioritization.
"""

import sys
sys.path.append('gists')

from geometric_factorization import theta, theta_ultra_precise, circular_distance

def filter_candidates_geometric_enhanced(
    N: int,
    candidates,
    k: float,
    epsilon: float,
    ultra_precision: bool = False
):
    """
    Enhanced geometric filtering with distance-weighted sorting.

    Returns candidates sorted by increasing circular distance to N's theta.
    """
    if ultra_precision:
        theta_N = theta_ultra_precise(N, k)
        theta_func = lambda x: theta_ultra_precise(x, k)
    else:
        theta_N = theta(N, k)
        theta_func = lambda x: theta(x, k)

    # Compute distances for all candidates
    candidate_distances = []
    for p in candidates:
        theta_p = theta_func(p)
        dist = circular_distance(theta_p, theta_N)
        candidate_distances.append((p, dist))

    # Filter by epsilon
    filtered = [(p, dist) for p, dist in candidate_distances if dist <= epsilon]

    # Sort by increasing distance (best first)
    filtered.sort(key=lambda x: x[1])

    # Return just candidates, sorted
    return [p for p, dist in filtered]

# Test
if __name__ == '__main__':
    candidates = [11, 13, 17, 19, 23]
    N = 143  # 11 * 13
    filtered = filter_candidates_geometric_enhanced(N, candidates, 0.2, 0.1)
    print(f"Filtered and sorted: {filtered}")