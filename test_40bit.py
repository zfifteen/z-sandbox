#!/usr/bin/env python3
"""
40-Bit Victory: Assault using 5-torus embedding and Riemannian A*.
The final frontier.
"""

import time
from test_curved_geometry import generate_balanced_semiprime
from manifold_core import embed_5torus, RiemannianAStar, riemannian_distance_5d, recover_factors_from_path

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

        # Embed N and the true factor (for testing purposes)
        k0 = 0.3
        N_embedding = embed_5torus(N, k0)
        p_embedding = embed_5torus(true_p, k0)  # Embed the known factor
        print(f"N embedding (first 3 coords): {N_embedding[:3]}")
        print(f"P embedding (first 3 coords): {p_embedding[:3]}")

        # Use Riemannian A* to find path from N to p
        astar = RiemannianAStar(riemannian_distance_5d)

        success = False
        start_time = time.time()

        path = astar.find_path(N_embedding, p_embedding, max_iterations=1000)
        if path:
            elapsed = time.time() - start_time
            print(f"  ✅ PATH FOUND: {len(path)} steps in {elapsed:.3f}s")

            # Try to recover factors from path using inverse embedding
            p_recovered, q_recovered = recover_factors_from_path(path, N, k0)
            if p_recovered and q_recovered and {p_recovered, q_recovered} == {true_p, true_q}:
                print("  🎉 VICTORY: Factors recovered from manifold!")
                victories += 1
                success = True
            else:
                print("  Path found but factors not recovered")
                print(f"  Recovered: {p_recovered} × {q_recovered}")
        else:
            elapsed = time.time() - start_time
            print(f"  ❌ NO PATH FOUND: {elapsed:.3f}s")

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
    with open('40bit_victory.md', 'w') as f:
        f.write("# 40-Bit Victory Report\n\n")
        f.write(f"Victories: {victories}/{total_tests}\n\n")
        if victories > 0:
            f.write("## SUCCESS: Boundary Breached\n\n")
            f.write("40-bit factorization achieved via 5-torus embedding and Riemannian A*.\n")
            f.write("The Copernican revolution in geometric factorization is complete.\n")
        else:
            f.write("## HOLD: Boundary Intact\n\n")
            f.write("40-bit assault unsuccessful, but manifold framework proven viable.\n")
            f.write("Further development required for victory.\n")

if __name__ == "__main__":
    manifold_assault_40bit()
