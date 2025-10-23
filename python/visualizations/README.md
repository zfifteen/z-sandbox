# Visualization Suite for Z5D Prime Predictor and GVA Factorizer

This module provides comprehensive visualizations for the Z5D Prime Predictor and GVA (Geodesic Validation Assault) Factorizer, as well as the integrated RSA Factorization Ladder Framework.

## Overview

The visualization suite includes three main components:

### 1. Z5D Prime Predictor Visualizations (`z5d_visualizations.py`)

Demonstrates the accuracy and performance of the Z5D prime predictor at various scales.

**Available Visualizations:**
- **Log-Log Plot of Relative Error**: Compares Z5D with Li(k) and PNT approximations
- **Component Contribution Stacked Area Chart**: Shows how base PNT, dilation correction, and curvature correction contribute to the final prediction
- **Interactive Comparison Dashboard**: Plotly-based interactive exploration

### 2. GVA Factorizer Visualizations (`gva_visualizations.py`)

Makes the abstract geometric approach of GVA intuitive through 3D visualizations.

**Available Visualizations:**
- **Interactive 3D Torus Embedding**: Shows candidates plotted on the 5-torus with Z5D seeds highlighted and factors marked
- **3D Animation of A* Geodesic Path**: Animates the search from Z5D seed to target factor
- **3D Performance Landscape**: Maps success rate vs factor ratio and bit length
- **Curvature Effect Plot**: Visualizes how Riemannian curvature affects distance measurements

### 3. Framework Visualizations (`framework_visualizations.py`)

Provides high-level views of the integrated system architecture.

**Available Visualizations:**
- **System Architecture Flowchart**: Shows how components (Z5D, GVA, builders) work together
- **Interactive Parameter Tuning Dashboard**: Explore effects of κ (curvature) and k (skew) parameters
- **Component Integration Analysis**: Visualizes cumulative contributions

## Installation

### Requirements

```bash
cd /home/runner/work/z-sandbox/z-sandbox/python
pip install -r requirements.txt
```

Required packages:
- matplotlib >= 3.9.0
- plotly >= 5.18.0
- numpy >= 2.0.0
- scipy >= 1.13.0
- mpmath >= 1.3.0
- sympy >= 1.13.0
- dash >= 2.14.0 (for interactive dashboards)
- kaleido >= 0.2.1 (for static image export from Plotly)

## Usage

### Quick Start - Generate All Visualizations

```bash
cd /home/runner/work/z-sandbox/z-sandbox/python/visualizations
python3 generate_all_visualizations.py
```

This will generate all visualizations and save them to the `plots/` directory.

### Individual Modules

#### Z5D Visualizations

```python
from visualizations import z5d_visualizations

# Generate log-log error plot
z5d_visualizations.plot_log_log_error()

# Generate component contribution chart
z5d_visualizations.plot_component_contributions()

# Create interactive comparison
z5d_visualizations.create_interactive_comparison()
```

#### GVA Visualizations

```python
from visualizations import gva_visualizations

# Example semiprime
N = 11541040183  # 106661 × 108203
p, q = 106661, 108203

# 3D torus embedding
gva_visualizations.plot_3d_torus_embedding(N, true_factors=(p, q))

# A* path animation
gva_visualizations.plot_astar_path_animation(N, p)

# Performance landscape
gva_visualizations.plot_performance_landscape()

# Curvature effect
gva_visualizations.plot_curvature_effect()
```

#### Framework Visualizations

```python
from visualizations import framework_visualizations

# System architecture
framework_visualizations.plot_system_architecture()

# Parameter tuning dashboard
framework_visualizations.create_parameter_tuning_dashboard()

# Component integration
framework_visualizations.plot_component_integration()
```

## Output Files

All visualizations are saved to `/home/runner/work/z-sandbox/z-sandbox/plots/`:

### Static Images (PNG)
- `z5d_log_log_error.png` - Z5D error comparison
- `z5d_component_contributions.png` - Component contributions
- `gva_curvature_effect.png` - Curvature visualization
- `framework_architecture.png` - System architecture flowchart
- `framework_component_integration.png` - Component integration analysis

### Interactive HTML (Plotly)
- `z5d_interactive_comparison.html` - Interactive Z5D comparison
- `gva_3d_torus_embedding.html` - 3D torus with interactive rotation
- `gva_astar_animation.html` - Animated A* search path
- `gva_performance_landscape.html` - 3D performance surface
- `framework_parameter_dashboard.html` - Parameter tuning interface

## Key Features

### Z5D Visualizations
- **Power-law convergence**: Clearly demonstrates Z5D's superior error decay
- **Component analysis**: Shows negligible correction terms at small scales become crucial at large scales
- **Comparative benchmarks**: Direct comparison with established methods (Li, PNT)

### GVA Visualizations
- **Geometric intuition**: Transforms abstract torus embedding into tangible 3D space
- **Search visualization**: Shows GVA is targeted navigation, not brute-force
- **Performance mapping**: Identifies optimal operating conditions (balanced factors, 64-128 bits)

### Framework Visualizations
- **System overview**: Clear map of how components collaborate
- **Parameter sensitivity**: Interactive exploration of configuration space
- **Contribution analysis**: Quantifies impact of each component

## Customization

All visualization functions accept parameters for customization:

```python
# Custom k values for Z5D analysis
k_values = [10**i for i in range(1, 8)]
z5d_visualizations.plot_log_log_error(k_values=k_values)

# Custom number of candidates for GVA
gva_visualizations.plot_3d_torus_embedding(N, true_factors=(p,q), num_candidates=200)

# Custom output paths
z5d_visualizations.plot_log_log_error(output_path='custom/path/plot.png')
```

## Performance Notes

- Z5D log-log plots: Computing actual primes using sympy can be slow for k > 10^6. Use smaller ranges for faster generation.
- GVA 3D embeddings: Interactive HTML files can be large (1-5 MB) with many points.
- Animations: A* path animations may take a few seconds to generate and load in browser.

## Troubleshooting

### Import Errors
Ensure you're running from the correct directory or add the parent directory to Python path:
```python
import sys
sys.path.insert(0, '/home/runner/work/z-sandbox/z-sandbox/python')
```

### Missing Plots Directory
The scripts will automatically create the `plots/` directory if it doesn't exist.

### Plotly Rendering Issues
If interactive HTML files don't render in browser:
1. Check browser console for JavaScript errors
2. Try opening in a different browser (Chrome, Firefox recommended)
3. Ensure kaleido is installed for static image export

## Examples

See `generate_all_visualizations.py` for comprehensive examples of all visualization capabilities.

## References

- **Z5D Prime Predictor**: `../z5d_predictor.py`
- **GVA Factorizer**: `../gva_factorize.py`, `../manifold_core.py`
- **Framework**: See main repository README and architecture docs

## License

Same as parent project.
