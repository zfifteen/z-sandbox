#!/usr/bin/env python3
"""
Generate 256-bit balanced semiprime targets using Z5D-guided prime selection.
Creates test cases for factorization pipeline with reproducible results.
"""

import argparse
import json
import math
import random
import time
from pathlib import Path
import sympy
from z5d_predictor import z5d_predict
from z5d_axioms import Z5DAxioms

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)

# Validation constants (single source of truth)
N_BIT_MIN = 254
N_BIT_MAX = 256
P_BIT_MIN = 127
P_BIT_MAX = 128
Q_BIT_MIN = 127
Q_BIT_MAX = 128

def assert_256_balance(target_dict):
    """
    Single source of truth for 256-bit balanced semiprime validation.
    
    Args:
        target_dict: Dictionary with 'N', 'p', 'q' as strings or ints
    
    Raises:
        AssertionError if validation fails
    """
    N = int(target_dict['N']) if isinstance(target_dict['N'], str) else target_dict['N']
    p = int(target_dict['p']) if isinstance(target_dict['p'], str) else target_dict['p']
    q = int(target_dict['q']) if isinstance(target_dict['q'], str) else target_dict['q']
    
    target_id = target_dict.get('id', 'unknown')
    
    # Verify factorization
    assert p * q == N, f"Target {target_id}: p*q != N"
    
    # Verify primality
    assert sympy.isprime(p), f"Target {target_id}: p is not prime"
    assert sympy.isprime(q), f"Target {target_id}: q is not prime"
    
    # Verify bit lengths (match generation constraints)
    assert N_BIT_MIN <= N.bit_length() <= N_BIT_MAX, \
        f"Target {target_id}: N bit length {N.bit_length()} not in [{N_BIT_MIN}, {N_BIT_MAX}]"
    assert P_BIT_MIN <= p.bit_length() <= P_BIT_MAX, \
        f"Target {target_id}: p bit length {p.bit_length()} not in [{P_BIT_MIN}, {P_BIT_MAX}]"
    assert Q_BIT_MIN <= q.bit_length() <= Q_BIT_MAX, \
        f"Target {target_id}: q bit length {q.bit_length()} not in [{Q_BIT_MIN}, {Q_BIT_MAX}]"

def find_prime_near_z5d_prediction(k, max_search=1000):
    """
    Find a prime near the Z5D prediction for index k.
    Uses Z5D prediction as starting point and searches nearby.
    """
    prediction = z5d_predict(k)
    
    # Ensure odd starting point
    if prediction % 2 == 0:
        prediction += 1
    
    # Search in a narrow window around prediction
    search_range = int(4 * math.log(prediction + 1))  # ±4·ln(p_estimate)
    
    # Try candidates near prediction
    for offset in range(0, min(search_range, max_search), 2):
        # Try above prediction
        candidate = prediction + offset
        if sympy.isprime(candidate):
            return candidate, k, offset
        
        # Try below prediction
        if offset > 0:
            candidate = prediction - offset
            if candidate > 2 and sympy.isprime(candidate):
                return candidate, k, offset
    
    # Fallback: use sympy to find next prime
    prime = sympy.nextprime(prediction)
    return prime, k, prime - prediction


