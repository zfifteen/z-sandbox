#!/usr/bin/env python3
"""
Summarize ECM distance break results and generate report.
"""

import argparse
import json
import csv
from pathlib import Path
from collections import defaultdict


def load_log(log_file):
    """Load JSONL log file."""
    entries = []
    metadata = None
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            entry = json.loads(line)
            
            if entry.get('meta') == 'RUN':
                metadata = entry
            else:
                entries.append(entry)
    
    return metadata, entries


def analyze_results(entries):
    """Analyze results and compute statistics."""
    stats = {
        'total': len(entries),
        'factored': sum(1 for e in entries if e.get('status') == 'factored'),
        'not_factored': sum(1 for e in entries if e.get('status') == 'not_factored'),
        'gated': sum(1 for e in entries if e.get('gate') is True),
        'ungated': sum(1 for e in entries if e.get('gate') is False),
        'no_gate': sum(1 for e in entries if e.get('gate') is None),
        'gated_factored': sum(1 for e in entries if e.get('gate') is True and e.get('status') == 'factored'),
        'ungated_factored': sum(1 for e in entries if e.get('gate') is False and e.get('status') == 'factored'),
        'full_schedule': sum(1 for e in entries if e.get('schedule_type') == 'full'),
        'light_schedule': sum(1 for e in entries if e.get('schedule_type') == 'light'),
    }
    
    # Group by tier
    by_tier = defaultdict(list)
    for e in entries:
        tier = e.get('tier') or e.get('fermat_tier', 'unknown')
        by_tier[tier].append(e)
    
    # Compute per-tier stats
    tier_stats = {}
    for tier, tier_entries in by_tier.items():
        tier_stats[tier] = {
            'total': len(tier_entries),
            'factored': sum(1 for e in tier_entries if e.get('status') == 'factored'),
            'gated': sum(1 for e in tier_entries if e.get('gate') is True),
            'gated_factored': sum(1 for e in tier_entries if e.get('gate') is True and e.get('status') == 'factored'),
        }
    
    # Find exemplar gated success
    exemplar = None
    for e in entries:
        if e.get('gate') is True and e.get('status') == 'factored' and e.get('integrity', False):
            exemplar = e
            break
    
    return stats, tier_stats, exemplar


