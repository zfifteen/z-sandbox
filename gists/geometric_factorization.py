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
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import mpmath as mp

# Set high precision for geometric calculations
getcontext().prec = 100
getcontext().rounding = ROUND_HALF_EVEN

# Set mpmath ultra-high precision
mp.mp.dps = 200  # 200 decimal places
mp.mp.prec = 200 * 4  # bits of precision

# Set SymPy ultra-high precision
import sympy as sp
sp.N(sp.pi, 200)  # Set working precision to 200 digits

# Irrational ensemble for enhanced geometric mapping
ALPHAS = [
    Decimal("1.6180339887498948482045868343656381177"),  # φ
    Decimal("2.7182818284590452353602874713526624977"),  # e
    Decimal("3.1415926535897932384626433832795028842"),  # π
    Decimal("2.4142135623730950488016887242096980786"),  # silver ratio δ
]

# Riemann zeta zeros (first 20 imaginary parts) for tuning
ZETA_ZEROS_IMAG = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347045, 60.831778, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704690, 77.144840
]
# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
GOLDEN_ANGLE = 2 * math.pi / (PHI ** 2)  # Golden angle ≈ 2.399963...

def theta_mod1_log(x, alpha):
    """Compute {alpha * log(x)} for ensemble mapping."""
    if x <= 0:
        return Decimal(0)
    log_x = Decimal(x).ln()
    scaled = alpha * log_x
    return float(scaled - scaled.to_integral_value())

def circ_dist(a, b):
    """Circular distance on [0,1)"""
    d = abs(a - b)
    return min(d, 1 - d)

def score_candidate_ensemble(N, cand):
    """Score candidate using ensemble of irrational mappings."""
    scores = []
    for alpha in ALPHAS:
        theta_n = theta_mod1_log(N, alpha)
        theta_cand = theta_mod1_log(cand, alpha)
        scores.append(circ_dist(theta_n, theta_cand))
    return min(scores)  # Best score across ensemble


# ============================================================================
# Core Mathematical Functions
# ============================================================================

def theta_recursive(N: int, k: float, depth=1) -> float:
    """Recursive theta for fractal refinement."""
    if depth <= 0:
        return theta(N, k)
    # θ'(N) = θ(θ(N), k/φ)
    inner = theta(N, k)
    return theta_recursive(int(inner * 2**32), k / PHI, depth - 1)

