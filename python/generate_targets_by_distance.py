#!/usr/bin/env python3
"""
Generate targets by distance from sqrt(N) for ECM factorization experiments.
Creates batches with specific distance ratios and Fermat-normal forms.
"""

import argparse
import json
import random
import math
from mpmath import mp, mpf, sqrt as mpsqrt, log as mplog, frac, exp as mpexp, fmod
import sympy

mp.dps = 100

PHI = (1 + mpf(5).sqrt()) / 2


def generate_semiprime(bits, ratio_target=1.0, fermat_normal=0, seed=None):
    """
    Generate a semiprime N = p*q of the given bit size.
    
    Args:
        bits: Target bit size for N
        ratio_target: Ratio p/sqrt(N), where 1.0 means p ~ sqrt(N)
        fermat_normal: Fermat normal form bias (2^k for factors near 2^k ± small)
        seed: Random seed for reproducibility
    
    Returns:
        (N, p, q, metadata)
    """
    if seed is not None:
        random.seed(seed)
    
    # Target N size
    target_N_bits = bits
    
    # For ratio_target ~ 1.0, we want p ~ sqrt(N), so p has ~ bits/2 bits
    # For ratio_target > 1.0, p is larger than sqrt(N)
    # For ratio_target < 1.0, p is smaller than sqrt(N)
    
    # Start with balanced case
    p_bits = target_N_bits // 2
    
    # Adjust for ratio
    if ratio_target != 1.0:
        # log2(p) = log2(sqrt(N)) + log2(ratio_target)
        # log2(p) = (log2(N)/2) + log2(ratio_target)
        adjustment = int(math.log2(ratio_target) * target_N_bits / 2)
        p_bits = p_bits + adjustment
    
    # Generate p
    if fermat_normal > 0:
        # Generate p near 2^p_bits ± small offset
        base = 2 ** p_bits
        offset = random.randint(1, min(2**20, base // 100))
        if random.random() > 0.5:
            p = sympy.nextprime(base + offset)
        else:
            p = sympy.prevprime(base - offset)
    else:
        # Standard random prime
        p_min = 2 ** (p_bits - 1)
        p_max = 2 ** p_bits - 1
        p = sympy.randprime(p_min, p_max)
    
    p = int(p)
    
    # Generate q to achieve target bit size for N
    # We want N = p*q to have target_N_bits bits
    # So q ~ N/p ~ 2^target_N_bits / p
    q_bits = target_N_bits - p.bit_length()
    
    if fermat_normal > 0:
        base = 2 ** q_bits
        offset = random.randint(1, min(2**20, base // 100))
        if random.random() > 0.5:
            q = sympy.nextprime(base + offset)
        else:
            q = sympy.prevprime(base - offset)
    else:
        q_min = 2 ** (q_bits - 1)
        q_max = 2 ** q_bits - 1
        q = sympy.randprime(q_min, q_max)
    
    q = int(q)
    N = p * q
    
    # Compute metadata
    sqrt_N = mpsqrt(mpf(N))
    actual_ratio = mpf(p) / sqrt_N
    distance = abs(mpf(p) - sqrt_N)
    
    metadata = {
        "bits": N.bit_length(),
        "p_bits": p.bit_length(),
        "q_bits": q.bit_length(),
        "ratio_target": float(ratio_target),
        "actual_ratio": float(actual_ratio),
        "distance": float(distance),
        "fermat_normal": fermat_normal,
        "seed": seed
    }
    
    return N, p, q, metadata


def parse_tier_spec(spec):
    """
    Parse tier specification like "1.0+2^-32" into a float.
    
    Examples:
        "1.0" -> 1.0
        "1.0+2^-32" -> 1.0 + 2^-32
        "1.125" -> 1.125
    """
    if '+' in spec:
        parts = spec.split('+')
        base = float(parts[0])
        offset_spec = parts[1]
        if '^' in offset_spec:
            # Parse "2^-32"
            base_exp, exp = offset_spec.split('^')
            offset = float(base_exp) ** float(exp)
        else:
            offset = float(offset_spec)
        return base + offset
    else:
        return float(spec)


def parse_fermat_spec(spec):
    """
    Parse Fermat normal specification like "2^24" into an integer.
    
    Examples:
        "2^24" -> 16777216
        "0" -> 0
    """
    if '^' in spec:
        base, exp = spec.split('^')
        return int(base) ** int(exp)
    else:
        return int(spec)


def main():
    parser = argparse.ArgumentParser(
        description="Generate targets by distance for ECM experiments"
    )
    parser.add_argument(
        "--bits",
        type=int,
        required=True,
        help="Target bit size for semiprimes"
    )
    parser.add_argument(
        "--per-tier",
        type=int,
        default=25,
        help="Number of targets per tier"
    )
    parser.add_argument(
        "--tiers",
        type=str,
        required=True,
        help="Comma-separated list of ratio tiers (e.g., '1.0+2^-32,1.0+2^-24,1.125')"
    )
    parser.add_argument(
        "--fermats",
        type=str,
        default="0",
        help="Comma-separated list of Fermat normal forms (e.g., '0,2^24,2^28')"
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    # Parse tiers and fermats
    tier_ratios = [parse_tier_spec(t.strip()) for t in args.tiers.split(',')]
    fermat_normals = [parse_fermat_spec(f.strip()) for f in args.fermats.split(',')]
    
    print(f"Generating targets with {args.bits} bits")
    print(f"Tiers: {tier_ratios}")
    print(f"Fermat normals: {fermat_normals}")
    print(f"Per tier: {args.per_tier}")
    
    # Generate targets
    targets = []
    seed_base = args.seed
    
    for tier_idx, ratio in enumerate(tier_ratios):
        for fermat in fermat_normals:
            for i in range(args.per_tier):
                seed = seed_base + tier_idx * 10000 + fermat + i
                N, p, q, metadata = generate_semiprime(
                    args.bits, 
                    ratio_target=ratio, 
                    fermat_normal=fermat,
                    seed=seed
                )
                
                target = {
                    "N": str(N),
                    "p": str(p),
                    "q": str(q),
                    "tier": tier_idx,
                    "tier_ratio": ratio,
                    "fermat_normal": fermat,
                    **metadata
                }
                targets.append(target)
    
    # Write to JSON
    output = {
        "config": {
            "bits": args.bits,
            "per_tier": args.per_tier,
            "tiers": tier_ratios,
            "fermats": fermat_normals,
            "seed": args.seed
        },
        "targets": targets
    }
    
    with open(args.out, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {len(targets)} targets")
    print(f"Saved to {args.out}")
    
    # Show summary
    print("\nSummary by tier:")
    for tier_idx, ratio in enumerate(tier_ratios):
        tier_targets = [t for t in targets if t['tier'] == tier_idx]
        print(f"  Tier {tier_idx} (ratio={ratio}): {len(tier_targets)} targets")


if __name__ == "__main__":
    main()
