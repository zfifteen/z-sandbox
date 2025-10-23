#!/usr/bin/env python3
"""
GVA Intermediate Scale Testing: 150-180 bit Semiprimes
Tests GVA factorization on bit sizes between 128 and 200 bits to find the breaking point.
"""

import sympy as sp
import mpmath as mp
import random
import csv
import time
import math
from datetime import datetime

# Set high precision for mpmath
mp.mp.dps = 20  # Precision < 1e-16 as required

def generate_semiprime(bits, seed=None):
    """Generate a balanced semiprime of specified bit length."""
    if seed:
        random.seed(seed)

    # Create primes of roughly equal size
    half_bits = bits // 2
    # Use a base that will give us approximately the right bit length
    base = 2**(half_bits - 1)

    # Add larger random offset to get better bit length distribution
    offset = random.randint(0, 2**half_bits // 4)  # Quarter of the half range

    p = sp.nextprime(base + offset)
    # Ensure we got a valid prime
    if p is None:
        raise ValueError(f"Could not find prime near {base + offset}")

    # Ensure second prime is different and roughly same size
    q_offset = random.randint(1, 10**6)
    q = sp.nextprime(base + offset + q_offset)
    if q is None:
        raise ValueError(f"Could not find prime near {base + offset + q_offset}")

    N = int(p) * int(q)
    return N, int(p), int(q)

def embed(n, dims=13, k=None):
    """Enhanced embedding function using mpmath for high precision."""
    phi = mp.mpf((1 + mp.sqrt(5)) / 2)  # Golden ratio with high precision

    if k is None:
        # Adaptive k based on number magnitude
        k = mp.mpf('0.3') / (mp.log(mp.log(n + 1)) / mp.log(2))

    x = mp.mpf(n) / mp.exp(2)
    frac = mp.frac(x / phi)  # Fractional part only

    # Generate d-dimensional embedding
    embedding = []
    for _ in range(dims):
        coord = mp.frac(phi * frac ** k)  # Fractional part
        embedding.append(float(coord))  # Convert to float for compatibility

    return embedding

def riemann_dist(c1, c2, N):
    """Calculate Riemannian distance with curvature correction."""
    kappa = 4 * math.log(N + 1) / math.exp(2)

    # Convert back to mpmath for precision in distance calculation
    c1_mp = [mp.mpf(x) for x in c1]
    c2_mp = [mp.mpf(x) for x in c2]

    squared_diffs = []
    for a, b in zip(c1_mp, c2_mp):
        # Minimum distance on torus
        diff = min(abs(a - b), 1 - abs(a - b))
        # Apply curvature correction
        corrected_diff = diff * (1 + kappa * 0.01)
        squared_diffs.append(corrected_diff ** 2)

    return math.sqrt(sum(float(x) for x in squared_diffs))

def gva_factorize(N, bits, max_candidates=1000, dims=13, search_range=10000):
    """Attempt GVA factorization with enhanced precision."""
    start_time = time.time()

    # Embed target number
    theta_N = embed(N, dims)

    # Generate candidate range around sqrt(N)
    sqrtN = int(math.sqrt(N))
    candidates = range(max(2, sqrtN - search_range), sqrtN + search_range + 1)

    # Rank candidates by Riemannian distance
    ranked_candidates = sorted(candidates,
        key=lambda c: riemann_dist(embed(c, dims), theta_N, N))

    # Test top candidates
    for cand in ranked_candidates[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed

    elapsed = time.time() - start_time
    return None, elapsed

def run_intermediate_scale_test():
    """Run GVA tests across intermediate bit sizes."""

    print("=== GVA Intermediate Scale Testing ===")
    print("Testing bit sizes: 150, 160, 170, 180")
    print("100 trials per bit size, dims=13, search_range=10000")
    print("Target: Find GVA breaking point between 128-200 bits")
    print()

    # Test parameters
    bits_range = [150, 160, 170, 180]
    trials_per_bits = 100
    dims = 13
    search_range = 10000

    # Results storage
    all_results = []

    # CSV output file
    csv_filename = "gva_intermediate_scale_results.csv"

    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['bits', 'trial', 'N', 'p', 'q', 'success', 'factor_found',
                     'time_seconds', 'dims', 'search_range', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Test each bit size
        for bits in bits_range:
            print(f"Testing {bits}-bit semiprimes...")
            successes = 0
            total_time = 0

            for trial in range(trials_per_bits):
                # Generate semiprime
                N, p, q = generate_semiprime(bits, seed=12345 + trial)

                # Verify bit length
                actual_bits = N.bit_length()
                if actual_bits != bits:
                    print(f"  Warning: Generated {actual_bits}-bit number instead of {bits}-bit")

                # Attempt factorization
                factor, elapsed = gva_factorize(N, bits, dims=dims, search_range=search_range)

                # Check success
                success = factor is not None and factor in (p, q)
                if success:
                    successes += 1

                total_time += elapsed

                # Log result
                result = {
                    'bits': bits,
                    'trial': trial + 1,
                    'N': str(N),
                    'p': str(p),
                    'q': str(q),
                    'success': success,
                    'factor_found': str(factor) if factor else None,
                    'time_seconds': round(elapsed, 3),
                    'dims': dims,
                    'search_range': search_range,
                    'timestamp': datetime.now().isoformat()
                }
                all_results.append(result)
                writer.writerow(result)

                # Progress indicator
                if (trial + 1) % 10 == 0:
                    print(f"  Trial {trial+1}/{trials_per_bits}: {successes} successes so far")

            # Summary for this bit size
            success_rate = (successes / trials_per_bits) * 100
            avg_time = total_time / trials_per_bits

            print(f"  {bits} bits: {successes}/{trials_per_bits} successes ({success_rate:.1f}%)")
            print(".3f")
            print()

    # Overall summary
    print("=== Overall Results ===")

    for bits in bits_range:
        bits_results = [r for r in all_results if r['bits'] == bits]
        successes = sum(1 for r in bits_results if r['success'])
        success_rate = (successes / len(bits_results)) * 100 if bits_results else 0
        print(".1f")

    print(f"\nResults saved to: {csv_filename}")

    # Check if any successes found
    total_successes = sum(1 for r in all_results if r['success'])
    if total_successes > 0:
        print(f"✅ SUCCESS: Found {total_successes} factorizations across all bit sizes!")
        print("   GVA shows potential at intermediate scales.")
    else:
        print("❌ NO SUCCESS: GVA failed on all intermediate bit sizes (150-180).")
        print("   Breaking point may be at or below 150 bits.")

    return total_successes > 0

if __name__ == "__main__":
    success = run_intermediate_scale_test()
    exit(0 if success else 1)