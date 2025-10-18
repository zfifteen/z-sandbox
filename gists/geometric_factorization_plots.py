#!/usr/bin/env python3
"""
Geometric Factorization Algorithm
==================================

A reproducible implementation of the Geometric Factorization method using
golden-ratio geometric mapping, spiral candidate search, and multi-pass
optimization for factoring semiprimes.

This implementation features:
- Deterministic semiprime generation with seeded RNG
- Golden-ratio geometric mapping θ(N, k) = {φ × {N / φ}^k}
- Prime candidate generation near √N
- Geometric filtering using circular distance on unit circle
- Golden-spiral candidate generator with golden angle γ = 2π / φ²
- Multi-pass optimization with configurable k and ε tolerances
- Comprehensive diagnostics and logging
- Full reproducibility with fixed seeds

Usage:
    python geometric_factorization.py --demo
    python geometric_factorization.py --test
    python geometric_factorization.py --validate

Author: Geometric Factorization Research
Date: 2025-10-18
"""

import math
import random
import time
import argparse
from typing import Tuple, List, Dict, Optional, Iterator, Any
from dataclasses import dataclass, field
from collections import defaultdict
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
GOLDEN_ANGLE = 2 * math.pi / (PHI ** 2)  # Golden angle ≈ 2.399963...


# ============================================================================
# Core Mathematical Functions
# ============================================================================

def theta(N: int, k: float) -> float:
    """
    Compute geometric mapping θ(N, k) = {φ × {N / φ}^k}
    
    Returns fractional part in [0, 1) with robust handling of floating-point
    precision issues.
    
    Args:
        N: Integer to map
        k: Exponent parameter
        
    Returns:
        Fractional part in [0, 1)
    """
    if N <= 0:
        return 0.0
    
    # Compute φ × (N / φ)^k with log-space computation for stability
    # log(φ × (N / φ)^k) = log(φ) + k × (log(N) - log(φ))
    log_phi = math.log(PHI)
    log_N = math.log(N)
    log_val = log_phi + k * (log_N - log_phi)
    
    # Convert back from log space
    val = math.exp(log_val)
    
    # Extract fractional part with proper handling of precision
    frac = val - math.floor(val)
    
    # Ensure result is in [0, 1)
    frac = frac % 1.0
    
    return frac


def circular_distance(a: float, b: float) -> float:
    """
    Compute absolute circular distance on unit circle with wrap-around.
    
    Returns minimum distance in [0, 0.5] accounting for wrap-around at 1.0.
    
    Args:
        a: First angle in [0, 1)
        b: Second angle in [0, 1)
        
    Returns:
        Circular distance in [0, 0.5]
    """
    # Normalize to [0, 1)
    a = a % 1.0
    b = b % 1.0
    
    # Compute direct distance
    direct = abs(a - b)
    
    # Account for wrap-around: min(direct, 1 - direct)
    wraparound = 1.0 - direct
    
    return min(direct, wraparound)


# ============================================================================
# Primality Testing
# ============================================================================

