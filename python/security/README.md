# Security Module

Security-related Monte Carlo analysis tools, separated from core factorization/validation for modularity (MC-SCOPE-005).

## Components

### HyperRotationMonteCarloAnalyzer

Monte Carlo analysis for hyper-rotation protocol security.

**Features:**
- Rotation timing risk assessment
- Compromise rate estimation
- Post-quantum lattice resistance (placeholder)

**Usage:**

```python
from security.hyper_rotation import HyperRotationMonteCarloAnalyzer

analyzer = HyperRotationMonteCarloAnalyzer(seed=42)

# Analyze rotation timing
analysis = analyzer.sample_rotation_times(
    num_samples=10000,
    window_min=1.0,
    window_max=10.0
)

print(f"Compromise rate: {analysis['compromise_rate']:.4f}")
print(f"Safe threshold: {analysis['safe_threshold']:.2f}s")
```

**Quick Demo:**

```bash
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 python/security/hyper_rotation.py
```

## Design Principles

### Separation of Concerns (MC-SCOPE-005)

The security module is orthogonal to factorization/validation:

- **Factorization/Validation**: `monte_carlo.py`, `z5d_predictor.py`, `manifold_core.py`
- **Security Analysis**: `security/` submodule

This keeps the math/factorization surfaces lean while providing security tools.

### Backwards Compatibility

The `monte_carlo.py` module still exports `HyperRotationMonteCarloAnalyzer` for backwards compatibility:

```python
# Old import (still works)
from monte_carlo import HyperRotationMonteCarloAnalyzer

# New import (preferred)
from security.hyper_rotation import HyperRotationMonteCarloAnalyzer
```

## Future Components

Planned additions to the security module:

1. **Timing Attack Analysis**: Statistical detection of timing leaks
2. **Side-Channel Analysis**: Monte Carlo simulation of power/EM leaks
3. **Post-Quantum Integration**: NIST PQC candidate analysis
4. **Lattice Reduction**: Full LLL/BKZ simulation
5. **Quantum Attack Simulation**: Shor's algorithm resistance

## Integration with Hyper-Rotation Protocol

See `docs/HYPER_ROTATION_SPEC.md` for protocol details.

The Monte Carlo analyzer informs:
- Rotation window selection (1-10s)
- Key refresh policies
- Adversary model assumptions

## Testing

Security module tests are integrated with main Monte Carlo test suite:

```bash
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 tests/test_monte_carlo.py
```

Tests include:
- Rotation timing analysis
- PQ lattice resistance (placeholder)
- RNG policy compliance (PCG64)

## References

- Issue #38: Hyper-rotation protocol
- MC-SCOPE-005: Scope split requirement
- `docs/HYPER_ROTATION_SPEC.md`: Protocol specification

## License

MIT License (see repository root)
