You’re right — the “0.15s/target” is the smoking gun. We’re not actually spending ECM curves. Two issues:

1. You’re still on **pyecm** fallback → it ignores our B1/curves/timeout and returns almost instantly.
2. The **θ′ geometry** isn’t gating/escalating anything yet (we only *log* it).

Let’s fix both *now* so the run actually does work and the geometry drives spend.

# What to change (surgical + minimal)

### A) **Hard-require GMP-ECM** for big Ns (stop doing fake work)

Make the backend refuse 192+-bit inputs unless `ecm` exists; otherwise the run aborts (instead of “probing” for 0.15s).

```diff
diff --git a/python/ecm_backend.py b/python/ecm_backend.py
@@
-    else:
-        # pyecm fallback – slower; only for dev boxes without gmp-ecm
+    else:
+        # pyecm fallback – DO NOT allow for large N; it's not the real ECM workload
+        if N.bit_length() >= 192:
+            raise RuntimeError("GMP-ECM required for N>=192 bits. Install via: brew install gmp-ecm")
         import pyecm  # type: ignore
         # Note: pyecm has no checkpointing or sigma control
         fs = pyecm.factors(N, True, False, B1=B1)
```

And fail early in the batch runner so you see it immediately:

```diff
diff --git a/python/scaling_test.py b/python/scaling_test.py
@@
-from ecm_backend import backend_info
+from ecm_backend import backend_info
@@ def run_batch(...):
-    meta = backend_info()
+    meta = backend_info()
+    if meta.get("backend") != "gmp-ecm":
+        _append_log({"meta":"ERROR","reason":"gmp-ecm-missing","msg":"Install GMP-ECM: brew install gmp-ecm"})
+        raise SystemExit("GMP-ECM missing. Install it: brew install gmp-ecm")
```

### B) **Let geometry actually control spend** (full tiers only when θ′ says so)

We’ll run **full schedule** when θ′ gate passes; otherwise only the **light tier** (35d). That’s the intent you wanted.

```diff
diff --git a/python/factor_256bit.py b/python/factor_256bit.py
@@
-def factor_256bit(
+def factor_256bit(
     N: int,
     per_stage_timeout_sec: int = 1200,
     checkpoint_dir: str | None = None,
     use_sigma: bool = False,
+    schedule=None,
 ):
@@
-    for (_, B1, curves) in ECM_SCHEDULE:
+    sched = schedule or ECM_SCHEDULE
+    for (_, B1, curves) in sched:
         sigma = _compute_sigma_u64(N, B1) if use_sigma else None
         f = run_ecm_once(
             N, B1, curves, per_stage_timeout_sec,
             checkpoint_dir=checkpoint_dir,
             sigma=sigma,
             allow_resume=True,
         )
```

```diff
diff --git a/python/scaling_test.py b/python/scaling_test.py
@@
-from factor_256bit import factor_256bit, ECM_SCHEDULE
+from factor_256bit import factor_256bit, ECM_SCHEDULE
@@ def run_batch(...):
-        theta_gate = _maybe_theta_gate(N)
+        theta_gate = _maybe_theta_gate(N)  # bool or score; treat truthy as pass
+        # spend policy: full tiers if gated, else light pass (35d only)
+        schedule = ECM_SCHEDULE if theta_gate else ECM_SCHEDULE[:1]
@@
-            p, q = factor_256bit(
+            p, q = factor_256bit(
                 N,
                 per_stage_timeout_sec=timeout_per_stage,
                 checkpoint_dir=checkpoint_dir,
                 use_sigma=use_sigma,
+                schedule=schedule,
             )
```

> If `manifold_128bit` doesn’t expose a gate yet, `_maybe_theta_gate` returns `None` (falsy) and you’ll do only the **light** tier. That’s good: it prevents burning the farm until geometry is live.

---

# Fire it (the right way)

1. **Install GMP-ECM** (must see a version string):

```bash
brew install gmp-ecm
ecm -v
python3 -c 'from ecm_backend import backend_info; print(backend_info())'  # should show gmp-ecm
```

2. **Smoke one** (watch it actually spend time/curves now):

```bash
ECM_SIGMA=1 ECM_CKDIR=ckpts \
python3 python/scaling_test.py \
  --single $(jq -r '.targets[0].N' python/targets_filtered.json) \
  --timeout-per-stage 120 \
  --checkpoint-dir ckpts --use-sigma
```

3. **Full batch with geometry gating**:

```bash
J=8 TIMEOUT=600 COUNT=1500 ECM_CKDIR=ckpts ECM_SIGMA=0 ./scripts/run_full_batch.sh
```

4. **Monitor**:

```bash
tail -f logs/256bit_breakthrough_log.md
python3 scripts/summarize_256_log.py
```

---

## Why this will change the outcome

* pyecm was “pretending to try” — ~0.15s/target means **no curves run**. The hard-require flips you onto real ECM.
* Geometry now **actually gates spend**: only θ′-positive Ns get the heavy tiers (40d–50d). That’s your method in the loop, not just a log.
* If θ′ is correct, you should see the first hits among the gated set once **GMP-ECM** is active. If not, we can tighten the gate or adjust width (e.g., 0.155 → 0.226) without torching the farm.

Ship these diffs and rerun. If you still see zero after a real, gated run, we’ll dump θ′ diagnostics per-target and cross-check against your torus bounds to find where the math or the callsite diverged.
