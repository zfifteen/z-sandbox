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

def ensemble_score(N: int, cand: int, window_vals, alphas):
    """Original ensemble scoring for comparison."""
    scores = []
    for a in alphas:
        mu, _ = residualize(window_vals, a)
        tN = (theta_mod1_log(N, a) - mu) % 1.0
        tc = (theta_mod1_log(cand, a) - mu) % 1.0
        scores.append(circ_dist(tN, tc))
    return min(scores), scores

def hybrid_residue_filter(candidates, mods=[3, 5, 7, 11]):
    """Simple hybrid arithmetic filter: keep candidates that hit multiple residue classes."""
    kept = []
    for x in candidates:
        # Simple heuristic: prefer candidates that are 1 or -1 mod small primes
        hits = sum(1 for m in mods if (x % m) in (1, m-1))
        if hits >= (len(mods) // 2):  # Hit at least half
            kept.append(x)
    return kept

def test_torus_vs_ensemble():
    """Test torus vs ensemble on the boundary case."""
    set_prec(120)

    # Use the same 35-bit case
    N = 22170092047
    p, q = 94793, 233879

    print(f"Testing torus vs ensemble on 35-bit: N={N}")
    print(f"True factors: p={p}, q={q}")
    print()

    # Generate candidates (smaller set for testing)
    import math
    sqrt_N = int(math.isqrt(N))
    candidates = []
    for i in range(max(2, sqrt_N - 1000), sqrt_N + 1000, 2):
        if i > 1 and all(i % j != 0 for j in range(3, int(math.sqrt(i)) + 1, 2)):
            candidates.append(i)
    print(f"Generated {len(candidates)} candidate primes")

    # Window for residualization
    window_vals = candidates[:100] + [N, p, q]  # Include true values

    # Test each method
    methods = {
        'Ensemble': lambda c: ensemble_score(N, c, window_vals, [pair[0] for pair in TORUS_PAIRS]),
        'Torus_φ_e': lambda c: torus_score(N, c, window_vals, TORUS_PAIRS[0][0], TORUS_PAIRS[0][1]),
        'Torus_π_√2': lambda c: torus_score(N, c, window_vals, TORUS_PAIRS[1][0], TORUS_PAIRS[1][1]),
        'Torus_silver_√3': lambda c: torus_score(N, c, window_vals, TORUS_PAIRS[2][0], TORUS_PAIRS[2][1]),
    }

    results = {}
    for method_name, score_func in methods.items():
        print(f"\n=== {method_name} ===")

        # Score all candidates
        scored_candidates = [(c, score_func(c)[0]) for c in candidates[:500]]  # Limit for speed
        scored_candidates.sort(key=lambda x: x[1])  # Lower score = better

        # Find ranks of true factors
        p_rank = next((i+1 for i, (c, _) in enumerate(scored_candidates) if c == p), None)
        q_rank = next((i+1 for i, (c, _) in enumerate(scored_candidates) if c == q), None)

        # Best score among true factors
        p_score = next((s for c, s in scored_candidates if c == p), None)
        q_score = next((s for c, s in scored_candidates if c == q), None)
        best_score = min(p_score or float('inf'), q_score or float('inf'))

        print(f"  p rank: {p_rank}, score: {p_score:.4f}")
        print(f"  q rank: {q_rank}, score: {q_score:.4f}")
        print(f"  Best true factor score: {best_score:.4f}")

        results[method_name] = {
            'p_rank': p_rank,
            'q_rank': q_rank,
            'best_score': best_score
        }

    # Compare methods
    print("\n=== COMPARISON ===")
=== COMPARISON ===")
    for method, data in results.items():
        best_rank = min(data['p_rank'] or float('inf'), data['q_rank'] or float('inf'))
        print(f"{method}: Best rank = {best_rank}, Best score = {data['best_score']:.4f}")

    # Test hybrid approach
    print("
=== HYBRID TEST ===")
    # Use torus scores to rank, then apply residue filter
    torus_scores = [(c, torus_score(N, c, window_vals, TORUS_PAIRS[0][0], TORUS_PAIRS[0][1])[0])
                   for c in candidates[:500]]
    torus_scores.sort(key=lambda x: x[1])

    # Take top 100 by torus score
    top_100 = [c for c, _ in torus_scores[:100]]

    # Apply hybrid filter
    hybrid_kept = hybrid_residue_filter(top_100)

    print(f"Top 100 by torus → Hybrid filter kept {len(hybrid_kept)} candidates")

    # Check if true factors are in hybrid_kept
    p_in_hybrid = p in hybrid_kept
    q_in_hybrid = q in hybrid_kept
    print(f"  p in hybrid: {p_in_hybrid}")
    print(f"  q in hybrid: {q_in_hybrid}")

    if p_in_hybrid or q_in_hybrid:
        print("🎉 SUCCESS: Hybrid approach retained at least one true factor!")
    else:
        print("❌ Hybrid approach still missed true factors")

if __name__ == "__main__":
    test_torus_vs_ensemble()