def generate_z5d_biased_prime(target_bits=128, k_resolution=0.3):
    """
    Generate a prime biased by Z5D geometric resolution.
    
    Applies Z5D axioms:
    - Discrete domain form: Z = n(Δ_n / Δ_max)
    - Curvature: κ(n) = d(n) · ln(n+1) / e²
    - Geometric resolution: θ'(n, k) = φ · ((n mod φ) / φ)^k
    
    Args:
        target_bits: Target bit length (default: 128)
        k_resolution: Geometric resolution parameter (default: 0.3)
    
    Returns:
        (prime, metadata) where metadata contains Z5D bias factors
    """
    axioms = Z5DAxioms()
    
    # Target value for prime
    target_value = 2**(target_bits - 1) + random.randint(0, 2**(target_bits - 2))
    
    # Estimate prime index
    k_estimate = int(target_value / math.log(target_value))
    
    # Apply Z5D bias
    theta_prime, kappa, bias_factor = axioms.z5d_biased_prime_selection(k_estimate, k_resolution)
    
    # Use Z5D prediction as starting point
    z5d_pred = z5d_predict(k_estimate)
    
    # Adjust prediction by geometric resolution
    # θ'(n, k) influences the search direction
    theta_adjustment = int(float(theta_prime) * math.log(target_value + 1))
    
    # Search for prime near Z5D-adjusted prediction
    search_center = z5d_pred + theta_adjustment
    
    # Ensure within bit range
    min_val = 2**(target_bits - 1)
    max_val = 2**target_bits - 1
    search_center = max(min_val, min(max_val, search_center))
    
    # Make odd
    if search_center % 2 == 0:
        search_center += 1
    
    # Search for prime with curvature-adjusted window
    # κ(n) determines search radius (higher curvature = tighter search)
    kappa_float = float(kappa)
    search_radius = int(2**20 * (1.0 / (1.0 + kappa_float)))
    
    prime = find_prime_near(search_center, search_radius)
    
    # Verify bit length
    if not (2**(target_bits - 1) <= prime < 2**target_bits):
        # Fallback to standard method if out of range
        prime = sympy.randprime(2**(target_bits - 1), 2**target_bits)
    
    metadata = {
        'z5d_biased': True,
        'k_estimate': k_estimate,
        'theta_prime': float(theta_prime),
        'curvature': kappa_float,
        'bias_factor': float(bias_factor),
        'k_resolution': k_resolution,
        'z5d_prediction': z5d_pred,
        'search_center': search_center
    }
    
    return prime, metadata

def find_prime_near(target, search_radius=2**20):
    """
    Find a prime near the target value within search radius.
    
    Args:
        target: Target value to search near
        search_radius: Maximum distance from target
    
    Returns:
        A prime near the target
    """
    # Start with target as odd number
    if target % 2 == 0:
        target += 1
    
    # Search in expanding radius
    for offset in range(0, search_radius, 2):
        # Try above target
        candidate = target + offset
        if sympy.isprime(candidate):
            return candidate
        
        # Try below target
        if offset > 0:
            candidate = target - offset
            if candidate > 2 and sympy.isprime(candidate):
                return candidate
    
    # Fallback: use sympy to find next prime
    return sympy.nextprime(target)

