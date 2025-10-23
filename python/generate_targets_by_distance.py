#!/usr/bin/env python3
"""
Generate balanced semiprime targets organized by distance tiers and Fermat normals.
Creates test cases where factors are positioned at specific ratios from sqrt(N).
"""

import argparse
import json
import math
import random
import time
from pathlib import Path
import sympy


def generate_semiprime_at_ratio(bits, ratio_target, seed):
    """
    Generate a semiprime N = p*q where p/sqrt(N) ≈ ratio_target.
    
    For a target ratio r, we want p/sqrt(N) = r
    Since N = p*q, we have sqrt(N) = sqrt(p*q)
    So p/sqrt(p*q) = r => p = r*sqrt(p*q) => p^2 = r^2*p*q => p = r^2*q
    
    Therefore: p ≈ r^2 * q
    
    Args:
        bits: Target bit size for N
        ratio_target: Target ratio p/sqrt(N) (should be close to 1.0)
        seed: Random seed
    
    Returns:
        Dictionary with N, p, q and metadata
    """
    random.seed(seed)
    
    # For balanced semiprimes, each factor should be around bits//2
    target_p_bits = bits // 2
    
    # Adjust for the ratio: if ratio > 1, p should be slightly larger
    # p_bits ≈ target_p_bits + log2(ratio_target)
    adjustment = math.log2(ratio_target) if ratio_target > 0 else 0
    p_bits_target = target_p_bits + int(adjustment)
    
    # Generate p in the appropriate bit range
    p_min = 2 ** (p_bits_target - 1)
    p_max = 2 ** p_bits_target
    
    # Generate a prime p
    p = sympy.randprime(p_min, p_max)
    
    # Calculate target q based on ratio
    # From p = r^2 * q, we get q = p / r^2
    r_squared = ratio_target ** 2
    q_estimate = int(p / r_squared)
    
    # Find a prime near q_estimate
    q = sympy.nextprime(q_estimate)
    
    # Fine-tune: ensure N has the right bit size
    N = p * q
    actual_bits = N.bit_length()
    
    # If not in range, adjust q
    max_attempts = 50
    attempt = 0
    while (actual_bits < bits - 1 or actual_bits > bits + 1) and attempt < max_attempts:
        if actual_bits < bits:
            # N too small, increase q
            q = sympy.nextprime(q)
        else:
            # N too large, decrease q
            q = sympy.prevprime(q)
            if q < 2:
                break
        N = p * q
        actual_bits = N.bit_length()
        attempt += 1
    
    # Verify primality
    if not sympy.isprime(p) or not sympy.isprime(q):
        # Retry with different seed
        return generate_semiprime_at_ratio(bits, ratio_target, seed + 1)
    
    # Calculate actual ratio
    sqrt_N = math.sqrt(N)
    actual_ratio = p / sqrt_N
    
    return {
        'N': str(N),
        'p': str(p),
        'q': str(q),
        'N_bits': N.bit_length(),
        'p_bits': p.bit_length(),
        'q_bits': q.bit_length(),
        'ratio_target': ratio_target,
        'ratio_actual': actual_ratio,
        'sqrt_N': sqrt_N,
        'distance_from_sqrt': abs(p - sqrt_N),
        'seed': seed
    }


