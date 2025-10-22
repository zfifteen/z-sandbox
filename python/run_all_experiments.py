#!/usr/bin/env python3
"""
Master Experiment Runner
=========================

Runs all experiments specified in the issue:
1. 127-bit validation (100 samples) - CRITICAL
2. Dimensionality optimization
3. Curvature formula ablation
4. Threshold sensitivity
5. Alternative constants

Generates a comprehensive report.
"""

import sys
import time
import subprocess
from datetime import datetime

def run_experiment(name, script_path):
    """Run an experiment script and capture output."""
    print(f"\n{'='*80}")
    print(f"RUNNING: {name}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout per experiment
        )
        
        elapsed = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\n{name} completed in {elapsed:.1f}s")
        print(f"Exit code: {result.returncode}")
        
        return {
            'name': name,
            'success': result.returncode == 0,
            'elapsed': elapsed,
            'stdout': result.stdout,
            'stderr': result.stderr,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"\n⚠ {name} TIMED OUT after {elapsed:.1f}s")
        return {
            'name': name,
            'success': False,
            'elapsed': elapsed,
            'stdout': '',
            'stderr': 'Timeout',
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ {name} FAILED: {e}")
        return {
            'name': name,
            'success': False,
            'elapsed': elapsed,
            'stdout': '',
            'stderr': str(e),
        }

def main():
    print("=" * 80)
    print("127-BIT VALIDATION EXPERIMENT SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This suite addresses the critical question from the issue:")
    print("  'What's the TRUE success rate at 127-bit?'")
    print()
    print("Experiments to run:")
    print("  1. 127-bit Validation (100 samples) - CRITICAL")
    print("  2. Dimensionality Optimization")
    print("  3. Curvature Formula Ablation")
    print("  4. Threshold Sensitivity")
    print("  5. Alternative Constants")
    print()
    
    experiments = [
        ("127-bit Validation (CRITICAL)", "validate_127bit.py"),
        ("Dimensionality Optimization", "experiment_dimensionality.py"),
        ("Curvature Formula Ablation", "experiment_curvature.py"),
        ("Threshold Sensitivity", "experiment_threshold.py"),
        ("Alternative Constants", "experiment_constants.py"),
    ]
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    results = []
    overall_start = time.time()
    
    for name, script in experiments:
        script_path = os.path.join(script_dir, script)
        if not os.path.exists(script_path):
            print(f"\n⚠ WARNING: {script_path} not found, skipping")
            continue
        
        result = run_experiment(name, script_path)
        results.append(result)
        
        # Brief pause between experiments
        time.sleep(2)
    
    overall_elapsed = time.time() - overall_start
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("EXPERIMENT SUITE SUMMARY")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {overall_elapsed:.1f}s ({overall_elapsed/60:.1f} minutes)")
    print()
    
    print(f"{'Experiment':<40} {'Status':<10} {'Time':<12}")
    print("-" * 80)
    for r in results:
        status = "✓ PASS" if r['success'] else "✗ FAIL"
        print(f"{r['name']:<40} {status:<10} {r['elapsed']:>8.1f}s")
    
    print()
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()
    print("The 127-bit validation experiment is CRITICAL.")
    print("Check its output above to determine:")
    print("  - If success rate is >90%: BREAKTHROUGH")
    print("  - If success rate is 30-50%: SIGNIFICANT IMPROVEMENT")
    print("  - If success rate is ~16%: CONSISTENT WITH BASELINE")
    print()
    print("Other experiments provide insights into:")
    print("  - Optimal dimensionality")
    print("  - Importance of curvature")
    print("  - Threshold calibration")
    print("  - Specificity of golden ratio")
    print()
    print("Review the detailed outputs above for complete analysis.")
    print("=" * 80)
    
    # Save summary to file
    summary_file = os.path.join(script_dir, 'experiment_summary.txt')
    with open(summary_file, 'w') as f:
        f.write(f"Experiment Suite Summary\n")
        f.write(f"{'='*80}\n")
        f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total time: {overall_elapsed:.1f}s\n\n")
        
        for r in results:
            f.write(f"\n{'='*80}\n")
            f.write(f"{r['name']}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Status: {'PASS' if r['success'] else 'FAIL'}\n")
            f.write(f"Time: {r['elapsed']:.1f}s\n")
            if r['stdout']:
                f.write(f"\nOutput:\n{r['stdout']}\n")
            if r['stderr']:
                f.write(f"\nErrors:\n{r['stderr']}\n")
    
    print(f"\nSummary saved to: {summary_file}")
    
    # Exit with success if all experiments passed
    if all(r['success'] for r in results):
        print("\n✓ All experiments completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠ Some experiments failed. Review the outputs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
