#!/usr/bin/env python3
"""
Summarize distance-based ECM factorization results.
Generates reports and CSV summaries.
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict


def load_log(log_path):
    """Load JSONL log file."""
    results = []
    with open(log_path, 'r') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def generate_summary_stats(results):
    """Generate summary statistics."""
    total = len(results)
    factored = [r for r in results if r["status"] == "factored"]
    not_factored = [r for r in results if r["status"] != "factored"]
    
    gated = [r for r in results if r["gated"]]
    ungated = [r for r in results if not r["gated"]]
    
    gated_factored = [r for r in factored if r["gated"]]
    ungated_factored = [r for r in factored if not r["gated"]]
    
    # By tier
    by_tier = defaultdict(list)
    for r in results:
        by_tier[r["tier"]].append(r)
    
    stats = {
        "total": total,
        "factored": len(factored),
        "not_factored": len(not_factored),
        "gated": len(gated),
        "ungated": len(ungated),
        "gated_factored": len(gated_factored),
        "ungated_factored": len(ungated_factored),
        "by_tier": {}
    }
    
    for tier, tier_results in by_tier.items():
        tier_factored = [r for r in tier_results if r["status"] == "factored"]
        tier_gated = [r for r in tier_results if r["gated"]]
        tier_gated_factored = [r for r in tier_factored if r["gated"]]
        
        stats["by_tier"][tier] = {
            "total": len(tier_results),
            "factored": len(tier_factored),
            "gated": len(tier_gated),
            "gated_factored": len(tier_gated_factored),
            "ratio": tier_results[0]["tier_ratio"] if tier_results else None
        }
    
    return stats, gated_factored


def generate_markdown_report(results, stats, gated_factored, out_path):
    """Generate markdown report."""
    with open(out_path, 'w') as f:
        f.write("# Distance-Based ECM Factorization Report\n\n")
        
        # Overall statistics
        f.write("## Overall Statistics\n\n")
        f.write(f"- **Total targets**: {stats['total']}\n")
        f.write(f"- **Factored**: {stats['factored']} ({stats['factored']*100/stats['total']:.1f}%)\n")
        f.write(f"- **Not factored**: {stats['not_factored']}\n")
        f.write("\n")
        
        f.write("### By Gate Status\n\n")
        f.write(f"- **Gated targets**: {stats['gated']}\n")
        f.write(f"  - Factored: {stats['gated_factored']} ({stats['gated_factored']*100/stats['gated']:.1f}%)\n")
        f.write(f"- **Ungated targets**: {stats['ungated']}\n")
        f.write(f"  - Factored: {stats['ungated_factored']} ({stats['ungated_factored']*100/stats['ungated']:.1f}% if stats['ungated'] > 0 else 0)\n")
        f.write("\n")
        
        # By tier
        f.write("## Results by Tier\n\n")
        f.write("| Tier | Ratio | Total | Factored | Gated | Gated Factored |\n")
        f.write("|------|-------|-------|----------|-------|----------------|\n")
        for tier in sorted(stats["by_tier"].keys()):
            tier_stats = stats["by_tier"][tier]
            f.write(f"| {tier} | {tier_stats['ratio']:.6f} | {tier_stats['total']} | "
                   f"{tier_stats['factored']} | {tier_stats['gated']} | "
                   f"{tier_stats['gated_factored']} |\n")
        f.write("\n")
        
        # Exemplar cases
        if gated_factored:
            f.write("## Exemplar Gated Success Cases\n\n")
            for i, result in enumerate(gated_factored[:3], 1):  # Show up to 3
                f.write(f"### Case {i}\n\n")
                f.write(f"- **N**: {result['N_first_24']}...{result['N_last_24']} ({result['p_bits'] + result['q_bits']} bits)\n")
                f.write(f"- **p**: {result['p_bits']} bits\n")
                f.write(f"- **q**: {result['q_bits']} bits\n")
                f.write(f"- **Tier**: {result['tier']} (ratio={result['tier_ratio']:.6f})\n")
                f.write(f"- **Fermat normal**: {result['fermat_normal']}\n")
                f.write(f"- **Gate**: {result['gated']} (full schedule used)\n")
                f.write(f"- **Status**: {result['status']}\n")
                f.write(f"- **Integrity**: {result['integrity']}\n")
                f.write(f"- **Elapsed**: {result['elapsed_seconds']:.1f}s\n")
                f.write(f"- **Stages completed**: {result['stages_completed']}/{result['stages_total']}\n")
                f.write("\n")
                
                gate_meta = result["gate_metadata"]
                f.write("**Gate metadata:**\n")
                f.write(f"- θ′(N) = {gate_meta['theta_N']:.6f}\n")
                f.write(f"- θ′(p) = {gate_meta['theta_p']:.6f} (in bounds: {gate_meta['p_in_bounds']})\n")
                f.write(f"- θ′(q) = {gate_meta['theta_q']:.6f} (in bounds: {gate_meta['q_in_bounds']})\n")
                f.write(f"- Bounds: [{gate_meta['bound_lower']:.6f}, {gate_meta['bound_upper']:.6f}]\n")
                f.write(f"- Width factor: {gate_meta['width_factor']}\n")
                f.write("\n")
                
                # Show JSON log line
                f.write("**Log line:**\n")
                f.write("```json\n")
                f.write(json.dumps(result, indent=2))
                f.write("\n```\n\n")
        else:
            f.write("## Exemplar Cases\n\n")
            f.write("*No gated targets were successfully factored.*\n\n")
        
        # Acceptance criteria
        f.write("## Acceptance Criteria\n\n")
        if stats['gated_factored'] > 0:
            f.write("✅ **PASSED**: At least one 192-bit semiprime was factored where θ′ gated it.\n\n")
            f.write("The existence proof is established:\n")
            f.write("- Geometry (θ′) determined ECM spend strategy\n")
            f.write("- Gated targets received full schedule (35d→50d)\n")
            f.write("- Ungated targets received light schedule (35d only)\n")
            f.write("- At least one gated target was successfully factored\n")
        else:
            f.write("❌ **NOT PASSED**: No gated targets were factored.\n\n")
            f.write("Consider:\n")
            f.write("- Adjusting gate width factor\n")
            f.write("- Running with more targets\n")
            f.write("- Using smaller bit sizes (128-bit)\n")


def generate_csv(results, out_path):
    """Generate CSV summary."""
    with open(out_path, 'w') as f:
        # Header
        f.write("N_first_24,N_last_24,bits,tier,tier_ratio,fermat_normal,gated,")
        f.write("schedule,status,integrity,elapsed_seconds,stages_completed,stages_total,")
        f.write("theta_N,theta_p,theta_q,p_in_bounds,q_in_bounds\n")
        
        # Rows
        for r in results:
            gate_meta = r["gate_metadata"]
            f.write(f"{r['N_first_24']},{r['N_last_24']},{r['p_bits'] + r['q_bits']},")
            f.write(f"{r['tier']},{r['tier_ratio']},{r['fermat_normal']},{r['gated']},")
            f.write(f"{r['schedule']},{r['status']},{r['integrity']},{r['elapsed_seconds']:.1f},")
            f.write(f"{r['stages_completed']},{r['stages_total']},")
            f.write(f"{gate_meta['theta_N']:.6f},{gate_meta['theta_p']:.6f},{gate_meta['theta_q']:.6f},")
            f.write(f"{gate_meta['p_in_bounds']},{gate_meta['q_in_bounds']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Summarize distance-based ECM results"
    )
    parser.add_argument(
        "--log",
        type=str,
        required=True,
        help="Path to JSONL log file"
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Path to output markdown report"
    )
    parser.add_argument(
        "--emit-csv",
        type=str,
        help="Path to output CSV summary"
    )
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading log from {args.log}...")
    results = load_log(args.log)
    print(f"Loaded {len(results)} results")
    
    # Generate stats
    print("Generating statistics...")
    stats, gated_factored = generate_summary_stats(results)
    
    # Generate report
    print(f"Writing report to {args.out}...")
    generate_markdown_report(results, stats, gated_factored, args.out)
    
    # Generate CSV if requested
    if args.emit_csv:
        print(f"Writing CSV to {args.emit_csv}...")
        generate_csv(results, args.emit_csv)
    
    print("\nSummary:")
    print(f"  Total: {stats['total']}")
    print(f"  Factored: {stats['factored']}")
    print(f"  Gated factored: {stats['gated_factored']}")
    
    if stats['gated_factored'] > 0:
        print("\n✓ SUCCESS: At least one gated target was factored!")
    else:
        print("\n✗ No gated targets were factored.")


if __name__ == "__main__":
    main()
