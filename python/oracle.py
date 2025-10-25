#!/usr/bin/env python3
"""
Deterministic Oracle Module

Provides deterministic, RNG-free ground truth targets using rapidly convergent
hypergeometric series for 1/π (Ramanujan/Chudnovsky type). These series achieve
≈14 decimal digits per term (Chudnovsky) and enable:

1. Precise, reproducible error accounting for QMC variance-reduction claims
2. Separation of algorithmic variance from truth error
3. Validation of expected QMC error rate O((log N)^s/N)
4. Portable calibration path for Z-Framework experiments

Mathematical Foundation:
------------------------
Chudnovsky formula (1988):
  1/π = 12 Σ_{k=0}^∞ [(-1)^k (6k)! (13591409 + 545140134k)] / 
                      [(3k)! (k!)^3 (640320)^(3k+3/2)]

This achieves approximately 14.18 decimal digits per term through:
- Modular equations from elliptic integrals
- Ramanujan-type hypergeometric identities
- Optimized rational approximations to π

Convergence rate: exponential, ~10^(-14) improvement per term
Terms needed for precision P: roughly P/14

References:
- Ramanujan (1914): Modular Equations and Approximations to π
- Chudnovsky & Chudnovsky (1988): Approximations and Complex Multiplication
- Bailey, Borwein & Plouffe (1997): On the Rapid Computation of Various Polylogarithmic Constants
"""

import math
from mpmath import mp, mpf, sqrt as mp_sqrt, factorial, power
from typing import Tuple, Optional
import numpy as np


class DeterministicOracle:
    """
    Deterministic oracle using hypergeometric series for high-precision π.
    
    Provides ground truth values for calibrating MC/QMC methods without
    introducing stochastic noise from the target itself.
    """
    
    def __init__(self, precision: int = 100):
        """
        Initialize oracle with specified precision.
        
        Args:
            precision: Decimal places for mpmath calculations
        """
        self.precision = precision
        mp.dps = precision
        self._pi_cache = None
        
    def compute_pi_chudnovsky(self, terms: Optional[int] = None) -> mpf:
        """
        Compute π using Chudnovsky formula.
        
        The Chudnovsky formula achieves ~14.18 digits per term:
          1/π = 12 Σ [(-1)^k (6k)! (A + Bk)] / [(3k)! (k!)^3 C^(3k+3/2)]
        
        where:
          A = 13591409
          B = 545140134  
          C = 640320
          
        Args:
            terms: Number of terms to compute. If None, auto-determines from precision.
            
        Returns:
            High-precision value of π
        """
        # Auto-determine terms needed for target precision
        if terms is None:
            # ~14.18 digits per term, add buffer
            terms = max(2, int(self.precision / 14) + 2)
        
        # Chudnovsky constants
        A = mpf(13591409)
        B = mpf(545140134)
        C = mpf(640320)
        C_cubed = C ** 3
        
        # Compute series sum
        sum_val = mpf(0)
        
        for k in range(terms):
            # Numerator: (-1)^k * (6k)! * (A + B*k)
            numerator = ((-1) ** k) * factorial(6 * k) * (A + B * k)
            
            # Denominator: (3k)! * (k!)^3 * C^(3k)
            denominator = factorial(3 * k) * (factorial(k) ** 3) * (C_cubed ** k)
            
            term = numerator / denominator
            sum_val += term
        
        # Final formula: π = 1 / [12 * sum * C^(3/2) / (640320^(3/2))]
        # Simplified: π = C^(3/2) / (12 * sum)
        C_sqrt = mp_sqrt(C)
        pi_val = (C_sqrt * C) / (mpf(12) * sum_val)
        
        return pi_val
    
    def compute_pi_ramanujan(self, terms: Optional[int] = None) -> mpf:
        """
        Compute π using Ramanujan's 1914 formula.
        
        One of Ramanujan's formulas:
          1/π = (2√2/9801) Σ [(4k)! (1103 + 26390k)] / [(k!)^4 396^(4k)]
          
        Achieves ~8 digits per term.
        
        Args:
            terms: Number of terms to compute
            
        Returns:
            High-precision value of π
        """
        if terms is None:
            # ~8 digits per term
            terms = max(2, int(self.precision / 8) + 2)
        
        sum_val = mpf(0)
        
        for k in range(terms):
            numerator = factorial(4 * k) * (mpf(1103) + mpf(26390) * k)
            denominator = (factorial(k) ** 4) * (mpf(396) ** (4 * k))
            sum_val += numerator / denominator
        
        # π = 9801 / (2√2 * sum)
        pi_val = mpf(9801) / (mpf(2) * mp_sqrt(mpf(2)) * sum_val)
        
        return pi_val
    
    def get_pi(self, method: str = 'chudnovsky', force_recompute: bool = False) -> mpf:
        """
        Get high-precision π value.
        
        Args:
            method: 'chudnovsky' or 'ramanujan'
            force_recompute: Force recomputation instead of using cache
            
        Returns:
            High-precision π
        """
        if not force_recompute and self._pi_cache is not None:
            return self._pi_cache
        
        if method == 'chudnovsky':
            pi_val = self.compute_pi_chudnovsky()
        elif method == 'ramanujan':
            pi_val = self.compute_pi_ramanujan()
        else:
            # Fallback to mpmath's built-in π (uses similar methods)
            pi_val = mp.pi
        
        self._pi_cache = pi_val
        return pi_val
    
    def circle_area_exact(self, radius: float = 1.0) -> mpf:
        """
        Compute exact circle area using high-precision π.
        
        Args:
            radius: Circle radius
            
        Returns:
            Exact area = π * r²
        """
        pi_val = self.get_pi()
        return pi_val * (mpf(radius) ** 2)
    
    def estimate_pi_error(self, estimate: float, method: str = 'chudnovsky') -> float:
        """
        Compute absolute error of a π estimate.
        
        Args:
            estimate: Estimated value of π
            method: Method to use for ground truth
            
        Returns:
            Absolute error |estimate - π_true|
        """
        pi_true = self.get_pi(method=method)
        return abs(float(pi_true) - estimate)
    
    def convergence_oracle(self, sample_counts: list, 
                          estimator_fn,
                          true_value: Optional[mpf] = None) -> dict:
        """
        Evaluate estimator convergence against oracle ground truth.
        
        This enables clean measurement of algorithmic variance (MC vs QMC)
        without noise from stochastic ground truth.
        
        Args:
            sample_counts: List of N values to test
            estimator_fn: Function(N) -> estimate, takes sample count, returns estimate
            true_value: Known exact value. If None, uses π
            
        Returns:
            Dictionary with convergence data:
            - 'N': sample counts
            - 'estimates': estimator outputs  
            - 'errors': absolute errors
            - 'rel_errors': relative errors
            - 'log_N': log of sample counts (for plotting)
        """
        if true_value is None:
            true_value = self.get_pi()
        
        estimates = []
        errors = []
        rel_errors = []
        
        for N in sample_counts:
            estimate = estimator_fn(N)
            estimates.append(float(estimate))
            
            error = abs(float(true_value) - float(estimate))
            errors.append(error)
            
            rel_error = error / float(true_value) if float(true_value) != 0 else 0
            rel_errors.append(rel_error)
        
        return {
            'N': sample_counts,
            'estimates': estimates,
            'errors': errors,
            'rel_errors': rel_errors,
            'log_N': [math.log(N) for N in sample_counts],
            'true_value': float(true_value)
        }
    
    def qmc_expected_error(self, N: int, dimension: int = 2) -> float:
        """
        Theoretical QMC error bound: O((log N)^s / N)
        
        For QMC methods like Sobol/Halton sequences, the expected
        discrepancy scales as (log N)^s / N where s is dimension.
        
        Args:
            N: Number of samples
            dimension: Space dimension
            
        Returns:
            Expected error bound (approximate, for comparison)
        """
        if N <= 1:
            return 1.0
        
        # Simplified bound: C * (log N)^s / N
        # C ~ 1 for normalized problem
        C = 1.0
        error_bound = C * (math.log(N) ** dimension) / N
        return error_bound
    
    def mc_expected_error(self, N: int) -> float:
        """
        Theoretical MC error bound: O(1/√N)
        
        Standard Monte Carlo has probabilistic error O(1/√N).
        
        Args:
            N: Number of samples
            
        Returns:
            Expected error bound (approximate)
        """
        if N <= 0:
            return float('inf')
        
        # Simplified bound: C / √N
        # C ~ 1 for normalized problem
        C = 1.0
        return C / math.sqrt(N)


