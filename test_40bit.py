#!/usr/bin/env python3
"""
40-Bit Victory: Assault using 5-torus embedding and Riemannian A*.
The final frontier.
"""

import time
from test_curved_geometry import generate_balanced_semiprime
from manifold_core import manifold_factorize

def manifold_assault_40bit():
    """Launch 40-bit assault with manifold methods and inverse embedding."""
    print("=== 40-Bit Victory: Manifold Assault ===\n")
    print("Method: 5-Torus Embedding + Riemannian A* + Inverse Embedding\n")

    # Test cases
    test_cases = [
        (40, 200, "40-bit primary assault"),
        (40, 250, "40-bit secondary assault"),
    ]

    victories = 0
    total_tests = len(test_cases)

    for i, (bits, seed, desc) in enumerate(test_cases):
        print(f"Assault {i+1}: {desc}")
        N, true_p, true_q = generate_balanced_semiprime(bits, seed)
        print(f"N = {N} ({N.bit_length()} bits)")
        print(f"Target factors: {true_p} × {true_q}")

        start_time = time.time()
        result = manifold_factorize(N, k0=0.3, max_attempts=20)        if result and result[0] is not None:            p, q = result        else:            p, q = None, None
        elapsed = time.time() - start_time

        if p and q and {p, q} == {true_p, true_q}:
            print(f"  🎉 VICTORY: {p} × {q} = {p*q} in {elapsed:.3f}s")
            victories += 1
        else:
            print(f"  ❌ NO VICTORY: {elapsed:.3f}s elapsed")

        print("-" * 80)

    print("=== FINAL ASSAULT SUMMARY ===")
    print(f"Victories: {victories}/{total_tests}")
    if victories > 0:
        print("🎉 BREAKTHROUGH: 40-bit boundary breached via manifold!")
        print("The revolution is complete.")
    else:
        print("❌ Boundary holds, but manifold foundation established.")
        print("Further refinement needed for victory.")

    # Log results
    with open('40bit_factorized.txt', 'w') as f:
        f.write("40-Bit Factorization Results\n")
        f.write("=" * 50 + "\n")
        for i, (bits, seed, desc) in enumerate(test_cases):
            N, true_p, true_q = generate_balanced_semiprime(bits, seed)
            f.write(f"Case {i+1}: {desc}\n")
            f.write(f"N = {N}\n")
            f.write(f"True factors: {true_p} × {true_q}\n")
            f.write(f"Result: {'SUCCESS' if victories > i else 'FAILED'}\n")
            f.write("-" * 30 + "\n")

if __name__ == "__main__":
    manifold_assault_40bit()
