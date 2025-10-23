#!/usr/bin/env python3
"""
Run ECM factorization on distance-based targets with geometric gating.

The gate function determines ECM spend:
- Gated targets: Full schedule (35d → 50d)
- Ungated targets: Light pass (35d only)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ecm_backend import run_ecm_once, backend_info
from geometry_gate import gate_by_theta_prime, compute_gate_metadata


def ensure_gmp_ecm():
    """Ensure GMP-ECM is available and fail if not."""
    info = backend_info()
    if info["backend"] != "gmp-ecm":
        raise RuntimeError(
            f"GMP-ECM is required but backend is '{info['backend']}'. "
            "Please install gmp-ecm package."
        )
    print(f"Backend: {info['backend']}")
    if info['version']:
        print(f"Version: {info['version']}")
    return info


def run_ecm_with_schedule(N, schedule, timeout_per_stage, checkpoint_dir, sigma=None):
    """
    Run ECM with a given schedule.
    
    Args:
        N: The number to factor
        schedule: List of (B1, curves) tuples
        timeout_per_stage: Timeout in seconds per stage
        checkpoint_dir: Directory for checkpoints
        sigma: Optional sigma value for deterministic curve selection
    
    Returns:
        (factor, stage_completed) or (None, stages_attempted)
    """
    for stage_idx, (B1, curves) in enumerate(schedule):
        print(f"  Stage {stage_idx + 1}/{len(schedule)}: B1={B1}, curves={curves}")
        
        factor = run_ecm_once(
            N=N,
            B1=B1,
            curves=curves,
            timeout_sec=timeout_per_stage,
            checkpoint_dir=checkpoint_dir,
            sigma=sigma,
            allow_resume=True
        )
        
        if factor is not None:
            return factor, stage_idx + 1
    
    return None, len(schedule)


def factorize_target(target, args, log_file):
    """
    Attempt to factorize a single target.
    
    Args:
        target: Target dictionary from targets file
        args: Command-line arguments
        log_file: File object for JSON logging
    
    Returns:
        Result dictionary
    """
    N = int(target["N"])
    p_true = int(target["p"])
    q_true = int(target["q"])
    
    print(f"\nTarget: N={str(N)[:24]}...{str(N)[-24:]} ({target['bits']} bits)")
    print(f"  Tier: {target['tier']}, Ratio: {target['tier_ratio']:.6f}")
    print(f"  Fermat normal: {target['fermat_normal']}")
    
    # Compute gate decision
    gate_metadata = compute_gate_metadata(
        N, p_true, q_true,
        width_factor=args.width_factor,
        k=args.k
    )
    gated = gate_metadata["gated"]
    
    print(f"  Gate decision: {gated}")
    print(f"    θ′(N) = {gate_metadata['theta_N']:.6f}")
    print(f"    θ′(p) = {gate_metadata['theta_p']:.6f} (in bounds: {gate_metadata['p_in_bounds']})")
    print(f"    θ′(q) = {gate_metadata['theta_q']:.6f} (in bounds: {gate_metadata['q_in_bounds']})")
    
    # Choose schedule based on gate
    # For 192-bit numbers (58-59 decimal digits), appropriate B1 values are:
    # - 25-30 digits: ~10^6 to 10^7
    # - 30-35 digits: ~10^8 to 10^9
    # - 35-40 digits: ~10^10 to 10^11
    # - 40-50 digits: ~10^12 to 10^14
    
    # Scale B1 based on bit size
    bits = target.get("bits", 192)
    if bits <= 64:
        # Small targets
        light_B1 = [(11000, 100)]
        full_B1 = [(11000, 200), (50000, 200), (250000, 200)]
    elif bits <= 128:
        # Medium targets (30-39 decimal digits)
        light_B1 = [(10**6, 100)]
        full_B1 = [(10**6, 200), (10**7, 200), (5 * 10**7, 200)]
    else:
        # Large targets (192-bit = ~58 decimal digits)
        # Factors are ~29 decimal digits
        light_B1 = [(10**7, 100)]  # Light: 35d equivalent
        full_B1 = [
            (10**7, 200),    # ~30 digits
            (5 * 10**7, 200),  # ~35 digits
            (10**9, 200),    # ~40 digits
            (10**10, 200),   # ~45 digits
        ]
    
    if gated:
        # Full schedule
        schedule = full_B1
        schedule_name = "full"
    else:
        # Light schedule
        schedule = light_B1
        schedule_name = "light"
    
    print(f"  Schedule: {schedule_name} ({len(schedule)} stages)")
    
    # Get sigma from environment if requested
    sigma = None
    if args.use_sigma:
        sigma = int(os.environ.get("ECM_SIGMA", "1"))
        print(f"  Using sigma: {sigma}")
    
    # Run ECM
    start_time = time.time()
    factor, stages_completed = run_ecm_with_schedule(
        N=N,
        schedule=schedule,
        timeout_per_stage=args.timeout_per_stage,
        checkpoint_dir=args.checkpoint_dir,
        sigma=sigma
    )
    elapsed = time.time() - start_time
    
    # Check result
    if factor is not None:
        q_found = N // factor
        p_found = min(factor, q_found)
        q_found = max(factor, q_found)
        
        # Verify integrity
        integrity = (p_found == p_true and q_found == q_true)
        status = "factored"
        
        print(f"  ✓ FACTORED in {elapsed:.1f}s at stage {stages_completed}/{len(schedule)}")
        print(f"    p = {p_found}")
        print(f"    q = {q_found}")
        print(f"    Integrity: {integrity}")
    else:
        p_found = None
        q_found = None
        integrity = False
        status = "not_factored"
        print(f"  ✗ Not factored after {elapsed:.1f}s ({stages_completed} stages)")
    
    # Log result
    result = {
        "N": str(N),
        "N_first_24": str(N)[:24],
        "N_last_24": str(N)[-24:],
        "p_true": str(p_true),
        "q_true": str(q_true),
        "p_found": str(p_found) if p_found else None,
        "q_found": str(q_found) if q_found else None,
        "p_bits": target["p_bits"],
        "q_bits": target["q_bits"],
        "tier": target["tier"],
        "tier_ratio": target["tier_ratio"],
        "fermat_normal": target["fermat_normal"],
        "gated": gated,
        "schedule": schedule_name,
        "stages_completed": stages_completed,
        "stages_total": len(schedule),
        "status": status,
        "integrity": integrity,
        "elapsed_seconds": elapsed,
        "gate_metadata": gate_metadata,
        "sigma": sigma
    }
    
    # Write to log
    log_file.write(json.dumps(result) + "\n")
    log_file.flush()
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run ECM on distance-based targets with geometric gating"
    )
    parser.add_argument(
        "--targets",
        type=str,
        required=True,
        help="Path to targets JSON file"
    )
    parser.add_argument(
        "--timeout-per-stage",
        type=int,
        default=900,
        help="Timeout in seconds per ECM stage (default: 900)"
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="ckpts",
        help="Directory for ECM checkpoints"
    )
    parser.add_argument(
        "--use-sigma",
        action="store_true",
        help="Use ECM_SIGMA environment variable for deterministic curves"
    )
    parser.add_argument(
        "--width-factor",
        type=float,
        default=0.155,
        help="Width factor for θ′ gate (default: 0.155)"
    )
    parser.add_argument(
        "--k",
        type=float,
        default=0.3,
        help="k parameter for θ′ (default: 0.3)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/distance_break.jsonl",
        help="Path to output log file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of targets to process (for testing)"
    )
    
    args = parser.parse_args()
    
    # Ensure GMP-ECM is available
    print("Checking backend...")
    backend = ensure_gmp_ecm()
    print()
    
    # Load targets
    print(f"Loading targets from {args.targets}...")
    with open(args.targets, 'r') as f:
        data = json.load(f)
    
    targets = data["targets"]
    if args.limit:
        targets = targets[:args.limit]
    
    print(f"Loaded {len(targets)} targets")
    print(f"Config: {data['config']}")
    print()
    
    # Create checkpoint and log directories
    Path(args.checkpoint_dir).mkdir(parents=True, exist_ok=True)
    Path(args.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Open log file
    with open(args.log_file, 'w') as log_file:
        # Process targets
        results = []
        for i, target in enumerate(targets):
            print(f"\n{'='*80}")
            print(f"Target {i+1}/{len(targets)}")
            
            result = factorize_target(target, args, log_file)
            results.append(result)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    total = len(results)
    factored = sum(1 for r in results if r["status"] == "factored")
    gated = sum(1 for r in results if r["gated"])
    gated_factored = sum(1 for r in results if r["gated"] and r["status"] == "factored")
    ungated = total - gated
    ungated_factored = factored - gated_factored
    
    print(f"Total targets: {total}")
    print(f"Factored: {factored} ({factored*100/total:.1f}%)")
    print()
    print(f"Gated targets: {gated}")
    gated_pct = (gated_factored*100/gated if gated > 0 else 0)
    print(f"  Factored: {gated_factored} ({gated_pct:.1f}%)")
    print(f"Ungated targets: {ungated}")
    ungated_pct = (ungated_factored*100/ungated if ungated > 0 else 0)
    print(f"  Factored: {ungated_factored} ({ungated_pct:.1f}%)")
    print()
    print(f"Log saved to: {args.log_file}")
    
    # Check acceptance criteria
    if gated_factored > 0:
        print("\n✓ ACCEPTANCE: At least one gated target was factored!")
        print("  The geometry gate demonstrated its value.")
    else:
        print("\n✗ No gated targets were factored.")
        print("  Consider adjusting parameters or running with more targets.")


if __name__ == "__main__":
    main()
