#!/usr/bin/env python3
"""
Precision Audit: Test high-precision residual angles on boundary data
Compare 64, 100, 160 digit precision for distance stability and rank improvement
"""

import csv
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import math

def set_prec(prec=120):
    getcontext().prec = prec
    getcontext().rounding = ROUND_HALF_EVEN

ALPHAS = [
    Decimal('1.6180339887498948'),  # φ
    Decimal('2.7182818284590452'),  # e
    Decimal('3.1415926535897932'),  # π
    Decimal('2.4142135623730951'),  # silver
]

def theta_mod1_log(x: int, alpha: Decimal) -> float:
    t = (alpha * Decimal(x).ln()) % Decimal(1)
    return float(t)

def circ_dist(a: float, b: float) -> float:
    d = abs(a - b)
    return d if d <= 0.5 else 1.0 - d

def circular_mean(ts):
    cs = [complex(math.cos(2*math.pi*t), math.sin(2*math.pi*t)) for t in ts]
    mx = sum(c.real for c in cs) / len(cs)
    my = sum(c.imag for c in cs) / len(cs)
    mu = math.atan2(my, mx) / (2 * math.pi)
    return mu % 1.0

def residual_angles(values, alpha: Decimal):
    ts = [theta_mod1_log(v, alpha) for v in values]
    mu = circular_mean(ts)
    res = [((t - mu) % 1.0) for t in ts]
    return mu, res

def score_candidate_residual(N: int, cand: int, window_vals, alphas=ALPHAS):
    scores = []
    for a in alphas:
        mu, _ = residual_angles(window_vals, a)
        tN = (theta_mod1_log(N, a) - mu) % 1.0
        tc = (theta_mod1_log(cand, a) - mu) % 1.0
        scores.append(circ_dist(tN, tc))
    return min(scores), scores

def load_boundary_data():
    """Load the boundary data CSV."""
    data = []
    with open('boundary_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert strings to appropriate types
            row['bit_size'] = int(row['bit_size'])
            row['success'] = row['success'] == 'True'
            row['N'] = int(row['N'])
            row['p'] = int(row['p'])
            row['q'] = int(row['q'])
            row['attempts'] = int(row['attempts'])
            row['elapsed'] = float(row['elapsed'])
            row['theta_N'] = float(row['theta_N'])
            row['theta_p'] = float(row['theta_p'])
            row['theta_q'] = float(row['theta_q'])
            row['dist_N_p'] = float(row['dist_N_p'])
            row['dist_N_q'] = float(row['dist_N_q'])
            row['candidates_pre'] = int(row['candidates_pre'])
            row['candidates_post'] = int(row['candidates_post'])
            data.append(row)
    return data

def audit_precision(precisions=[64, 100, 160]):
    """Run precision audit on boundary data."""
    data = load_boundary_data()

    results = []
    for prec in precisions:
        print(f"\n=== Testing {prec}-digit precision ===")
        set_prec(prec)

        for case in data:
            N = case['N']
            p = case['p']
            q = case['q']
            window_vals = [N, p, q]  # Simple window for testing

            # Score true factors
            score_p, _ = score_candidate_residual(N, p, window_vals)
            score_q, _ = score_candidate_residual(N, q, window_vals)

            # Generate some random candidates for rank comparison
            import random
            random_candidates = [N + random.randint(-1000, 1000) for _ in range(10)]
            random_scores = [score_candidate_residual(N, c, window_vals)[0] for c in random_candidates]

            # Compute ranks (lower score = better rank)
            p_rank = 1 + sum(1 for s in random_scores if s < score_p)
            q_rank = 1 + sum(1 for s in random_scores if s < score_q)

            result = {
                'precision': prec,
                'case_id': f"{case['bit_size']}bit_{case['success']}",
                'N': N,
                'p': p,
                'q': q,
                'score_p': score_p,
                'score_q': score_q,
                'rank_p': p_rank,
                'rank_q': q_rank,
                'avg_random_score': sum(random_scores) / len(random_scores),
                'min_distance': min(score_p, score_q),
                'improvement_over_random': (sum(random_scores) / len(random_scores)) - min(score_p, score_q)
            }
            results.append(result)

            print(f"  Case processed: min_dist={min(score_p, score_q):.4f}, ranks=({p_rank},{q_rank})")

    return results

def save_audit_results(results, filename='precision_audit.csv'):
    """Save audit results to CSV."""
    if not results:
        print("No results to save!")
        return

    fieldnames = results[0].keys()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Audit results saved to {filename}")

if __name__ == "__main__":
    results = audit_precision()
    save_audit_results(results)

    print("\n=== SUMMARY ===")
    for prec in [64, 100, 160]:
        prec_results = [r for r in results if r['precision'] == prec]
        avg_min_dist = sum(r['min_distance'] for r in prec_results) / len(prec_results)
        avg_rank = sum((r['rank_p'] + r['rank_q']) / 2 for r in prec_results) / len(prec_results)
        print(f"{prec} digits: Avg min distance = {avg_min_dist:.4f}, Avg rank = {avg_rank:.1f}")

    print("\nPrecision audit complete!")
