"""
Visualization Module for Z5D Prime Predictor and GVA Factorizer

This module provides comprehensive visualization tools for:
- Z5D Prime Predictor error analysis and component contributions
- GVA Factorizer torus embeddings, A* paths, and performance landscapes
- Integrated framework architecture and parameter tuning

Usage:
    from visualizations import z5d_visualizations, gva_visualizations, framework_visualizations
    
    # Generate Z5D visualizations
    z5d_visualizations.plot_log_log_error()
    z5d_visualizations.plot_component_contributions()
    
    # Generate GVA visualizations
    gva_visualizations.plot_3d_torus_embedding(N=11541040183, true_factors=(106661, 108203))
    gva_visualizations.plot_performance_landscape()
    
    # Generate framework visualizations
    framework_visualizations.plot_system_architecture()
    framework_visualizations.create_parameter_tuning_dashboard()
"""

__version__ = '1.0.0'
__all__ = ['z5d_visualizations', 'gva_visualizations', 'framework_visualizations']