def generate_fermat_vulnerable(bits, fermat_gap, seed):
    """
    Generate a semiprime with |p - q| = fermat_gap, making it Fermat-vulnerable.
    
    Args:
        bits: Target bit size for N
        fermat_gap: Target |p - q|
        seed: Random seed
    
    Returns:
        Dictionary with N, p, q and metadata
    """
    random.seed(seed)
    
    # For balanced semiprimes, each factor should be around bits//2
    target_bits = bits // 2
    
    # Start with a base prime
    p_min = 2 ** (target_bits - 1)
    p_max = 2 ** target_bits
    p = sympy.randprime(p_min, p_max)
    
    # q should be close to p
    q_target = p + fermat_gap if random.random() > 0.5 else p - fermat_gap
    
    # Ensure q is in valid range
    if q_target < p_min:
        q_target = p + fermat_gap
    elif q_target > p_max:
        q_target = p - fermat_gap
    
    # Find nearest prime
    q = sympy.nextprime(q_target)
    
    # Verify q is still in range and gap is reasonable
    max_attempts = 50
    attempt = 0
    while (q < p_min or q > p_max or abs(p - q) > fermat_gap * 2) and attempt < max_attempts:
        if q < p_min:
            q = sympy.nextprime(p_min)
        elif q > p_max:
            q = sympy.prevprime(p_max)
        elif abs(p - q) > fermat_gap * 2:
            # Try different base p
            p = sympy.randprime(p_min, p_max)
            q_target = p + fermat_gap if random.random() > 0.5 else p - fermat_gap
            q = sympy.nextprime(q_target)
        attempt += 1
    
    N = p * q
    
    # Ensure p < q for consistency
    if p > q:
        p, q = q, p
    
    sqrt_N = math.sqrt(N)
    
    return {
        'N': str(N),
        'p': str(p),
        'q': str(q),
        'N_bits': N.bit_length(),
        'p_bits': p.bit_length(),
        'q_bits': q.bit_length(),
        'fermat_gap': abs(p - q),
        'fermat_target': fermat_gap,
        'sqrt_N': sqrt_N,
        'distance_from_sqrt': abs(p - sqrt_N),
        'seed': seed
    }


def parse_tier_spec(tier_str):
    """
    Parse tier specification like "1.0+2^-32" or "1.125" into a numeric value.
    
    Examples:
        "1.0" -> 1.0
        "1.0+2^-32" -> 1.0 + 2^-32
        "1.125" -> 1.125
    """
    tier_str = tier_str.strip()
    
    # Check if it contains a "+"
    if '+' in tier_str:
        parts = tier_str.split('+')
        base = float(parts[0])
        
        # Parse the additive part (may contain "^")
        additive_str = parts[1]
        if '^' in additive_str:
            # Parse "2^-32" format
            exp_parts = additive_str.split('^')
            base_num = float(exp_parts[0])
            exponent = float(exp_parts[1])
            additive = base_num ** exponent
        else:
            additive = float(additive_str)
        
        return base + additive
    else:
        return float(tier_str)


def parse_fermat_spec(fermat_str):
    """
    Parse Fermat gap specification like "2^24" or "1000000" into a numeric value.
    
    Examples:
        "2^24" -> 16777216
        "1000000" -> 1000000
    """
    fermat_str = fermat_str.strip()
    
    if '^' in fermat_str:
        parts = fermat_str.split('^')
        base = float(parts[0])
        exponent = float(parts[1])
        return int(base ** exponent)
    else:
        return int(fermat_str)