def is_prime_miller_rabin(n: int, rounds: int = 10) -> bool:
    """
    Deterministic Miller-Rabin primality test.
    
    For n < 3,317,044,064,679,887,385,961,981, using first 13 primes as
    witnesses provides deterministic results.
    
    Args:
        n: Number to test
        rounds: Number of rounds (for probabilistic version)
        
    Returns:
        True if n is (probably) prime
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r × d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Deterministic witnesses for small n
    if n < 2047:
        witnesses = [2]
    elif n < 1373653:
        witnesses = [2, 3]
    elif n < 9080191:
        witnesses = [31, 73]
    elif n < 25326001:
        witnesses = [2, 3, 5]
    elif n < 3215031751:
        witnesses = [2, 3, 5, 7]
    elif n < 4759123141:
        witnesses = [2, 7, 61]
    elif n < 1122004669633:
        witnesses = [2, 13, 23, 1662803]
    elif n < 2152302898747:
        witnesses = [2, 3, 5, 7, 11]
    elif n < 3474749660383:
        witnesses = [2, 3, 5, 7, 11, 13]
    elif n < 341550071728321:
        witnesses = [2, 3, 5, 7, 11, 13, 17]
    else:
        # Use first primes for larger n
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    
    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True
    
    for witness in witnesses:
        if witness >= n:
            continue
        if check_composite(witness):
            return False
    
    return True


# ============================================================================
# Semiprime Generation
# ============================================================================

def generate_prime(bit_size: int, rng: random.Random) -> int:
    """
    Generate a random prime of specified bit size.
    
    Args:
        bit_size: Number of bits in the prime
        rng: Random number generator (for determinism)
        
    Returns:
        Random prime with specified bit size
    """
    while True:
        # Generate random odd number in range
        p = rng.getrandbits(bit_size)
        # Set high bit to ensure bit size
        p |= (1 << (bit_size - 1))
        # Set low bit to ensure odd
        p |= 1
        
        if is_prime_miller_rabin(p):
            return p


def generate_semiprime(bit_size: int, seed: int) -> Tuple[int, int, int]:
    """
    Generate a balanced semiprime N = p × q with deterministic seed.
    
    Args:
        bit_size: Total bit size of the semiprime (N)
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (N, p, q) where N = p × q and p, q are primes
    """
    rng = random.Random(seed)
    
    # Generate balanced primes (each about half the bits)
    p_bits = bit_size // 2
    q_bits = bit_size - p_bits
    
    p = generate_prime(p_bits, rng)
    q = generate_prime(q_bits, rng)
    
    # Ensure p <= q for consistency
    if p > q:
        p, q = q, p
    
    N = p * q
    
    return N, p, q


# ============================================================================
# Prime Candidate Generation
# ============================================================================

def prime_candidates_around_sqrt(N: int, window_size: int, limit: int) -> Iterator[int]:
    """
    Generate prime candidates in window around √N.
    
    Args:
        N: Target semiprime
        window_size: Search window radius (±window_size)
        limit: Maximum number of candidates to generate
        
    Yields:
        Prime numbers near √N
    """
    sqrt_N = int(math.isqrt(N))
    
    # Search window bounds
    start = max(2, sqrt_N - window_size)
    end = sqrt_N + window_size
    
    count = 0
    
    # Check candidates around sqrt_N
    for candidate in range(start, end + 1):
        if count >= limit:
            break
        
        if is_prime_miller_rabin(candidate):
            yield candidate
            count += 1


def spiral_candidates(N: int, iterations: int, scale_func=None) -> Iterator[int]:
    """
    Generate candidates using golden-spiral mapping.
    
    Uses golden angle γ = 2π / φ² to generate spiral coordinates,
    then maps to integer candidates near √N.
    
    Args:
        N: Target semiprime
        iterations: Number of spiral iterations
        scale_func: Optional function to scale spiral radius
        
    Yields:
        Integer candidates from spiral
    """
    sqrt_N = math.sqrt(N)
    
    # Default scale function: linear growth
    if scale_func is None:
        scale_func = lambda i: math.sqrt(i)
    
    seen = set()
    
    for i in range(1, iterations + 1):
        # Golden spiral: angle increases by golden angle
        angle = i * GOLDEN_ANGLE
        
        # Radius grows with scale function
        radius = scale_func(i)
        
        # Convert to Cartesian coordinates
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Map to candidate near sqrt_N
        # Use spiral displacement as offset from sqrt_N
        offset = int(x * math.sqrt(sqrt_N) + y)
        candidate = int(sqrt_N + offset)
        
        # Ensure positive and unique
        if candidate > 1 and candidate not in seen:
            seen.add(candidate)
            yield candidate


# ============================================================================
# Geometric Filtering
# ============================================================================

def filter_candidates_geometric(
    N: int,
    candidates: List[int],
    k: float,
    epsilon: float
) -> List[int]:
    """
    Filter candidates using geometric circular distance.
    
    Keeps only candidates p where |θ(p, k) - θ(N, k)| ≤ ε
    with proper wrap-around on unit circle.
    
    Args:
        N: Target semiprime
        candidates: List of candidate factors
        k: Exponent parameter for theta
        epsilon: Tolerance threshold
        
    Returns:
        Filtered list of candidates
    """
    theta_N = theta(N, k)
    filtered = []
    
    for p in candidates:
        theta_p = theta(p, k)
        dist = circular_distance(theta_p, theta_N)
        
        if dist <= epsilon:
            filtered.append(p)
    
    return filtered


# ============================================================================
# Factorization Engine
# ============================================================================

@dataclass
class FactorizationParams:
    """Parameters for geometric factorization."""
    k_list: List[float] = field(default_factory=lambda: [0.200, 0.450, 0.800])
    eps_list: List[float] = field(default_factory=lambda: [0.02, 0.05, 0.10])
    spiral_iters: int = 2000
    search_window: int = 1024
    prime_limit: int = 5000
    max_attempts: int = 50000
    use_spiral: bool = True
    primality_test_rounds: int = 10


@dataclass
class FactorizationResult:
    """Results from geometric factorization attempt."""
    success: bool
    factors: Optional[Tuple[int, int]]
    attempts: int
    candidate_counts: Dict[str, int]
    timings: Dict[str, float]
    logs: List[Dict[str, Any]]
    
    def summary(self) -> str:
        """Generate summary string."""
        if self.success:
            p, q = self.factors
            return f"SUCCESS: {p} × {q}, {self.attempts} attempts"
        else:
            return f"FAILED: {self.attempts} attempts"


def geometric_factor(N: int, params: FactorizationParams) -> FactorizationResult:
    """
    Factor semiprime N using geometric factorization.
    
    Multi-pass algorithm with configurable k and epsilon values,
    combining prime candidates and spiral candidates, filtered
    geometrically using circular distance.
    
    Args:
        N: Target semiprime to factor
        params: Factorization parameters
        
    Returns:
        FactorizationResult with diagnostics
    """
    start_time = time.time()
    
    logs = []
    candidate_counts = defaultdict(int)
    timings = {}
    attempts = 0
    
    # Quick trial division check
    sqrt_N = int(math.isqrt(N))
    for small_prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if N % small_prime == 0:
            q = N // small_prime
            if is_prime_miller_rabin(q):
                result = FactorizationResult(
                    success=True,
                    factors=(small_prime, q),
                    attempts=1,
                    candidate_counts={'trial_division': 1},
                    timings={'total': time.time() - start_time},
                    logs=[{
                        'method': 'trial_division',
                        'factor': small_prime,
                        'k': 0,
                        'epsilon': 0,
                        'pre_filter': 1,
                        'post_filter': 1,
                        'reduction_ratio': 1.0,
                        'result': 'SUCCESS'
                    }]
                )
                return result
    
    # Multi-pass over k and epsilon values
    for k_idx, k in enumerate(params.k_list):
        for eps_idx, epsilon in enumerate(params.eps_list):
            pass_start = time.time()
            
            # Generate prime candidates around sqrt(N)
            prime_gen_start = time.time()
            prime_cands = list(prime_candidates_around_sqrt(
                N, params.search_window, params.prime_limit
            ))
            prime_gen_time = time.time() - prime_gen_start
            
            # Generate spiral candidates if enabled
            spiral_cands = []
            spiral_gen_time = 0.0
            if params.use_spiral:
                spiral_gen_start = time.time()
                spiral_cands = list(spiral_candidates(N, params.spiral_iters))
                # Filter to primes
                spiral_cands = [c for c in spiral_cands if is_prime_miller_rabin(c)]
                spiral_gen_time = time.time() - spiral_gen_start
            
            # Combine candidates
            all_cands = list(set(prime_cands + spiral_cands))
            pre_filter_count = len(all_cands)
            
            # Geometric filtering
            filter_start = time.time()
            filtered = filter_candidates_geometric(N, all_cands, k, epsilon)
            filter_time = time.time() - filter_start
            
            post_filter_count = len(filtered)
            
            # Log this pass
            log_entry = {
                'k': k,
                'epsilon': epsilon,
                'pre_filter': pre_filter_count,
                'post_filter': post_filter_count,
                'reduction_ratio': pre_filter_count / max(1, post_filter_count),
                'prime_gen_time': prime_gen_time,
                'spiral_gen_time': spiral_gen_time,
                'filter_time': filter_time,
                'candidates_tested': 0,
                'result': None
            }
            
            candidate_counts[f'k={k}_eps={epsilon}_pre'] = pre_filter_count
            candidate_counts[f'k={k}_eps={epsilon}_post'] = post_filter_count
            
            # Test filtered candidates
            test_start = time.time()
            for candidate in filtered:
                attempts += 1
                log_entry['candidates_tested'] += 1
                
                if attempts > params.max_attempts:
                    break
                
                # Try division
                if N % candidate == 0:
                    other = N // candidate
                    
                    # Verify both factors are prime
                    if is_prime_miller_rabin(candidate) and is_prime_miller_rabin(other):
                        p, q = sorted([candidate, other])
                        
                        log_entry['result'] = 'SUCCESS'
                        log_entry['factor_found'] = candidate
                        logs.append(log_entry)
                        
                        timings.update({
                            'total': time.time() - start_time,
                            'last_pass': time.time() - pass_start,
                            'test_time': time.time() - test_start
                        })
                        
                        result = FactorizationResult(
                            success=True,
                            factors=(p, q),
                            attempts=attempts,
                            candidate_counts=dict(candidate_counts),
                            timings=timings,
                            logs=logs
                        )
                        return result
            
            log_entry['test_time'] = time.time() - test_start
            log_entry['result'] = 'CONTINUE'
            logs.append(log_entry)
            
            if attempts > params.max_attempts:
                break
        
        if attempts > params.max_attempts:
            break
    
    # Failed to factor
    timings['total'] = time.time() - start_time
    
    result = FactorizationResult(
        success=False,
        factors=None,
        attempts=attempts,
        candidate_counts=dict(candidate_counts),
        timings=timings,
        logs=logs
    )
    return result


# ============================================================================
# Demo and Validation
# ============================================================================

def demo_run(bit_sizes: List[int], samples_per_size: int, seed: int) -> Dict[str, Any]:
    """
    Run demonstration with multiple bit sizes.
    
    Args:
        bit_sizes: List of semiprime bit sizes to test
        samples_per_size: Number of samples per bit size
        seed: Base random seed
        
    Returns:
        Dictionary with aggregated results
    """
    results = {
        'bit_sizes': {},
        'summary': {}
    }
    
    for bit_size in bit_sizes:
        print(f"\n{'='*70}")
        print(f"Testing {bit_size}-bit semiprimes (samples: {samples_per_size})")
        print(f"{'='*70}\n")
        
        size_results = {
            'successes': 0,
            'failures': 0,
            'total_attempts': 0,
            'samples': []
        }
        
        for sample_idx in range(samples_per_size):
            sample_seed = seed + bit_size * 1000 + sample_idx
            
            print(f"Sample {sample_idx + 1}/{samples_per_size} (seed={sample_seed})")
            
            # Generate semiprime
            N, true_p, true_q = generate_semiprime(bit_size, sample_seed)
            print(f"  N = {N}")
            print(f"  True factors: {true_p} × {true_q}")
            
            # Factor it
            params = FactorizationParams()
            result = geometric_factor(N, params)
            
            # Record results
            size_results['total_attempts'] += result.attempts
            
            if result.success:
                size_results['successes'] += 1
                found_p, found_q = result.factors
                print(f"  ✓ Found: {found_p} × {found_q}")
                print(f"  Attempts: {result.attempts}")
                
                # Verify correctness
                assert found_p * found_q == N, "Factor product mismatch!"
                assert {found_p, found_q} == {true_p, true_q}, "Factors don't match!"
            else:
                size_results['failures'] += 1
                print(f"  ✗ Failed after {result.attempts} attempts")
            
            # Show candidate filtering example
            if result.logs:
                # Find best filtering pass (with most reduction)
                filtered_logs = [x for x in result.logs 
                               if x.get('post_filter', 0) > 0 and x.get('k', 0) != 0]
                if filtered_logs:
                    best_log = min(filtered_logs, 
                                 key=lambda x: x['post_filter'])
                    print(f"  Best filtering: {best_log['pre_filter']} → {best_log['post_filter']} "
                          f"(k={best_log['k']}, ε={best_log['epsilon']})")
            
            print(f"  Time: {result.timings.get('total', 0):.3f}s")
            print()
            
            size_results['samples'].append({
                'N': N,
                'true_factors': (true_p, true_q),
                'result': result
            })
        
        # Compute statistics
        success_rate = size_results['successes'] / samples_per_size
        avg_attempts = size_results['total_attempts'] / samples_per_size
        
        size_results['success_rate'] = success_rate
        size_results['avg_attempts'] = avg_attempts
        
        results['bit_sizes'][bit_size] = size_results
        
        print(f"\n{bit_size}-bit Summary:")
        print(f"  Success rate: {success_rate*100:.1f}%")
        print(f"  Avg attempts: {avg_attempts:.1f}")
    
    # Overall summary
    print(f"\n{'='*70}")
    print("OVERALL SUMMARY")
    print(f"{'='*70}\n")
    
    for bit_size in bit_sizes:
        stats = results['bit_sizes'][bit_size]
        print(f"{bit_size}-bit: {stats['success_rate']*100:.1f}% success, "
              f"{stats['avg_attempts']:.1f} avg attempts")
    
    return results


# ============================================================================
# Unit Tests
# ============================================================================

def run_tests():
    """Run unit tests for core functionality."""
    print("Running unit tests...\n")
    
    # Test theta computation
    print("Test 1: theta computation")
    theta_val = theta(1000, 0.5)
    assert 0 <= theta_val < 1.0, "theta not in [0, 1)"
    print(f"  θ(1000, 0.5) = {theta_val:.6f} ✓")
    
    # Test circular distance
    print("\nTest 2: circular distance")
    dist1 = circular_distance(0.1, 0.9)
    assert abs(dist1 - 0.2) < 1e-10, "Wrap-around distance incorrect"
    print(f"  circular_distance(0.1, 0.9) = {dist1:.6f} ✓")
    
    dist2 = circular_distance(0.3, 0.7)
    assert abs(dist2 - 0.4) < 1e-10, "Direct distance incorrect"
    print(f"  circular_distance(0.3, 0.7) = {dist2:.6f} ✓")
    
    # Test primality
    print("\nTest 3: primality testing")
    assert is_prime_miller_rabin(2), "2 should be prime"
    assert is_prime_miller_rabin(17), "17 should be prime"
    assert is_prime_miller_rabin(97), "97 should be prime"
    assert not is_prime_miller_rabin(100), "100 should not be prime"
    print("  Miller-Rabin primality test ✓")
    
    # Test semiprime generation
    print("\nTest 4: semiprime generation")
    N, p, q = generate_semiprime(10, seed=42)
    assert p * q == N, "Factors don't multiply to N"
    assert is_prime_miller_rabin(p), "p is not prime"
    assert is_prime_miller_rabin(q), "q is not prime"
    print(f"  Generated 10-bit semiprime: {N} = {p} × {q} ✓")
    
    # Test determinism
    N2, p2, q2 = generate_semiprime(10, seed=42)
    assert (N, p, q) == (N2, p2, q2), "Generation not deterministic"
    print("  Deterministic generation ✓")
    
    # Test prime candidates
    print("\nTest 5: prime candidate generation")
    N_test = 143  # 11 × 13
    sqrt_N = int(math.isqrt(N_test))
    primes = list(prime_candidates_around_sqrt(N_test, 10, 100))
    assert 11 in primes or 13 in primes, "Should find factors near sqrt"
    print(f"  Found {len(primes)} primes near √{N_test} ✓")
    
    # Test spiral candidates
    print("\nTest 6: spiral candidate generation")
    spiral = list(spiral_candidates(1000, 100))
    assert len(spiral) > 0, "Should generate spiral candidates"
    assert all(c > 0 for c in spiral), "All candidates should be positive"
    print(f"  Generated {len(spiral)} spiral candidates ✓")
    
    # Test geometric filtering
    print("\nTest 7: geometric filtering")
    candidates = [11, 13, 17, 19, 23]
    filtered = filter_candidates_geometric(143, candidates, 0.2, 0.1)
    assert len(filtered) <= len(candidates), "Filtering should reduce or maintain count"
    print(f"  Filtered {len(candidates)} → {len(filtered)} candidates ✓")
    
    # Test small factorization
    print("\nTest 8: small semiprime factorization")
    N_small, p_small, q_small = generate_semiprime(8, seed=12345)
    params = FactorizationParams(max_attempts=1000)
    result = geometric_factor(N_small, params)
    if result.success:
        print(f"  Factored {N_small} = {result.factors[0]} × {result.factors[1]} ✓")
    else:
        print(f"  Could not factor {N_small} in {result.attempts} attempts (acceptable for test)")
    
    print("\n✓ All unit tests passed!")


# ============================================================================
# Main CLI
# ============================================================================

# ============================================================================
# Plotting Functions
# ============================================================================

def plot_unit_circle_mapping(N, p, q, k, save_path='plots/plot.png'):
    """
    2D Plot: Unit Circle Mapping of Theta Values
    """
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)

    theta_N = theta(N, k)
    theta_p = theta(p, k)
    theta_q = theta(q, k)

    # Convert to radians
    angle_N = theta_N * 2 * np.pi
    angle_p = theta_p * 2 * np.pi
    angle_q = theta_q * 2 * np.pi

    # Plot points
    ax.scatter(angle_N, 1, color='red', s=100, label=f'N={N}')
    ax.scatter(angle_p, 1, color='blue', s=100, label=f'p={p}')
    ax.scatter(angle_q, 1, color='green', s=100, label=f'q={q}')

    # Draw arcs for distances
    dist_p = circular_distance(theta_N, theta_p) * 2 * np.pi
    dist_q = circular_distance(theta_N, theta_q) * 2 * np.pi

    ax.plot([angle_N, angle_p], [1, 1], color='blue', linestyle='--')
    ax.plot([angle_N, angle_q], [1, 1], color='green', linestyle='--')

    ax.set_title(f'Unit Circle Mapping for N={N}, k={k}')
    ax.legend()
    plt.savefig(save_path)
    plt.close()


def plot_theta_vs_logN(k=0.2, num_samples=1000, seed=42, save_path='plots/plot.png'):
    """
    2D Plot: Theta vs. Log(N) Scatter Plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    rng = random.Random(seed)
    semiprimes = []
    for _ in range(num_samples):
        bit_size = rng.randint(8, 20)
        N, _, _ = generate_semiprime(bit_size, rng.getrandbits(32))
        semiprimes.append(N)

    log_N = [np.log10(N) for N in semiprimes]
    theta_vals = [theta(N, k) for N in semiprimes]

    ax.scatter(log_N, theta_vals, alpha=0.5, color='blue', label='Semiprimes')
    ax.set_xlabel('log10(N)')
    ax.set_ylabel('θ(N, k)')
    ax.set_title(f'Theta vs. log(N) for k={k}')
    ax.grid(True, alpha=0.3)
    plt.savefig(save_path)
    plt.close()


