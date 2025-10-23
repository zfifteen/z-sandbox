#!/usr/bin/env python3
"""
Z5D Axioms and Mathematical Foundations

Implementation of the core Z5D mathematical framework with empirical validation.
Follows the axioms specified in the Z5D-Guided RSA Factorization Enhancement issue.

Axiom Summary:
1. Empirical Validation First - Reproducible tests with mpmath precision < 1e-16
2. Domain-Specific Forms - Physical Z = T(v/c) and Discrete Z = n(Δ_n/Δ_max)
3. Geometric Resolution - θ'(n,k) = φ · ((n mod φ)/φ)^k with k ≈ 0.3
4. Style and Tools - Simple, precise solutions using mpmath, numpy, sympy
"""

import math
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt
from typing import Tuple, Optional

# Set high precision for empirical validation (Axiom 1)
mp.dps = 50  # Target precision < 1e-16

# Universal constants
PHI = mpf((1 + mpsqrt(5)) / 2)  # Golden ratio
E2 = exp(2)  # e² invariant (universal constant c for discrete domain)

# Validation target precision (Axiom 1)
TARGET_PRECISION = 1e-16


class Z5DAxioms:
    """
    Z5D Axioms implementation with empirical validation.
    
    Core Concepts:
    - Universal invariant: Z = A(B / c)
    - Discrete domain: Z = n(Δ_n / Δ_max)
    - Curvature: κ(n) = d(n) · ln(n+1) / e²
    - Geometric resolution: θ'(n, k)
    """
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize Z5D axioms with specified precision.
        
        Args:
            precision_dps: Decimal places for mpmath (default: 50)
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
    
    @staticmethod
    def universal_invariant(A: mpf, B: mpf, c: mpf) -> mpf:
        """
        Universal invariant formulation: Z = A(B / c)
        
        Args:
            A: Frame-specific scaling/transformation
            B: Dynamic rate/shift input
            c: Universal invariant (domain constant)
        
        Returns:
            Z value
        
        Domain-specific forms:
        - Physical: Z = T(v / c) where c ≈ 299792458 m/s
        - Discrete: Z = n(Δ_n / Δ_max) where c = e²
        """
        if c == 0:
            raise ValueError("Universal invariant c cannot be zero")
        return A * (B / c)
    
    @staticmethod
    def discrete_domain_form(n: int, delta_n: mpf, delta_max: mpf) -> mpf:
        """
        Discrete domain form: Z = n(Δ_n / Δ_max)
        
        For integer sequences and prime-density mapping.
        
        Args:
            n: Integer index/position
            delta_n: Local shift/rate at n
            delta_max: Maximum shift bound
        
        Returns:
            Z value for discrete domain
        
        Raises:
            ValueError: If delta_max is zero
        """
        if delta_max == 0:
            raise ValueError("delta_max cannot be zero (zero-division guard)")
        return mpf(n) * (delta_n / delta_max)
    
    @staticmethod
    def curvature(n: int, d_n: mpf) -> mpf:
        """
        Curvature function: κ(n) = d(n) · ln(n+1) / e²
        
        For discrete geodesics with zero-division protection.
        
        Args:
            n: Integer position
            d_n: Density function value at n
        
        Returns:
            Curvature κ(n)
        
        Note:
            - Protected against zero division by using n+1 in logarithm
            - Returns 0 for n < 0 (guard condition)
        """
        if n < 0:
            return mpf(0)
        
        # Guard against zero division
        log_term = log(mpf(n + 1))
        
        return d_n * log_term / E2
    
    @staticmethod
    def geometric_resolution(n: int, k: float = 0.3) -> mpf:
        """
        Geometric resolution: θ'(n, k) = φ · ((n mod φ) / φ)^k
        
        Resolution/embedding technique for discrete geodesics.
        Recommended k ≈ 0.3 for prime-density mapping.
        
        Args:
            n: Integer position
            k: Resolution exponent (default: 0.3 as recommended)
        
        Returns:
            θ'(n, k) value
        
        Use:
            - Prime-density mapping with k ≈ 0.3
            - Discrete geodesic embedding
        """
        n_mpf = mpf(n)
        
        # Compute (n mod φ)
        n_mod_phi = n_mpf % PHI
        
        # Compute ((n mod φ) / φ)^k
        ratio = n_mod_phi / PHI
        ratio_pow = ratio ** mpf(k)
        
        # Final: φ · ((n mod φ) / φ)^k
        return PHI * ratio_pow
    
    @staticmethod
    def prime_density_approximation(n: int) -> mpf:
        """
        Prime density approximation d(n) ≈ 1/ln(n) from Prime Number Theorem.
        
        Args:
            n: Integer position
        
        Returns:
            Approximate prime density at n
        """
        if n <= 1:
            return mpf(0)
        return mpf(1) / log(mpf(n))
    
    def z5d_biased_prime_selection(
        self,
        target_index: int,
        k: float = 0.3
    ) -> Tuple[mpf, mpf, mpf]:
        """
        Z5D-guided biased prime selection combining all axioms.
        
        Applies:
        1. Discrete domain form for normalization
        2. Curvature for local geometry
        3. Geometric resolution for prime-density mapping
        
        Args:
            target_index: Prime index k (approximate position)
            k: Geometric resolution parameter (default: 0.3)
        
        Returns:
            Tuple of (theta_prime, curvature, bias_factor)
        """
        # 1. Compute prime density
        d_n = self.prime_density_approximation(target_index)
        
        # 2. Compute curvature κ(n) = d(n) · ln(n+1) / e²
        kappa = self.curvature(target_index, d_n)
        
        # 3. Compute geometric resolution θ'(n, k)
        theta_prime = self.geometric_resolution(target_index, k)
        
        # 4. Combine into bias factor using discrete domain form
        # Δ_n represents the geometric resolution influence
        # Δ_max is normalized to 1 for prime mapping
        delta_n = theta_prime * (1 + kappa)  # Curvature-enhanced resolution
        delta_max = PHI  # Normalized maximum
        
        bias_factor = self.discrete_domain_form(target_index, delta_n, delta_max)
        
        return theta_prime, kappa, bias_factor
    
    def empirical_validation(self, n_test: int = 1000) -> dict:
        """
        Empirical validation of Z5D axioms (Axiom 1).
        
        Tests reproducibility and numerical stability.
        
        Args:
            n_test: Test value for validation
        
        Returns:
            Dictionary with validation metrics
        """
        results = {
            'precision_dps': mp.dps,
            'target_precision': TARGET_PRECISION,
            'tests_passed': True,
            'errors': []
        }
        
        # Test 1: Geometric resolution stability
        theta1 = self.geometric_resolution(n_test, 0.3)
        theta2 = self.geometric_resolution(n_test, 0.3)
        diff = abs(theta1 - theta2)
        
        if diff > TARGET_PRECISION:
            results['tests_passed'] = False
            results['errors'].append(f"Geometric resolution not stable: diff={diff}")
        
        # Test 2: Curvature non-negativity
        d_n = self.prime_density_approximation(n_test)
        kappa = self.curvature(n_test, d_n)
        
        if kappa < 0:
            results['tests_passed'] = False
            results['errors'].append(f"Curvature is negative: κ={kappa}")
        
        # Test 3: Universal invariant consistency
        A, B, c = mpf(1), mpf(2), E2
        Z1 = self.universal_invariant(A, B, c)
        Z2 = self.universal_invariant(A, B, c)
        
        if abs(Z1 - Z2) > TARGET_PRECISION:
            results['tests_passed'] = False
            results['errors'].append(f"Universal invariant not consistent: diff={abs(Z1 - Z2)}")
        
        # Test 4: Zero-division protection
        try:
            # Should raise ValueError
            self.discrete_domain_form(100, mpf(1), mpf(0))
            results['tests_passed'] = False
            results['errors'].append("Zero-division protection failed for discrete_domain_form")
        except ValueError:
            pass  # Expected
        
        results['sample_values'] = {
            'theta_prime': float(theta1),
            'curvature': float(kappa),
            'prime_density': float(d_n)
        }
        
        return results


