#!/usr/bin/env python3
"""
Monte Carlo Factorization Benchmark (MC-BENCH-001)

A/B benchmark comparing Monte Carlo φ-biased sampling vs. existing candidate builders
on RSA challenge numbers (RSA-100, RSA-129, RSA-155, RSA-250, RSA-260).

Outputs CSV with: tries to hit, wall time, candidates tested for each method.

Usage:
    PYTHONPATH=python python3 scripts/benchmark_monte_carlo_rsa.py

Output:
    monte_carlo_rsa_benchmark.csv
"""

import sys
import os
import time
import csv
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from monte_carlo import FactorizationMonteCarloEnhancer
from z5d_predictor import get_factor_candidates
import numpy as np


@dataclass
class RSAChallenge:
    """RSA challenge number with known factors."""
    id: str
    N: int
    p: Optional[int] = None
    q: Optional[int] = None
    factored: bool = False


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    method: str
    rsa_id: str
    N_decimal: str
    N_digits: int
    N_bits: int
    candidates_tested: int
    factor_found: bool
    factor_value: Optional[int]
    tries_to_hit: Optional[int]
    wall_time_seconds: float
    seed: int
    samples_per_try: int
    numpy_version: str
    sampling_mode: str = "uniform"  # Mode for variance reduction
    candidates_per_second: float = 0.0  # Performance metric


# RSA Challenge Numbers (from rsa_challenges.csv)
RSA_CHALLENGES = {
    'RSA-100': RSAChallenge(
        id='RSA-100',
        N=1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139,
        p=37975227936943673922808872755445627854565536638199,
        q=40094690950920881030683735292761468389214899724061,
        factored=True
    ),
    'RSA-129': RSAChallenge(
        id='RSA-129',
        N=114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541,
        p=3490529510847650949147849619903898133417764638493387843990820577,
        q=32769132993266709549961988190834461413177642967992942539798288533,
        factored=True
    ),
    'RSA-155': RSAChallenge(
        id='RSA-155',
        N=10941738641570527421809707322040357612003732945449205990913842131476349984288934784717997257891267332497625752899781833797076537244027146743531593354333897,
        p=102639592829741105772054196573991675900716567808038066803341933521790711307779,
        q=106603488380168454820927220360012878679207958575989291522270608237193062808643,
        factored=True
    ),
    'RSA-250': RSAChallenge(
        id='RSA-250',
        N=2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589325976697471681738069364894699871578494975937497937,
        p=64135289477071580278790190170577389084825014742943447208116859632024532344630238623598752668347708737661925585694639798853367,
        q=33372027594978156556226010605355114227940760344767554666784520987023841729210037080257448673296881877565718986258036932062711,
        factored=True
    ),
    'RSA-260': RSAChallenge(
        id='RSA-260',
        N=22112825529529666435281085255026230927612089502470015394413748319128822941402001986512729726569746599085900330031400051170742204560859276357953757185954298838958709229238491006703034124620545784566413664540684214361293017694020846391065875914794251435144458199,
        factored=False
    ),
}


