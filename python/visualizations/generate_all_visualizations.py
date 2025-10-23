#!/usr/bin/env python3
"""
Comprehensive Visualization Examples

This script demonstrates all visualization capabilities for the Z5D Prime Predictor
and GVA Factorizer, generating all plots and dashboards described in the issue.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizations import z5d_visualizations
from visualizations import gva_visualizations
from visualizations import framework_visualizations


def generate_all_visualizations():
    """
    Generate all visualizations for Z5D, GVA, and the integrated framework.
    """
    print("=" * 80)
    print("COMPREHENSIVE VISUALIZATION SUITE")
    print("Z5D Prime Predictor & GVA Factorizer")
    print("=" * 80)
    
    # Ensure plots directory exists
    plots_dir = Path(__file__).parent.parent.parent / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # ====================================================================
    # Part 1: Z5D Prime Predictor Visualizations
    # ====================================================================
    print("\n" + "=" * 80)
    print("PART 1: Z5D PRIME PREDICTOR VISUALIZATIONS")
    print("=" * 80)
    
    print("\n1.1 Log-Log Plot of Relative Error")
    print("-" * 80)
    print("Comparing Z5D, Li(k), and PNT approximations...")
    z5d_visualizations.plot_log_log_error()
    
    print("\n1.2 Component Contribution Stacked Area Chart")
    print("-" * 80)
    print("Showing PNT base, dilation correction, and curvature correction...")
    z5d_visualizations.plot_component_contributions()
    
    print("\n1.3 Interactive Comparison Dashboard")
    print("-" * 80)
    print("Creating interactive Plotly visualization...")
    z5d_visualizations.create_interactive_comparison()
    
    # ====================================================================
    # Part 2: GVA Factorizer Visualizations
    # ====================================================================
    print("\n" + "=" * 80)
    print("PART 2: GVA FACTORIZER VISUALIZATIONS")
    print("=" * 80)
    
    # Example semiprime
    N = 11541040183  # 106661 × 108203
    p, q = 106661, 108203
    print(f"\nUsing example semiprime: N = {N} = {p} × {q}")
    print(f"Bit length: {N.bit_length()} bits")
    print(f"Factor ratio: {max(p,q)/min(p,q):.4f}")
    
    print("\n2.1 Interactive 3D Torus Embedding")
    print("-" * 80)
    print("Visualizing candidates on 5-torus with Z5D seeds and true factors...")
    gva_visualizations.plot_3d_torus_embedding(N, true_factors=(p, q), num_candidates=100)
    
    print("\n2.2 3D Animation of A* Geodesic Path")
    print("-" * 80)
    print("Animating the search from Z5D seed to target factor...")
    gva_visualizations.plot_astar_path_animation(N, p, num_steps=50)
    
    print("\n2.3 3D Surface Plot of Performance Landscape")
    print("-" * 80)
    print("Mapping success rate vs factor ratio and bit length...")
    gva_visualizations.plot_performance_landscape()
    
    print("\n2.4 Curvature Effect Visualization")
    print("-" * 80)
    print("Showing how Riemannian curvature affects distance measurements...")
    gva_visualizations.plot_curvature_effect()
    
    # ====================================================================
    # Part 3: Integrated Framework Visualizations
    # ====================================================================
    print("\n" + "=" * 80)
    print("PART 3: INTEGRATED FRAMEWORK VISUALIZATIONS")
    print("=" * 80)
    
    print("\n3.1 System Architecture Flowchart")
    print("-" * 80)
    print("Creating high-level architecture diagram...")
    framework_visualizations.plot_system_architecture()
    
    print("\n3.2 Interactive Parameter Tuning Dashboard")
    print("-" * 80)
    print("Building interactive dashboard for κ and k parameters...")
    framework_visualizations.create_parameter_tuning_dashboard()
    
    print("\n3.3 Component Integration Analysis")
    print("-" * 80)
    print("Visualizing cumulative contributions of each component...")
    framework_visualizations.plot_component_integration()
    
    # ====================================================================
    # Summary
    # ====================================================================
    print("\n" + "=" * 80)
    print("VISUALIZATION GENERATION COMPLETE")
    print("=" * 80)
    
    print("\nGenerated files:")
    print("-" * 80)
    
    output_files = [
        # Z5D visualizations
        ("Z5D Log-Log Error Plot", "plots/z5d_log_log_error.png"),
        ("Z5D Component Contributions", "plots/z5d_component_contributions.png"),
        ("Z5D Interactive Comparison", "plots/z5d_interactive_comparison.html"),
        # GVA visualizations
        ("GVA 3D Torus Embedding", "plots/gva_3d_torus_embedding.html"),
        ("GVA A* Animation", "plots/gva_astar_animation.html"),
        ("GVA Performance Landscape", "plots/gva_performance_landscape.html"),
        ("GVA Curvature Effect", "plots/gva_curvature_effect.png"),
        # Framework visualizations
        ("Framework Architecture", "plots/framework_architecture.png"),
        ("Framework Parameter Dashboard", "plots/framework_parameter_dashboard.html"),
        ("Framework Component Integration", "plots/framework_component_integration.png"),
    ]
    
    for name, path in output_files:
        full_path = Path(__file__).parent.parent.parent / path
        if full_path.exists():
            size = full_path.stat().st_size / 1024  # KB
            print(f"✓ {name:40s} -> {path:50s} ({size:.1f} KB)")
        else:
            print(f"✗ {name:40s} -> {path:50s} (NOT FOUND)")
    
    print("\n" + "=" * 80)
    print("To view the visualizations:")
    print("  - PNG files: Open with any image viewer")
    print("  - HTML files: Open with a web browser for interactive 3D/animations")
    print("=" * 80)


if __name__ == "__main__":
    try:
        generate_all_visualizations()
    except KeyboardInterrupt:
        print("\n\nVisualization generation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during visualization generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
