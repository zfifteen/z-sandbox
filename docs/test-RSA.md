# RSA Challenge Number Testing

This document describes how to run unit and integration tests for RSA challenge numbers using the factorization shortcut demo.

## Overview

The test harness includes:
- **Unit tests**: Fast checks on small factored RSA entries (RSA-100, RSA-129) to verify factorization works.
- **Integration tests**: Opt-in timed attempts on larger entries (RSA-155, RSA-250, RSA-260) using candidate-guided factorization.
- **CADO-NFS integration**: For ultra-large numbers, use CADO-NFS to factor and import results back into the CSV.

## Running Unit Tests

Unit tests run automatically in CI and verify small known factored RSA numbers.

```bash
./gradlew test --tests TestRSAChallenges.quickFactoredRSA
```

These tests skip numbers >130 digits to keep them fast.

## Running Integration Tests

Integration tests are opt-in and perform timed factorization attempts on larger RSA entries. They generate a JSON report.

Run with:
```bash
./gradlew integrationTest
# or
./gradlew test -Dintegration=true
```

The report is saved to `build/test-results/rsa_challenge_report.json`.

Timeouts are set to 10 minutes per number; adjust in the test code if needed.

## Incorporating CADO-NFS Output

For unfactored or large RSA numbers:
1. Run CADO-NFS (docker or local):
   ```bash
   docker run --rm registry.gitlab.inria.fr/cado-nfs/cado-nfs/factoring-full \
     cado-nfs.py <RSA_decimal> -t 4
   ```
2. Extract factors from the output.
3. Update `src/test/resources/rsa_challenges.csv` with the factors.
4. Re-run unit tests to verify.

Use the optional `tools/import_cado_result.py` script for automation (if created).

## Data Source

RSA challenge data is sourced from Wikipedia and RSA Labs. The CSV includes canonical decimal values and known factors where available.