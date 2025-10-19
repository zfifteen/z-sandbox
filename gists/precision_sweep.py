#!/usr/bin/env python3
"""
Quick Precision Sweep: Test if higher dps breaks the 34-35 bit boundary
Tests the same 35-bit semiprime with dps ∈ {50, 80, 120, 160}
Logs θ values, distances, and ranks to identify precision artifacts
"""

import csv
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import math

def set_precision(dps):
    """Set decimal precision."""
    getcontext().prec = dps
    getcontext().rounding = ROUND_HALF_EVEN

def theta_precise(N: int, k: float) -> Decimal:
    """Compute theta with current precision."""
    if N <= 0:
        return Decimal(0)
    phi = Decimal('1.61803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475408807538689175212663386222353693179318006076672635443338908659593958290563832266131692896')
    log_N = Decimal(N).ln()
    log_phi = phi.ln()
    ratio = log_N / log_phi
    powered = Decimal(k) * ratio
    exp_powered = powered.exp()
    product = phi * exp_powered
    fractional = product - product.to_integral_value()
    return fractional

def circ_dist(a: float, b: float) -> float:
    """Circular distance."""
    d = abs(a - b)
    return d if d <= 0.5 else 1.0 - d

def generate_candidates(N, window=4096):
    """Generate candidate primes around sqrt(N)."""
    import math
    sqrt_N = int(math.isqrt(N))
    start = max(2, sqrt_N - window // 2)
    end = sqrt_N + window // 2
    candidates = []
    for i in range(start, end + 1, 2):  # Odd numbers only
        if i > 1 and all(i % j != 0 for j in range(3, int(math.sqrt(i)) + 1, 2)):
            candidates.append(i)
    return candidates

def run_precision_sweep():
    """Run precision sweep on a fixed 35-bit semiprime."""
    # Fixed 35-bit semiprime for consistent testing
    N = 22170092047
    p, q = 94793, 233879  # Known factors

    print(f"Testing fixed 35-bit semiprime: N={N}")
    print(f"Known factors: p={p}, q={q}")
    print()

    dps_levels = [50, 80, 120, 160]
    results = []

    candidates = generate_candidates(N, window=4096)
    print(f"Generated {len(candidates)} candidate primes")

    for dps in dps_levels:
        print(f"\n=== Testing dps={dps} ===")
        set_precision(dps)

        # Compute theta values
        theta_N = float(theta_precise(N, 0.45))
        theta_p = float(theta_precise(p, 0.45))
        theta_q = float(theta_precise(q, 0.45))

        # Compute distances
        dist_N_p = circ_dist(theta_N, theta_p)
        dist_N_q = circ_dist(theta_N, theta_q)

        print(".6f")
        print(".6f")
        print(".6f")

        # Score candidates and find ranks
        candidate_scores = [(c, circ_dist(theta_N, float(theta_precise(c, 0.45)))) for c in candidates[:500]]  # Limit for speed
        candidate_scores.sort(key=lambda x: x[1])  # Sort by score (lower is better)

        # Find ranks of p and q
        p_rank = next((i+1 for i, (c, _) in enumerate(candidate_scores) if c == p), None)
        q_rank = next((i+1 for i, (c, _) in enumerate(candidate_scores) if c == q), None)

        print(f"True factor ranks: p={p_rank}, q={q_rank}")

        # Check if would succeed with ε=0.12
        best_dist = min(dist_N_p, dist_N_q)
        would_succeed = best_dist <= 0.12
        print(f"Best distance: {best_dist:.6f} → {'SUCCESS' if would_succeed else 'FAILED'} with ε=0.12")

        result = {
            'dps': dps,
            'theta_N': theta_N,
            'theta_p': theta_p,
            'theta_q': theta_q,
            'dist_N_p': dist_N_p,
            'dist_N_q': dist_N_q,
            'best_dist': best_dist,
            'p_rank': p_rank,
            'q_rank': q_rank,
            'would_succeed': would_succeed
        }
        results.append(result)

    # Compare across precision levels
    print(f"\n{'='*60}")
    print("PRECISION SWEEP ANALYSIS")
    print(f"{'='*60}")

    base_result = results[0]  # dps=50

    for result in results[1:]:
        dps = result['dps']
        delta_theta_N = abs(result['theta_N'] - base_result['theta_N'])
        delta_theta_p = abs(result['theta_p'] - base_result['theta_p'])
        delta_theta_q = abs(result['theta_q'] - base_result['theta_q'])
        delta_best_dist = result['best_dist'] - base_result['best_dist']

        print(f"\ndps={dps} vs dps=50:")
        print(".8f")
        print(".8f")
        print(".8f")
        print(".6f")

        # Check for significant changes
        max_delta_theta = max(delta_theta_N, delta_theta_p, delta_theta_q)
        if max_delta_theta > 0.01:
            print("  ⚠️  LARGE θ CHANGES - Potential precision artifact!")
        else:
            print("  ✅ Small θ changes - Precision stable")

        # Check rank improvements
        if result['p_rank'] and base_result['p_rank'] and result['p_rank'] < base_result['p_rank']:
            print(f"  📈 p rank improved: {base_result['p_rank']} → {result['p_rank']}")
        if result['q_rank'] and base_result['q_rank'] and result['q_rank'] < base_result['q_rank']:
            print(f"  📈 q rank improved: {base_result['q_rank']} → {result['q_rank']}")

        # Success change
        if result['would_succeed'] != base_result['would_succeed']:
            print(f"  🎯 SUCCESS STATUS CHANGED: {base_result['would_succeed']} → {result['would_succeed']}")

    # Save detailed results
    with open('precision_sweep_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['dps', 'theta_N', 'theta_p', 'theta_q', 'dist_N_p', 'dist_N_q', 'best_dist', 'p_rank', 'q_rank', 'would_succeed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDetailed results saved to precision_sweep_results.csv")

    # Final conclusion
    success_at_high_prec = any(r['would_succeed'] for r in results if r['dps'] >= 120)
    if success_at_high_prec:
        print("🎉 SUCCESS: Higher precision enables factorization - boundary is precision artifact!")
    else:
        print("❌ CONFIRMED: Boundary persists at all precisions - geometric limitation confirmed")

if __name__ == "__main__":
    run_precision_sweep()