def generate_targets_by_distance(bits, tiers, fermats, per_tier, seed):
    """
    Generate targets organized by distance tiers and Fermat gaps.
    
    Args:
        bits: Target bit size for N
        tiers: List of ratio targets (e.g., [1.0, 1.125, 1.25])
        fermats: List of Fermat gaps (e.g., [2^24, 2^28])
        per_tier: Number of targets per tier
        seed: Base random seed
    
    Returns:
        Dictionary with metadata and categorized targets
    """
    targets = []
    target_id = 0
    
    print(f"Generating targets:")
    print(f"  Bit size: {bits}")
    print(f"  Tiers: {tiers}")
    print(f"  Fermats: {fermats}")
    print(f"  Per tier: {per_tier}")
    
    # Generate ratio-based targets
    for tier_idx, ratio in enumerate(tiers):
        print(f"\n  Generating tier {tier_idx + 1}/{len(tiers)}: ratio={ratio:.10f}")
        for i in range(per_tier):
            target_seed = seed + target_id
            try:
                target = generate_semiprime_at_ratio(bits, ratio, target_seed)
                target['id'] = f"T{tier_idx + 1:02d}-{i + 1:03d}"
                target['tier'] = tier_idx + 1
                target['tier_type'] = 'ratio'
                targets.append(target)
                target_id += 1
                
                if (i + 1) % 5 == 0:
                    print(f"    Generated {i + 1}/{per_tier}")
            except Exception as e:
                print(f"    Error generating target {i}: {e}")
    
    # Generate Fermat-vulnerable targets
    for fermat_idx, fermat_gap in enumerate(fermats):
        print(f"\n  Generating Fermat tier {fermat_idx + 1}/{len(fermats)}: gap={fermat_gap}")
        for i in range(per_tier):
            target_seed = seed + target_id + 10000
            try:
                target = generate_fermat_vulnerable(bits, fermat_gap, target_seed)
                target['id'] = f"F{fermat_idx + 1:02d}-{i + 1:03d}"
                target['fermat_tier'] = fermat_idx + 1
                target['tier_type'] = 'fermat'
                targets.append(target)
                target_id += 1
                
                if (i + 1) % 5 == 0:
                    print(f"    Generated {i + 1}/{per_tier}")
            except Exception as e:
                print(f"    Error generating Fermat target {i}: {e}")
    
    return {
        'metadata': {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'bits': bits,
            'tiers': tiers,
            'fermats': [int(f) for f in fermats],
            'per_tier': per_tier,
            'seed': seed,
            'total_targets': len(targets)
        },
        'targets': targets
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate balanced semiprimes organized by distance tiers'
    )
    parser.add_argument('--bits', type=int, default=192,
                       help='Target bit size for N (default: 192)')
    parser.add_argument('--per-tier', type=int, default=25,
                       help='Number of targets per tier (default: 25)')
    parser.add_argument('--tiers', type=str,
                       default='1.0+2^-32,1.0+2^-24,1.0+2^-16,1.0+2^-12,1.125,1.25',
                       help='Comma-separated ratio tiers (default: 1.0+2^-32,...)')
    parser.add_argument('--fermats', type=str, default='2^24,2^28',
                       help='Comma-separated Fermat gaps (default: 2^24,2^28)')
    parser.add_argument('--out', type=str, default='python/targets_by_distance.json',
                       help='Output JSON file (default: python/targets_by_distance.json)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Parse tier specifications
    tier_strs = args.tiers.split(',')
    tiers = [parse_tier_spec(t) for t in tier_strs]
    
    # Parse Fermat specifications
    fermat_strs = args.fermats.split(',')
    fermats = [parse_fermat_spec(f) for f in fermat_strs]
    
    print("="*70)
    print("Generate Targets by Distance")
    print("="*70)
    
    # Generate targets
    result = generate_targets_by_distance(
        bits=args.bits,
        tiers=tiers,
        fermats=fermats,
        per_tier=args.per_tier,
        seed=args.seed
    )
    
    # Save to file
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Generated {result['metadata']['total_targets']} targets")
    print(f"✓ Saved to {output_path}")
    
    # Print summary statistics
    ratio_targets = [t for t in result['targets'] if t.get('tier_type') == 'ratio']
    fermat_targets = [t for t in result['targets'] if t.get('tier_type') == 'fermat']
    
    print(f"\nSummary:")
    print(f"  Ratio-based targets: {len(ratio_targets)}")
    print(f"  Fermat-vulnerable targets: {len(fermat_targets)}")
    
    if ratio_targets:
        actual_ratios = [t['ratio_actual'] for t in ratio_targets]
        print(f"  Ratio range: [{min(actual_ratios):.6f}, {max(actual_ratios):.6f}]")
    
    if fermat_targets:
        actual_gaps = [t['fermat_gap'] for t in fermat_targets]
        print(f"  Fermat gap range: [{min(actual_gaps)}, {max(actual_gaps)}]")


if __name__ == "__main__":
    main()
