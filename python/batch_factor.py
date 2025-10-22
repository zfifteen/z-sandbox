#!/usr/bin/env python3
"""
Batch factorization runner for 256-bit RSA targets.
Processes multiple targets from targets_256bit.json and reports statistics.
"""

import json
import time
from pathlib import Path
from typing import List, Dict
from factor_256bit import factor_single_target, verify_factors

def load_targets(filepath: Path) -> List[Dict]:
    """Load targets from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['targets']

def run_batch_factorization(targets: List[Dict], timeout_per_target: float = 3600,
                            max_targets: int = None) -> List[Dict]:
    """
    Run factorization on multiple targets.
    
    Args:
        targets: List of target dictionaries
        timeout_per_target: Timeout per target in seconds
        max_targets: Maximum number of targets to process (None = all)
    
    Returns:
        List of result dictionaries
    """
    if max_targets:
        targets = targets[:max_targets]
    
    results = []
    
    print("="*60)
    print(f"Batch Factorization: {len(targets)} targets")
    print(f"Timeout per target: {timeout_per_target}s ({timeout_per_target/60:.1f} minutes)")
    print("="*60)
    
    for i, target in enumerate(targets):
        print(f"\n[{i+1}/{len(targets)}] Target {target['id']}")
        print(f"  Biased close: {target['bias_close']}")
        print(f"  Balance ratio: {target['balance_ratio']:.6f}")
        
        N = int(target['N'])
        true_p = int(target['p'])
        true_q = int(target['q'])
        
        start_time = time.time()
        result = factor_single_target(N, timeout=timeout_per_target, verbose=True)
        
        # Add metadata
        result['target_id'] = target['id']
        result['bias_close'] = target['bias_close']
        result['true_p'] = str(true_p)
        result['true_q'] = str(true_q)
        
        # Verify correctness
        if result['success']:
            found_p = int(result['p'])
            found_q = int(result['q'])
            
            # Check if factors match (order doesn't matter)
            correct = {found_p, found_q} == {true_p, true_q}
            result['correct'] = correct
            
            if correct:
                print(f"  ✓✓ CORRECT factors found!")
            else:
                print(f"  ✗ Wrong factors (this shouldn't happen)")
                print(f"    Expected: {true_p} × {true_q}")
                print(f"    Found: {found_p} × {found_q}")
        else:
            result['correct'] = False
        
        results.append(result)
        
        # Summary so far
        successes = sum(1 for r in results if r['success'])
        print(f"\n  Progress: {successes}/{len(results)} successful ({successes/len(results)*100:.1f}%)")
    
    return results

def print_summary(results: List[Dict]):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("FACTORIZATION SUMMARY")
    print("="*60)
    
    total = len(results)
    successes = sum(1 for r in results if r['success'])
    correct = sum(1 for r in results if r.get('correct', False))
    
    print(f"\nTotal targets: {total}")
    print(f"Successful factorizations: {successes}")
    print(f"Success rate: {successes/total*100:.1f}%")
    print(f"Correct factorizations: {correct}")
    
    if successes > 0:
        # Statistics for successful factorizations
        successful_results = [r for r in results if r['success']]
        times = [r['elapsed_time'] for r in successful_results]
        methods = [r['method'] for r in successful_results]
        
        print(f"\nTime statistics (successful):")
        print(f"  Min: {min(times):.2f}s")
        print(f"  Max: {max(times):.2f}s")
        print(f"  Average: {sum(times)/len(times):.2f}s")
        print(f"  Median: {sorted(times)[len(times)//2]:.2f}s")
        
        print(f"\nMethods used:")
        from collections import Counter
        method_counts = Counter(methods)
        for method, count in method_counts.most_common():
            print(f"  {method}: {count} ({count/successes*100:.1f}%)")
        
        # Analyze biased vs unbiased
        biased_successes = sum(1 for r in successful_results if r.get('bias_close', False))
        unbiased_successes = successes - biased_successes
        
        biased_total = sum(1 for r in results if r.get('bias_close', False))
        unbiased_total = total - biased_total
        
        if biased_total > 0:
            print(f"\nBiased (close factors):")
            print(f"  Success rate: {biased_successes}/{biased_total} ({biased_successes/biased_total*100:.1f}%)")
        
        if unbiased_total > 0:
            print(f"Unbiased:")
            print(f"  Success rate: {unbiased_successes}/{unbiased_total} ({unbiased_successes/unbiased_total*100:.1f}%)")
    
    # Failed cases
    failed = total - successes
    if failed > 0:
        print(f"\nFailed factorizations: {failed}")
        failed_results = [r for r in results if not r['success']]
        reasons = [r['method'] for r in failed_results]
        
        from collections import Counter
        reason_counts = Counter(reasons)
        for reason, count in reason_counts.most_common():
            print(f"  {reason}: {count}")

def save_results(results: List[Dict], filepath: Path):
    """Save results to JSON file."""
    output = {
        'metadata': {
            'completed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_targets': len(results),
            'successful': sum(1 for r in results if r['success']),
            'success_rate': sum(1 for r in results if r['success']) / len(results) if results else 0
        },
        'results': results
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Results saved to {filepath}")

def main():
    """Main batch processing function."""
    # Load targets
    targets_file = Path(__file__).parent / 'targets_256bit.json'
    
    if not targets_file.exists():
        print(f"Error: {targets_file} not found")
        print("Run generate_256bit_targets.py first")
        return
    
    targets = load_targets(targets_file)
    
    # Run batch factorization
    # For testing, use shorter timeout and fewer targets
    # For real runs, use timeout=3600 and max_targets=None
    results = run_batch_factorization(
        targets, 
        timeout_per_target=120,  # 2 minutes per target for quick test
        max_targets=5  # Process first 5 targets
    )
    
    # Print summary
    print_summary(results)
    
    # Save results
    results_file = Path(__file__).parent / 'factorization_results_256bit.json'
    save_results(results, results_file)
    
    print("\n" + "="*60)
    print("✓ Batch factorization complete!")
    print("="*60)

if __name__ == "__main__":
    main()