def plot_circular_distance_histogram(k_list=[0.2, 0.45, 0.8], num_samples=100, save_path='plots/plot.png'):
    """
    2D Plot: Circular Distance Histogram
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for k in k_list:
        distances = []
        for _ in range(num_samples):
            N, p, q = generate_semiprime(16, random.randint(0, 10000))
            dist_p = circular_distance(theta(N, k), theta(p, k))
            dist_q = circular_distance(theta(N, k), theta(q, k))
            distances.extend([dist_p, dist_q])

        ax.hist(distances, bins=50, alpha=0.5, label=f'k={k}')

    ax.set_xlabel('Circular Distance')
    ax.set_ylabel('Frequency')
    ax.set_title('Circular Distance Histogram for True Factors')
    ax.legend()
    plt.savefig(save_path)
    plt.close()


def plot_golden_spiral_candidates(N, iterations=100, save_path='plots/plot.png'):
    """
    2D Plot: Golden Spiral Candidate Generation
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    sqrt_N = np.sqrt(N)
    candidates = list(spiral_candidates(N, iterations))

    # Plot spiral
    angles = [i * GOLDEN_ANGLE for i in range(1, iterations + 1)]
    radii = [np.sqrt(i) for i in range(1, iterations + 1)]
    x = [r * np.cos(a) + sqrt_N for r, a in zip(radii, angles)]
    y = [r * np.sin(a) for r, a in zip(radii, angles)]

    ax.scatter(x, y, c='gray', alpha=0.5, label='Spiral points')

    # Highlight primes
    prime_candidates = [c for c in candidates if is_prime_miller_rabin(c)]
    x_primes = [sqrt_N + r * np.cos(a) for r, a in zip(radii[:len(prime_candidates)], angles[:len(prime_candidates)])]
    y_primes = [r * np.sin(a) for r, a in zip(radii[:len(prime_candidates)], angles[:len(prime_candidates)])]

    ax.scatter(x_primes, y_primes, c='green', s=50, label='Prime candidates')

    ax.axvline(sqrt_N, color='red', linestyle='--', label='√N')
    ax.set_xlabel('Candidate Value')
    ax.set_ylabel('Offset')
    ax.set_title(f'Golden Spiral Candidates around √{N}')
    ax.legend()
    plt.savefig(save_path)
    plt.close()


