# z-sandbox

**Purpose:** scratchpad for Z-Framework experiments (prime geometry, φ-mappings, Z-triangles, RSA grid filters, imaging demos). Expect messy prototypes, fast iteration, and structured logs.

> ⚠️ Research sandbox — not production-secure. Expect breaking changes.

## Recent Updates

### 🎉 Z5D Predictor Now Supports Ultra-High Scales (10^1233)!

The Z5D prime counting predictor has been upgraded with **arbitrary-precision BigDecimal arithmetic**, enabling predictions at cosmological scales far beyond the double-precision limit:

- **Previous limit:** ~10^305 (double overflow)
- **New capability:** Scales up to **10^1233** and beyond
- **Backward compatible:** Existing double-precision API unchanged
- **Performance:** ~10-20ms per prediction even at 10^1233

**Quick example:**
```java
// Ultra-high scale using BigDecimal
String result = Z5dPredictor.z5dPrimeString("1e1233", 0, 0, 0, true);
System.out.println("π(10^1233) ≈ " + result);
// Output: π(10^1233) ≈ 2.69E+1236

// Traditional double precision still works
double result = Z5dPredictor.z5dPrime(100000, 0, 0, 0, true);
```

See `scripts/demo_ultra_high_scale.java` for a complete demonstration.

## Structure
```
/src/                    # Java experiments (Gradle)
  main/java/org/zfifteen/sandbox/...
/python/                 # Python experiments (mpmath/numpy/etc.)
/plots/                  # Generated figures (git-tracked if small)
/data/                   # Local datasets (gitignored)
/out/                    # Run artifacts, logs, CSV, PNG (gitignored)
/scripts/                # One-liners, bootstrap helpers
```

## Quickstart

### Java
```bash
./gradlew run        # runs org.zfifteen.sandbox.Main
./gradlew test
```

### Python
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r python/requirements.txt
python python/examples/phi_bias_demo.py
```

## Logging standard

Every experiment should emit a line-oriented JSON log to `out/<exp>/<RUN_ID>.jsonl`:

```json
{"ts":"2025-10-11T12:00:00Z","exp":"phi_bias","host":"m1max","params":{"k":0.3},"metrics":{"enhancement_pct":15.0}}
```

## Disclaimers

* For educational/research use only. Crypto demos are **insecure** by design.
* Large data and private DICOM go in `/data/` (gitignored).
