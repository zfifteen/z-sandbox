#!/usr/bin/env python3
"""
2D Torus Geometric Factorization: Lift angles to 2D for improved alignment
Uses two incommensurate rotations on the torus to reduce simultaneous misalignment.
"""

from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import math

def set_prec(prec=120):
    getcontext().prec = prec
    getcontext().rounding = ROUND_HALF_EVEN

# Torus alpha/beta pairs
TORUS_PAIRS = [
    (Decimal('1.6180339887498948'), Decimal('2.7182818284590452')),  # φ, e
    (Decimal('3.1415926535897932'), Decimal('1.4142135623730951')),  # π, √2
    (Decimal('2.4142135623730951'), Decimal('1.7320508075688772')),  # silver, √3
]

def theta_mod1_log(x: int, a: Decimal) -> float:
    """Compute {a * log(x)} for torus mapping."""
    if x <= 0:
        return 0.0
    return float((a * Decimal(x).ln()) % Decimal(1))

def circ_dist(a: float, b: float) -> float:
    """Circular distance on [0,1)."""
    d = abs(a - b)
    return d if d <= 0.5 else 1.0 - d

def circular_mean(ts):
    """Compute circular mean of angles in [0,1)."""
    if not ts:
        return 0.0
    cs = [complex(math.cos(2*math.pi*t), math.sin(2*math.pi*t)) for t in ts]
    mx = sum(c.real for c in cs) / len(cs)
    my = sum(c.imag for c in cs) / len(cs)
    mu = math.atan2(my, mx) / (2 * math.pi)
    return mu % 1.0

def residualize(values, alpha: Decimal):
    """Apply residualization: subtract circular mean."""
    ts = [theta_mod1_log(v, alpha) for v in values]
    mu = circular_mean(ts)
    res = [((t - mu) % 1.0) for t in ts]
    return mu, res

def torus_score(N: int, cand: int, window_vals, alpha: Decimal, beta: Decimal):
    """Compute 2D torus score using residualized angles."""
    # Alpha angle
    mu_a, _ = residualize(window_vals, alpha)
    tN_a = (theta_mod1_log(N, alpha) - mu_a) % 1.0
    tc_a = (theta_mod1_log(cand, alpha) - mu_a) % 1.0
    dist_a = circ_dist(tN_a, tc_a)

    # Beta angle
    mu_b, _ = residualize(window_vals, beta)
    tN_b = (theta_mod1_log(N, beta) - mu_b) % 1.0
    tc_b = (theta_mod1_log(cand, beta) - mu_b) % 1.0
    dist_b = circ_dist(tN_b, tc_b)

    # Combined score (sum of distances)
    return dist_a + dist_b, (dist_a, dist_b)

if __name__ == "__main__":
    # Simple test
    set_prec(120)

    N = 22170092047
    p, q = 94793, 233879
    window_vals = [N, p, q]

    alpha = Decimal('1.6180339887498948')  # φ
    beta = Decimal('2.7182818284590452')   # e

    score_p, _ = torus_score(N, p, window_vals, alpha, beta)
    score_q, _ = torus_score(N, q, window_vals, alpha, beta)

    print(f"Torus test: p score = {score_p:.4f}, q score = {score_q:.4f}")
    print(f"Best score: {min(score_p, score_q):.4f}")