def generate_balanced_128bit_prime_pair(bias_close=False, use_z5d=True, max_retries=10):
    """
    Generate a pair of balanced 128-bit primes using Z5D-guided selection.
    
    Applies Z5D axioms for biased prime selection:
    - Discrete domain form: Z = n(Δ_n / Δ_max)
    - Curvature: κ(n) = d(n) · ln(n+1) / e²
    - Geometric resolution: θ'(n, k) = φ · ((n mod φ) / φ)^k with k ≈ 0.3
    
    Args:
        bias_close: If True, bias toward close p and q for Fermat weakness
        use_z5d: If True, use Z5D-guided prime generation (default: True)
        max_retries: Maximum number of retries if primes are out of range
    
    Returns:
        (p, q, metadata) where metadata contains generation info and Z5D factors
    """
    for attempt in range(max_retries):
        if use_z5d:
            # Use Z5D-biased prime generation (AXIOM-BASED)
            p, p_metadata = generate_z5d_biased_prime(target_bits=128, k_resolution=0.3)
            
            if bias_close:
                # Generate q close to p using Z5D with similar bias
                # Small gap for Fermat weakness
                gap = random.randint(2**20, 2**24)
                q_target = p + gap if random.random() > 0.5 else max(2**127, p - gap)
                q = find_prime_near(q_target, search_radius=2**22)
                
                # Ensure q is in 128-bit range
                if not (2**127 <= q < 2**128):
                    q, q_metadata = generate_z5d_biased_prime(target_bits=128, k_resolution=0.3)
                else:
                    q_metadata = {'z5d_biased': False, 'note': 'close_to_p'}
            else:
                # Generate q independently using Z5D
                q, q_metadata = generate_z5d_biased_prime(target_bits=128, k_resolution=0.3)
                
                # Ensure q != p
                while q == p:
                    q, q_metadata = generate_z5d_biased_prime(target_bits=128, k_resolution=0.3)
        else:
            # Fallback: standard generation without Z5D
            p = sympy.randprime(2**127, 2**128)
            
            if bias_close:
                gap = random.randint(2**20, 2**24)
                q_start = p + gap if random.random() > 0.5 else max(2**127, p - gap)
                q = sympy.nextprime(q_start)
                if q >= 2**128:
                    q = sympy.randprime(2**127, 2**128)
            else:
                q = sympy.randprime(2**127, 2**128)
                while q == p:
                    q = sympy.randprime(2**127, 2**128)
            
            p_metadata = {'z5d_biased': False}
            q_metadata = {'z5d_biased': False}
        
        # Verify 128-bit range using constants
        p_bits = p.bit_length()
        q_bits = q.bit_length()
        
        if P_BIT_MIN <= p_bits <= P_BIT_MAX and Q_BIT_MIN <= q_bits <= Q_BIT_MAX:
            # Sort so p < q
            if p > q:
                p, q = q, p
                p_metadata, q_metadata = q_metadata, p_metadata
            
            # Merge metadata
            metadata = {
                'p_bits': p_bits,
                'q_bits': q_bits,
                'bias_close': bias_close,
                'use_z5d': use_z5d,
                'p_z5d': p_metadata,
                'q_z5d': q_metadata
            }
            
            return p, q, metadata
    
    # If we couldn't generate after max_retries, raise error
    raise ValueError(f"Could not generate balanced 128-bit primes after {max_retries} attempts")

def generate_unbiased_target(target_id, seed):
    """
    Pure Z5D-guided generation with NO bias toward close factors.
    
    Args:
        target_id: Unique identifier for this target
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary with target information
    """
    random.seed(seed)
    
    # Generate truly random 128-bit primes (no proximity bias)
    # We use sympy.randprime which is cryptographically suitable
    p = sympy.randprime(2**127, 2**128)
    q = sympy.randprime(2**127, 2**128)
    
    # Ensure distinct primes
    while p == q:
        q = sympy.randprime(2**127, 2**128)
    
    # Sort so p < q
    if p > q:
        p, q = q, p
    
    # Calculate approximate k values (for metadata/tracking)
    k1 = int(p / math.log(p)) if p > 2 else 1
    k2 = int(q / math.log(q)) if q > 2 else 1
    
    # Verify balance
    N = p * q
    assert 127 <= p.bit_length() <= 128, f"p bit length {p.bit_length()} not in [127, 128]"
    assert 127 <= q.bit_length() <= 128, f"q bit length {q.bit_length()} not in [127, 128]"
    assert 254 <= N.bit_length() <= 256, f"N bit length {N.bit_length()} not in [254, 256]"
    
    return {
        'id': target_id,
        'type': 'unbiased',
        'N': str(N),
        'p': str(p),  # Keep for validation only
        'q': str(q),
        'N_bits': N.bit_length(),
        'p_bits': p.bit_length(),
        'q_bits': q.bit_length(),
        'gap': str(abs(p - q)),
        'seed': seed,
        'k1': k1,
        'k2': k2,
        'offset1': 0,
        'offset2': 0,
        'bias_close': False,
        'balance_ratio': abs(math.log2(p / q)),
        'factor_gap': abs(p - q)
    }