def demo_oracle():
    """Demonstrate oracle precision and convergence tracking."""
    print("=" * 80)
    print("Deterministic Oracle Demonstration")
    print("=" * 80)
    print()
    
    # Create oracle with 100 decimal places
    oracle = DeterministicOracle(precision=100)
    
    print("1. Computing π with Chudnovsky formula...")
    pi_chud = oracle.compute_pi_chudnovsky(terms=5)
    print(f"   π (5 terms):  {pi_chud}")
    
    pi_chud_10 = oracle.compute_pi_chudnovsky(terms=10)
    print(f"   π (10 terms): {pi_chud_10}")
    print()
    
    print("2. Computing π with Ramanujan formula...")
    pi_ram = oracle.compute_pi_ramanujan(terms=5)
    print(f"   π (5 terms):  {pi_ram}")
    print()
    
    print("3. Comparing with mpmath built-in π...")
    pi_mpmath = mp.pi
    print(f"   mpmath π:     {pi_mpmath}")
    print(f"   Chud error:   {abs(pi_chud_10 - pi_mpmath)}")
    print(f"   Ram error:    {abs(pi_ram - pi_mpmath)}")
    print()
    
    print("4. Circle area oracle (exact vs estimate)...")
    exact_area = oracle.circle_area_exact(radius=1.0)
    print(f"   Exact area (r=1): {exact_area}")
    
    # Simulate a rough estimate
    rough_estimate = 3.14
    error = oracle.estimate_pi_error(rough_estimate)
    print(f"   Rough π = {rough_estimate}, error = {error:.6e}")
    print()
    
    print("5. Theoretical error bounds...")
    sample_counts = [100, 1000, 10000, 100000]
    print(f"   {'N':<8} {'MC O(1/√N)':<15} {'QMC O((log N)²/N)':<20}")
    print("   " + "-" * 43)
    for N in sample_counts:
        mc_err = oracle.mc_expected_error(N)
        qmc_err = oracle.qmc_expected_error(N, dimension=2)
        print(f"   {N:<8} {mc_err:<15.6e} {qmc_err:<20.6e}")
    print()
    
    print("=" * 80)
    print("Oracle ready for QMC benchmark integration!")
    print("=" * 80)


if __name__ == "__main__":
    demo_oracle()
