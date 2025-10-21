#!/usr/bin/env python3
"""
Test script for 35-bit factorization attempts.
"""

import sys
sys.path.append('gists')

from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams

def test_35bit(samples=5, seed=42):
    """Test factorization on 35-bit semiprimes."""
    print("Testing 35-bit semiprime factorization")
    print("=" * 50)

    successes = 0
    total_attempts = 0

    for i in range(samples):
        sample_seed = seed + i
        N, p, q = generate_semiprime(35, sample_seed)
        print(f"\nSample {i+1}: N = {N} ({N.bit_length()} bits)")
        print(f"True factors: {p} × {q}")

        params = FactorizationParams(max_time=60.0, use_ensemble=False)
        try:
            result = geometric_factor(N, params)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        if result is None:
            print("  ERROR: result is None")
            continue

        total_attempts += result.attempts

        if result.success:
            successes += 1
            print(f"✓ SUCCESS: {result.factors[0]} × {result.factors[1]}")
        else:
            print(f"✗ FAILED after {result.attempts} attempts")

        print(f"  Time: {result.timings.get('total', 0):.3f}s")

        # Show best filtering
        if result.logs:
            filtered_logs = [log for log in result.logs if log.get('post_filter', 0) > 0]
            if filtered_logs:
                best_log = min(filtered_logs, key=lambda x: x['post_filter'])
                print(f"Best filter: {best_log['pre_filter']} → {best_log['post_filter']} (k={best_log['k']:.3f}, ε={best_log['epsilon']:.3f})")

    success_rate = successes / samples if samples > 0 else 0
    avg_attempts = total_attempts / samples if samples > 0 else 0

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Samples: {samples}")
    print(f"Successes: {successes}")
    print(f"Success rate: {success_rate*100:.1f}%")
    print(f"Avg attempts: {avg_attempts:.1f}")

    return success_rate, avg_attempts

if __name__ == '__main__':
    test_35bit()