#!/usr/bin/env python3
"""
Unit tests for 128-bit GVA: Test 100 balanced semiprimes for correctness and performance.
"""

import time
import random
import sympy
from manifold_128bit import gva_factorize_128bit, adaptive_threshold, check_balance

def generate_balanced_128bit_semiprime(seed):
    """Generate N = p * q with p, q ~2^32, balanced."""
    random.seed(seed)
    base = 2**63
    offset = random.randint(0, 10**6)
    p = sympy.nextprime(base + offset)
    q = sympy.nextprime(base + offset + random.randint(1, 10**5))  # Close to p
    N = p * q
    return N, p, q

def test_gva_128bit():
    """Test GVA on 100 samples."""
    num_tests = 100
    successes = 0
    total_time = 0
    false_positives = 0

    print("Testing 128-bit GVA on 100 balanced semiprimes...")

    for i in range(num_tests):
        N, true_p, true_q = generate_balanced_128bit_semiprime(i)

        adaptive_R = min(int(N**0.5), 10**7)
        start_time = time.time()
        result = gva_factorize_128bit(N, R=1000000)  # Use 4 cores for test
        end_time = time.time()
        elapsed = end_time - start_time
        total_time += elapsed

        if result[0]:
            found_p, found_q, dist = result
            correct = {found_p, found_q} == {true_p, true_q}
            epsilon = adaptive_threshold(N)
            if correct and dist < epsilon and elapsed < 30:
                successes += 1
            elif not correct:
                false_positives += 1
                print(f"Test {i}: Wrong factors {found_p} × {found_q}, expected {true_p} × {true_q}")
        else:
            print(f"Test {i}: No factors found")

    success_rate = successes / num_tests * 100
    avg_time = total_time / num_tests
    fp_rate = false_positives / num_tests * 100

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
    test_gva_128bit()