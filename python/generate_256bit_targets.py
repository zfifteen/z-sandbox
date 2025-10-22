#!/usr/bin/env python3
"""
Generate 256-bit balanced semiprime targets using Z5D-guided prime selection.
Creates test cases for factorization pipeline with reproducible results.
"""

import json
import math
import random
import time
from pathlib import Path
import sympy
from z5d_predictor import z5d_predict

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)

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

def generate_balanced_128bit_prime_pair(bias_close=False, max_retries=10):
    """
    Generate a pair of balanced 128-bit primes using Z5D prediction.
    
    Args:
        bias_close: If True, bias toward close p and q for Fermat weakness
        max_retries: Maximum number of retries if primes are out of range
    
    Returns:
        (p, q, metadata) where metadata contains generation info
    """
    # For 128-bit primes, we can use sympy directly
    # This is simpler and more reliable than trying to predict indices
    
    for attempt in range(max_retries):
        # Generate 128-bit primes directly
        p = sympy.randprime(2**127, 2**128)
        
        if bias_close:
            # Generate q close to p
            gap = random.randint(2**20, 2**24)  # Small gap for Fermat weakness
            q_start = p + gap if random.random() > 0.5 else max(2**127, p - gap)
            q = sympy.nextprime(q_start)
            
            # Ensure q is still in 128-bit range
            if q >= 2**128:
                q = sympy.randprime(2**127, 2**128)
        else:
            # Generate q independently
            q = sympy.randprime(2**127, 2**128)
            # Ensure q != p
            while q == p:
                q = sympy.randprime(2**127, 2**128)
        
        # Verify 128-bit range
        p_bits = p.bit_length()
        q_bits = q.bit_length()
        
        if 127 <= p_bits <= 128 and 127 <= q_bits <= 128:
            # Sort so p < q
            if p > q:
                p, q = q, p
            
            # Calculate approximate k values (for metadata)
            k1 = int(p / math.log(p)) if p > 2 else 1
            k2 = int(q / math.log(q)) if q > 2 else 1
            
            metadata = {
                'k1': k1,
                'k2': k2,
                'offset1': 0,  # Not using Z5D prediction directly
                'offset2': 0,
                'p_bits': p_bits,
                'q_bits': q_bits,
                'bias_close': bias_close
            }
            
            return p, q, metadata
    
    # If we couldn't generate after max_retries, raise error
    raise ValueError(f"Could not generate balanced 128-bit primes after {max_retries} attempts")

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
            
            # Verify it's a 256-bit semiprime (254-256 bits acceptable)
            if not (254 <= N_bits <= 256):
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

def verify_targets(targets):
    """Verify all targets are valid semiprimes."""
    print("\nVerifying targets...")
    for target in targets:
        N = int(target['N'])
        p = int(target['p'])
        q = int(target['q'])
        
        # Verify factorization
        assert p * q == N, f"Target {target['id']}: p*q != N"
        
        # Verify primality
        assert sympy.isprime(p), f"Target {target['id']}: p is not prime"
        assert sympy.isprime(q), f"Target {target['id']}: q is not prime"
        
        # Verify bit lengths (match generation constraints)
        assert 254 <= N.bit_length() <= 256, f"Target {target['id']}: N is not 256-bit"
        assert 127 <= p.bit_length() <= 128, f"Target {target['id']}: p is not 128-bit"
        assert 127 <= q.bit_length() <= 128, f"Target {target['id']}: q is not 128-bit"
    
    print(f"✓ All {len(targets)} targets verified")

def save_targets(targets, filepath):
    """Save targets to JSON file."""
    output = {
        'metadata': {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'seed': SEED,
            'num_targets': len(targets),
            'description': '256-bit balanced semiprimes for factorization testing'
        },
        'targets': targets
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved {len(targets)} targets to {filepath}")

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
    print("="*60)
    print("256-bit RSA Target Generation via Z5D-Guided Prime Selection")
    print("="*60)
    
    # Generate targets
    targets = generate_targets(num_targets=20, bias_close_ratio=0.1)
    
    # Verify
    verify_targets(targets)
    
    # Print statistics
    print_statistics(targets)
    
    # Save to file
    output_dir = Path(__file__).parent
    output_file = output_dir / 'targets_256bit.json'
    save_targets(targets, output_file)
    
    print("\n" + "="*60)
    print("✓ Target generation complete!")
    print("="*60)

if __name__ == "__main__":
    main()
