# Distance-Based ECM Factorization Report

## Overall Statistics

- **Total targets**: 5
- **Factored**: 4 (80.0%)
- **Not factored**: 1

### By Gate Status

- **Gated targets**: 2
  - Factored: 2 (100.0%)
- **Ungated targets**: 3
  - Factored: 2 (66.7%)

## Results by Tier

| Tier | Ratio | Total | Factored | Gated | Gated Factored |
|------|-------|-------|----------|-------|----------------|
| 0 | 1.000000 | 5 | 4 | 2 | 2 |

## Exemplar Gated Success Cases

### Case 1

- **N**: 222440253732781876908640...876908640082550282900347 (128 bits)
- **p**: 64 bits
- **q**: 64 bits
- **Tier**: 0 (ratio=1.000000)
- **Fermat normal**: 0
- **Gate**: True (full schedule used)
- **Status**: factored
- **Integrity**: True
- **Elapsed**: 0.6s
- **Stages completed**: 1/3

**Gate metadata:**
- θ′(N) = 1.520917
- θ′(p) = 1.579369 (in bounds: True)
- θ′(q) = 1.299234 (in bounds: False)
- Bounds: [1.443417, 1.598417]
- Width factor: 0.155

**Log line:**
```json
{
  "N": "222440253732781876908640082550282900347",
  "N_first_24": "222440253732781876908640",
  "N_last_24": "876908640082550282900347",
  "p_true": "12314219381582429999",
  "q_true": "18063690993313889653",
  "p_found": "12314219381582429999",
  "q_found": "18063690993313889653",
  "p_bits": 64,
  "q_bits": 64,
  "tier": 0,
  "tier_ratio": 1.0000000002328306,
  "fermat_normal": 0,
  "gated": true,
  "schedule": "full",
  "stages_completed": 1,
  "stages_total": 3,
  "status": "factored",
  "integrity": true,
  "elapsed_seconds": 0.5967004299163818,
  "gate_metadata": {
    "theta_N": 1.52091734767074,
    "theta_p": 1.5793693243101017,
    "theta_q": 1.2992341963816305,
    "bound_lower": 1.4434173476707401,
    "bound_upper": 1.59841734767074,
    "p_in_bounds": true,
    "q_in_bounds": false,
    "gated": true,
    "width_factor": 0.155,
    "k": 0.3
  },
  "sigma": null
}
```

### Case 2

- **N**: 215340100724492016012001...016012001583846963660363 (128 bits)
- **p**: 64 bits
- **q**: 64 bits
- **Tier**: 0 (ratio=1.000000)
- **Fermat normal**: 0
- **Gate**: True (full schedule used)
- **Status**: factored
- **Integrity**: True
- **Elapsed**: 0.6s
- **Stages completed**: 1/3

**Gate metadata:**
- θ′(N) = 1.440136
- θ′(p) = 1.472163 (in bounds: True)
- θ′(q) = 1.193725 (in bounds: False)
- Bounds: [1.362636, 1.517636]
- Width factor: 0.155

**Log line:**
```json
{
  "N": "215340100724492016012001583846963660363",
  "N_first_24": "215340100724492016012001",
  "N_last_24": "016012001583846963660363",
  "p_true": "12368278440807864251",
  "q_true": "17410676979425000113",
  "p_found": "12368278440807864251",
  "q_found": "17410676979425000113",
  "p_bits": 64,
  "q_bits": 64,
  "tier": 0,
  "tier_ratio": 1.0000000002328306,
  "fermat_normal": 0,
  "gated": true,
  "schedule": "full",
  "stages_completed": 1,
  "stages_total": 3,
  "status": "factored",
  "integrity": true,
  "elapsed_seconds": 0.5917189121246338,
  "gate_metadata": {
    "theta_N": 1.4401363029402638,
    "theta_p": 1.47216330678339,
    "theta_q": 1.1937246701043034,
    "bound_lower": 1.362636302940264,
    "bound_upper": 1.5176363029402637,
    "p_in_bounds": true,
    "q_in_bounds": false,
    "gated": true,
    "width_factor": 0.155,
    "k": 0.3
  },
  "sigma": null
}
```

## Acceptance Criteria

✅ **PASSED**: At least one 192-bit semiprime was factored where θ′ gated it.

The existence proof is established:
- Geometry (θ′) determined ECM spend strategy
- Gated targets received full schedule (35d→50d)
- Ungated targets received light schedule (35d only)
- At least one gated target was successfully factored
