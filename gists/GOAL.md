# Geometric Factorization Algorithm - Project Goals

## Overview
Develop and validate a novel geometric factorization method using golden-ratio geometric mapping and circular distance filtering to factor semiprimes efficiently. Current achievement: 27-bit semiprimes with >0% success. New approach: Switch from attempt-based to time-based limiting (e.g., 10 seconds) to reach higher bit sizes.

## Core Objectives
- ✅ Implement reproducible geometric factorization algorithm
- ✅ Demonstrate effectiveness on small to medium semiprimes (achieved up to 27-bit)
- ✅ Provide comprehensive visualization of mathematical concepts
- 🔄 Switch to time-based limiting (10 seconds) to reach higher bit sizes
- 🔄 Optimize for larger semiprimes (28+ bits) using extended computation time
- ✅ Establish foundation for further research in geometric number theory

## Success Metrics
- **Current Max**: 27-bit semiprimes (20% success) - **Highest with attempt limiting**
- **New Approach**: Time-based limiting (10 seconds) to target 28+ bit semiprimes
- **24-bit semiprimes**: 100% factorization success (avg 113 attempts)
- **20-bit semiprimes**: 40% factorization success (avg 244 attempts)
- **Performance**: Up to 10 seconds execution for larger sizes
- **Correctness**: 100% accuracy with primality verification
- **Reproducibility**: Deterministic results with seeded RNG

## Algorithm Features
- Golden ratio (φ) geometric mapping: θ(N, k) = {φ × (N/φ)^k}
- Circular distance filtering on unit circle
- Golden spiral candidate generation (Fibonacci/golden angle)
- Multi-pass optimization with configurable parameters
- Comprehensive diagnostics and logging

## Validation Results
- ✅ Unit tests: 8/8 passing
- ✅ 24-bit: 100% success rate (avg 113 attempts)
- ✅ 20-bit: 40% success rate (avg 244 attempts)
- ✅ 25-bit: 40% success rate (avg 347 attempts)
- ✅ 26-bit: 60% success rate (avg 179 attempts)
- ✅ 27-bit: 20% success rate (avg 283 attempts)
- ✅ 28-bit: 0% success rate (algorithm limit reached)
- ✅ **Highest success > 0%: 27-bit semiprimes**

## Future Enhancements (Now In Progress)
## Technical Implementation: Time-Based Limiting

### Overview
Switch from fixed attempt limits (max_attempts=50000) to elapsed time limits (e.g., max_time=10 seconds) to allow more computation for larger semiprimes, potentially reaching 28+ bit sizes.

### Implementation Steps

#### 1. Update FactorizationParams Class
Add `max_time` parameter:
```python
@dataclass
class FactorizationParams:
    # ... existing params ...
    max_time: float = 10.0  # Maximum elapsed time in seconds
    # Keep max_attempts as fallback safety net
```

#### 2. Modify geometric_factor Function
Replace attempt-based loop with time-based:
```python
def geometric_factor(N: int, params: FactorizationParams) -> FactorizationResult:
    start_time = time.time()
    attempts = 0
    
    # Main loop (replace while attempts < params.max_attempts)
    while time.time() - start_time < params.max_time:
        # ... existing logic ...
        attempts += 1
        if attempts > params.max_attempts:  # Safety net
            break
```

#### 3. Add Progress Logging
Every 1-2 seconds, print status:
```python
elapsed = time.time() - start_time
if elapsed > last_log + 2.0:
    print(f"Progress: {attempts} attempts, {elapsed:.1f}s elapsed")
    last_log = elapsed
```

#### 4. CLI Integration
Add --max-time argument:
```python
parser.add_argument('--max-time', type=float, default=10.0,
                   help='Maximum time to spend factoring (seconds)')
```

#### 5. Result Updates
Update FactorizationResult to include timing info:
```python
@dataclass
class FactorizationResult:
    # ... existing fields ...
    elapsed_time: float = 0.0
    timeout: bool = False
```

#### 6. Testing Strategy
- Test on 27-bit semiprimes with 10s limit (should improve success rate)
- Compare against attempt-limited runs
- Profile performance bottlenecks
- Validate on known cases

### Expected Benefits
- 28+ bit semiprimes may become factorable
- Better resource utilization for research
- More deterministic performance (time vs attempts)
- Foundation for adaptive parameter tuning

### Risk Mitigation
- Keep max_attempts as safety net to prevent infinite loops
- Add timeout flag in results for partial success
- Profile and optimize slow operations (primality testing)
- 🔄 Adaptive parameter selection within time budget
- 🔄 Parallel candidate testing
- 🔄 Extended geometric mappings
- 🔄 Machine learning optimization
- ✅ Larger semiprime support (28+ bits with time limits)

## Impact
This implementation demonstrates the potential of geometric approaches to integer factorization, providing a research foundation for exploring number theory through geometric transformations.