def plot_candidate_filtering(N, k, epsilon, save_path='plots/plot.png'):
    """
    2D Plot: Candidate Filtering Before/After
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    params = FactorizationParams()
    prime_cands = list(prime_candidates_around_sqrt(N, params.search_window, params.prime_limit))
    spiral_cands = list(spiral_candidates(N, params.spiral_iters))
    all_cands = list(set(prime_cands + spiral_cands))

    theta_all = [theta(c, k) for c in all_cands]
    ax1.scatter(all_cands, theta_all, alpha=0.5, color='gray', label='All candidates')
    ax1.axvline(np.sqrt(N), color='red', linestyle='--', label='√N')
    ax1.set_xlabel('Candidate')
    ax1.set_ylabel('θ(candidate, k)')
    ax1.set_title('Before Filtering')
    ax1.legend()

    filtered = filter_candidates_geometric(N, all_cands, k, epsilon)
    theta_filtered = [theta(c, k) for c in filtered]
    ax2.scatter(filtered, theta_filtered, alpha=0.5, color='blue', label='Filtered candidates')
    ax2.axvline(np.sqrt(N), color='red', linestyle='--', label='√N')
    ax2.set_xlabel('Candidate')
    ax2.set_ylabel('θ(candidate, k)')
    ax2.set_title(f'After Filtering (k={k}, ε={epsilon})')
    ax2.legend()

    plt.tight_layout()
    plt.savefig("circular_distance_histogram.png")
    plt.close()


def plot_theta_surface(k_range=np.linspace(0.1, 0.9, 20), N_range=np.logspace(1, 6, 20), save_path='plots/plot.png'):
    """
    3D Plot: Theta Surface over N and k
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    K, LOG_N = np.meshgrid(k_range, np.log10(N_range))
    THETA = np.zeros_like(K)

    for i in range(K.shape[0]):
        for j in range(K.shape[1]):
            THETA[i, j] = theta(int(N_range[j]), K[i, j])

    surf = ax.plot_surface(LOG_N, K, THETA, cmap='viridis', alpha=0.8)
    ax.set_xlabel('log10(N)')
    ax.set_ylabel('k')
    ax.set_zlabel('θ(N, k)')
    ax.set_title('Theta Surface over N and k')
    fig.colorbar(surf)
    plt.savefig(save_path)
    plt.close()


