import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

phi = (1 + math.sqrt(5)) / 2
e = math.e

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def helical_embedding(n, k=0.3, steps=20):
    theta = phi * math.pow(n / phi, k) * math.log(n)  # Add log(n) for better spread
    x = math.cos(theta)
    y = math.sin(theta)
    z = theta / (e**2) * math.log(n)  # Scale z by log(n)
    return x, y, z

def plot_holograms(n_range):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    primes_x, primes_y, primes_z = [], [], []
    composites_x, composites_y, composites_z = [], [], []
    for n in n_range:
        x, y, z = helical_embedding(n)
        if is_prime(n):
            primes_x.append(x)
            primes_y.append(y)
            primes_z.append(z)
        else:
            composites_x.append(x)
            composites_y.append(y)
            composites_z.append(z)
    if primes_x:
        ax.plot(primes_x, primes_y, primes_z, c='red', label='Primes', marker='o')
    if composites_x:
        ax.plot(composites_x, composites_y, composites_z, c='blue', label='Composites', marker='s')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.title('Helical Embeddings: Primes vs Composites (Expanded Range)')
    plt.show()

# Example: plot for n=100000 to 100100
plot_holograms(range(100000, 100101))
