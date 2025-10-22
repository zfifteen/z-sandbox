#!/usr/bin/env python3
"""
256-bit RSA Factorization Pipeline
Implements multiple factorization methods with priority ordering and timeout.
"""

import time
import math
import sympy
import subprocess
import shutil
import json
from typing import Optional, Tuple, List, Dict
from pathlib import Path

def verify_factors(N: int, p: int, q: int) -> bool:
    """
    Verify that p and q are valid factors of N.
    
    Args:
        N: The number to factor
        p: First factor
        q: Second factor
    
    Returns:
        True if p * q = N and both are prime
    """
    if p * q != N:
        return False
    
    if not sympy.isprime(p) or not sympy.isprime(q):
        return False
    
    return True

def pollard_rho(N: int, max_iterations: int = 10**8, x0: int = 2) -> Optional[int]:
    """
    Pollard's Rho factorization algorithm.
    
    Args:
        N: Number to factor
        max_iterations: Maximum iterations before giving up
        x0: Starting point for the sequence
    
    Returns:
        A factor of N if found, None otherwise
    """
    if N % 2 == 0:
        return 2
    
    def f(x):
        return (x * x + 1) % N
    
    x = x0
    y = x0
    d = 1
    
    iterations = 0
    while d == 1 and iterations < max_iterations:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), N)
        iterations += 1
    
    if d != N and d != 1:
        return d
    
    return None