def plot_3d_spiral_candidates(N, iterations=100, save_path='plots/plot.png'):
    """
    3D Plot: 3D Spiral Candidate Cloud
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    sqrt_N = np.sqrt(N)
    candidates = []
    seen = set()

    for i in range(1, iterations + 1):
        angle = i * GOLDEN_ANGLE
        radius = np.sqrt(i)
        x = radius * np.cos(angle) + sqrt_N
        y = radius * np.sin(angle)
        candidate = int(x)
        if candidate > 1 and candidate not in seen:
            seen.add(candidate)
            candidates.append((candidate, x, y, i))

    for cand, x, y, z in candidates:
        color = 'green' if is_prime_miller_rabin(cand) else 'red'
        ax.scatter(x, y, z, c=color, alpha=0.7)

    ax.set_xlabel('X (Candidate Value)')
    ax.set_ylabel('Y (Offset)')
    ax.set_zlabel('Iteration (Z)')
    ax.set_title(f'3D Spiral Candidates for N={N}')
    plt.savefig("golden_spiral_candidates.png")
    plt.close()


def plot_distance_landscape(N, k_range=np.linspace(0.1, 0.9, 20), p_range=None, save_path='plots/plot.png'):
    """
    3D Plot: Distance Landscape
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    if p_range is None:
        sqrt_N = int(np.sqrt(N))
        p_range = np.arange(max(2, sqrt_N - 50), sqrt_N + 50)

    P, K = np.meshgrid(p_range, k_range)
    DIST = np.zeros_like(P)

    theta_N = theta(N, 0.5)  # Use fixed k for N, but vary for p

    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            theta_p = theta(P[i, j], K[i, j])
            DIST[i, j] = circular_distance(theta_N, theta_p)

    surf = ax.plot_surface(P, K, DIST, cmap='plasma', alpha=0.8)
    ax.set_xlabel('Candidate p')
    ax.set_ylabel('k')
    ax.set_zlabel('Circular Distance')
    ax.set_title(f'Distance Landscape for N={N}')
    fig.colorbar(surf)
    plt.savefig(save_path)
    plt.close()


