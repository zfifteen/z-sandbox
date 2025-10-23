#!/usr/bin/env python3
"""
Geometry gate function based on θ′ (theta_prime).
Determines whether a target should receive full ECM spend based on its geometric properties.
"""

import math
from mpmath import mp, mpf, frac, fmod

mp.dps = 100

PHI = (1 + mpf(5).sqrt()) / 2


def theta_prime(n, k=0.3):
    """
    Compute θ′(n, k) = φ · (frac(n/φ))^k
    
    This is the core geometric transformation used for gating.
    
    Args:
        n: The number to transform
        k: The exponent parameter (default 0.3)
    
    Returns:
        The θ′ value as a float
    """
    if n < 2:
        raise ValueError('n must be >= 2')
    
    n_mpf = mpf(n)
    k_mpf = mpf(k)
    
    # Compute frac(n / φ)
    mod_phi = fmod(n_mpf, PHI)
    ratio = mod_phi / PHI
    
    # θ′(n, k) = φ · ratio^k
    theta = PHI * (ratio ** k_mpf)
    
    return float(theta)


def gate_by_theta_prime(N, p=None, q=None, width_factor=0.155, k=0.3):
    """
    Gate function based on θ′ geometry.
    
    Determines if a semiprime N should receive full ECM spend based on
    whether its factors fall within a geometric window around θ′(N).
    
    Args:
        N: The semiprime to test
        p, q: Optional known factors (for validation/testing)
        width_factor: Width of the acceptance window (default 0.155)
        k: θ′ exponent parameter (default 0.3)
    
    Returns:
        True if gated (should receive full spend), False otherwise
    """
    # Compute θ′(N)
    theta_N = theta_prime(N, k=k)
    
    # Compute acceptance bounds
    bound_lower = theta_N - width_factor / 2
    bound_upper = theta_N + width_factor / 2
    
    # If we know the factors, check if they fall within bounds
    if p is not None and q is not None:
        theta_p = theta_prime(p, k=k)
        theta_q = theta_prime(q, k=k)
        
        # Gate passes if either factor's θ′ is within bounds
        p_in_bounds = bound_lower <= theta_p <= bound_upper
        q_in_bounds = bound_lower <= theta_q <= bound_upper
        
        return p_in_bounds or q_in_bounds
    
    # If we don't know factors, we need to use other heuristics
    # For now, always return True to allow ECM to run
    # (In practice, you might use additional geometric properties)
    return True


def estimate_gate_probability(N, width_factor=0.155, k=0.3):
    """
    Estimate the probability that a random semiprime of size N
    would pass the geometric gate.
    
    This is useful for understanding the selectivity of the gate.
    
    Args:
        N: Size of semiprime
        width_factor: Width of acceptance window
        k: θ′ exponent parameter
    
    Returns:
        Estimated probability (0 to 1)
    """
    # The probability is roughly proportional to the width_factor
    # relative to the range of possible θ′ values
    
    # θ′ values are bounded by [0, φ] in the limit
    # So the probability is approximately width_factor / φ
    
    max_theta = float(PHI)
    prob = width_factor / max_theta
    
    # Adjust for the fact that not all values are equally likely
    # (This is a rough approximation)
    return min(1.0, prob * 2)


def compute_gate_metadata(N, p, q, width_factor=0.155, k=0.3):
    """
    Compute detailed metadata about gate decision for a target.
    
    Args:
        N: The semiprime
        p, q: Known factors
        width_factor: Width of acceptance window
        k: θ′ exponent parameter
    
    Returns:
        Dictionary with gate metadata
    """
    theta_N = theta_prime(N, k=k)
    theta_p = theta_prime(p, k=k)
    theta_q = theta_prime(q, k=k)
    
    bound_lower = theta_N - width_factor / 2
    bound_upper = theta_N + width_factor / 2
    
    p_in_bounds = bound_lower <= theta_p <= bound_upper
    q_in_bounds = bound_lower <= theta_q <= bound_upper
    gated = p_in_bounds or q_in_bounds
    
    return {
        "theta_N": theta_N,
        "theta_p": theta_p,
        "theta_q": theta_q,
        "bound_lower": bound_lower,
        "bound_upper": bound_upper,
        "p_in_bounds": p_in_bounds,
        "q_in_bounds": q_in_bounds,
        "gated": gated,
        "width_factor": width_factor,
        "k": k
    }


if __name__ == "__main__":
    # Test the gate function
    print("Testing θ′ gate function\n")
    
    # Example: 1000
    n_example = 1000
    theta = theta_prime(n_example)
    print(f"θ′({n_example}) = {theta:.6f}")
    
    width = 0.155
    bound_lower = theta - width / 2
    bound_upper = theta + width / 2
    print(f"Bounds with width={width}: [{bound_lower:.6f}, {bound_upper:.6f}]")
    
    # Example semiprime
    p = 1009
    q = 1013
    N = p * q
    print(f"\nTest semiprime: N = {p} × {q} = {N}")
    
    metadata = compute_gate_metadata(N, p, q, width_factor=width)
    print(f"θ′(N) = {metadata['theta_N']:.6f}")
    print(f"θ′(p) = {metadata['theta_p']:.6f} - in bounds: {metadata['p_in_bounds']}")
    print(f"θ′(q) = {metadata['theta_q']:.6f} - in bounds: {metadata['q_in_bounds']}")
    print(f"Gate decision: {metadata['gated']}")
    
    # Test probability estimate
    prob = estimate_gate_probability(N, width_factor=width)
    print(f"\nEstimated gate probability: {prob:.2%}")
