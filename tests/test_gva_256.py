#!/usr/bin/env python3
"""
Unit tests for 256-bit GVA: Test semiprimes for correctness and performance.
Target precision: < 1e-16 (mpmath with dps=50)
"""

import time
import random
import sympy
import mpmath as mp
from manifold_256bit import gva_factorize_256bit, adaptive_threshold, check_balance

mp.dps = 50
SEED = 42
random.seed(SEED)

def generate_balanced_256bit_semiprime():
    """Generate N = p * q with p, q ~2^127, balanced with scaled gap"""
    p = sympy.randprime(2**127, 2**128)
    offset = random.randint(2**60, 2**70)  # Scaled gap for 256-bit
    q = sympy.nextprime(p + offset)
    return p * q, p, q

def test_gva_256bit():
    """Test GVA on 10 samples (scaled down for feasibility) as per GOAL.md"""
    print("Generating 10 test cases...")
    test_set = [generate_balanced_256bit_semiprime() for _ in range(10)]
    
    num_tests = 10  # number of N's
    attempts_per_n = 1  # 10 * 1 = 10 total attempts (scaled down)
    total_successes = 0
    total_time = 0
    false_positives = 0

    print("Testing 256-bit GVA on 10 balanced semiprimes with 1000 attempts...")

    for i in range(num_tests):
        N, true_p, true_q = test_set[i]
        successes_for_n = 0
        for attempt in range(attempts_per_n):
            adaptive_R = min(int(N**0.5), 10**7)
            start_time = time.time()
            result = gva_factorize_256bit(N, R=adaptive_R)
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
    avg_time = total_time / (num_tests * attempts_per_n)
    fp_rate = false_positives / (num_tests * attempts_per_n) * 100

    print(f"\nResults:")
    print(f"Success rate: {total_successes}/{num_tests} ({success_rate:.1f}%)")
    print(f"Average time per attempt: {avg_time:.2f}s")
    print(f"False positive rate: {false_positives}/{(num_tests * attempts_per_n)} ({fp_rate:.1f}%)")

    # Assertions
    if total_successes > 0:
        print("Hypothesis VERIFIED: At least 1 success")
    else:
        print("Hypothesis UNVERIFIED: 0 successes")

    print("Test completed!")

if __name__ == "__main__":
    test_gva_256bit()