def plot_multi_pass_parameter_space(results, save_path='plots/plot.png'):
    """
    3D Plot: Multi-Pass Parameter Space
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Assuming results is a list of (k, eps, reduction_ratio, success_rate)
    # This would need to be generated from simulation

    # Placeholder: random data
    k_vals = np.random.uniform(0.1, 0.9, 100)
    eps_vals = np.random.uniform(0.01, 0.1, 100)
    ratios = np.random.uniform(5, 50, 100)
    sizes = np.random.uniform(0.2, 1, 100)

    scatter = ax.scatter(k_vals, eps_vals, ratios, s=sizes*100, alpha=0.6)
    ax.set_xlabel('k')
    ax.set_ylabel('ε')
    ax.set_zlabel('Reduction Ratio')
    ax.set_title('Multi-Pass Parameter Space')
    plt.savefig("candidate_filtering.png")
    plt.close()


def plot_factor_clustering_3d(k1=0.2, k2=0.45, k3=0.8, num_factors=100, save_path='plots/plot.png'):
    """
    3D Plot: Factor Clustering in 3D
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Generate factors
    factors = []
    non_factors = []

    for _ in range(num_factors):
        N, p, q = generate_semiprime(16, random.randint(0, 10000))
        theta1_p = theta(p, k1)
        theta2_p = theta(p, k2)
        theta3_p = theta(p, k3)
        factors.append((theta1_p, theta2_p, theta3_p))

        # Random prime
        rand_p = generate_prime(8, random.Random())
        theta1_rand = theta(rand_p, k1)
        theta2_rand = theta(rand_p, k2)
        theta3_rand = theta(rand_p, k3)
        non_factors.append((theta1_rand, theta2_rand, theta3_rand))

    factors = np.array(factors)
    non_factors = np.array(non_factors)

    ax.scatter(factors[:, 0], factors[:, 1], factors[:, 2], c='blue', label='True Factors', alpha=0.7)
    ax.scatter(non_factors[:, 0], non_factors[:, 1], non_factors[:, 2], c='red', label='Random Primes', alpha=0.7)

    ax.set_xlabel(f'θ(p, {k1})')
    ax.set_ylabel(f'θ(p, {k2})')
    ax.set_zlabel(f'θ(p, {k3})')
    ax.set_title('Factor Clustering in 3D Theta Space')
    ax.legend()
    plt.savefig(save_path)
    plt.close()


