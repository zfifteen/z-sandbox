#!/usr/bin/env python3
"""
Comprehensive statistical analysis of 100-target factorization batch.
Calculates success rates with Wilson confidence intervals and generates report.
"""

import argparse
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np
from scipy import stats


def load_results(results_file: Path) -> List[Dict]:
    """Load factorization results from JSON file."""
    with open(results_file, 'r') as f:
        data = json.load(f)
    return data.get('results', [])


def wilson_ci(successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Wilson score confidence interval for binomial proportion.
    More accurate than normal approximation for small success counts.
    
    Args:
        successes: Number of successes
        trials: Total number of trials
        confidence: Confidence level (default: 0.95)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if trials == 0:
        return (0.0, 0.0)
    
    z = stats.norm.ppf((1 + confidence) / 2)
    p = successes / trials
    n = trials
    
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denominator
    margin = z * math.sqrt(p * (1-p) / n + z**2 / (4*n**2)) / denominator
    
    lower = max(0, center - margin)
    upper = min(1, center + margin)
    
    return (lower, upper)


def analyze_results(results: List[Dict]) -> Dict:
    """
    Comprehensive statistical analysis of factorization results.
    
    Args:
        results: List of result dictionaries
    
    Returns:
        Dictionary with comprehensive analysis
    """
    # Separate by type
    unbiased = [r for r in results if r.get('target_type') == 'unbiased']
    biased = [r for r in results if r.get('target_type') == 'biased']
    
    # Success counts
    unbiased_success = len([r for r in unbiased if r.get('success', False)])
    biased_success = len([r for r in biased if r.get('success', False)])
    
    # Success rates
    rate_unbiased = unbiased_success / len(unbiased) if unbiased else 0
    rate_biased = biased_success / len(biased) if biased else 0
    
    # Wilson score confidence intervals (95%)
    ci_unbiased = wilson_ci(unbiased_success, len(unbiased), 0.95)
    ci_biased = wilson_ci(biased_success, len(biased), 0.95)
    
    # Runtime statistics
    times_unbiased = [r.get('elapsed_seconds', r.get('elapsed_time', 0)) 
                     for r in unbiased if r.get('success', False)]
    times_biased = [r.get('elapsed_seconds', r.get('elapsed_time', 0)) 
                   for r in biased if r.get('success', False)]
    
    # Method effectiveness
    methods_unbiased = [r.get('method') for r in unbiased if r.get('success', False)]
    methods_biased = [r.get('method') for r in biased if r.get('success', False)]
    
    # Timeout analysis
    timeout_unbiased = len([r for r in unbiased if r.get('method') == 'timeout' or r.get('method') == 'exhausted_methods'])
    timeout_biased = len([r for r in biased if r.get('method') == 'timeout' or r.get('method') == 'exhausted_methods'])
    
    return {
        'unbiased': {
            'total': len(unbiased),
            'success': unbiased_success,
            'rate': rate_unbiased,
            'ci_95': ci_unbiased,
            'avg_time': np.mean(times_unbiased) if times_unbiased else None,
            'median_time': np.median(times_unbiased) if times_unbiased else None,
            'min_time': min(times_unbiased) if times_unbiased else None,
            'max_time': max(times_unbiased) if times_unbiased else None,
            'method_counts': dict(Counter(methods_unbiased)),
            'timeout_count': timeout_unbiased,
            'all_times': times_unbiased
        },
        'biased': {
            'total': len(biased),
            'success': biased_success,
            'rate': rate_biased,
            'ci_95': ci_biased,
            'avg_time': np.mean(times_biased) if times_biased else None,
            'median_time': np.median(times_biased) if times_biased else None,
            'min_time': min(times_biased) if times_biased else None,
            'max_time': max(times_biased) if times_biased else None,
            'method_counts': dict(Counter(methods_biased)),
            'timeout_count': timeout_biased,
            'all_times': times_biased
        },
        'overall': {
            'total': len(results),
            'success': unbiased_success + biased_success,
            'rate': (unbiased_success + biased_success) / len(results) if results else 0
        }
    }


def generate_markdown_report(analysis: Dict, output_file: Path):
    """
    Generate comprehensive markdown report.
    
    Args:
        analysis: Analysis dictionary from analyze_results
        output_file: Path to output markdown file
    """
    lines = []
    
    # Header
    lines.append("# 100-Target Factorization Validation Results")
    lines.append("")
    lines.append("## Quick Facts")
    lines.append("")
    lines.append(f"- **Total Targets**: {analysis['overall']['total']}")
    lines.append(f"- **Unbiased**: {analysis['unbiased']['total']}")
    lines.append(f"- **Biased**: {analysis['biased']['total']}")
    lines.append(f"- **Overall Success Rate**: {analysis['overall']['success']}/{analysis['overall']['total']} ({analysis['overall']['rate']*100:.1f}%)")
    lines.append("")
    
    # Primary Finding: Unbiased
    lines.append("## Primary Finding: Unbiased 256-Bit Factorization")
    lines.append("")
    
    ub = analysis['unbiased']
    lines.append(f"**Success Rate**: {ub['success']} / {ub['total']} = {ub['rate']*100:.2f}%")
    lines.append(f"**95% Confidence Interval**: [{ub['ci_95'][0]*100:.2f}%, {ub['ci_95'][1]*100:.2f}%]")
    lines.append("")
    
    if ub['success'] > 0:
        lines.append("**Interpretation**: ECM with aggressive parameters CAN factor unbiased 256-bit, ")
        lines.append(f"but success rate is low ({ub['rate']*100:.1f}%). Viable for research, not production.")
        lines.append("")
        lines.append("**Time Statistics (Successful Factorizations)**:")
        lines.append(f"- Min: {ub['min_time']:.2f}s")
        lines.append(f"- Max: {ub['max_time']:.2f}s")
        lines.append(f"- Average: {ub['avg_time']:.2f}s")
        lines.append(f"- Median: {ub['median_time']:.2f}s")
        lines.append("")
        
        if ub['method_counts']:
            lines.append("**Methods Used**:")
            for method, count in sorted(ub['method_counts'].items(), key=lambda x: -x[1]):
                lines.append(f"- {method}: {count}")
            lines.append("")
    else:
        lines.append("**Interpretation**: Strong evidence (p < 0.05) that unbiased 256-bit exceeds ")
        lines.append("current capability with these parameters. True success rate < {:.1f}% at 95% confidence.".format(ub['ci_95'][1]*100))
        lines.append("")
        lines.append("**Recommendation**: Pivot to 192-bit unbiased or focus on biased targets.")
        lines.append("")
    
    lines.append(f"**Timeouts**: {ub['timeout_count']}/{ub['total']} ({ub['timeout_count']/ub['total']*100:.1f}%)")
    lines.append("")
    
    # Control Group: Biased
    lines.append("## Control Group: Biased Targets")
    lines.append("")
    
    bi = analysis['biased']
    lines.append(f"**Success Rate**: {bi['success']} / {bi['total']} = {bi['rate']*100:.2f}%")
    lines.append(f"**95% Confidence Interval**: [{bi['ci_95'][0]*100:.2f}%, {bi['ci_95'][1]*100:.2f}%]")
    lines.append(f"**Expected**: > 90%")
    lines.append("")
    
    if bi['rate'] >= 0.90:
        lines.append("**Status**: ✅ Validates PR #42 findings at scale.")
        lines.append("")
    else:
        lines.append("**Status**: ⚠️ Below expected 90% threshold - may indicate implementation regression.")
        lines.append("")
    
    if bi['success'] > 0:
        lines.append("**Time Statistics (Successful Factorizations)**:")
        lines.append(f"- Min: {bi['min_time']:.2f}s")
        lines.append(f"- Max: {bi['max_time']:.2f}s")
        lines.append(f"- Average: {bi['avg_time']:.2f}s")
        lines.append(f"- Median: {bi['median_time']:.2f}s")
        lines.append("")
        
        if bi['method_counts']:
            lines.append("**Methods Used**:")
            for method, count in sorted(bi['method_counts'].items(), key=lambda x: -x[1]):
                lines.append(f"- {method}: {count}")
            lines.append("")
    
    lines.append(f"**Timeouts**: {bi['timeout_count']}/{bi['total']} ({bi['timeout_count']/bi['total']*100:.1f}%)")
    lines.append("")
    
    # Method Effectiveness Comparison
    lines.append("## Method Effectiveness Comparison")
    lines.append("")
    lines.append("| Method | Unbiased Success | Biased Success | Avg Time (Unbiased) | Avg Time (Biased) |")
    lines.append("|--------|------------------|----------------|---------------------|-------------------|")
    
    all_methods = set(list(ub['method_counts'].keys()) + list(bi['method_counts'].keys()))
    for method in sorted(all_methods):
        ub_count = ub['method_counts'].get(method, 0)
        bi_count = bi['method_counts'].get(method, 0)
        # For now, we don't have per-method timing, just show counts
        lines.append(f"| {method} | {ub_count} | {bi_count} | - | - |")
    
    lines.append("")
    
    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    
    if ub['success'] > 0:
        lines.append("1. **Success Demonstrated**: Characterize successful cases to optimize parameters")
        lines.append("2. **Scale Compute**: Consider GPU acceleration (CUDA-ECM) for higher success rates")
        lines.append("3. **Estimate Requirements**: Calculate compute needed for 5%, 10%, 25% success rates")
    else:
        lines.append("1. **Capability Ceiling Identified**: Unbiased 256-bit is beyond current method/resource limits")
        lines.append("2. **Pivot Strategy**: Focus on 192-bit unbiased to find success baseline")
        lines.append("3. **Tactical Approach**: Use 256-bit biased for demonstrations, 2048-bit for production")
    
    if bi['rate'] < 0.90:
        lines.append("4. **⚠️ URGENT**: Investigate biased underperformance - possible regression from PR #42")
    
    lines.append("")
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Analysis report saved to {output_file}")


def print_summary(analysis: Dict):
    """Print summary to console."""
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal Targets: {analysis['overall']['total']}")
    print(f"Overall Success: {analysis['overall']['success']} ({analysis['overall']['rate']*100:.1f}%)")
    
    print("\n--- UNBIASED TARGETS ---")
    ub = analysis['unbiased']
    print(f"Count: {ub['total']}")
    print(f"Success: {ub['success']} ({ub['rate']*100:.2f}%)")
    print(f"95% CI: [{ub['ci_95'][0]*100:.2f}%, {ub['ci_95'][1]*100:.2f}%]")
    if ub['avg_time'] is not None:
        print(f"Avg Time: {ub['avg_time']:.2f}s")
    print(f"Timeouts: {ub['timeout_count']}")
    
    print("\n--- BIASED TARGETS ---")
    bi = analysis['biased']
    print(f"Count: {bi['total']}")
    print(f"Success: {bi['success']} ({bi['rate']*100:.2f}%)")
    print(f"95% CI: [{bi['ci_95'][0]*100:.2f}%, {bi['ci_95'][1]*100:.2f}%]")
    if bi['avg_time'] is not None:
        print(f"Avg Time: {bi['avg_time']:.2f}s")
    print(f"Timeouts: {bi['timeout_count']}")
    
    print("\n" + "="*60)


def main():
    """Main analysis function."""
    parser = argparse.ArgumentParser(
        description='Analyze 100-target factorization batch results'
    )
    parser.add_argument('--results', type=str, required=True,
                       help='Input results JSON file')
    parser.add_argument('--output', type=str, default='ANALYSIS_100SAMPLE.md',
                       help='Output markdown report (default: ANALYSIS_100SAMPLE.md)')
    
    args = parser.parse_args()
    
    # Load results
    results_file = Path(args.results)
    if not results_file.exists():
        print(f"Error: {results_file} not found")
        return 1
    
    print(f"Loading results from {results_file}...")
    results = load_results(results_file)
    print(f"Loaded {len(results)} results")
    
    # Analyze
    print("\nPerforming statistical analysis...")
    analysis = analyze_results(results)
    
    # Print summary
    print_summary(analysis)
    
    # Generate report
    output_file = Path(__file__).parent / args.output
    print(f"\nGenerating markdown report...")
    generate_markdown_report(analysis, output_file)
    
    print("\n" + "="*60)
    print("✓ Analysis complete!")
    print("="*60)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
