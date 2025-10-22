#!/usr/bin/env python3
"""
Batch factorization runner for 256-bit RSA targets.
Processes multiple targets from targets_256bit.json and reports statistics.
Supports parallel processing, checkpointing, and adaptive timeouts.
"""

import argparse
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional
from multiprocessing import Pool, cpu_count
from factor_256bit import factor_single_target, verify_factors

def load_targets(filepath: Path) -> List[Dict]:
    """Load targets from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['targets']

def load_checkpoint(checkpoint_file: Path) -> List[Dict]:
    """Load checkpoint results if they exist."""
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        return data.get('results', [])
    return []

def save_checkpoint(results: List[Dict], checkpoint_file: Path):
    """Save intermediate results to checkpoint file."""
    output = {
        'checkpoint_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'completed_count': len(results),
        'results': results
    }
    
    # Write to temp file first, then rename for atomicity
    temp_file = checkpoint_file.with_suffix('.tmp')
    with open(temp_file, 'w') as f:
        json.dump(output, f, indent=2)
    temp_file.replace(checkpoint_file)

def get_target_type(target: Dict) -> str:
    """Get target type (biased or unbiased)."""
    if 'type' in target:
        return target['type']
    # Fallback for old format
    return 'biased' if target.get('bias_close', False) else 'unbiased'

def get_timeout_for_target(target: Dict, timeout_unbiased: float, timeout_biased: float) -> float:
    """Get appropriate timeout for target based on type."""
    target_type = get_target_type(target)
    return timeout_unbiased if target_type == 'unbiased' else timeout_biased

def factor_single_wrapper(args):
    """
    Wrapper function for parallel factorization.
    
    Args:
        args: Tuple of (target, timeout, verbose)
    
    Returns:
        Result dictionary
    """
    target, timeout, verbose = args
    
    N = int(target['N'])
    true_p = int(target['p'])
    true_q = int(target['q'])
    target_id = target.get('id', 'unknown')
    target_type = get_target_type(target)
    
    if verbose:
        print(f"\n[Worker] Processing target {target_id} ({target_type})")
    
    start_time = time.time()
    result = factor_single_target(N, timeout=timeout, verbose=verbose)
    
    # Add metadata
    result['target_id'] = str(target_id)
    result['target_type'] = target_type
    result['bias_close'] = target.get('bias_close', target_type == 'biased')
    result['true_p'] = str(true_p)
    result['true_q'] = str(true_q)
    result['elapsed_seconds'] = time.time() - start_time
    
    # Verify correctness
    if result['success']:
        found_p = int(result['p'])
        found_q = int(result['q'])
        
        # Check if factors match (order doesn't matter)
        correct = {found_p, found_q} == {true_p, true_q}
        result['correct'] = correct
        
        if verbose:
            if correct:
                print(f"  ✓✓ CORRECT factors found for {target_id}!")
            else:
                print(f"  ✗ Wrong factors for {target_id} (this shouldn't happen)")
    else:
        result['correct'] = False
    
    return result

def run_batch_factorization(targets: List[Dict], 
                            timeout_unbiased: float = 3600,
                            timeout_biased: float = 300,
                            num_workers: int = 1,
                            checkpoint_file: Optional[Path] = None,
                            checkpoint_interval: int = 10,
                            verbose: bool = True) -> List[Dict]:
    """
    Run factorization on multiple targets with parallel processing.
    
    Args:
        targets: List of target dictionaries
        timeout_unbiased: Timeout per unbiased target in seconds
        timeout_biased: Timeout per biased target in seconds
        num_workers: Number of parallel workers (1 = sequential)
        checkpoint_file: Path to checkpoint file for crash recovery
        checkpoint_interval: Save checkpoint every N targets
        verbose: Print progress
    
    Returns:
        List of result dictionaries
    """
    # Load existing checkpoint if available
    completed_results = []
    completed_ids = set()
    
    if checkpoint_file and checkpoint_file.exists():
        completed_results = load_checkpoint(checkpoint_file)
        completed_ids = {r['target_id'] for r in completed_results}
        if verbose and completed_results:
            print(f"Resuming from checkpoint: {len(completed_results)} targets already completed")
    
    # Filter out already completed targets
    remaining_targets = [t for t in targets if str(t.get('id', '')) not in completed_ids]
    
    if not remaining_targets:
        if verbose:
            print("All targets already completed!")
        return completed_results
    
    total_targets = len(targets)
    
    if verbose:
        print("="*60)
        print(f"Batch Factorization: {len(remaining_targets)} targets to process")
        print(f"  (Total: {total_targets}, Already completed: {len(completed_results)})")
        print(f"Timeout per unbiased target: {timeout_unbiased}s ({timeout_unbiased/60:.1f} minutes)")
        print(f"Timeout per biased target: {timeout_biased}s ({timeout_biased/60:.1f} minutes)")
        print(f"Workers: {num_workers}")
        print("="*60)
    
    # Prepare arguments for parallel processing
    args_list = []
    for target in remaining_targets:
        timeout = get_timeout_for_target(target, timeout_unbiased, timeout_biased)
        args_list.append((target, timeout, False))  # Set verbose=False for workers
    
    # Process targets
    results = list(completed_results)
    
    if num_workers > 1:
        # Parallel processing
        with Pool(processes=num_workers) as pool:
            for i, result in enumerate(pool.imap(factor_single_wrapper, args_list)):
                results.append(result)
                
                if verbose:
                    completed = len(results)
                    successes = sum(1 for r in results if r['success'])
                    target_id = result['target_id']
                    target_type = result['target_type']
                    status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
                    
                    print(f"\n[{completed}/{total_targets}] Target {target_id} ({target_type}): {status}")
                    if result['success']:
                        print(f"  Method: {result['method']}, Time: {result['elapsed_seconds']:.2f}s")
                    print(f"  Progress: {successes}/{completed} successful ({successes/completed*100:.1f}%)")
                
                # Checkpoint periodically
                if checkpoint_file and (len(results) % checkpoint_interval == 0):
                    save_checkpoint(results, checkpoint_file)
                    if verbose:
                        print(f"  Checkpoint saved: {len(results)} targets")
    else:
        # Sequential processing
        for i, (target, timeout, _) in enumerate(args_list):
            if verbose:
                target_id = target.get('id', i)
                target_type = get_target_type(target)
                print(f"\n[{len(results)+1}/{total_targets}] Target {target_id} ({target_type})")
                print(f"  Balance ratio: {target.get('balance_ratio', 'N/A')}")
            
            N = int(target['N'])
            true_p = int(target['p'])
            true_q = int(target['q'])
            
            start_time = time.time()
            result = factor_single_target(N, timeout=timeout, verbose=verbose)
            
            # Add metadata
            result['target_id'] = str(target.get('id', i))
            result['target_type'] = target_type
            result['bias_close'] = target.get('bias_close', target_type == 'biased')
            result['true_p'] = str(true_p)
            result['true_q'] = str(true_q)
            result['elapsed_seconds'] = time.time() - start_time
            
            # Verify correctness
            if result['success']:
                found_p = int(result['p'])
                found_q = int(result['q'])
                
                correct = {found_p, found_q} == {true_p, true_q}
                result['correct'] = correct
                
                if correct and verbose:
                    print(f"  ✓✓ CORRECT factors found!")
                elif not correct and verbose:
                    print(f"  ✗ Wrong factors (this shouldn't happen)")
            else:
                result['correct'] = False
            
            results.append(result)
            
            # Summary so far
            if verbose:
                successes = sum(1 for r in results if r['success'])
                print(f"\n  Progress: {successes}/{len(results)} successful ({successes/len(results)*100:.1f}%)")
            
            # Checkpoint periodically
            if checkpoint_file and (len(results) % checkpoint_interval == 0):
                save_checkpoint(results, checkpoint_file)
                if verbose:
                    print(f"  Checkpoint saved: {len(results)} targets")
    
    # Final checkpoint
    if checkpoint_file:
        save_checkpoint(results, checkpoint_file)
    
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
    
    # Analyze by type
    unbiased_results = [r for r in results if r.get('target_type') == 'unbiased']
    biased_results = [r for r in results if r.get('target_type') == 'biased']
    
    if unbiased_results:
        unbiased_success = sum(1 for r in unbiased_results if r['success'])
        print(f"\nUnbiased targets: {len(unbiased_results)}")
        print(f"  Success rate: {unbiased_success}/{len(unbiased_results)} ({unbiased_success/len(unbiased_results)*100:.1f}%)")
    
    if biased_results:
        biased_success = sum(1 for r in biased_results if r['success'])
        print(f"\nBiased targets: {len(biased_results)}")
        print(f"  Success rate: {biased_success}/{len(biased_results)} ({biased_success/len(biased_results)*100:.1f}%)")
    
    if successes > 0:
        # Statistics for successful factorizations
        successful_results = [r for r in results if r['success']]
        times = [r.get('elapsed_seconds', r.get('elapsed_time', 0)) for r in successful_results]
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
    parser = argparse.ArgumentParser(
        description='Batch factorization for 256-bit RSA targets with parallel processing'
    )
    parser.add_argument('--targets', type=str, default='targets_256bit.json',
                       help='Input targets JSON file (default: targets_256bit.json)')
    parser.add_argument('--output', type=str, default='factorization_results_256bit.json',
                       help='Output results JSON file (default: factorization_results_256bit.json)')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of parallel workers (default: 1, max: CPU count)')
    parser.add_argument('--timeout-unbiased', type=int, default=3600,
                       help='Timeout per unbiased target in seconds (default: 3600 = 1 hour)')
    parser.add_argument('--timeout-biased', type=int, default=300,
                       help='Timeout per biased target in seconds (default: 300 = 5 minutes)')
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Checkpoint file for crash recovery (default: auto-generated)')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                       help='Save checkpoint every N targets (default: 10)')
    parser.add_argument('--max-targets', type=int, default=None,
                       help='Maximum number of targets to process (default: all)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Validate workers
    max_workers = cpu_count()
    if args.workers > max_workers:
        print(f"Warning: Requested {args.workers} workers but only {max_workers} CPUs available")
        print(f"Using {max_workers} workers instead")
        args.workers = max_workers
    
    # Load targets
    targets_file = Path(__file__).parent / args.targets
    
    if not targets_file.exists():
        print(f"Error: {targets_file} not found")
        print("Run generate_256bit_targets.py first")
        return 1
    
    targets = load_targets(targets_file)
    
    # Limit targets if requested
    if args.max_targets and args.max_targets < len(targets):
        print(f"Limiting to first {args.max_targets} targets (of {len(targets)} available)")
        targets = targets[:args.max_targets]
    
    # Setup checkpoint file
    checkpoint_file = None
    if args.checkpoint:
        checkpoint_file = Path(__file__).parent / args.checkpoint
    else:
        # Auto-generate checkpoint filename
        checkpoint_file = Path(__file__).parent / f"checkpoint_{Path(args.output).stem}.json"
    
    print(f"Checkpoint file: {checkpoint_file}")
    
    # Run batch factorization
    results = run_batch_factorization(
        targets,
        timeout_unbiased=args.timeout_unbiased,
        timeout_biased=args.timeout_biased,
        num_workers=args.workers,
        checkpoint_file=checkpoint_file,
        checkpoint_interval=args.checkpoint_interval,
        verbose=(args.log_level in ['INFO', 'DEBUG'])
    )
    
    # Print summary
    print_summary(results)
    
    # Save results
    results_file = Path(__file__).parent / args.output
    save_results(results, results_file)
    
    print("\n" + "="*60)
    print("✓ Batch factorization complete!")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
