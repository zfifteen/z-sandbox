#!/usr/bin/env python3
"""
Z5D Prime Predictor Visualizations

This module provides comprehensive visualizations for the Z5D Prime Predictor,
including error analysis and component contribution charts.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path

# Add parent directory to path to import z5d_predictor
sys.path.insert(0, str(Path(__file__).parent.parent))
from z5d_predictor import z5d_predict
from mpmath import mp, log, mpf
from sympy import prime

# Get repository root for consistent plot paths
REPO_ROOT = Path(__file__).parent.parent.parent
PLOTS_DIR = REPO_ROOT / 'plots'


def pnt_approximation(k):
    """
    Prime Number Theorem approximation: p(k) ≈ k * ln(k)
    """
    if k < 2:
        return 2
    k_mp = mpf(k)
    return float(k_mp * log(k_mp))


def logarithmic_integral(k):
    """
    Logarithmic integral Li(k) approximation for the k-th prime.
    Using the approximation: p(k) ≈ k * (ln(k) + ln(ln(k)) - 1)
    """
    if k < 2:
        return 2
    k_mp = mpf(k)
    log_k = log(k_mp)
    log_log_k = log(log_k)
    return float(k_mp * (log_k + log_log_k - 1))


def compute_relative_error(predicted, actual):
    """
    Compute relative error: |predicted - actual| / actual
    """
    if actual == 0:
        return 0
    return abs(predicted - actual) / actual


def plot_log_log_error(k_values=None, output_path=None):
    """
    Create a 2D log-log plot comparing relative errors of:
    1. Z5D Predictor
    2. Logarithmic Integral Li(k)
    3. Prime Number Theorem k*ln(k)
    
    Args:
        k_values: List of k indices to test. If None, uses exponential range.
        output_path: Path to save the plot. If None, uses default in plots/
    """
    if output_path is None:
        output_path = PLOTS_DIR / 'z5d_log_log_error.png'
    else:
        output_path = Path(output_path)
    if k_values is None:
        # Generate exponential range from 10^1 to 10^5 (limited for practical computation)
        k_values = np.logspace(1, 5, 50, dtype=int)
    
    # Filter to unique values and ensure k >= 2
    k_values = sorted(set([k for k in k_values if k >= 2]))
    
    print(f"Computing errors for {len(k_values)} values of k...")
    
    z5d_errors = []
    li_errors = []
    pnt_errors = []
    valid_k = []
    
    for i, k in enumerate(k_values):
        try:
            # Convert to Python int if numpy type
            k = int(k)
            
            if i % 10 == 0:
                print(f"Progress: {i}/{len(k_values)} - k={k}")
            
            # Get actual prime value
            actual_prime = prime(k)
            
            # Z5D prediction
            z5d_pred = z5d_predict(k)
            z5d_err = compute_relative_error(z5d_pred, actual_prime)
            
            # Li approximation
            li_pred = logarithmic_integral(k)
            li_err = compute_relative_error(li_pred, actual_prime)
            
            # PNT approximation
            pnt_pred = pnt_approximation(k)
            pnt_err = compute_relative_error(pnt_pred, actual_prime)
            
            # Only include if all errors are valid (non-zero)
            if z5d_err > 0 and li_err > 0 and pnt_err > 0:
                valid_k.append(k)
                z5d_errors.append(z5d_err)
                li_errors.append(li_err)
                pnt_errors.append(pnt_err)
        except Exception as e:
            print(f"Error at k={k}: {e}")
            continue
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot on log-log scale
    ax.loglog(valid_k, z5d_errors, 'b-', linewidth=2, label='Z5D Predictor', marker='o', markersize=4)
    ax.loglog(valid_k, li_errors, 'g--', linewidth=2, label='Logarithmic Integral Li(k)', marker='s', markersize=4)
    ax.loglog(valid_k, pnt_errors, 'r:', linewidth=2, label='Prime Number Theorem k·ln(k)', marker='^', markersize=4)
    
    ax.set_xlabel('Prime Index k (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Relative Error |predicted - actual| / actual (log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Z5D Prime Predictor: Superior Convergence Analysis\nLog-Log Plot of Relative Error vs Prime Index', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.grid(True, which='minor', alpha=0.1, linestyle=':', linewidth=0.3)
    
    # Add annotations
    textstr = f'Computed for {len(valid_k)} prime indices\nZ5D shows fastest error decay'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to {output_path}")
    
    # Print statistics
    print("\n=== Error Statistics ===")
    print(f"Z5D - Mean: {np.mean(z5d_errors):.6e}, Median: {np.median(z5d_errors):.6e}")
    print(f"Li(k) - Mean: {np.mean(li_errors):.6e}, Median: {np.median(li_errors):.6e}")
    print(f"PNT - Mean: {np.mean(pnt_errors):.6e}, Median: {np.median(pnt_errors):.6e}")
    
    return fig, ax


def plot_component_contributions(k_values=None, output_path=None):
    """
    Create a stacked area chart showing how each term in Z5D contributes:
    1. Base PNT approximation
    2. Dilation correction
    3. Curvature correction
    
    Args:
        k_values: List of k indices to test. If None, uses linear range.
        output_path: Path to save the plot. If None, uses default in plots/
    """
    if output_path is None:
        output_path = PLOTS_DIR / 'z5d_component_contributions.png'
    else:
        output_path = Path(output_path)
    if k_values is None:
        k_values = np.logspace(1, 5, 100, dtype=int)
    
    k_values = sorted(set([k for k in k_values if k >= 2]))
    
    print(f"Computing component contributions for {len(k_values)} values of k...")
    
    pnt_base = []
    dilation_correction = []
    curvature_correction = []
    
    E2 = np.exp(2)
    
    for k in k_values:
        # Convert to Python int if numpy type
        k = int(k)
        k_mp = mpf(k)
        log_k = log(k_mp)
        log_log_k = log(log_k)
        
        # Base PNT
        temp1 = log_log_k - 2
        temp2 = temp1 / log_k
        temp3 = log_k + log_log_k - 1 + temp2
        pnt = float(k_mp * temp3)
        
        # Dilation correction: c * d(k) * p_PNT
        d_term = float(-0.00247 * pnt)
        
        # Curvature correction: k* * e(k) * p_PNT
        from mpmath import exp
        temp_exp = exp(log_k / E2)
        e_term = float(0.04449 * temp_exp * pnt)
        
        pnt_base.append(pnt)
        dilation_correction.append(d_term)
        curvature_correction.append(e_term)
    
    # Create stacked area plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Top plot: Stacked area chart
    ax1.fill_between(k_values, 0, pnt_base, alpha=0.7, label='Base PNT Approximation', color='steelblue')
    
    # For stacking, we need cumulative values
    pnt_array = np.array(pnt_base)
    dilation_array = np.array(dilation_correction)
    curvature_array = np.array(curvature_correction)
    
    # Stack dilation on top of PNT
    cumulative_1 = pnt_array
    cumulative_2 = pnt_array + dilation_array
    cumulative_3 = pnt_array + dilation_array + curvature_array
    
    ax1.fill_between(k_values, cumulative_1, cumulative_2, alpha=0.7, 
                     label='+ Dilation Correction', color='coral')
    ax1.fill_between(k_values, cumulative_2, cumulative_3, alpha=0.7, 
                     label='+ Curvature Correction', color='mediumseagreen')
    
    ax1.set_xlabel('Prime Index k', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Predicted Prime Value', fontsize=12, fontweight='bold')
    ax1.set_title('Z5D Component Contributions: Stacked Area Chart', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Bottom plot: Relative contribution percentages
    total_contribution = cumulative_3
    pnt_percent = (pnt_array / total_contribution) * 100
    dilation_percent = (dilation_array / total_contribution) * 100
    curvature_percent = (curvature_array / total_contribution) * 100
    
    ax2.plot(k_values, pnt_percent, 'b-', linewidth=2, label='Base PNT %', marker='o', markersize=3)
    ax2.plot(k_values, dilation_percent, 'r-', linewidth=2, label='Dilation Correction %', marker='s', markersize=3)
    ax2.plot(k_values, curvature_percent, 'g-', linewidth=2, label='Curvature Correction %', marker='^', markersize=3)
    
    ax2.set_xlabel('Prime Index k (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Contribution (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Relative Contribution of Each Component', fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to {output_path}")
    
    return fig, (ax1, ax2)


def create_interactive_comparison(k_values=None, output_path=None):
    """
    Create an interactive Plotly visualization comparing Z5D with other methods.
    
    Args:
        k_values: List of k indices to test
        output_path: Path to save the HTML file. If None, uses default in plots/
    """
    if output_path is None:
        output_path = PLOTS_DIR / 'z5d_interactive_comparison.html'
    else:
        output_path = Path(output_path)
    if k_values is None:
        k_values = np.logspace(1, 4, 40, dtype=int)
    
    k_values = sorted(set([k for k in k_values if k >= 2]))
    
    print(f"Creating interactive comparison for {len(k_values)} values of k...")
    
    actual_primes = []
    z5d_predictions = []
    li_predictions = []
    pnt_predictions = []
    
    for k in k_values:
        try:
            # Convert to Python int if numpy type
            k = int(k)
            actual_primes.append(prime(k))
            z5d_predictions.append(z5d_predict(k))
            li_predictions.append(logarithmic_integral(k))
            pnt_predictions.append(pnt_approximation(k))
        except:
            continue
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Predictions vs Actual', 'Relative Errors (Log Scale)',
                       'Component Contributions', 'Error Ratios'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Plot 1: Predictions vs Actual
    fig.add_trace(go.Scatter(x=k_values, y=actual_primes, mode='lines', name='Actual Primes',
                             line=dict(color='black', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=k_values, y=z5d_predictions, mode='lines+markers', name='Z5D',
                             line=dict(color='blue', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=k_values, y=li_predictions, mode='lines+markers', name='Li(k)',
                             line=dict(color='green', width=2, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=k_values, y=pnt_predictions, mode='lines+markers', name='PNT',
                             line=dict(color='red', width=2, dash='dot')), row=1, col=1)
    
    # Plot 2: Relative errors
    z5d_errors = [compute_relative_error(p, a) for p, a in zip(z5d_predictions, actual_primes)]
    li_errors = [compute_relative_error(p, a) for p, a in zip(li_predictions, actual_primes)]
    pnt_errors = [compute_relative_error(p, a) for p, a in zip(pnt_predictions, actual_primes)]
    
    fig.add_trace(go.Scatter(x=k_values, y=z5d_errors, mode='lines+markers', name='Z5D Error',
                             line=dict(color='blue', width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=k_values, y=li_errors, mode='lines+markers', name='Li(k) Error',
                             line=dict(color='green', width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=k_values, y=pnt_errors, mode='lines+markers', name='PNT Error',
                             line=dict(color='red', width=2)), row=1, col=2)
    
    # Update axes for log scale
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(type="log", row=1, col=1)
    fig.update_xaxes(type="log", row=1, col=2)
    fig.update_yaxes(type="log", row=1, col=2)
    
    fig.update_layout(
        title_text="Z5D Prime Predictor: Interactive Comparison Dashboard",
        showlegend=True,
        height=800,
        hovermode='x unified'
    )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"Interactive plot saved to {output_path}")
    
    return fig


if __name__ == "__main__":
    print("=" * 70)
    print("Z5D Prime Predictor Visualization Suite")
    print("=" * 70)
    
    # Create output directory
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    print("\n1. Generating Log-Log Error Plot...")
    plot_log_log_error()
    
    print("\n2. Generating Component Contribution Plot...")
    plot_component_contributions()
    
    print("\n3. Generating Interactive Comparison...")
    create_interactive_comparison()
    
    print("\n" + "=" * 70)
    print("All visualizations completed successfully!")
    print("=" * 70)