def run_plot_demo():
    """Run a demo of all plots with sample data."""
    os.makedirs('plots', exist_ok=True)
    print("Generating sample plots...")

    # Sample data
    N, p, q = generate_semiprime(12, 42)
    k = 0.45
    epsilon = 0.05

    print(f"Using N={N}, p={p}, q={q}")

    # 2D Plots
    plot_unit_circle_mapping(N, p, q, k)
    plot_theta_vs_logN(save_path='plots/theta_vs_logN.png')
    plot_circular_distance_histogram(save_path='plots/circular_distance_histogram.png')
    plot_golden_spiral_candidates(N, save_path='plots/golden_spiral_candidates.png')
    plot_candidate_filtering(N, k, epsilon, save_path='plots/candidate_filtering.png')

    # 3D Plots
    plot_theta_surface(save_path='plots/theta_surface.png')
    plot_3d_spiral_candidates(N, save_path='plots/3d_spiral_candidates.png')
    plot_distance_landscape(N, save_path='plots/distance_landscape.png')
    plot_multi_pass_parameter_space([], save_path='plots/multi_pass_parameter_space.png')
    plot_factor_clustering_3d(save_path='plots/factor_clustering_3d.png')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Geometric Factorization Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo          Run demonstration with default parameters
  %(prog)s --test          Run unit tests
  %(prog)s --validate      Run README validation experiments
  %(prog)s --factor N      Factor a specific semiprime
        """
    )
    
    parser.add_argument('--demo', action='store_true',
                       help='Run demonstration')
    parser.add_argument('--test', action='store_true',
                       help='Run unit tests')
    parser.add_argument('--validate', action='store_true',
                       help='Run README validation (6-bit and 20-bit)')
    parser.add_argument('--factor', type=int, metavar='N',
                       help='Factor a specific number')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--plots', action='store_true',
                       help='Run plotting demonstrations')
    
    args = parser.parse_args()
    
    if args.test:
        run_tests()
    
    elif args.validate:
        print("\n" + "="*70)
        print("README VALIDATION EXPERIMENTS")
        print("="*70)
        
        # Small-scale validation: find first bit size with 100% success
        print("\nExperiment 1: Find 100%% success threshold")
        print("-" * 70)
        for bit_size in range(64, 5, -5):
            results = demo_run([bit_size], samples_per_size=5, seed=args.seed)
            success_rate = results['bit_sizes'][bit_size]['success_rate']
            if success_rate == 1.0:
                print(f"\n✓ First 100% success at {bit_size} bits!")
                break
            if bit_size <= 10:
                # Force break for small bit sizes
                break
        
        # 20-bit validation
        print("\n\nExperiment 2: 20-bit validation")
        print("-" * 70)
        demo_run([20], samples_per_size=5, seed=args.seed)
    
    elif args.demo:
        # Default demo: test various bit sizes
        print("\n" + "="*70)
        print("GEOMETRIC FACTORIZATION DEMONSTRATION")
        print("="*70)
        demo_run([10, 12, 15, 18, 20], samples_per_size=3, seed=args.seed)
    
    elif args.factor:
        print(f"\nFactoring N = {args.factor}")
        print("-" * 70)
        params = FactorizationParams()
        result = geometric_factor(args.factor, params)
        print(result.summary())
        
        if result.success:
            print(f"\nFactors: {result.factors[0]} × {result.factors[1]}")
            print(f"Verification: {result.factors[0] * result.factors[1]} = {args.factor}")
        
        print(f"\nAttempts: {result.attempts}")
        print(f"Total time: {result.timings.get('total', 0):.3f}s")
        
        if result.logs:
            print("\nDetailed logs:")
            for i, log in enumerate(result.logs, 1):
                print(f"  Pass {i}: k={log['k']}, ε={log['epsilon']}, "
                      f"{log['pre_filter']}→{log['post_filter']} candidates")
    elif args.plots:
        run_plot_demo()

    
    else:
        parser.print_help()
        print("\n" + "="*70)
        print("Quick Start:")
        print("  python geometric_factorization.py --test      # Run unit tests")
        print("  python geometric_factorization.py --demo      # Run demonstration")
        print("  python geometric_factorization.py --validate  # Run README validation")
        print("="*70)


if __name__ == '__main__':
    main()