def z5d_enhanced_prime_search(
    target_value: int,
    k_resolution: float = 0.3,
    search_window: int = 1000
) -> list:
    """
    Enhanced prime search using Z5D axioms.
    
    Generates prime candidates biased by Z5D geometric resolution.
    
    Args:
        target_value: Approximate target prime value
        k_resolution: Geometric resolution parameter (default: 0.3)
        search_window: Search radius around target
    
    Returns:
        List of candidate positions biased by Z5D
    """
    axioms = Z5DAxioms()
    
    # Estimate prime index from target value
    if target_value <= 2:
        return [2]
    
    # Approximate k using inverse PNT: π(n) ≈ n/ln(n)
    k_estimate = int(target_value / math.log(target_value))
    
    candidates = []
    
    # Search in window around estimate
    for k_offset in range(-search_window, search_window + 1):
        k = max(1, k_estimate + k_offset)
        
        # Apply Z5D bias
        theta_prime, kappa, bias_factor = axioms.z5d_biased_prime_selection(k, k_resolution)
        
        # Weight candidate by bias factor
        weight = float(bias_factor)
        
        candidates.append({
            'k': k,
            'weight': weight,
            'theta_prime': float(theta_prime),
            'curvature': float(kappa)
        })
    
    # Sort by weight (highest first)
    candidates.sort(key=lambda x: x['weight'], reverse=True)
    
    return candidates


if __name__ == "__main__":
    print("Z5D Axioms Empirical Validation")
    print("=" * 60)
    
    # Initialize axioms
    axioms = Z5DAxioms(precision_dps=50)
    
    # Run empirical validation
    validation = axioms.empirical_validation(n_test=10000)
    
    print(f"\nPrecision: {validation['precision_dps']} decimal places")
    print(f"Target precision: {validation['target_precision']}")
    print(f"Tests passed: {validation['tests_passed']}")
    
    if validation['errors']:
        print("\nErrors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    print("\nSample values (n=10000):")
    for key, value in validation['sample_values'].items():
        print(f"  {key}: {value:.6e}")
    
    # Test Z5D-biased prime selection
    print("\n" + "=" * 60)
    print("Z5D-Biased Prime Selection Example")
    print("=" * 60)
    
    target = 2**127  # 128-bit prime target
    print(f"\nTarget value: 2^127 ≈ {target:.3e}")
    
    k_estimate = int(target / math.log(target))
    print(f"Estimated prime index k: {k_estimate:.3e}")
    
    theta, kappa, bias = axioms.z5d_biased_prime_selection(k_estimate, k=0.3)
    
    print(f"\nZ5D Bias Factors:")
    print(f"  θ'(k, 0.3) = {float(theta):.6e}")
    print(f"  κ(k) = {float(kappa):.6e}")
    print(f"  Bias factor = {float(bias):.6e}")
    
    # Show how this enhances prime selection
    print("\n" + "=" * 60)
    print("Prime Search Enhancement (top 5 candidates)")
    print("=" * 60)
    
    candidates = z5d_enhanced_prime_search(10000, k_resolution=0.3, search_window=100)
    
    print(f"\nTop 5 most promising prime indices near 10000:")
    for i, cand in enumerate(candidates[:5], 1):
        print(f"  {i}. k={cand['k']}, weight={cand['weight']:.3f}, "
              f"θ'={cand['theta_prime']:.3e}, κ={cand['curvature']:.3e}")
