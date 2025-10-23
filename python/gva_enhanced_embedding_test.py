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
        k = mp.mpf('0.3') / mp.log(mp.log(n + 1), 2)

    x = mp.mpf(n) / mp.exp(2)
    frac = mp.frac(x / phi)  # Fractional part only

    # Generate d-dimensional embedding
    embedding = []
    for _ in range(dims):
        coord = mp.frac(phi * frac ** k)  # Fractional part
        embedding.append(float(coord))  # Convert to float for compatibility

    return embedding
    
def embed_alt(n, dims=13, base='phi', k=None):
    """Enhanced embedding with alternative base constants."""
    base_val = {'phi': (1 + mp.sqrt(5)) / 2, 'sqrt2': mp.sqrt(2), 'pi': mp.pi}[base]
    
    if k is None:
        # Adaptive k with magnitude scaling
        k = mp.mpf('0.3') / mp.log(mp.log(n + 1), 2) * mp.log10(n) / 100
    
    x = mp.mpf(n) / mp.exp(2)
    frac = mp.frac(x / base_val)
    
    embedding = []
    for _ in range(dims):
        coord = mp.frac(base_val * frac ** k)
        embedding.append(float(coord))
    
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
    theta_N = embed_alt(N, dims, 'phi')

    # Generate candidate range around sqrt(N)
    sqrtN = int(math.sqrt(N))
    candidates = range(max(2, sqrtN - search_range), sqrtN + search_range + 1)

    # Rank candidates by Riemannian distance
    ranked_candidates = sorted(candidates,
        key=lambda c: riemann_dist(embed_alt(c, dims, 'phi'), theta_N, N))

    # Test top candidates
    for cand in ranked_candidates[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed

    elapsed = time.time() - start_time
    return None, elapsed

def gva_factorize_alt(N, base='phi', dims=13, search_range=10000):
    """GVA factorization with alternative embedding base."""
    start_time = time.time()
    
    theta_N = embed_alt(N, dims, base)
    sqrtN = int(math.sqrt(N))
    candidates = range(max(2, sqrtN - search_range), sqrtN + search_range + 1)
    
    ranked = sorted(candidates, key=lambda c: riemann_dist(embed_alt(c, dims, base), theta_N, N))
    
    for cand in ranked[:1000]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed
    
    elapsed = time.time() - start_time
    return None, elapsed

def run_enhanced_embedding_test():
    """Test alternative embedding bases on 200-bit semiprimes."""

    print("=== GVA Enhanced Embedding Testing ===")
    print("Testing bases: phi, sqrt2, pi")
    print("100 trials per base on 200-bit semiprimes")
    print("Target: Success rate >0% for any base")
    print()

    # Test parameters
    bases = ['phi', 'sqrt2', 'pi']
    trials_per_base = 100
    dims = 13
    search_range = 10000

    # Results storage
    all_results = []

    # CSV output file
    csv_filename = "gva_enhanced_embedding_results.csv"

    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['base', 'trial', 'N', 'p', 'q', 'success', 'factor_found',
                     'time_seconds', 'dims', 'search_range', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Test each bit size
        for base in bases:
            print(f"Testing base: {base}")
            successes = 0
            total_time = 0

            for trial in range(trials_per_base):
                # Generate semiprime
                N, p, q = generate_semiprime(200, seed=12345 + trial)

                # Verify bit length
                #
                #
                    #

                # Attempt factorization
                factor, elapsed = gva_factorize_alt(N, base=base, dims=dims, search_range=search_range)

                # Check success
                success = factor is not None and factor in (p, q)
                if success:
                    successes += 1

                total_time += elapsed

                # Log result
                result = {
                    'base': base,
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
                    print(f"  Trial {trial+1}/{trials_per_base}: {successes} successes so far")

            # Summary for this bit size
            success_rate = (successes / trials_per_base) * 100
            avg_time = total_time / trials_per_base

            print(f"  {base}: {successes}/{trials_per_base} successes ({success_rate:.1f}%)")
            print(".3f")
            print()

    # Overall summary
    print("=== Overall Results ===")

    for base in bases:
        base_results = [r for r in all_results if r['base'] == base]
        successes = sum(1 for r in base_results if r['success'])
        success_rate = (successes / len(base_results)) * 100 if base_results else 0
        print(".1f")

    print(f"\nResults saved to: {csv_filename}")

    # Check if any successes found
    total_successes = sum(1 for r in all_results if r['success'])
    if total_successes > 0:
        print(f"✅ SUCCESS: Found {total_successes} factorizations with enhanced embeddings!")
        print("   GVA shows potential at intermediate scales.")
    else:
        print("❌ NO SUCCESS: All embedding bases failed on 200-bit semiprimes.")
        print("   Consider hybrid approach (Proposal 3) or further embedding refinements.")

    return total_successes > 0

if __name__ == "__main__":
    success = run_enhanced_embedding_test()
    exit(0 if success else 1)