def try_pollard_rho(N: int, timeout_seconds: float = 60) -> Optional[Tuple[int, int]]:
    """
    Try Pollard's Rho with multiple starting points.
    
    Args:
        N: Number to factor
        timeout_seconds: Maximum time to spend
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    start_time = time.time()
    
    # Try different starting points
    for x0 in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if time.time() - start_time > timeout_seconds:
            break
        
        remaining_time = timeout_seconds - (time.time() - start_time)
        max_iter = int(min(10**8, remaining_time * 10**6))  # Roughly 1M iterations per second
        
        factor = pollard_rho(N, max_iterations=max_iter, x0=x0)
        
        if factor and factor != N:
            q = N // factor
            if verify_factors(N, factor, q):
                return (factor, q)
    
    return None

def fermat_factorization(N: int, max_iterations: int = 10**7) -> Optional[Tuple[int, int]]:
    """
    Fermat's factorization method.
    Works well when |p - q| is small.
    
    Args:
        N: Number to factor (must be odd)
        max_iterations: Maximum iterations to try
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    if N % 2 == 0:
        return (2, N // 2)
    
    # Use integer square root for large numbers
    a = int(N**0.5) + 1
    b2 = a * a - N
    
    iterations = 0
    while iterations < max_iterations and b2 >= 0:
        # Check if b2 is a perfect square
        b = int(b2**0.5)
        
        if b * b == b2:
            p = a - b
            q = a + b
            if p > 1 and q > 1 and p * q == N:
                return (p, q)
        
        a += 1
        b2 = a * a - N
        iterations += 1
    
    return None

def try_fermat(N: int, timeout_seconds: float = 60) -> Optional[Tuple[int, int]]:
    """
    Try Fermat's factorization with timeout.
    
    Args:
        N: Number to factor
        timeout_seconds: Maximum time to spend
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    # Estimate iterations based on timeout
    # Assume ~10M iterations per second
    max_iter = int(min(10**7, timeout_seconds * 10**7))
    
    result = fermat_factorization(N, max_iterations=max_iter)
    
    if result and verify_factors(N, result[0], result[1]):
        return result
    
    return None

def try_ecm_sympy(N: int, timeout_seconds: float = 600, B1: int = 10**6) -> Optional[Tuple[int, int]]:
    """
    Try Elliptic Curve Method using sympy's built-in implementation.
    
    Args:
        N: Number to factor
        timeout_seconds: Maximum time to spend
        B1: Stage 1 bound for ECM
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    start_time = time.time()
    
    # Try multiple curves
    curves_to_try = min(100, int(timeout_seconds / 5))  # Assume ~5 seconds per curve
    
    for curve in range(curves_to_try):
        if time.time() - start_time > timeout_seconds:
            break
        
        try:
            # Use sympy's factorization with trial division and ECM
            factors = sympy.factorint(N, limit=B1, use_trial=True, use_rho=True, 
                                     use_pm1=True, verbose=False)
            
            if len(factors) == 2:
                p, q = list(factors.keys())
                if verify_factors(N, p, q):
                    return (p, q)
            
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            continue
    
    return None

def try_ecm_gmp(N: int, timeout_seconds: float = 3600, 
                B1: int = 10**8, curves: int = 10000) -> Optional[Tuple[int, int]]:
    """
    Try Elliptic Curve Method using gmp-ecm via subprocess.
    
    Args:
        N: Number to factor
        timeout_seconds: Maximum time to spend
        B1: Stage 1 bound
        curves: Number of curves to try
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    try:
        # Check if ecm is available (cross-platform)
        if shutil.which('ecm') is None:
            return None
        
        # Run ECM
        cmd = f'echo {N} | ecm -c {curves} {B1}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, 
                              timeout=timeout_seconds)
        
        # Parse output for factors
        output = result.stdout + result.stderr
        
        # Look for factor lines
        for line in output.split('\n'):
            if 'factor' in line.lower() or 'found' in line.lower():
                # Try to extract numbers
                import re
                numbers = re.findall(r'\d+', line)
                for num_str in numbers:
                    try:
                        factor = int(num_str)
                        if 1 < factor < N and N % factor == 0:
                            q = N // factor
                            if verify_factors(N, factor, q):
                                return (factor, q)
                    except ValueError:
                        continue
        
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        pass
    except Exception:
        pass
    
    return None

def try_trial_division(N: int, limit: int = 10**6) -> Optional[Tuple[int, int]]:
    """
    Try simple trial division up to a limit.
    
    Args:
        N: Number to factor
        limit: Maximum divisor to try
    
    Returns:
        (p, q) if factors found, None otherwise
    """
    if N % 2 == 0:
        q = N // 2
        if verify_factors(N, 2, q):
            return (2, q)
    
    for p in range(3, min(limit, int(math.sqrt(N)) + 1), 2):
        if N % p == 0:
            q = N // p
            if verify_factors(N, p, q):
                return (p, q)
    
    return None

class FactorizationPipeline:
    """
    Factorization pipeline that tries multiple methods in priority order.
    """
    
    def __init__(self, target_N: int, timeout_seconds: float = 3600):
        """
        Initialize the factorization pipeline.
        
        Args:
            target_N: Number to factor
            timeout_seconds: Total timeout for all methods
        """
        self.N = target_N
        self.timeout = timeout_seconds
        
        # Methods in priority order: (name, function, time_allocation_ratio)
        self.methods = [
            ('trial_division', self.run_trial_division, 0.01),
            ('pollard_rho', self.run_pollard_rho, 0.05),
            ('fermat', self.run_fermat, 0.05),
            ('ecm_sympy', self.run_ecm_sympy, 0.39),
            ('ecm_gmp', self.run_ecm_gmp, 0.50),
        ]
    
    def run_trial_division(self, time_budget: float) -> Optional[Tuple[int, int]]:
        """Run trial division."""
        return try_trial_division(self.N, limit=10**6)
    
    def run_pollard_rho(self, time_budget: float) -> Optional[Tuple[int, int]]:
        """Run Pollard's Rho."""
        return try_pollard_rho(self.N, timeout_seconds=time_budget)
    
    def run_fermat(self, time_budget: float) -> Optional[Tuple[int, int]]:
        """Run Fermat's factorization."""
        return try_fermat(self.N, timeout_seconds=time_budget)
    
    def run_ecm_sympy(self, time_budget: float) -> Optional[Tuple[int, int]]:
        """Run ECM with sympy."""
        return try_ecm_sympy(self.N, timeout_seconds=time_budget, B1=10**7)
    
    def run_ecm_gmp(self, time_budget: float) -> Optional[Tuple[int, int]]:
        """Run ECM with gmp-ecm if available."""
        return try_ecm_gmp(self.N, timeout_seconds=time_budget, B1=10**8, curves=10000)
    
    def run(self) -> Tuple[Optional[Tuple[int, int]], str, float, Dict]:
        """
        Run the factorization pipeline.
        
        Returns:
            (factors, method_name, elapsed_time, metadata) where factors is (p, q) or None
            metadata contains: B1, curves, method_order, time_per_method
        """
        start_time = time.time()
        metadata = {
            'method_order': [],
            'time_per_method': {},
            'parameters': {}
        }
        
        for method_name, method_func, time_ratio in self.methods:
            if time.time() - start_time > self.timeout:
                return None, 'timeout', time.time() - start_time, metadata
            
            # Calculate time budget for this method
            remaining_time = self.timeout - (time.time() - start_time)
            time_budget = min(remaining_time, self.timeout * time_ratio)
            
            # Record method order and parameters
            metadata['method_order'].append(method_name)
            if 'ecm' in method_name:
                if method_name == 'ecm_sympy':
                    metadata['parameters'][method_name] = {'B1': 10**7}
                elif method_name == 'ecm_gmp':
                    metadata['parameters'][method_name] = {'B1': 10**8, 'curves': 10000}
            
            print(f"  Trying {method_name} with {time_budget:.1f}s budget...")
            method_start = time.time()
            
            try:
                factors = method_func(time_budget)
                method_elapsed = time.time() - method_start
                metadata['time_per_method'][method_name] = method_elapsed
                
                if factors:
                    p, q = factors
                    if verify_factors(self.N, p, q):
                        elapsed = time.time() - start_time
                        print(f"  ✓ SUCCESS with {method_name} in {method_elapsed:.2f}s")
                        return factors, method_name, elapsed, metadata
                
                print(f"    {method_name} failed after {method_elapsed:.2f}s")
            
            except Exception as e:
                method_elapsed = time.time() - method_start
                metadata['time_per_method'][method_name] = method_elapsed
                print(f"    {method_name} error: {e}")
                continue
        
        elapsed = time.time() - start_time
        return None, 'exhausted_methods', elapsed, metadata

def factor_single_target(N: int, timeout: float = 3600, verbose: bool = True) -> dict:
    """
    Factor a single target and return results.
    
    Args:
        N: Number to factor
        timeout: Timeout in seconds
        verbose: Print progress
    
    Returns:
        Dictionary with factorization results
    """
    if verbose:
        print(f"\nFactoring N = {N}")
        print(f"  N bit length: {N.bit_length()}")
    
    pipeline = FactorizationPipeline(N, timeout_seconds=timeout)
    factors, method, elapsed, metadata = pipeline.run()
    
    result = {
        'N': str(N),
        'success': factors is not None,
        'method': method,
        'elapsed_time': elapsed,
        'p': str(factors[0]) if factors else None,
        'q': str(factors[1]) if factors else None,
        'metadata': metadata
    }
    
    if verbose:
        if factors:
            print(f"  ✓ FACTORED: {factors[0]} × {factors[1]}")
            print(f"    Method: {method}")
            print(f"    Time: {elapsed:.2f}s")
        else:
            print(f"  ✗ Failed to factor (reason: {method}, time: {elapsed:.2f}s)")
    
    return result

def main():
    """Test the factorization pipeline with a small example."""
    print("="*60)
    print("256-bit RSA Factorization Pipeline Test")
    print("="*60)
    
    # Test with a small semiprime first
    p_test = sympy.randprime(10**9, 10**10)
    q_test = sympy.randprime(10**9, 10**10)
    N_test = p_test * q_test
    
    print(f"\nTest 1: Small semiprime (60-bit)")
    result = factor_single_target(N_test, timeout=60)
    
    if result['success']:
        print("\n✓ Small test passed!")
    else:
        print("\n✗ Small test failed - pipeline may have issues")
    
    # Test with actual 256-bit target (if available)
    import json
    from pathlib import Path
    
    targets_file = Path(__file__).parent / 'targets_256bit.json'
    if targets_file.exists():
        with open(targets_file, 'r') as f:
            data = json.load(f)
        
        if data['targets']:
            print("\n" + "="*60)
            print("Test 2: Actual 256-bit target")
            print("="*60)
            
            target = data['targets'][0]
            N_256 = int(target['N'])
            
            # Short timeout for demo
            result = factor_single_target(N_256, timeout=120)
            
            if result['success']:
                print("\n✓ 256-bit factorization succeeded!")
            else:
                print("\n⚠ 256-bit factorization did not complete in 120s")
                print("  This is expected - real attempts need hours")

if __name__ == "__main__":
    main()
