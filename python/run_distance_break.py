#!/usr/bin/env python3
"""
Run ECM factorization with theta-gating on distance-organized targets.
Gated targets get full schedule, ungated get light pass.
"""

import argparse
import json
import os
import time
import datetime
from pathlib import Path
from ecm_backend import run_ecm_once, backend_info

# Try to import theta_gate
try:
    from manifold_128bit import theta_gate
    THETA_GATE_AVAILABLE = True
except ImportError:
    THETA_GATE_AVAILABLE = False
    print("Warning: theta_gate not available, all targets will be ungated")


# ECM schedules
# Full schedule: 35d → 50d (multiple stages)
FULL_SCHEDULE = [
    ("35d", 11000000, 20),       # ~35 decimal digit factors
    ("40d", 110000000, 20),      # ~40 decimal digit factors
    ("45d", 850000000, 20),      # ~45 decimal digit factors
    ("50d", 2900000000, 20),     # ~50 decimal digit factors
]

# Light schedule: 35d only
LIGHT_SCHEDULE = [
    ("35d", 11000000, 20),       # ~35 decimal digit factors only
]


def load_targets(filepath):
    """Load targets from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['metadata'], data['targets']


def determine_schedule(N, use_gate):
    """
    Determine ECM schedule based on theta-gating.
    
    Args:
        N: The semiprime to factor
        use_gate: Whether to use theta-gating
    
    Returns:
        Tuple of (schedule, gate_result)
        - schedule: List of (name, B1, curves) tuples
        - gate_result: Boolean indicating if gate passed
    """
    if not use_gate or not THETA_GATE_AVAILABLE:
        return LIGHT_SCHEDULE, None
    
    # Apply theta-gate
    gate_passed = theta_gate(N)
    
    if gate_passed:
        return FULL_SCHEDULE, True
    else:
        return LIGHT_SCHEDULE, False


def factor_with_ecm(N, schedule, timeout_per_stage, checkpoint_dir, use_sigma):
    """
    Attempt to factor N using the given ECM schedule.
    
    Args:
        N: The semiprime to factor
        schedule: List of (name, B1, curves) tuples
        timeout_per_stage: Timeout in seconds per stage
        checkpoint_dir: Directory for checkpoints
        use_sigma: Whether to use deterministic sigma seeding
    
    Returns:
        Dictionary with factorization result
    """
    result = {
        'factored': False,
        'factor': None,
        'stage': None,
        'time_sec': 0.0,
        'stages_attempted': []
    }
    
    start_time = time.time()
    
    for stage_name, B1, curves in schedule:
        stage_start = time.time()
        
        # Use a valid sigma value for determinism (any large number works)
        # Sigma=1 is invalid, use a large prime-like number instead
        sigma = 2147483647 if use_sigma else None  # Mersenne prime 2^31-1
        
        # Try to factor
        factor = run_ecm_once(
            N=N,
            B1=B1,
            curves=curves,
            timeout_sec=timeout_per_stage,
            checkpoint_dir=checkpoint_dir,
            sigma=sigma,
            allow_resume=True
        )
        
        stage_time = time.time() - stage_start
        
        result['stages_attempted'].append({
            'stage': stage_name,
            'B1': B1,
            'curves': curves,
            'time_sec': round(stage_time, 3),
            'found_factor': factor is not None
        })
        
        if factor:
            result['factored'] = True
            result['factor'] = factor
            result['stage'] = stage_name
            result['time_sec'] = round(time.time() - start_time, 3)
            return result
    
    result['time_sec'] = round(time.time() - start_time, 3)
    return result


def run_distance_break(targets_file, timeout_per_stage, checkpoint_dir, use_sigma, log_file):
    """
    Run ECM factorization on distance-organized targets with theta-gating.
    
    Args:
        targets_file: Path to targets JSON file
        timeout_per_stage: Timeout in seconds per ECM stage
        checkpoint_dir: Directory for checkpoints
        use_sigma: Whether to use deterministic sigma seeding
        log_file: Path to log file (JSONL format)
    """
    # Create directories
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Load targets
    print("Loading targets...")
    metadata, targets = load_targets(targets_file)
    print(f"Loaded {len(targets)} targets")
    print(f"Target bits: {metadata['bits']}")
    print(f"Theta-gating: {'enabled' if use_sigma and THETA_GATE_AVAILABLE else 'disabled'}")
    
    # Write run metadata
    run_meta = {
        'meta': 'RUN',
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
        'backend': backend_info(),
        'targets_file': str(targets_file),
        'target_bits': metadata['bits'],
        'num_targets': len(targets),
        'timeout_per_stage': timeout_per_stage,
        'checkpoint_dir': str(checkpoint_dir),
        'use_sigma': use_sigma,
        'theta_gate_available': THETA_GATE_AVAILABLE,
        'full_schedule': [{'stage': s, 'B1': b, 'curves': c} for s, b, c in FULL_SCHEDULE],
        'light_schedule': [{'stage': s, 'B1': b, 'curves': c} for s, b, c in LIGHT_SCHEDULE],
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(run_meta) + '\n')
    
    print(f"\nProcessing targets...")
    print("="*70)
    
    # Process each target
    for idx, target in enumerate(targets, 1):
        target_id = target.get('id', f'T{idx:03d}')
        N = int(target['N'])
        
        print(f"\n[{idx}/{len(targets)}] Target {target_id}")
        print(f"  N bits: {target['N_bits']}")
        print(f"  N (head): {str(N)[:24]}...")
        print(f"  N (tail): ...{str(N)[-24:]}")
        
        if 'ratio_actual' in target:
            print(f"  Ratio: {target['ratio_actual']:.6f} (target: {target.get('ratio_target', 'N/A')})")
        if 'fermat_gap' in target:
            print(f"  Fermat gap: {target['fermat_gap']}")
        
        # Determine schedule based on theta-gating
        schedule, gate_result = determine_schedule(N, use_sigma and THETA_GATE_AVAILABLE)
        schedule_type = 'full' if len(schedule) > 1 else 'light'
        
        print(f"  Gate result: {gate_result} → {schedule_type} schedule ({len(schedule)} stages)")
        
        # Run ECM
        start_time = time.time()
        ecm_result = factor_with_ecm(
            N=N,
            schedule=schedule,
            timeout_per_stage=timeout_per_stage,
            checkpoint_dir=checkpoint_dir,
            use_sigma=use_sigma
        )
        
        # Check integrity if factored
        integrity = False
        p_actual = None
        q_actual = None
        if ecm_result['factored']:
            factor = ecm_result['factor']
            p_actual = factor
            q_actual = N // factor
            integrity = (p_actual * q_actual == N)
            print(f"  ✓ FACTORED at stage {ecm_result['stage']}")
            print(f"    p = {p_actual} ({p_actual.bit_length()} bits)")
            print(f"    q = {q_actual} ({q_actual.bit_length()} bits)")
            print(f"    Integrity: {integrity}")
        else:
            print(f"  ✗ Not factored after {len(ecm_result['stages_attempted'])} stages")
        
        # Log result
        log_entry = {
            'idx': idx,
            'id': target_id,
            'N_bits': target['N_bits'],
            'N_head': str(N)[:24],
            'N_tail': str(N)[-24:],
            'tier': target.get('tier'),
            'tier_type': target.get('tier_type'),
            'ratio_target': target.get('ratio_target'),
            'ratio_actual': target.get('ratio_actual'),
            'fermat_gap': target.get('fermat_gap'),
            'fermat_target': target.get('fermat_target'),
            'gate': gate_result,
            'schedule_type': schedule_type,
            'status': 'factored' if ecm_result['factored'] else 'not_factored',
            'stage': ecm_result.get('stage'),
            'time_sec': ecm_result['time_sec'],
            'stages_attempted': ecm_result['stages_attempted'],
            'integrity': integrity,
        }
        
        if ecm_result['factored']:
            log_entry['p_bits'] = p_actual.bit_length()
            log_entry['q_bits'] = q_actual.bit_length()
            log_entry['p_head'] = str(p_actual)[:24]
            log_entry['q_head'] = str(q_actual)[:24]
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"  Time: {ecm_result['time_sec']:.2f}s")
    
    print("\n" + "="*70)
    print(f"✓ Processing complete. Log written to {log_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Run ECM factorization with theta-gating on distance targets'
    )
    parser.add_argument('--targets', type=str, required=True,
                       help='Path to targets JSON file')
    parser.add_argument('--timeout-per-stage', type=int, default=900,
                       help='Timeout in seconds per ECM stage (default: 900)')
    parser.add_argument('--checkpoint-dir', type=str, default='ckpts',
                       help='Directory for ECM checkpoints (default: ckpts)')
    parser.add_argument('--use-sigma', action='store_true',
                       help='Enable deterministic sigma seeding and theta-gating')
    parser.add_argument('--log', type=str, default='logs/distance_break.jsonl',
                       help='Log file path (default: logs/distance_break.jsonl)')
    
    args = parser.parse_args()
    
    # Check environment variables for overrides
    if 'ECM_SIGMA' in os.environ:
        args.use_sigma = bool(int(os.environ.get('ECM_SIGMA', '0')))
    if 'ECM_CKDIR' in os.environ:
        args.checkpoint_dir = os.environ['ECM_CKDIR']
    
    print("="*70)
    print("ECM Distance Break with Theta-Gating")
    print("="*70)
    print(f"Backend: {backend_info()['backend']}")
    print(f"Targets: {args.targets}")
    print(f"Timeout per stage: {args.timeout_per_stage}s")
    print(f"Checkpoint dir: {args.checkpoint_dir}")
    print(f"Use sigma/gating: {args.use_sigma}")
    print(f"Log file: {args.log}")
    
    run_distance_break(
        targets_file=args.targets,
        timeout_per_stage=args.timeout_per_stage,
        checkpoint_dir=args.checkpoint_dir,
        use_sigma=args.use_sigma,
        log_file=args.log
    )


if __name__ == "__main__":
    main()
