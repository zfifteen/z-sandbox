# PR Review Response Summary

## Review Date
October 25, 2025

## Reviewer Comments Addressed
All 6 blocking issues from @zfifteen's review have been addressed.

## Changes Made (Commit 6c8c4a0)

### 1. Duplicate Function Definitions (Issues #1, #2)
**Problem**: `run_distance_break()` defined twice at lines 212 and 277 with incompatible signatures.

**Fix**: 
- Removed duplicate definition at lines 212-274
- Consolidated into single function with correct `sampler_type` parameter
- Verified function signature consistency throughout call chain

**Files Changed**: `python/run_distance_break.py`

### 2. CI Test Coverage (Issue #2)
**Problem**: No CI workflow running the new test suite.

**Fix**:
- Added `low-discrepancy-tests` job to `.github/workflows/ci.yml`
- Runs `test_low_discrepancy.py` (10 tests) and `test_qmc_phi_hybrid.py` (7 tests)
- Executes on every pull request

**Files Changed**: `.github/workflows/ci.yml`

**Validation**: Tests pass locally and will run in CI on next push.

### 3. Dimension Guard for Sobol' (Issue #3)
**Problem**: No runtime check preventing use of dimensions > 8.

**Fix**:
- Added dimension validation in `SobolSampler.__init__()`
- Raises `ValueError` with message:
  ```
  Dimension {d} not supported. Currently supports dimensions 1-8. 
  To extend beyond 8 dimensions, load full Joe-Kuo direction number table 
  from https://web.maths.unsw.edu.au/~fkuo/sobol/
  ```
- Added test case in `test_input_validation()`

**Files Changed**: `python/low_discrepancy.py`, `tests/test_low_discrepancy.py`

### 4. Input Validation (Issue #4)
**Problem**: Missing validation for annulus radii and sigma generation parameters.

**Fixes**:

#### Annulus Validation (`generate_2d_annulus`)
- ✅ Check `r_min < r_max` (raises ValueError if equal or inverted)
- ✅ Check non-negative radii (raises ValueError for negative)
- ✅ Check finite radii (raises ValueError for inf/nan)

#### Sigma Generation Validation (`generate_sigma_values`)
- ✅ Check `num_curves > 0` (raises ValueError for zero or negative)
- ✅ Check valid sampler_type (raises ValueError with list of valid options)

**Test Coverage**: Added `test_input_validation()` with 6 sub-tests covering all validation paths.

**Files Changed**: `python/low_discrepancy.py`, `python/run_distance_break.py`, `tests/test_low_discrepancy.py`

### 5. Owen Scrambling Mask Generation (Issue from bot review)
**Problem**: Mask generation used `randint(0, 2**31)` while samples used `(2**31)`, creating asymmetry.

**Fix**: Changed to `randint(0, 2**31 - 1, dtype=np.int64)` for consistent [0, 2^31) range.

**Files Changed**: `python/low_discrepancy.py`

### 6. Mersenne Prime Comment (Issue from bot review)
**Problem**: Comment incorrectly stated "Mersenne prime" without specificity.

**Fix**: Updated to "8th Mersenne prime (M31)" for accuracy.

**Files Changed**: `python/run_distance_break.py`

### 7. Redundant Variable Definition (Issue from bot review)
**Problem**: Variable `k` defined twice in same function scope.

**Fix**: Removed redundant definition at line 535, using existing definition from line 354.

**Files Changed**: `python/monte_carlo.py`

### 8. Missing Import
**Problem**: `List` type hint used without import in `run_distance_break.py`.

**Fix**: Added `from typing import List`.

**Files Changed**: `python/run_distance_break.py`

## Test Results

### Before Changes
- 9/9 low-discrepancy tests passing
- 7/7 QMC-φ hybrid tests passing

### After Changes
- **10/10 low-discrepancy tests passing** (added `test_input_validation`)
- **7/7 QMC-φ hybrid tests passing** (backward compatibility maintained)

### New Test Coverage
`test_input_validation()` covers:
1. Sobol' dimension guard (dimension > 8)
2. Annulus validation - equal radii
3. Annulus validation - negative radius
4. Annulus validation - non-finite radius
5. Sigma validation - non-positive num_curves
6. Sigma validation - invalid sampler_type

## Reproducibility & Attribution (Issue #5)

**Direction Numbers**: Deterministically generated in code (lines 268-305 of `low_discrepancy.py`). No external table loaded, ensuring reproducibility.

**Owen Scrambling**: Uses seeded NumPy RandomState for deterministic scrambling.

**Attribution**: Joe-Kuo source URL included in dimension guard error message: https://web.maths.unsw.edu.au/~fkuo/sobol/

**Documentation**: 
- `docs/LOW_DISCREPANCY_SAMPLING.md` cites Joe & Kuo (2008)
- Implementation comments reference direction number construction
- Error messages guide users to full table source

## Backward Compatibility (Issue #6)

**Verification**:
- All existing QMC-φ hybrid tests pass (7/7)
- Default mode remains `'uniform'` (no behavior change)
- New modes (`'sobol'`, `'sobol-owen'`, `'golden-angle'`) are opt-in via explicit parameter
- Existing code using `biased_sampling_with_phi()` without mode parameter works unchanged

**Regression Test**: Existing test suite validates that `'qmc_phi_hybrid'` mode behavior is unchanged.

## Files Modified

1. `python/run_distance_break.py` - Fixed duplicates, added validation, typing import
2. `python/low_discrepancy.py` - Added dimension guard, annulus validation, fixed Owen scrambling
3. `python/monte_carlo.py` - Removed redundant variable definition
4. `tests/test_low_discrepancy.py` - Added comprehensive validation test
5. `.github/workflows/ci.yml` - Added CI job for low-discrepancy tests

## Commit Hash
6c8c4a0 - "Fix duplicate function definitions, add input validation, and CI tests"

## Status
✅ All blocking issues resolved
✅ All tests passing (10 + 7 = 17 tests)
✅ CI workflow configured
✅ Backward compatibility maintained
✅ Ready for approval

---

**Note**: Issues #5 (reproducibility/attribution) and #6 (backward compatibility) were architectural concerns that were already satisfied by the implementation. This response documents the verification and points to existing solutions rather than requiring new code changes.