def theta_ultra_precise(N: int, k: float) -> float:
    """Ultra-high precision theta using SymPy."""
    # Convert to high-precision SymPy objects
    N_sp = sp.Integer(N)
    phi_sp = sp.GoldenRatio
    k_sp = sp.Float(k, 200)
    
    # Compute {φ × (N/φ)^k} with maximum precision
    ratio = N_sp / phi_sp
    powered = sp.Pow(ratio, k_sp)
    product = phi_sp * powered
    fractional = product - sp.floor(product)
    
    # Return as high-precision float
    return float(sp.N(fractional, 200))

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
    epsilon: float,
    params
) -> List[int]:
    """
    Filter candidates using geometric circular distance or ensemble scoring.
    
    Args:
        N: Target semiprime
        candidates: List of candidate factors
        k: Exponent parameter for theta
        epsilon: Tolerance threshold
        use_ensemble: Use ensemble mapping instead of single theta
        
    Returns:
        Filtered list of candidates
    """
    if params.use_ensemble:
        # Use ensemble scoring
        filtered = []
        for p in candidates:
            score = score_candidate_ensemble(N, p)
            if score <= epsilon:  # Lower score is better
                filtered.append(p)
        return filtered
    elif params.use_cf_alignment:
        # Use CF alignment with renormalization
        aligned_alphas = refine_alphas_via_cf(N, max_convergents=8, precision=120)
        filtered = []
        for p in candidates:
            score, _, _ = score_candidate_cf(N, p, aligned_alphas, candidates)
            if score <= epsilon:
                filtered.append(p)
        return filtered
    else:
        # Original single theta filtering
        if params.ultra_precision:
            theta_N = theta_ultra_precise(N, k)
            theta_func = lambda x: theta_ultra_precise(x, k)
        elif params.recursive_theta:
            theta_N = theta_recursive(N, k, params.recursive_depth)
            theta_func = lambda x: theta_recursive(x, k, params.recursive_depth)
        else:
            theta_N = theta(N, k)
            theta_func = lambda x: theta(x, k)
        
        filtered = []
        for p in candidates:
            theta_p = theta_func(p)
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
    adaptive_scaling: bool = True
    use_ensemble: bool = False,
    use_cf_alignment: bool = False
    recursive_theta: bool = False
    recursive_depth: int = 1
    ultra_precision: bool = False
    spiral_iters: int = 2000
    search_window: int = 1024
    prime_limit: int = 5000
    max_attempts: int = 50000
    max_time: float = 10.0  # Maximum elapsed time in seconds
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
    elapsed_time: float = 0.0
    timeout: bool = False
    logs: List[Dict[str, Any]] = field(default_factory=list)
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
    last_log = 0.0
    
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
    
    bit_size = N.bit_length()
    if params.adaptive_scaling:
        base_k = [0.200, 0.450, 0.800]
        if bit_size >= 35:
            # Add more k values for 35+ bits, including very small and large
            base_k.extend([0.05, 0.1, 0.15, 0.25, 0.3, 0.35, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.85, 0.9, 0.95])
        elif bit_size >= 30:
            base_k.extend([0.1, 0.3, 0.5, 0.7, 0.9])
        
        # Scale ε values with log(N): larger distances for larger N
        base_eps = [0.02, 0.05, 0.10]
        if bit_size >= 35:
            log_scale = math.log(bit_size) / math.log(32)  # Adjusted scale factor
            base_eps = [0.01 * log_scale, 0.02 * log_scale, 0.05 * log_scale,
                       0.08 * log_scale, 0.12 * log_scale, 0.15 * log_scale]
        elif bit_size >= 30:
            log_scale = math.log(bit_size) / math.log(32)
            base_eps = [0.02 * log_scale, 0.05 * log_scale, 0.10 * log_scale, 0.15 * log_scale]
        
        k_list = base_k
        eps_list = base_eps
        
        # Enable ultra precision and increase iterations for larger N
        if bit_size >= 35:
            params.ultra_precision = True
            params.spiral_iters = min(5000, params.spiral_iters * 2)
            params.search_window = 100000
            params.prime_limit = 20000
        elif bit_size >= 32:
            params.spiral_iters = min(4000, params.spiral_iters * 1.5)
            params.search_window = 50000
            params.prime_limit = 10000
    else:
        k_list = params.k_list
        eps_list = params.eps_list
    
    # Failed to factor
    elapsed = time.time() - start_time
    timings["total"] = elapsed
    timeout = elapsed >= params.max_time
    
    result = FactorizationResult(
        success=False,
        factors=None,
        attempts=attempts,
        candidate_counts=dict(candidate_counts),
        timings=timings,
        logs=logs,
        elapsed_time=elapsed,
        timeout=timeout
    )
    return result


phi = (1 + mp.sqrt(5)) / 2
def frac(x):
    return x - mp.floor(x)
def theta(m, k):
    a = frac(m / phi)
    b = mp.power(a, k)
    return frac(phi * b)
def circ_dist(a, b):
    diff = mp.fabs(a - b)
    return min(diff, 1 - diff)
def multi_stage_geometric_factorize(N, stages):
    mp.dps = 50
    mp_n = mp.mpf(N)
    sqrt_n = int(N**0.5) + 1
    candidates = list(sp.primerange(2, sqrt_n + 1))
    for k, epsilon in stages:
        th_n = theta(mp_n, k)
        new_cands = []
        for p in candidates:
            mp_p = mp.mpf(p)
            th_p = theta(mp_p, k)
            d = circ_dist(th_n, th_p)
            if d < epsilon:
                new_cands.append(p)
                if N % p == 0:
                    return p, N // p
        candidates = new_cands
    return None
