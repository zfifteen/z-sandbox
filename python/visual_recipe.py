import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal, getcontext

# Set high precision for calculations
getcontext().prec = 50

# Golden ratio
PHI = Decimal((1 + 5**0.5) / 2)

def theta(m, k):
    """Compute theta(m, k) = fractional part of phi * (m/phi)^k"""
    m = Decimal(m)
    k = Decimal(k)
    return float((PHI * (m / PHI) ** k) % 1)

def circular_distance(a, b):
    """Circular distance on [0,1)"""
    diff = abs(a - b)
    return min(diff, 1 - diff)

# Example: N = 91 = 7 * 13
N = 91
p1, p2 = 7, 13

# Range of k
k_values = np.linspace(0.1, 10, 100)

# Compute theta for N, p1, p2
theta_N = [theta(N, k) for k in k_values]
theta_p1 = [theta(p1, k) for k in k_values]
theta_p2 = [theta(p2, k) for k in k_values]

# Compute distances
dist_p1 = [circular_distance(tn, tp1) for tn, tp1 in zip(theta_N, theta_p1)]
dist_p2 = [circular_distance(tn, tp2) for tn, tp2 in zip(theta_N, theta_p2)]

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Top plot: theta values
ax1.plot(k_values, theta_N, label=f'θ({N}, k)', color='blue', linewidth=2)
ax1.plot(k_values, theta_p1, label=f'θ({p1}, k)', color='green', linestyle='--')
ax1.plot(k_values, theta_p2, label=f'θ({p2}, k)', color='red', linestyle='--')
ax1.set_xlabel('k')
ax1.set_ylabel('θ(m, k)')
ax1.set_title('Geometric Factorization: θ(N,k) vs θ(p,k) for N=91=7×13')
ax1.legend()
ax1.grid(True)

# Bottom plot: distances
ax2.plot(k_values, dist_p1, label=f'distance to {p1}', color='green')
ax2.plot(k_values, dist_p2, label=f'distance to {p2}', color='red')
ax2.axhline(y=0.15, color='black', linestyle=':', label='tolerance ε=0.15')
ax2.set_xlabel('k')
ax2.set_ylabel('Circular Distance')
ax2.set_title('Circular Distances: Clustering Effect')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('geometric_factorization_plot.png', dpi=300)
plt.show()

print("Plot saved as 'geometric_factorization_plot.png'")
print(f"At k=5: θ({N},5) ≈ {theta(N,5):.3f}, θ({p1},5) ≈ {theta(p1,5):.3f}, distance ≈ {circular_distance(theta(N,5), theta(p1,5)):.3f}")
print(f"At k=5: θ({p2},5) ≈ {theta(p2,5):.3f}, distance ≈ {circular_distance(theta(N,5), theta(p2,5)):.3f}")