def benchmark_phi_biased_sampling(
    rsa: RSAChallenge,
    seed: int = 42,
    max_tries: int = 100,
    samples_per_try: int = 1000,
    timeout_seconds: float = 300.0,
    sampling_mode: str = "uniform"
) -> BenchmarkResult:
    """
    Benchmark φ-biased Monte Carlo sampling with variance reduction modes.
    
    Args:
        rsa: RSA challenge
        seed: RNG seed
        max_tries: Maximum sampling attempts
        samples_per_try: Number of candidates per try
        timeout_seconds: Wall time timeout
        sampling_mode: Sampling mode ("uniform", "stratified", "qmc")
        
    Returns:
        Benchmark result
    """
    enhancer = FactorizationMonteCarloEnhancer(seed=seed)
    
    start_time = time.time()
    total_candidates = 0
    factor_found = False
    factor_value = None
    tries_to_hit = None
    
    for attempt in range(max_tries):
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            break
        
        # Generate candidates with specified mode
        candidates = enhancer.biased_sampling_with_phi(
            rsa.N,
            num_samples=samples_per_try,
            mode=sampling_mode
        )
        total_candidates += len(candidates)
        
        # Test candidates
        for c in candidates:
            if c > 1 and rsa.N % c == 0:
                factor_found = True
                factor_value = c
                tries_to_hit = attempt + 1
                break
        
        if factor_found:
            break
    
    wall_time = time.time() - start_time
    candidates_per_sec = total_candidates / wall_time if wall_time > 0 else 0
    
    return BenchmarkResult(
        method=f'phi_biased_monte_carlo_{sampling_mode}',
        rsa_id=rsa.id,
        N_decimal=str(rsa.N)[:50] + '...' if len(str(rsa.N)) > 50 else str(rsa.N),
        N_digits=len(str(rsa.N)),
        N_bits=rsa.N.bit_length(),
        candidates_tested=total_candidates,
        factor_found=factor_found,
        factor_value=factor_value,
        tries_to_hit=tries_to_hit,
        wall_time_seconds=wall_time,
        seed=seed,
        samples_per_try=samples_per_try,
        numpy_version=np.__version__,
        sampling_mode=sampling_mode,
        candidates_per_second=candidates_per_sec
    )


def benchmark_standard_sampling(
    rsa: RSAChallenge,
    seed: int = 42,
    max_tries: int = 100,
    samples_per_try: int = 1000,
    timeout_seconds: float = 300.0
) -> BenchmarkResult:
    """
    Benchmark standard Monte Carlo sampling (baseline).
    
    Args:
        rsa: RSA challenge
        seed: RNG seed
        max_tries: Maximum sampling attempts
        samples_per_try: Number of candidates per try
        timeout_seconds: Wall time timeout
        
    Returns:
        Benchmark result
    """
    enhancer = FactorizationMonteCarloEnhancer(seed=seed)
    
    start_time = time.time()
    total_candidates = 0
    factor_found = False
    factor_value = None
    tries_to_hit = None
    
    for attempt in range(max_tries):
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            break
        
        # Generate candidates (standard sampling)
        candidates = enhancer.sample_near_sqrt(
            rsa.N,
            num_samples=samples_per_try,
            spread_factor=0.01
        )
        total_candidates += len(candidates)
        
        # Test candidates
        for c in candidates:
            if c > 1 and rsa.N % c == 0:
                factor_found = True
                factor_value = c
                tries_to_hit = attempt + 1
                break
        
        if factor_found:
            break
    
    wall_time = time.time() - start_time
    candidates_per_sec = total_candidates / wall_time if wall_time > 0 else 0
    
    return BenchmarkResult(
        method='standard_monte_carlo',
        rsa_id=rsa.id,
        N_decimal=str(rsa.N)[:50] + '...' if len(str(rsa.N)) > 50 else str(rsa.N),
        N_digits=len(str(rsa.N)),
        N_bits=rsa.N.bit_length(),
        candidates_tested=total_candidates,
        factor_found=factor_found,
        factor_value=factor_value,
        tries_to_hit=tries_to_hit,
        wall_time_seconds=wall_time,
        seed=seed,
        samples_per_try=samples_per_try,
        numpy_version=np.__version__,
        sampling_mode="uniform",
        candidates_per_second=candidates_per_sec
    )


