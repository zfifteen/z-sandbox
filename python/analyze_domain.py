import math
import matplotlib.pyplot as plt

phi = (1 + math.sqrt(5)) / 2
e = math.e

def fib(k):
    return int(math.pow(phi, k) / math.sqrt(5) + 0.5)

def log_magnitude(n, k):
    ln_n = math.log(n)
    Fk = fib(k)
    Fkp1 = fib(k + 1)
    if k % 2 == 1:  # odd k
        return abs(Fk * ln_n - Fkp1)
    else:  # even k
        return abs(Fkp1 - Fk * ln_n)

def analyze_domain(n, max_k=22):
    print(f"Analysis for n={n}:")
    for k in range(1, max_k + 1):
        logmag = log_magnitude(n, k)
        print(f"k={k}: log|s_k| ≈ {logmag:.2f}")
    # Plot
    k_values = list(range(1, max_k + 1))
    logmags = [log_magnitude(n, k) for k in k_values]
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, logmags, marker='o', linestyle='-', color='b')
    plt.xlabel('k')
    plt.ylabel('log|s_k|')
    plt.title(f'Log Magnitude Oscillation for n={n}')
    plt.grid(True)
    plt.show()

def prime_discriminators(n_list):
    print("Prime vs Composite Discriminators (based on κ(n)):")
    for n in n_list:
        d_n = sum(1 for i in range(1, n+1) if n % i == 0)  # divisor count
        kappa = d_n * math.log(n + 1) / (e ** 2)
        is_prime = all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)) and n > 1
        print(f"n={n}: κ={kappa:.4f}, {'Prime' if is_prime else 'Composite'}")
    # Plot
    labels = [f'n={n}' for n in n_list]
    kappas = []
    colors = []
    for n in n_list:
        d_n = sum(1 for i in range(1, n+1) if n % i == 0)
        kappa = d_n * math.log(n + 1) / (e ** 2)
        is_prime = all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)) and n > 1
        kappas.append(kappa)
        colors.append('g' if is_prime else 'r')
    plt.figure(figsize=(8, 5))
    plt.bar(labels, kappas, color=colors)
    plt.xlabel('n')
    plt.ylabel('κ(n)')
    plt.title('Prime vs Composite κ(n)')
    plt.show()

# Example usage
if __name__ == "__main__":
    n = 100000
    analyze_domain(n)
    prime_discriminators([100000, 100003, 100008, 100012])  # Mix of primes/composites