def generate_report(metadata, entries, stats, tier_stats, exemplar, output_file):
    """Generate markdown report."""
    lines = []
    
    lines.append("# ECM Distance Break Report")
    lines.append("")
    lines.append("## Run Configuration")
    lines.append("")
    
    if metadata:
        lines.append(f"- **Timestamp**: {metadata.get('timestamp', 'N/A')}")
        lines.append(f"- **Backend**: {metadata.get('backend', {}).get('backend', 'N/A')}")
        if metadata.get('backend', {}).get('version'):
            lines.append(f"- **ECM Version**: {metadata['backend']['version']}")
        lines.append(f"- **Targets File**: {metadata.get('targets_file', 'N/A')}")
        lines.append(f"- **Target Bits**: {metadata.get('target_bits', 'N/A')}")
        lines.append(f"- **Timeout per Stage**: {metadata.get('timeout_per_stage', 'N/A')}s")
        lines.append(f"- **Checkpoint Dir**: {metadata.get('checkpoint_dir', 'N/A')}")
        lines.append(f"- **Use Sigma**: {metadata.get('use_sigma', 'N/A')}")
        lines.append(f"- **Theta Gate Available**: {metadata.get('theta_gate_available', 'N/A')}")
        lines.append("")
        
        lines.append("### ECM Schedules")
        lines.append("")
        lines.append("**Full Schedule (gated targets):**")
        lines.append("")
        for stage in metadata.get('full_schedule', []):
            lines.append(f"- {stage['stage']}: B1={stage['B1']}, curves={stage['curves']}")
        lines.append("")
        
        lines.append("**Light Schedule (ungated targets):**")
        lines.append("")
        for stage in metadata.get('light_schedule', []):
            lines.append(f"- {stage['stage']}: B1={stage['B1']}, curves={stage['curves']}")
        lines.append("")
    
    lines.append("## Overall Results")
    lines.append("")
    lines.append(f"- **Total Targets**: {stats['total']}")
    lines.append(f"- **Factored**: {stats['factored']} ({100*stats['factored']/max(stats['total'],1):.1f}%)")
    lines.append(f"- **Not Factored**: {stats['not_factored']} ({100*stats['not_factored']/max(stats['total'],1):.1f}%)")
    lines.append("")
    lines.append(f"- **Gated (full schedule)**: {stats['gated']}")
    lines.append(f"- **Ungated (light schedule)**: {stats['ungated']}")
    lines.append(f"- **No gate info**: {stats['no_gate']}")
    lines.append("")
    lines.append(f"- **Gated & Factored**: {stats['gated_factored']} ({100*stats['gated_factored']/max(stats['gated'],1):.1f}% of gated)")
    lines.append(f"- **Ungated & Factored**: {stats['ungated_factored']} ({100*stats['ungated_factored']/max(stats['ungated'],1):.1f}% of ungated)")
    lines.append("")
    
    lines.append("## Per-Tier Results")
    lines.append("")
    lines.append("| Tier | Total | Factored | Gated | Gated & Factored |")
    lines.append("|------|-------|----------|-------|------------------|")
    
    for tier in sorted(tier_stats.keys(), key=lambda x: (isinstance(x, str), x)):
        ts = tier_stats[tier]
        lines.append(f"| {tier} | {ts['total']} | {ts['factored']} | {ts['gated']} | {ts['gated_factored']} |")
    
    lines.append("")
    
    if exemplar:
        lines.append("## ✓ Exemplar Gated Success")
        lines.append("")
        lines.append("> **This is the existence proof: a θ′-gated target was factored by ECM.**")
        lines.append("")
        lines.append(f"**Target ID**: {exemplar.get('id', 'N/A')}")
        lines.append("")
        lines.append(f"- **N** (first 24 digits): `{exemplar.get('N_head', 'N/A')}`")
        lines.append(f"- **N** (last 24 digits): `{exemplar.get('N_tail', 'N/A')}`")
        lines.append(f"- **N bits**: {exemplar.get('N_bits', 'N/A')}")
        lines.append(f"- **p bits**: {exemplar.get('p_bits', 'N/A')}")
        lines.append(f"- **q bits**: {exemplar.get('q_bits', 'N/A')}")
        lines.append("")
        
        if exemplar.get('tier_type') == 'ratio':
            lines.append(f"- **Tier**: {exemplar.get('tier', 'N/A')} (ratio-based)")
            lines.append(f"- **Ratio Target**: {exemplar.get('ratio_target', 'N/A')}")
            lines.append(f"- **Ratio Actual**: {exemplar.get('ratio_actual', 'N/A'):.8f}")
        elif exemplar.get('tier_type') == 'fermat':
            lines.append(f"- **Fermat Tier**: {exemplar.get('tier', 'N/A')}")
            lines.append(f"- **Fermat Gap**: {exemplar.get('fermat_gap', 'N/A')}")
        
        lines.append("")
        lines.append(f"- **Gate Result**: {exemplar.get('gate', 'N/A')} (enabled full schedule)")
        lines.append(f"- **Schedule Type**: {exemplar.get('schedule_type', 'N/A')}")
        lines.append(f"- **Factored at Stage**: {exemplar.get('stage', 'N/A')}")
        lines.append(f"- **Time**: {exemplar.get('time_sec', 'N/A')}s")
        lines.append(f"- **Integrity**: {exemplar.get('integrity', 'N/A')}")
        lines.append("")
        
        lines.append("**Stages Attempted:**")
        lines.append("")
        for stage in exemplar.get('stages_attempted', []):
            status = "✓ FOUND" if stage.get('found_factor') else "✗"
            lines.append(f"- {stage['stage']}: B1={stage['B1']}, curves={stage['curves']}, time={stage['time_sec']}s {status}")
        lines.append("")
        
        lines.append("**Raw Log Entry:**")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(exemplar, indent=2))
        lines.append("```")
        lines.append("")
    else:
        lines.append("## ⚠ No Gated Success Found")
        lines.append("")
        lines.append("No target with `gate=true` and `status=factored` was found.")
        lines.append("")
    
    lines.append("## All Factored Targets")
    lines.append("")
    
    factored = [e for e in entries if e.get('status') == 'factored']
    
    if factored:
        lines.append("| ID | N bits | Gate | Schedule | Stage | Time (s) | Integrity |")
        lines.append("|----|--------|------|----------|-------|----------|-----------|")
        
        for e in factored:
            lines.append(f"| {e.get('id', 'N/A')} | {e.get('N_bits', 'N/A')} | {e.get('gate', 'N/A')} | {e.get('schedule_type', 'N/A')} | {e.get('stage', 'N/A')} | {e.get('time_sec', 'N/A'):.2f} | {e.get('integrity', 'N/A')} |")
        
        lines.append("")
    else:
        lines.append("No targets were factored.")
        lines.append("")
    
    # Write report
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Report written to {output_file}")


def generate_csv(entries, output_file):
    """Generate CSV summary."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'id', 'N_bits', 'tier', 'tier_type', 'ratio_target', 'ratio_actual',
        'fermat_gap', 'gate', 'schedule_type', 'status', 'stage',
        'time_sec', 'integrity', 'p_bits', 'q_bits'
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for entry in entries:
            writer.writerow(entry)
    
    print(f"✓ CSV written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Summarize ECM distance break results'
    )
    parser.add_argument('--log', type=str, required=True,
                       help='Path to JSONL log file')
    parser.add_argument('--out', type=str, default='reports/distance_break_report.md',
                       help='Output markdown report (default: reports/distance_break_report.md)')
    parser.add_argument('--emit-csv', type=str, default=None,
                       help='Also emit CSV summary (optional)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Summarize Distance Break Results")
    print("="*70)
    print(f"Log file: {args.log}")
    
    # Load log
    metadata, entries = load_log(args.log)
    print(f"Loaded {len(entries)} result entries")
    
    # Analyze
    stats, tier_stats, exemplar = analyze_results(entries)
    
    # Generate report
    generate_report(metadata, entries, stats, tier_stats, exemplar, args.out)
    
    # Generate CSV if requested
    if args.emit_csv:
        generate_csv(entries, args.emit_csv)
    
    print("="*70)
    print("Summary:")
    print(f"  Total: {stats['total']}")
    print(f"  Factored: {stats['factored']}")
    print(f"  Gated & Factored: {stats['gated_factored']}")
    print(f"  Exemplar found: {exemplar is not None}")
    
    if exemplar:
        print(f"\n✓ EXISTENCE PROOF: Target {exemplar['id']} was gated and factored!")
    else:
        print(f"\n⚠ No gated factorization found yet.")


if __name__ == "__main__":
    main()