def benchmark_z5d_builder(
    rsa: RSAChallenge,
    seed: int = 42,
    max_tries: int = 100,
    samples_per_try: int = 1000,
    timeout_seconds: float = 300.0
) -> BenchmarkResult:
    """
    Benchmark Z5D candidate builder (existing production path).
    
    Args:
        rsa: RSA challenge
        seed: RNG seed (not used by Z5D, included for consistency)
        max_tries: Maximum sampling attempts (limited by candidate generation)
        samples_per_try: Not used, Z5D generates fixed candidate set
        timeout_seconds: Wall time timeout
        
    Returns:
        Benchmark result
    """
    start_time = time.time()
    
    # Z5D generates candidates once
    try:
        candidate_data = get_factor_candidates(rsa.N)
        candidates = [c for c, _, _ in candidate_data]
        total_candidates = len(candidates)
    except Exception as e:
        # Z5D may fail on very large numbers
        return BenchmarkResult(
            method='z5d_builder',
            rsa_id=rsa.id,
            N_decimal=str(rsa.N)[:50] + '...' if len(str(rsa.N)) > 50 else str(rsa.N),
            N_digits=len(str(rsa.N)),
            N_bits=rsa.N.bit_length(),
            candidates_tested=0,
            factor_found=False,
            factor_value=None,
            tries_to_hit=None,
            wall_time_seconds=time.time() - start_time,
            seed=seed,
            samples_per_try=samples_per_try,
            numpy_version=np.__version__,
            sampling_mode="z5d",
            candidates_per_second=0
        )
    
    # Check timeout
    if time.time() - start_time > timeout_seconds:
        wall_time = time.time() - start_time
        candidates_per_sec = total_candidates / wall_time if wall_time > 0 else 0
        return BenchmarkResult(
            method='z5d_builder',
            rsa_id=rsa.id,
            N_decimal=str(rsa.N)[:50] + '...' if len(str(rsa.N)) > 50 else str(rsa.N),
            N_digits=len(str(rsa.N)),
            N_bits=rsa.N.bit_length(),
            candidates_tested=total_candidates,
            factor_found=False,
            factor_value=None,
            tries_to_hit=None,
            wall_time_seconds=wall_time,
            seed=seed,
            samples_per_try=samples_per_try,
            numpy_version=np.__version__,
            sampling_mode="z5d",
            candidates_per_second=candidates_per_sec
        )
    
    # Test candidates
    factor_found = False
    factor_value = None
    
    for c in candidates:
        if c > 1 and rsa.N % c == 0:
            factor_found = True
            factor_value = c
            break
    
    wall_time = time.time() - start_time
    candidates_per_sec = total_candidates / wall_time if wall_time > 0 else 0
    
    return BenchmarkResult(
        method='z5d_builder',
        rsa_id=rsa.id,
        N_decimal=str(rsa.N)[:50] + '...' if len(str(rsa.N)) > 50 else str(rsa.N),
        N_digits=len(str(rsa.N)),
        N_bits=rsa.N.bit_length(),
        candidates_tested=total_candidates,
        factor_found=factor_found,
        factor_value=factor_value,
        tries_to_hit=1 if factor_found else None,
        wall_time_seconds=wall_time,
        seed=seed,
        samples_per_try=samples_per_try,
        numpy_version=np.__version__,
        sampling_mode="z5d",
        candidates_per_second=candidates_per_sec
    )


