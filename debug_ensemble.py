#!/usr/bin/env python3
"""
Debug ensemble scoring for 35-bit semiprimes.
"""

import sys
sys.path.append('gists')

from geometric_factorization import generate_semiprime, theta_mod1_log, ALPHAS

def debug_ensemble(N, p, q):
    """Debug ensemble scores for true factors."""
    print(f"N = {N}")
    print(f"p = {p}, q = {q}")

    for alpha in ALPHAS:
        theta_N = theta_mod1_log(N, alpha)
        theta_p = theta_mod1_log(p, alpha)
        theta_q = theta_mod1_log(q, alpha)

        dist_p = abs(theta_N - theta_p)
        dist_q = abs(theta_q - theta_q)  # Wait, typo? theta_q - theta_N

        dist_p = min(dist_p, 1 - dist_p)
        dist_q = min(abs(theta_N - theta_q), 1 - abs(theta_N - theta_q))

        print(f"Alpha {float(alpha):.3f}: θ_N={theta_N:.3f}, θ_p={theta_p:.3f}, θ_q={theta_q:.3f}")
        print(f"  dist_p={dist_p:.3f}, dist_q={dist_q:.3f}")

    # Ensemble score
    scores_p = [min(abs(theta_mod1_log(N, alpha) - theta_mod1_log(p, alpha)), 1 - abs(theta_mod1_log(N, alpha) - theta_mod1_log(p, alpha))) for alpha in ALPHAS]
    scores_q = [min(abs(theta_mod1_log(N, alpha) - theta_mod1_log(q, alpha)), 1 - abs(theta_mod1_log(N, alpha) - theta_mod1_log(q, alpha))) for alpha in ALPHAS]

    min_score_p = min(scores_p)
    min_score_q = min(scores_q)

    print(f"\nEnsemble score p: {min_score_p:.3f} (min of {scores_p})")
    print(f"Ensemble score q: {min_score_q:.3f} (min of {scores_q})")

# Test on first sample
N, p, q = generate_semiprime(35, 42)
debug_ensemble(N, p, q)