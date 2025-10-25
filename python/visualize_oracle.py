#!/usr/bin/env python3
"""
Oracle Visualization Script

Generates error-vs-N plots demonstrating QMC convergence behavior
against deterministic oracle ground truth.

Creates visualizations showing:
1. Absolute error vs sample count (log-log scale)
2. Theoretical vs empirical convergence rates
3. QMC improvement factors over MC
"""

import sys
import os
import math
import numpy as np

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, plots will not be generated")

from oracle import DeterministicOracle
from benchmark_oracle_qmc import OracleQMCBenchmark


def plot_convergence_comparison(results, pi_true, output_file='oracle_convergence.png'):
    """
    Generate convergence comparison plot.
    
    Args:
        results: Results dictionary from benchmark
        pi_true: True value of π
        output_file: Output filename
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, skipping plot generation")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Error vs N (log-log scale)
    ax1.set_title('Convergence Rate Comparison', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Sample Count (N)', fontsize=12)
    ax1.set_ylabel('Absolute Error', fontsize=12)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    colors = {'uniform': 'red', 'stratified': 'orange', 'qmc': 'blue', 'qmc_phi_hybrid': 'green'}
    markers = {'uniform': 'o', 'stratified': 's', 'qmc': '^', 'qmc_phi_hybrid': 'd'}
    
    for mode, data in results.items():
        ax1.plot(data['N'], data['errors'], 
                marker=markers.get(mode, 'o'),
                color=colors.get(mode, 'black'),
                label=mode, linewidth=2, markersize=8)
    
    # Add theoretical bounds
    N_range = np.array(results['uniform']['N'])
    mc_theory = 1.0 / np.sqrt(N_range)
    qmc_theory = (np.log(N_range) ** 2) / N_range
    
    ax1.plot(N_range, mc_theory, '--', color='gray', 
            label='MC theory: O(1/√N)', linewidth=1.5, alpha=0.7)
    ax1.plot(N_range, qmc_theory, '-.', color='gray',
            label='QMC theory: O((log N)²/N)', linewidth=1.5, alpha=0.7)
    
    ax1.legend(loc='upper right', fontsize=10)
    
    # Plot 2: Improvement factor vs N
    ax2.set_title('QMC Improvement Over MC', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Sample Count (N)', fontsize=12)
    ax2.set_ylabel('Improvement Factor (MC error / QMC error)', fontsize=12)
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.3)
    
    if 'uniform' in results and 'qmc' in results:
        uniform_errors = np.array(results['uniform']['errors'])
        qmc_errors = np.array(results['qmc']['errors'])
        
        # Avoid division by zero
        improvement = np.where(qmc_errors > 0, uniform_errors / qmc_errors, 1.0)
        
        ax2.plot(results['uniform']['N'], improvement,
                marker='^', color='purple', linewidth=2, markersize=8,
                label='QMC / Uniform MC')
        
        # Add theoretical improvement: √N / (log N)²
        theory_improvement = np.sqrt(N_range) / (np.log(N_range) ** 2)
        ax2.plot(N_range, theory_improvement, '--', color='gray',
                label='Theory: √N / (log N)²', linewidth=1.5, alpha=0.7)
    
    ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.legend(loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Convergence plot saved to {output_file}")
    plt.close()


def plot_method_comparison(results, output_file='oracle_methods.png'):
    """
    Generate detailed method comparison plots.
    
    Args:
        results: Results dictionary from benchmark
        output_file: Output filename
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, skipping plot generation")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = {'uniform': 'red', 'stratified': 'orange', 'qmc': 'blue', 'qmc_phi_hybrid': 'green'}
    
    # Plot 1: Absolute Error
    ax1.set_title('Absolute Error vs Sample Count', fontsize=12, fontweight='bold')
    ax1.set_xlabel('N')
    ax1.set_ylabel('Absolute Error')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    for mode, data in results.items():
        ax1.plot(data['N'], data['errors'], 
                marker='o', color=colors.get(mode, 'black'),
                label=mode, linewidth=2)
    ax1.legend()
    
    # Plot 2: Relative Error
    ax2.set_title('Relative Error vs Sample Count', fontsize=12, fontweight='bold')
    ax2.set_xlabel('N')
    ax2.set_ylabel('Relative Error')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    for mode, data in results.items():
        ax2.plot(data['N'], data['rel_errors'],
                marker='s', color=colors.get(mode, 'black'),
                label=mode, linewidth=2)
    ax2.legend()
    
    # Plot 3: Computation Time
    ax3.set_title('Computation Time vs Sample Count', fontsize=12, fontweight='bold')
    ax3.set_xlabel('N')
    ax3.set_ylabel('Time (seconds)')
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    for mode, data in results.items():
        ax3.plot(data['N'], data['times'],
                marker='^', color=colors.get(mode, 'black'),
                label=mode, linewidth=2)
    ax3.legend()
    
    # Plot 4: Efficiency (Error × Time)
    ax4.set_title('Efficiency Metric (Error × Time)', fontsize=12, fontweight='bold')
    ax4.set_xlabel('N')
    ax4.set_ylabel('Error × Time')
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    for mode, data in results.items():
        efficiency = np.array(data['errors']) * np.array(data['times'])
        ax4.plot(data['N'], efficiency,
                marker='d', color=colors.get(mode, 'black'),
                label=mode, linewidth=2)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Method comparison plot saved to {output_file}")
    plt.close()


def generate_visualizations():
    """Generate all oracle visualization plots."""
    print("=" * 80)
    print("Oracle Visualization Generator")
    print("=" * 80)
    print()
    
    if not MATPLOTLIB_AVAILABLE:
        print("ERROR: matplotlib is required for visualization")
        print("Install with: pip install matplotlib")
        return False
    
    # Run benchmark to get fresh data
    print("Running oracle benchmark to generate data...")
    benchmark = OracleQMCBenchmark(precision=100, seed=42)
    sample_counts = [100, 500, 1000, 5000, 10000, 50000, 100000]
    
    print(f"Testing {len(sample_counts)} sample counts...")
    results, pi_true = benchmark.run_convergence_test(sample_counts)
    print()
    
    # Generate plots
    print("Generating visualizations...")
    plot_convergence_comparison(results, pi_true, 'oracle_convergence.png')
    plot_method_comparison(results, 'oracle_methods.png')
    
    print()
    print("=" * 80)
    print("Visualization Summary")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  1. oracle_convergence.png - Main convergence comparison")
    print("  2. oracle_methods.png     - Detailed method comparison")
    print()
    print("Key observations:")
    print("  • QMC achieves O((log N)²/N) convergence")
    print("  • MC achieves O(1/√N) convergence")
    print("  • QMC improvement factor increases with N")
    print("  • Deterministic oracle provides clean error measurement")
    print()
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = generate_visualizations()
    sys.exit(0 if success else 1)