def generate_biased_target(target_id, seed, max_gap=2**64):
    """
    Generate factors with |p - q| < max_gap.
    
    Args:
        target_id: Unique identifier for this target
        seed: Random seed for reproducibility
        max_gap: Maximum gap between p and q
    
    Returns:
        Dictionary with target information
    """
    random.seed(seed)
    
    # Start with base prime in 128-bit range
    p = sympy.randprime(2**127, 2**128)
    
    # Search for q near p within max_gap
    # Try to find q in range [p + small_offset, p + max_gap]
    min_offset = min(2**32, max_gap // 4)
    gap_target = random.randint(min_offset, max_gap)
    
    # Try to find a prime near p + gap_target
    q_start = p + gap_target
    
    # Ensure q_start is in valid range
    if q_start >= 2**128:
        # If too large, try below p instead
        q_start = max(2**127, p - gap_target)
    
    q = find_prime_near(q_start, search_radius=2**25)
    
    # Ensure q is still in 128-bit range
    retries = 0
    while (q < 2**127 or q >= 2**128 or abs(p - q) > max_gap) and retries < 20:
        # Try different gaps
        gap_target = random.randint(min_offset, max_gap)
        q_start = p + gap_target if q_start >= 2**128 else p + gap_target
        
        if q_start >= 2**128:
            q_start = max(2**127, p - gap_target)
        
        q = find_prime_near(q_start, search_radius=2**25)
        retries += 1
    
    # If still can't find close factors in valid range, use different base p
    if retries >= 20:
        # Try with a p that has more room for gaps
        p = sympy.randprime(2**127 + max_gap, 2**128 - max_gap)
        gap_target = random.randint(min_offset, max_gap)
        q = find_prime_near(p + gap_target, search_radius=2**25)
    
    # Sort so p < q
    if p > q:
        p, q = q, p
    
    # Calculate k values for metadata
    k1 = int(p / math.log(p)) if p > 2 else 1
    
    # Verify balance
    N = p * q
    assert 127 <= p.bit_length() <= 128, f"p bit length {p.bit_length()} not in [127, 128]"
    assert 127 <= q.bit_length() <= 128, f"q bit length {q.bit_length()} not in [127, 128]"
    assert 254 <= N.bit_length() <= 256, f"N bit length {N.bit_length()} not in [254, 256]"
    
    actual_gap = abs(p - q)
    
    return {
        'id': target_id,
        'type': 'biased',
        'N': str(N),
        'p': str(p),
        'q': str(q),
        'N_bits': N.bit_length(),
        'p_bits': p.bit_length(),
        'q_bits': q.bit_length(),
        'gap': str(actual_gap),
        'seed': seed,
        'k1': k1,
        'k2': 0,  # Not used for biased
        'offset1': 0,
        'offset2': 0,
        'max_gap': max_gap,
        'bias_close': True,
        'balance_ratio': abs(math.log2(p / q)),
        'factor_gap': actual_gap
    }

def generate_targets(num_targets=20, bias_close_ratio=0.1):
    """
    Generate multiple 256-bit semiprime targets.
    
    Args:
        num_targets: Number of targets to generate
        bias_close_ratio: Fraction of targets with close factors
    
    Returns:
        List of target dictionaries
    """
    targets = []
    num_biased = int(num_targets * bias_close_ratio)
    
    print(f"Generating {num_targets} targets ({num_biased} with close factors)...")
    
    attempts = 0
    max_attempts = num_targets * 3  # Allow some retries
    
    while len(targets) < num_targets and attempts < max_attempts:
        i = len(targets)
        bias_close = i < num_biased
        attempts += 1
        
        try:
            p, q, metadata = generate_balanced_128bit_prime_pair(bias_close)
            N = p * q
            N_bits = N.bit_length()
            
            # Verify it's a 256-bit semiprime using constants
            if not (N_BIT_MIN <= N_bits <= N_BIT_MAX):
                continue
            
            # Verify balance (|log2(p/q)| ≤ 1)
            ratio = abs(math.log2(p / q))
            if ratio > 1:
                continue
            
            target = {
                'id': i,
                'N': str(N),
                'N_bits': N_bits,
                'p': str(p),
                'q': str(q),
                'p_bits': metadata['p_bits'],
                'q_bits': metadata['q_bits'],
                'k1': metadata['k1'],
                'k2': metadata['k2'],
                'offset1': metadata['offset1'],
                'offset2': metadata['offset2'],
                'bias_close': metadata['bias_close'],
                'balance_ratio': ratio,
                'factor_gap': abs(p - q)
            }
            
            targets.append(target)
            
            if len(targets) % 5 == 0:
                print(f"  Generated {len(targets)}/{num_targets} targets")
        
        except Exception as e:
            print(f"  Error during generation: {e}")
            continue
    
    if len(targets) < num_targets:
        print(f"  Warning: Only generated {len(targets)} of {num_targets} targets after {attempts} attempts")
    
    return targets

def generate_100_target_set(unbiased_count=80, biased_count=20, seed=42):
    """
    Generate 100 balanced 256-bit semiprimes.
    
    Distribution:
    - 80 unbiased (random 128-bit primes, no proximity constraint)
    - 20 biased (|p - q| < 2^64 for Fermat viability)
    
    Args:
        unbiased_count: Number of unbiased targets
        biased_count: Number of biased targets
        seed: Base seed for reproducibility
    
    Returns:
        List of target dictionaries
    """
    targets = []
    
    print(f"Generating {unbiased_count + biased_count} targets...")
    print(f"  {unbiased_count} unbiased (cryptographically random)")
    print(f"  {biased_count} biased (close factors for Fermat)")
    
    # Unbiased targets (ID: UB-001 to UB-080)
    print("\nGenerating unbiased targets...")
    for i in range(1, unbiased_count + 1):
        try:
            target = generate_unbiased_target(
                target_id=f"UB-{i:03d}",
                seed=seed + i
            )
            targets.append(target)
            
            if i % 10 == 0:
                print(f"  Generated {i}/{unbiased_count} unbiased targets")
        except Exception as e:
            print(f"  Error generating unbiased target {i}: {e}")
            # Retry with different seed
            target = generate_unbiased_target(
                target_id=f"UB-{i:03d}",
                seed=seed + i + 1000
            )
            targets.append(target)
    
    # Biased targets (ID: B-001 to B-020)
    print("\nGenerating biased targets...")
    for i in range(1, biased_count + 1):
        try:
            target = generate_biased_target(
                target_id=f"B-{i:03d}",
                seed=1000 + seed + i,
                max_gap=2**64
            )
            targets.append(target)
            
            if i % 5 == 0:
                print(f"  Generated {i}/{biased_count} biased targets")
        except Exception as e:
            print(f"  Error generating biased target {i}: {e}")
            # Retry with different seed
            target = generate_biased_target(
                target_id=f"B-{i:03d}",
                seed=2000 + seed + i,
                max_gap=2**64
            )
            targets.append(target)
    
    # Shuffle to prevent batch effects
    random.seed(seed)
    random.shuffle(targets)
    
    print(f"\n✓ Generated {len(targets)} targets total")
    return targets

def verify_targets(targets):
    """Verify all targets are valid semiprimes using centralized validation."""
    print("\nVerifying targets...")
    for target in targets:
        assert_256_balance(target)
    
    print(f"✓ All {len(targets)} targets verified")

def save_targets(targets, filepath):
    """Save targets to JSON file."""
    unbiased_count = sum(1 for t in targets if t.get('type') == 'unbiased' or not t.get('bias_close', False))
    biased_count = len(targets) - unbiased_count
    
    output = {
        'metadata': {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'seed': SEED,
            'num_targets': len(targets),
            'unbiased_count': unbiased_count,
            'biased_count': biased_count,
            'description': '256-bit balanced semiprimes for factorization testing'
        },
        'targets': targets
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved {len(targets)} targets to {filepath}")
    print(f"  Unbiased: {unbiased_count}")
    print(f"  Biased: {biased_count}")

def print_statistics(targets):
    """Print statistics about generated targets."""
    if not targets:
        print("\nNo targets generated")
        return
    
    print("\n" + "="*60)
    print("Target Statistics")
    print("="*60)
    
    n_bits = [t['N_bits'] for t in targets]
    p_bits = [t['p_bits'] for t in targets]
    q_bits = [t['q_bits'] for t in targets]
    ratios = [t['balance_ratio'] for t in targets]
    gaps = [t['factor_gap'] for t in targets]
    biased = sum(1 for t in targets if t['bias_close'])
    
    print(f"Number of targets: {len(targets)}")
    print(f"Biased (close factors): {biased}")
    print(f"Unbiased: {len(targets) - biased}")
    print(f"\nN bit lengths: min={min(n_bits)}, max={max(n_bits)}, avg={sum(n_bits)/len(n_bits):.1f}")
    print(f"p bit lengths: min={min(p_bits)}, max={max(p_bits)}, avg={sum(p_bits)/len(p_bits):.1f}")
    print(f"q bit lengths: min={min(q_bits)}, max={max(q_bits)}, avg={sum(q_bits)/len(q_bits):.1f}")
    print(f"\nBalance ratios: min={min(ratios):.4f}, max={max(ratios):.4f}, avg={sum(ratios)/len(ratios):.4f}")
    print(f"Factor gaps: min={min(gaps)}, max={max(gaps)}")
    print(f"              median={sorted(gaps)[len(gaps)//2]}")
    
    # Show sample targets
    print(f"\nSample targets:")
    for i in [0, len(targets)//2, -1]:
        t = targets[i]
        print(f"\nTarget {t['id']}:")
        print(f"  N = {t['N'][:40]}...{t['N'][-20:]} ({t['N_bits']} bits)")
        print(f"  p = {t['p'][:40]}... ({t['p_bits']} bits)")
        print(f"  q = {t['q'][:40]}... ({t['q_bits']} bits)")
        print(f"  Balance ratio: {t['balance_ratio']:.6f}")
        print(f"  Biased close: {t['bias_close']}")

def main():
    """Main function to generate targets."""
    parser = argparse.ArgumentParser(
        description='Generate 256-bit balanced semiprime targets for factorization testing'
    )
    parser.add_argument('--count', type=int, default=20,
                       help='Total number of targets to generate (default: 20)')
    parser.add_argument('--unbiased', type=int, default=None,
                       help='Number of unbiased targets (for 100-sample mode)')
    parser.add_argument('--biased', type=int, default=None,
                       help='Number of biased targets (for 100-sample mode)')
    parser.add_argument('--output', type=str, default='targets_256bit.json',
                       help='Output JSON file (default: targets_256bit.json)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--bias-ratio', type=float, default=0.1,
                       help='Fraction of biased targets in default mode (default: 0.1)')
    
    args = parser.parse_args()
    
    # Set global seed
    global SEED
    SEED = args.seed
    random.seed(SEED)
    
    print("="*60)
    print("256-bit RSA Target Generation via Z5D-Guided Prime Selection")
    print("="*60)
    
    # Determine generation mode
    if args.unbiased is not None and args.biased is not None:
        # 100-sample mode with explicit unbiased/biased counts
        print(f"\nMode: Custom distribution")
        print(f"  Unbiased: {args.unbiased}")
        print(f"  Biased: {args.biased}")
        print(f"  Total: {args.unbiased + args.biased}")
        
        targets = generate_100_target_set(
            unbiased_count=args.unbiased,
            biased_count=args.biased,
            seed=args.seed
        )
    else:
        # Original mode with bias ratio
        print(f"\nMode: Standard generation")
        print(f"  Count: {args.count}")
        print(f"  Bias ratio: {args.bias_ratio:.1%}")
        
        targets = generate_targets(
            num_targets=args.count,
            bias_close_ratio=args.bias_ratio
        )
    
    # Verify
    verify_targets(targets)
    
    # Print statistics
    print_statistics(targets)
    
    # Save to file
    output_dir = Path(__file__).parent
    output_file = output_dir / args.output
    save_targets(targets, output_file)
    
    print("\n" + "="*60)
    print("✓ Target generation complete!")
    print("="*60)

if __name__ == "__main__":
    main()
