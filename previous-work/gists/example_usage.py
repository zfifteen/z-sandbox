#!/usr/bin/env python3
"""
Example Usage of Geometric Factorization Algorithm
===================================================

This file demonstrates various ways to use the geometric factorization
implementation with practical examples.
"""

from geometric_factorization import (
    generate_semiprime,
    geometric_factor,
    FactorizationParams,
    theta,
    circular_distance,
    is_prime_miller_rabin
)

def example_1_basic_usage():
    """Example 1: Basic factorization with default parameters."""
    print("="*70)
    print("Example 1: Basic Factorization")
    print("="*70)
    
    # Generate a small semiprime
    N, p, q = generate_semiprime(bit_size=12, seed=42)
    print(f"\nGenerated 12-bit semiprime: N = {N}")
    print(f"True factors: {p} × {q}")
    
    # Factor it with default parameters
    params = FactorizationParams()
    result = geometric_factor(N, params)
    
    if result.success:
        found_p, found_q = result.factors
        print(f"\n✓ Successfully factored!")
        print(f"Found factors: {found_p} × {found_q}")
        print(f"Attempts: {result.attempts}")
        print(f"Time: {result.timings['total']:.3f}s")
    else:
        print(f"\n✗ Failed to factor after {result.attempts} attempts")


def example_2_custom_parameters():
    """Example 2: Factorization with custom parameters."""
    print("\n\n" + "="*70)
    print("Example 2: Custom Parameters")
    print("="*70)
    
    # Generate a semiprime
    N, p, q = generate_semiprime(bit_size=15, seed=999)
    print(f"\nGenerated 15-bit semiprime: N = {N}")
    print(f"True factors: {p} × {q}")
    
    # Custom parameters - more aggressive search
    params = FactorizationParams(
        k_list=[0.3, 0.5, 0.7],          # Different k values
        eps_list=[0.01, 0.03, 0.08],     # Tighter tolerances
        spiral_iters=3000,                # More spiral candidates
        search_window=2048,               # Wider search window
        max_attempts=5000                 # More attempts
    )
    
    print("\nUsing custom parameters:")
    print(f"  k_list: {params.k_list}")
    print(f"  eps_list: {params.eps_list}")
    print(f"  spiral_iters: {params.spiral_iters}")
    print(f"  search_window: {params.search_window}")
    
    result = geometric_factor(N, params)
    
    if result.success:
        found_p, found_q = result.factors
        print(f"\n✓ Successfully factored!")
        print(f"Found factors: {found_p} × {found_q}")
        print(f"Attempts: {result.attempts}")
    else:
        print(f"\n✗ Failed to factor after {result.attempts} attempts")


def example_3_detailed_diagnostics():
    """Example 3: Accessing detailed diagnostics."""
    print("\n\n" + "="*70)
    print("Example 3: Detailed Diagnostics")
    print("="*70)
    
    # Generate a semiprime
    N, p, q = generate_semiprime(bit_size=14, seed=12345)
    print(f"\nFactoring N = {N} (true: {p} × {q})")
    
    # Factor with default params
    params = FactorizationParams()
    result = geometric_factor(N, params)
    
    # Show detailed logs for each pass
    print("\nDetailed pass-by-pass logs:")
    print("-" * 70)
    for i, log in enumerate(result.logs, 1):
        print(f"\nPass {i}:")
        print(f"  Parameters: k={log['k']}, ε={log['epsilon']}")
        print(f"  Candidates: {log['pre_filter']} → {log['post_filter']}")
        
        if log['post_filter'] > 0:
            reduction = log['pre_filter'] / log['post_filter']
            print(f"  Reduction ratio: {reduction:.1f}:1")
        
        print(f"  Tested: {log['candidates_tested']}")
        print(f"  Result: {log['result']}")
        
        if log['result'] == 'SUCCESS':
            print(f"  ✓ Found factor: {log.get('factor_found')}")
            break
    
    # Show timing breakdown
    print("\nTiming breakdown:")
    for key, time_val in result.timings.items():
        print(f"  {key}: {time_val:.4f}s")
    
    # Show final result
    print("\nFinal result:")
    if result.success:
        print(f"  ✓ Success: {result.factors[0]} × {result.factors[1]}")
    else:
        print(f"  ✗ Failed after {result.attempts} attempts")