def run_benchmarks(
    rsa_ids: List[str] = None,
    seeds: List[int] = [42, 12345, 99999],
    output_file: str = 'monte_carlo_rsa_benchmark.csv',
    include_builders: bool = True,
    include_variance_reduction: bool = True
) -> List[BenchmarkResult]:
    """
    Run comprehensive benchmarks on RSA challenges.
    
    Args:
        rsa_ids: List of RSA IDs to benchmark (default: all factored)
        seeds: List of seeds for multiple runs
        output_file: Output CSV file
        include_builders: Include existing factorization builders (Z5D)
        include_variance_reduction: Include variance reduction modes (stratified, QMC)
        
    Returns:
        List of benchmark results
    """
    if rsa_ids is None:
        # Only benchmark factored RSA numbers by default
        rsa_ids = [k for k, v in RSA_CHALLENGES.items() if v.factored]
    
    results = []
    
    print("=" * 80)
    print("Monte Carlo RSA Factorization Benchmark (MC-BENCH-001)")
    print("=" * 80)
    print(f"NumPy version: {np.__version__}")
    print(f"RSA challenges: {rsa_ids}")
    print(f"Seeds: {seeds}")
    print(f"Output file: {output_file}")
    print(f"Include builders: {include_builders}")
    print(f"Include variance reduction: {include_variance_reduction}")
    print("=" * 80)
    
    for rsa_id in rsa_ids:
        rsa = RSA_CHALLENGES[rsa_id]
        
        print(f"\n{rsa_id}:")
        print(f"  N digits: {len(str(rsa.N))}")
        print(f"  N bits: {rsa.N.bit_length()}")
        
        # Adjust parameters based on size
        N_bits = rsa.N.bit_length()
        if N_bits <= 350:  # RSA-100, RSA-129
            max_tries = 100
            samples_per_try = 1000
            timeout = 60.0
        elif N_bits <= 520:  # RSA-155
            max_tries = 200
            samples_per_try = 5000
            timeout = 300.0
        else:  # RSA-250, RSA-260
            max_tries = 100
            samples_per_try = 10000
            timeout = 600.0
        
        for seed in seeds:
            print(f"  Seed {seed}:")
            
            # Benchmark φ-biased sampling (uniform mode)
            print("    Running φ-biased sampling (uniform)...")
            result_phi = benchmark_phi_biased_sampling(
                rsa, seed, max_tries, samples_per_try, timeout, sampling_mode="uniform"
            )
            results.append(result_phi)
            
            print(f"      Factor found: {result_phi.factor_found}")
            print(f"      Candidates/sec: {result_phi.candidates_per_second:.0f}")
            if result_phi.factor_found:
                print(f"      Tries to hit: {result_phi.tries_to_hit}")
                print(f"      Wall time: {result_phi.wall_time_seconds:.2f}s")
            
            # Benchmark φ-biased sampling with variance reduction modes
            if include_variance_reduction:
                for mode in ["stratified", "qmc"]:
                    print(f"    Running φ-biased sampling ({mode})...")
                    result_vr = benchmark_phi_biased_sampling(
                        rsa, seed, max_tries, samples_per_try, timeout, sampling_mode=mode
                    )
                    results.append(result_vr)
                    
                    print(f"      Factor found: {result_vr.factor_found}")
                    print(f"      Candidates/sec: {result_vr.candidates_per_second:.0f}")
                    if result_vr.factor_found:
                        print(f"      Tries to hit: {result_vr.tries_to_hit}")
            
            # Benchmark standard sampling
            print("    Running standard sampling...")
            result_std = benchmark_standard_sampling(
                rsa, seed, max_tries, samples_per_try, timeout
            )
            results.append(result_std)
            
            print(f"      Factor found: {result_std.factor_found}")
            print(f"      Candidates/sec: {result_std.candidates_per_second:.0f}")
            if result_std.factor_found:
                print(f"      Tries to hit: {result_std.tries_to_hit}")
                print(f"      Wall time: {result_std.wall_time_seconds:.2f}s")
            
            # Benchmark existing builders (only once per RSA, not per seed)
            if include_builders and seed == seeds[0]:
                print("    Running Z5D builder...")
                result_z5d = benchmark_z5d_builder(
                    rsa, seed, max_tries, samples_per_try, timeout
                )
                results.append(result_z5d)
                
                print(f"      Factor found: {result_z5d.factor_found}")
                print(f"      Candidates tested: {result_z5d.candidates_tested}")
                print(f"      Candidates/sec: {result_z5d.candidates_per_second:.0f}")
                print(f"      Wall time: {result_z5d.wall_time_seconds:.2f}s")
    
    # Write results to CSV
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))
    
    print(f"✓ Benchmark complete. Results saved to {output_file}")
    
    return results


