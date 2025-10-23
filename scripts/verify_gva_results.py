#!/usr/bin/env python3
"""
GVA Parameter Sweep Results Verification Script
Verifies the results of the GVA 200-bit parameter sweep experiment.
"""

import csv
import glob
import os

def analyze_results():
    """Analyze all GVA result files and print summary statistics."""

    result_files = glob.glob("gva_200bit_*_results.csv")
    if not result_files:
        print("No result files found. Run the parameter sweep first:")
        print("bash scripts/run_gva_parameter_sweep.sh")
        return

    print("=== GVA 200-bit Parameter Sweep Results Analysis ===\n")

    total_trials = 0
    total_successes = 0
    config_stats = {}

    for file_path in sorted(result_files):
        config = os.path.basename(file_path).replace('gva_200bit_', '').replace('_results.csv', '')

        if config not in config_stats:
            config_stats[config] = {'trials': 0, 'successes': 0, 'times': []}

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_trials += 1
                config_stats[config]['trials'] += 1

                if row['success'].lower() == 'true':
                    total_successes += 1
                    config_stats[config]['successes'] += 1

                try:
                    config_stats[config]['times'].append(float(row['time_seconds']))
                except (ValueError, KeyError):
                    pass

    # Print per-configuration results
    print("Per-Configuration Results:")
    print("-" * 70)
    print(f"{'Config':<12} {'Trials':<8} {'Success':<8} {'Rate':<8} {'Avg Time':<10} {'Min Time':<10} {'Max Time':<10}")
    print("-" * 70)

    for config in sorted(config_stats.keys()):
        stats = config_stats[config]
        trials = stats['trials']
        successes = stats['successes']
        success_rate = (successes / trials * 100) if trials > 0 else 0

        times = stats['times']
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0

        print(f"{config:<12} {trials:<8} {successes:<8} {success_rate:<7.1f}% {avg_time:<9.3f}s {min_time:<9.3f}s {max_time:<9.3f}s")

    print("-" * 70)

    # Overall statistics
    overall_success_rate = (total_successes / total_trials * 100) if total_trials > 0 else 0

    print("\nOverall Results:")
    print(f"Total Trials: {total_trials}")
    print(f"Total Successes: {total_successes}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")

    # Performance analysis
    all_times = []
    for stats in config_stats.values():
        all_times.extend(stats['times'])

    if all_times:
        avg_time = sum(all_times) / len(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        print(f"Average Trial Time: {avg_time:.3f}s")
        print(f"Time Range: {min_time:.3f}s - {max_time:.3f}s")

    # Conclusions
    print("\nConclusions:")
    if total_successes == 0:
        print("❌ GVA method shows 0% success rate on 200-bit numbers")
        print("   - No parameter combination yielded factorization")
        print("   - Method does not scale to 200-bit numbers with current implementation")
    else:
        print("✅ GVA method shows some success on 200-bit numbers")
        print(f"   - {total_successes} factorizations found across {total_trials} trials")
        print("   - Further optimization and scaling recommended")

    print("\nNext Steps:")
    print("1. Test on intermediate bit sizes (150-180) to find working range")
    print("2. Review mathematical foundations of GVA method")
    print("3. Consider hybrid approaches combining GVA with other filters")
    print("4. Investigate alternative embedding functions or distance metrics")

if __name__ == "__main__":
    analyze_results()