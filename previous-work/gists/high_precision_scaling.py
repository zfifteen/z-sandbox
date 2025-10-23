#!/usr/bin/env python3
"""
High-Precision Scaling for Geometric Factorization
Adapted from golden-ratio-spiral C implementation using mpmath for arbitrary precision
"""

import mpmath as mp
from decimal import Decimal
import math

# Set ultra-high precision
mp.mp.dps = 200  # 200 decimal places
mp.mp.prec = 200 * 4  # bits of precision

# Constants
PHI = mp.mpf('1.61803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475408807538689175212663386222353693179318006076672635443338908659593958290563832266131692896')
GOLDEN_ANGLE = 2 * mp.pi / (PHI ** 2)
PI = mp.pi

def theta_ultra_high_precision(N: int, k: float) -> mp.mpf:
    """Ultra-high precision theta using mpmath (equivalent to MPFR)."""
    if N <= 0:
        return mp.mpf(0)

    # Use mpmath for arbitrary precision
    N_mp = mp.mpf(N)
    phi_mp = PHI
    k_mp = mp.mpf(k)

    # Compute {φ × (N/φ)^k} with maximum precision
    ratio = N_mp / phi_mp
    powered = mp.power(ratio, k_mp)
    product = phi_mp * powered
    fractional = product - mp.floor(product)

    return fractional

def golden_ratio_scale(current_order: int) -> tuple:
    """Predict next order using golden ratio scaling (from C implementation)."""
    current = mp.mpf(current_order)
    scaling_factor = PHI

    # Simple prediction: next ≈ current × φ
    predicted_next = current * scaling_factor

    # Could add historical adjustment here (simplified)
    adjustment = mp.mpf(0)  # Placeholder

    return predicted_next, scaling_factor, adjustment

def calculate_spiral_coordinates(iteration: int, center: float, r_scale: float, s_scale: float):
    """Calculate golden angle spiral coordinates (from C implementation)."""
    angle = iteration * float(GOLDEN_ANGLE)
    r = r_scale * math.sqrt(iteration)
    s = s_scale * math.sqrt(iteration)

    x = r * math.cos(angle) + center
    y = s * math.sin(angle)

    return x, y

def curvature_kappa(n: int) -> float:
    """Calculate curvature κ(n) for primality filtering (from C implementation)."""
    # Simplified version - in C it's more complex
    # κ(n) is an empirical measure based on number theory properties
    if n < 2:
        return 1.0

    # Basic approximation - lower values suggest higher primality likelihood
    log_n = math.log(n)
    kappa = 0.0

    # Simple heuristic based on digit patterns and basic properties
    digits = str(n)
    digit_sum = sum(int(d) for d in digits)

    # Combine various number-theoretic properties
    kappa += abs(math.sin(n / 100.0)) * 0.1
    kappa += (digit_sum / len(digits)) / 10.0
    kappa += abs(n % 30) / 30.0  # Modulo small composites

    return kappa

def is_potential_candidate_mpmath(n: int) -> bool:
    """Check if candidate passes basic filters (adapted from C)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Small prime checks
    small_primes = [3, 5, 7, 11, 13]
    for p in small_primes:
        if n % p == 0 and n != p:
            return False

    # Curvature check
    kappa = curvature_kappa(n)
    if kappa >= 1.0:
        return False

    return True

def adaptive_spiral_search(center: int, bit_size: int, max_candidates: int = 1000):
    """Adaptive spiral search with scaling based on bit size."""
    candidates = []

    # Adaptive parameters based on bit size
    if bit_size <= 30:
        r_scale = s_scale = 1.0
        max_iter = 1000
    elif bit_size <= 40:
        r_scale = s_scale = 2.0
        max_iter = 2000
    else:
        r_scale = s_scale = 4.0
        max_iter = 5000

    for i in range(1, max_iter + 1):
        x, y = calculate_spiral_coordinates(i, center, r_scale, s_scale)

        # Convert to integer candidate
        candidate = int(round(x))

        if candidate > 1 and is_potential_candidate_mpmath(candidate):
            candidates.append(candidate)

        if len(candidates) >= max_candidates:
            break

    return candidates

def test_high_precision_scaling():
    """Test the high-precision scaling on boundary cases."""
    print("Testing high-precision geometric factorization scaling...")

    # Test cases
    test_cases = [
        (34, True),   # 34-bit success case
        (35, False),  # 35-bit failure case
        (40, False),  # 40-bit failure case
    ]

    for bit_size, expected_success in test_cases:
        print(f"\n=== Testing {bit_size}-bit case ===")

        # Generate test number
        N = (1 << bit_size) - 1  # Mersenne-like for testing

        # High-precision theta
        theta_hp = theta_ultra_high_precision(N, 0.45)
        print(f"Ultra-high precision θ({N}, 0.45) = {float(theta_hp):.10f}")

        # Compare with standard precision
        theta_std = float(Decimal(N) ** Decimal(0.45) * PHI % Decimal(1))
        print(f"Standard precision θ = {theta_std:.10f}")
        print(f"Difference: {abs(float(theta_hp) - theta_std):.2e}")

        # Adaptive spiral search
        sqrt_N = int(math.sqrt(N))
        candidates = adaptive_spiral_search(sqrt_N, bit_size, max_candidates=50)
        print(f"Adaptive spiral found {len(candidates)} candidates around √{N}")

        # Test geometric filtering with high precision
        k, epsilon = 0.45, 0.12
        filtered = []
        for cand in candidates:
            theta_cand_hp = theta_ultra_high_precision(cand, k)
            dist = min(abs(float(theta_hp) - float(theta_cand_hp)),
                      1 - abs(float(theta_hp) - float(theta_cand_hp)))
            if dist <= epsilon:
                filtered.append(cand)

        print(f"Geometric filtering: {len(candidates)} → {len(filtered)} candidates")
        print(f"Success prediction: {'YES' if len(filtered) > 0 else 'NO'}")

if __name__ == "__main__":
    test_high_precision_scaling()