def example_4_theta_function():
    """Example 4: Understanding the theta function."""
    print("\n\n" + "="*70)
    print("Example 4: Theta Function Behavior")
    print("="*70)
    
    # Demonstrate theta function on a known semiprime
    N = 143  # 11 × 13
    p, q = 11, 13
    
    print(f"\nSemiprime: N = {N} = {p} × {q}")
    print("\nComputing θ(N, k) for different k values:")
    
    k_values = [0.2, 0.45, 0.8]
    
    for k in k_values:
        theta_N = theta(N, k)
        theta_p = theta(p, k)
        theta_q = theta(q, k)
        
        dist_p = circular_distance(theta_p, theta_N)
        dist_q = circular_distance(theta_q, theta_N)
        
        print(f"\n  k = {k}:")
        print(f"    θ(N={N}) = {theta_N:.6f}")
        print(f"    θ(p={p})  = {theta_p:.6f}  distance: {dist_p:.6f}")
        print(f"    θ(q={q})  = {theta_q:.6f}  distance: {dist_q:.6f}")
        
        # Show which would pass filtering with ε=0.05
        epsilon = 0.05
        print(f"    With ε={epsilon}:")
        print(f"      p would {'PASS' if dist_p <= epsilon else 'FAIL'} filtering")
        print(f"      q would {'PASS' if dist_q <= epsilon else 'FAIL'} filtering")


def example_5_circular_distance():
    """Example 5: Understanding circular distance."""
    print("\n\n" + "="*70)
    print("Example 5: Circular Distance on Unit Circle")
    print("="*70)
    
    print("\nCircular distance accounts for wrap-around at 1.0:")
    
    test_pairs = [
        (0.1, 0.3, "Direct distance"),
        (0.1, 0.9, "Wrap-around distance"),
        (0.0, 0.99, "Near-wrap case"),
        (0.5, 0.5, "Same point"),
        (0.25, 0.75, "Opposite points"),
    ]
    
    for a, b, description in test_pairs:
        dist = circular_distance(a, b)
        direct = abs(a - b)
        wraparound = 1.0 - direct
        
        print(f"\n  {description}:")
        print(f"    Points: {a:.2f} and {b:.2f}")
        print(f"    Direct: {direct:.3f}, Wrap-around: {wraparound:.3f}")
        print(f"    Circular distance: {dist:.3f} (minimum)")


def example_6_batch_factoring():
    """Example 6: Batch factorization with statistics."""
    print("\n\n" + "="*70)
    print("Example 6: Batch Factorization")
    print("="*70)
    
    bit_size = 12
    num_samples = 10
    seed_base = 1000
    
    print(f"\nFactoring {num_samples} random {bit_size}-bit semiprimes...")
    
    params = FactorizationParams()
    successes = 0
    total_attempts = 0
    
    for i in range(num_samples):
        N, p, q = generate_semiprime(bit_size, seed=seed_base + i)
        result = geometric_factor(N, params)
        
        total_attempts += result.attempts
        
        if result.success:
            successes += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"  {i+1:2d}. N={N:6d} {status} ({result.attempts:3d} attempts)")
    
    # Print statistics
    success_rate = successes / num_samples
    avg_attempts = total_attempts / num_samples
    
    print(f"\nStatistics:")
    print(f"  Success rate: {success_rate*100:.1f}% ({successes}/{num_samples})")
    print(f"  Average attempts: {avg_attempts:.1f}")


def example_7_verify_factorization():
    """Example 7: Verification and validation."""
    print("\n\n" + "="*70)
    print("Example 7: Verification and Validation")
    print("="*70)
    
    # Generate and factor
    N, true_p, true_q = generate_semiprime(14, seed=7777)
    print(f"\nOriginal: N = {N}, factors = {true_p} × {true_q}")
    
    params = FactorizationParams()
    result = geometric_factor(N, params)
    
    if result.success:
        found_p, found_q = result.factors
        print(f"Found: factors = {found_p} × {found_q}")
        
        # Verification checks
        print("\nVerification:")
        
        # Check 1: Product equals N
        product = found_p * found_q
        print(f"  1. Product: {found_p} × {found_q} = {product}")
        assert product == N, "Product doesn't equal N!"
        print(f"     ✓ Product equals N")
        
        # Check 2: Both factors are prime
        p_is_prime = is_prime_miller_rabin(found_p)
        q_is_prime = is_prime_miller_rabin(found_q)
        print(f"  2. Primality:")
        print(f"     {found_p} is {'prime' if p_is_prime else 'NOT PRIME'}")
        print(f"     {found_q} is {'prime' if q_is_prime else 'NOT PRIME'}")
        assert p_is_prime and q_is_prime, "Factors are not prime!"
        print(f"     ✓ Both factors are prime")
        
        # Check 3: Match original factors
        found_set = {found_p, found_q}
        true_set = {true_p, true_q}
        print(f"  3. Match original:")
        print(f"     Found:    {{{found_p}, {found_q}}}")
        print(f"     Expected: {{{true_p}, {true_q}}}")
        assert found_set == true_set, "Factors don't match original!"
        print(f"     ✓ Factors match original")
        
        print("\n✓ All verification checks passed!")
    else:
        print(f"\n✗ Factorization failed after {result.attempts} attempts")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("GEOMETRIC FACTORIZATION - EXAMPLE USAGE")
    print("="*70)
    
    examples = [
        example_1_basic_usage,
        example_2_custom_parameters,
        example_3_detailed_diagnostics,
        example_4_theta_function,
        example_5_circular_distance,
        example_6_batch_factoring,
        example_7_verify_factorization,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Example failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
