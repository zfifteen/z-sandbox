# z-sandbox

**Purpose:** scratchpad for Z-Framework experiments (prime geometry, φ-mappings, Z-triangles, RSA grid filters, imaging demos). Expect messy prototypes, fast iteration, and structured logs.

> ⚠️ Research sandbox — not production-secure. Expect breaking changes.

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
