#!/usr/bin/env python3
"""
GVA Scaling Experiment: 200-bit Semiprime Factorization

Objective: Extend GVA to 200-bit semiprimes, aiming for >0% success rate
to establish baseline feasibility for larger factorization targets.

Uses geometric embedding with Riemannian distance on torus manifold.
"""

import sympy as sp
import math
import csv
import time
import random
from datetime import datetime

def embed(n, dims=11, k=None):
    """Embed number into d-dimensional torus using golden ratio modulation."""
    phi = (1 + math.sqrt(5)) / 2
    if k is None:
        k = 0.3 / (math.log(math.log(n + 1)) / math.log(2))
    x = n / math.exp(2)
    frac = (x / phi) % 1
    return [(phi * frac ** k) % 1 for _ in range(dims)]

def riemann_dist(c1, c2, N):
    """Calculate Riemannian distance with curvature correction."""
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return math.sqrt(sum((min(abs(a - b), 1 - abs(a - b)) * (1 + kappa * 0.01))**2 for a, b in zip(c1, c2)))

def generate_200bit_semiprime(seed=None):
    """Generate a balanced 200-bit semiprime."""
    if seed:
        random.seed(seed)

    # Generate two ~100-bit primes using nextprime for better distribution
    base = 2**99  # Each prime ~100 bits, product ~200 bits
    offset = random.randint(0, 10**8)  # Large offset range
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10**6))  # More spread
    N = int(p) * int(q)

    return N, int(p), int(q)

def gva_factorize_200bit(N, max_candidates=1000, dims=11):
    """Attempt GVA factorization on 200-bit semiprime."""
    start_time = time.time()

    # Embed N
    theta_N = embed(N, dims)

    # Search around sqrt(N)
    sqrtN = int(math.sqrt(N))
    R = 1000  # Search range
    candidates = range(max(2, sqrtN - R), sqrtN + R + 1)

    # Rank candidates by Riemannian distance
    ranked_candidates = sorted(candidates, key=lambda c: riemann_dist(embed(c, dims), theta_N, N))

    # Test top candidates
    for cand in ranked_candidates[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed

    elapsed = time.time() - start_time
    return None, elapsed

def run_experiment(num_trials=100, output_csv="gva_200bit_results.csv"):
    """Run GVA scaling experiment on 100 random 200-bit semiprimes."""
    print("=== GVA 200-bit Scaling Experiment ===")
    print(f"Running {num_trials} trials on 200-bit semiprimes")
    print(f"Target: >0% success rate (at least one factorization)")
    print()

    results = []
    successes = 0
    total_time = 0

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['trial', 'N_bits', 'success', 'factor_found', 'time_seconds', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trial in range(num_trials):
            # Generate semiprime
            N, p, q = generate_200bit_semiprime(seed=12345 + trial)

            print(f"Trial {trial+1}/{num_trials}: N = {N} ({N.bit_length()} bits)")

            # Attempt factorization
            factor, elapsed = gva_factorize_200bit(N)

            success = factor is not None
            if success:
                successes += 1
                print(f"  ✓ SUCCESS: Found factor {factor} in {elapsed:.3f}s")
            else:
                print(f"  ✗ FAILED: No factor found in {elapsed:.3f}s")

            total_time += elapsed

            # Log result
            result = {
                'trial': trial + 1,
                'N_bits': N.bit_length(),
                'success': success,
                'factor_found': str(factor) if factor else None,
                'time_seconds': round(elapsed, 3),
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            writer.writerow(result)

    # Summary
    success_rate = (successes / num_trials) * 100
    avg_time = total_time / num_trials

    print()
    print("=== Results Summary ===")
    print(f"Trials: {num_trials}")
    print(f"Successes: {successes}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Time: {avg_time:.3f}s per trial")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Results saved to: {output_csv}")

    if success_rate > 0:
        print("🎉 HYPOTHESIS VERIFIED: GVA shows potential for 200-bit factorization!")
    else:
        print("❌ Hypothesis not verified: No factorizations found. Consider parameter tuning.")

    return success_rate > 0

if __name__ == "__main__":
    success = run_experiment()
    exit(0 if success else 1)