def print_summary(results: List[BenchmarkResult]):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    # Group by method
    methods = set(r.method for r in results)
    
    for method in sorted(methods):
        method_results = [r for r in results if r.method == method]
        successful = [r for r in method_results if r.factor_found]
        
        print(f"\n{method}:")
        print(f"  Success rate: {len(successful)}/{len(method_results)}")
        
        if successful:
            avg_tries = sum(r.tries_to_hit for r in successful) / len(successful)
            avg_time = sum(r.wall_time_seconds for r in successful) / len(successful)
            avg_candidates = sum(r.candidates_tested for r in successful) / len(successful)
            avg_cand_per_sec = sum(r.candidates_per_second for r in successful) / len(successful)
            
            print(f"  Avg tries to hit: {avg_tries:.1f}")
            print(f"  Avg wall time: {avg_time:.2f}s")
            print(f"  Avg candidates tested: {avg_candidates:.0f}")
            print(f"  Avg candidates/sec: {avg_cand_per_sec:.0f}")
        else:
            # No factors found, but show perf metrics
            if method_results:
                avg_candidates = sum(r.candidates_tested for r in method_results) / len(method_results)
                avg_time = sum(r.wall_time_seconds for r in method_results) / len(method_results)
                avg_cand_per_sec = sum(r.candidates_per_second for r in method_results) / len(method_results)
                
                print(f"  Avg candidates tested: {avg_candidates:.0f}")
                print(f"  Avg wall time: {avg_time:.2f}s")
                print(f"  Avg candidates/sec: {avg_cand_per_sec:.0f}")
    
    # Compare variance reduction modes for φ-biased sampling
    phi_uniform = [r for r in results if r.method == 'phi_biased_monte_carlo_uniform' and r.factor_found]
    phi_stratified = [r for r in results if r.method == 'phi_biased_monte_carlo_stratified' and r.factor_found]
    phi_qmc = [r for r in results if r.method == 'phi_biased_monte_carlo_qmc' and r.factor_found]
    
    if phi_uniform and (phi_stratified or phi_qmc):
        print(f"\nVariance Reduction Comparison:")
        uniform_avg_tries = sum(r.tries_to_hit for r in phi_uniform) / len(phi_uniform)
        
        if phi_stratified:
            strat_avg_tries = sum(r.tries_to_hit for r in phi_stratified) / len(phi_stratified)
            improvement = ((uniform_avg_tries - strat_avg_tries) / uniform_avg_tries) * 100
            print(f"  Stratified vs Uniform: {improvement:+.1f}% change in tries")
        
        if phi_qmc:
            qmc_avg_tries = sum(r.tries_to_hit for r in phi_qmc) / len(phi_qmc)
            improvement = ((uniform_avg_tries - qmc_avg_tries) / uniform_avg_tries) * 100
            print(f"  QMC vs Uniform: {improvement:+.1f}% change in tries")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark Monte Carlo factorization on RSA challenges'
    )
    parser.add_argument(
        '--rsa-ids',
        nargs='+',
        default=None,
        help='RSA challenge IDs to benchmark (default: all factored)'
    )
    parser.add_argument(
        '--seeds',
        nargs='+',
        type=int,
        default=[42, 12345, 99999],
        help='Seeds for multiple runs (default: 42 12345 99999)'
    )
    parser.add_argument(
        '--output',
        default='monte_carlo_rsa_benchmark.csv',
        help='Output CSV file (default: monte_carlo_rsa_benchmark.csv)'
    )
    parser.add_argument(
        '--include-builders',
        action='store_true',
        default=True,
        help='Include existing factorization builders (Z5D) in benchmark (default: True)'
    )
    parser.add_argument(
        '--no-builders',
        action='store_true',
        help='Exclude factorization builders from benchmark'
    )
    parser.add_argument(
        '--include-variance-reduction',
        action='store_true',
        default=True,
        help='Include variance reduction modes (stratified, QMC) in benchmark (default: True)'
    )
    parser.add_argument(
        '--no-variance-reduction',
        action='store_true',
        help='Exclude variance reduction modes from benchmark'
    )
    
    args = parser.parse_args()
    
    # Handle negative flags
    include_builders = args.include_builders and not args.no_builders
    include_variance_reduction = args.include_variance_reduction and not args.no_variance_reduction
    
    results = run_benchmarks(
        rsa_ids=args.rsa_ids,
        seeds=args.seeds,
        output_file=args.output,
        include_builders=include_builders,
        include_variance_reduction=include_variance_reduction
    )
    
    print_summary(results)


if __name__ == '__main__':
    main()
