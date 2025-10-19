#!/usr/bin/env python3
"""
Benchmark script to find the highest bit size factorable in ≤30 seconds.
Tests semiprimes from 28-bit upwards until success rate drops to 0%.
"""

from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams
import time

def test_bit_size(bit_size, num_tests=5, max_time=30.0):
    """Test factorization success for a given bit size."""
    print(f"\n{'='*60}")
    print(f"Testing {bit_size}-bit semiprimes ({num_tests} samples, {max_time}s limit)")
    print(f"{'='*60}")

    successes = 0
    total_time = 0.0
    attempts_list = []

    for i in range(num_tests):
        # Generate semiprime
        N, p, q = generate_semiprime(bit_size, seed=1000 + bit_size * 100 + i)
        print(f"  Sample {i+1}: N={N} ({p}×{q})")

        # Factor with time limit
        params = FactorizationParams(
    max_time=max_time, 
    max_attempts=10000000, 
    search_window=4096, 
    spiral_iters=5000,
    k_list=[0.1, 0.2, 0.3, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9],
    eps_list=[0.01, 0.02, 0.05, 0.1, 0.15]
)
        start_time = time.time()
        result = geometric_factor(N, params)
        elapsed = time.time() - start_time

        total_time += elapsed
        attempts_list.append(result.attempts)

        if result.success:
            successes += 1
            status = "✓"
            print(f"    {status} SUCCESS: {result.attempts} attempts, {elapsed:.3f}s")
        else:
            status = "✗"
            print(f"    {status} FAILED: {result.attempts} attempts, {elapsed:.3f}s")

    success_rate = successes / num_tests
    avg_time = total_time / num_tests
    avg_attempts = sum(attempts_list) / len(attempts_list)

    print(f"\n  Results: {successes}/{num_tests} = {success_rate*100:.1f}% success")
    print(f"  Avg time: {avg_time:.3f}s")
    print(f"  Avg attempts: {avg_attempts:.1f}")

    return success_rate > 0, success_rate, avg_time

def find_max_bit_size(start_bit=28, max_time=30.0):
    """Find the highest bit size with >0% success in max_time seconds."""
    print("BENCHMARK: Finding highest bit size factorable in ≤30 seconds")
    print("="*70)

    max_successful_bit = 0

    for bit_size in range(start_bit, 50):  # Up to 50 bits as safety limit
        has_success, success_rate, avg_time = test_bit_size(bit_size, num_tests=3, max_time=max_time)

        if has_success:
            max_successful_bit = bit_size
            print(f"  → {bit_size}-bit: SUCCESS ({success_rate*100:.1f}%) - Continuing...")
        else:
            print(f"  → {bit_size}-bit: NO SUCCESS - Continuing...")

    print(f"\n{'='*70}")
    print("FINAL RESULT:")
    print(f"Highest bit size factorable in ≤{max_time} seconds: {max_successful_bit}-bit")
    print(f"{'='*70}")

    return max_successful_bit

if __name__ == "__main__":
    max_bit = find_max_bit_size()
    print(f"\nBenchmark complete. Maximum factorable bit size: {max_bit}")