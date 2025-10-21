#!/usr/bin/env python3
"""
Unit tests for 256-bit GVA: Test 100 balanced semiprimes for correctness and performance.
Target precision: < 1e-16 (mpmath with dps=400 in manifold_128bit.py)
"""

import time
import random
import sympy
from manifold_256bit import gva_factorize_256bit, adaptive_threshold, check_balance

def generate_balanced_256bit_semiprime(seed):
    """Generate N = p * q with p, q ~2^127, balanced."""
    random.seed(seed)
    base = 2**127
    offset = random.randint(0, 10**9)
    p = sympy.nextprime(base + offset)
    q = sympy.nextprime(base + offset + random.randint(1, 10**6))  # Close to p
    N = p * q
    return N, p, q

def test_gva_256():
    """Test GVA on 100 samples."""
    num_tests = 100  # number of N's
    attempts_per_n = 100  # 100 * 100 = 10,000 total attempts
    successes = 0
    total_time = 0
    false_positives = 0

    print("Testing 256-bit GVA on 100 balanced semiprimes...")

    total_successes = 0
    for i in range(num_tests):
        N, true_p, true_q = generate_balanced_256bit_semiprime(i)
        successes_for_n = 0
        for attempt in range(attempts_per_n):


            adaptive_R = min(int(N**0.5), 10**7)
            start_time = time.time()
            result = gva_factorize_256bit(N)  # Use 4 cores for test
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed

            if result[0]:
                found_p, found_q, dist = result
                correct = {found_p, found_q} == {true_p, true_q}
                epsilon = adaptive_threshold(N)
                if correct and dist < epsilon and elapsed < 30:
                    successes_for_n += 1
                    total_successes += 1
                    print(f"SUCCESS on N {i}, attempt {attempt}: {found_p} × {found_q} = {N}, dist={dist:.4f}")
                    break  # stop attempts for this N
                elif not correct:
                    false_positives += 1
            else:
                pass  # no print for no factors
        if successes_for_n == 0:
            print(f"N {i}: No factors found after {attempts_per_n} attempts")

    success_rate = total_successes / num_tests * 100
    avg_time = total_time / num_tests
    fp_rate = false_positives / (num_tests * attempts_per_n) * 100

    print(f"\nResults:")
    print(f"Success rate: {successes}/{num_tests} ({success_rate:.1f}%)")
    print(f"Average time: {avg_time:.2f}s")
    print(f"False positive rate: {false_positives}/{num_tests} ({fp_rate:.1f}%)")

    # Assertions
    assert success_rate > 0, f"Success rate {success_rate:.1f}% <= 0%"
    assert avg_time < 30, f"Average time {avg_time:.2f}s >= 30s"
    assert fp_rate < 1, f"FP rate {fp_rate:.1f}% >= 1%"

    print("All assertions passed!")

if __name__ == "__main__":
    test_gva_256()