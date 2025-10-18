# Suggested Visualizations for Geometric Factorization Algorithm

This document suggests 2D and 3D plots to visualize key concepts from the geometric_factorization.py implementation. Each suggestion includes a technical definition, purpose, and implementation notes. These plots can help understand the geometric mapping, candidate generation, and filtering processes.

## 2D Plots

### 1. Unit Circle Mapping of Theta Values
**Technical Definition**: Plot points on the unit circle where each point's angle is θ(N, k) * 2π for a semiprime N and its factors p, q. Use different colors for N (red), p (blue), q (green). Draw arcs representing the circular distance.

**Purpose**: Visualize how factors cluster near N on the unit circle for specific k values.

**Implementation Notes**: Use matplotlib polar plot. Compute θ using the theta function. Example for N=143 (11×13), k=0.45.

### 2. Theta vs. Log(N) Scatter Plot
**Technical Definition**: Scatter plot with x-axis as log10(N) for a range of semiprimes, y-axis as θ(N, k) in [0,1). Color points by whether N is semiprime (blue) or composite (gray).

**Purpose**: Show distribution patterns of θ values across number scales, highlighting clustering for factors.

**Implementation Notes**: Generate 1000+ semiprimes, compute θ for fixed k (e.g., 0.2). Use scatter with alpha=0.5 for density visualization.

### 3. Circular Distance Histogram
**Technical Definition**: Histogram of circular distances between θ(N, k) and θ(p, k) for true factors p across many semiprimes. Bin from 0 to 0.5.

**Purpose**: Demonstrate that true factors have small circular distances, justifying the ε threshold.

**Implementation Notes**: Use numpy histogram. Test with 100 semiprimes, multiple k values as separate curves.

### 4. Golden Spiral Candidate Generation
**Technical Definition**: Plot the golden spiral in 2D Cartesian coordinates, with points colored by whether they correspond to prime candidates near √N.

**Purpose**: Visualize how the spiral generates candidates distributed around √N.

**Implementation Notes**: Plot x = r * cos(γ*i), y = r * sin(γ*i) with r = sqrt(i). Scale and offset to √N. Mark primes in green.

### 5. Candidate Filtering Before/After
**Technical Definition**: Dual scatter plots: left shows all candidates vs. their θ values; right shows filtered candidates (those with dist ≤ ε). X-axis: candidate value, y-axis: θ(candidate, k).

**Purpose**: Illustrate reduction in candidate space via geometric filtering.

**Implementation Notes**: Use subplots. Vertical line at √N. Color filtered points in blue.

## 3D Plots

### 1. Theta Surface over N and k
**Technical Definition**: 3D surface plot with x=log10(N), y=k in [0,1], z=θ(N,k). Use meshgrid for semiprime N values.

**Purpose**: Show how θ varies with both N and the exponent k, revealing patterns in geometric mapping.

**Implementation Notes**: Use matplotlib 3D surface. Sample N from 10 to 10^6, k from 0.1 to 0.9.

### 2. 3D Spiral Candidate Cloud
**Technical Definition**: 3D scatter plot extending the golden spiral by adding a third dimension (e.g., iteration i as z-axis). Color by primality.

**Purpose**: Visualize the 3D structure of candidate generation, showing density and distribution.

**Implementation Notes**: x = r*cos(γ*i), y = r*sin(γ*i), z = i or log(i). Use Plotly for interactive viewing.

### 3. Distance Landscape
**Technical Definition**: 3D surface where x=candidate p, y=k, z=circular_distance(θ(p,k), θ(N,k)) for fixed N. Highlight minima.

**Purpose**: Identify optimal k values where true factors have minimal distance.

**Implementation Notes**: Meshgrid over p near √N and k range. Use wireframe or surface with colormap (low distance = blue).

### 4. Multi-Pass Parameter Space
**Technical Definition**: 3D scatter with x=k, y=ε, z=reduction ratio (pre/post filter count). Size points by success rate.

**Purpose**: Explore how parameter combinations affect filtering efficiency and success.

**Implementation Notes**: Run simulations over k_list and eps_list, plot results. Color by bit size.

### 5. Factor Clustering in 3D
**Technical Definition**: 3D scatter with axes as θ(p, k1), θ(p, k2), θ(p, k3) for different k values. Plot points for true factors vs. random primes.

**Purpose**: Show clustering of true factors in multi-dimensional geometric space.

**Implementation Notes**: Use three k values (e.g., 0.2, 0.45, 0.8). Blue for factors, red for non-factors.

These visualizations can be implemented using libraries like matplotlib, seaborn, or Plotly. They provide insights into the algorithm's geometric foundations and can aid in parameter tuning and educational purposes.