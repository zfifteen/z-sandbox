Nice bump! You cut runtime from 31.7s → **0.84s** and grew uniques **530 → 1,852**. But two signals say you’re still collapsing variants:

* **Dedup = 97.94%** → still sampling (nearly) the same indices.
* **Ratio to √N = [0.500, 1.000]** → your “Z-X [1.0, 3.0]” never crossed above √N. Something is still **clamping to ≤ √N** or centering all variants at √N.

Here’s a surgical fix list that will explode coverage and keep the speed:

# What to change (minimal & precise)

1. **Give each variant its own center in π-index space (not x-space):**

    * `centerRatios = {0.5, 1.0, 2.0}`  → centers at `{0.5√N, √N, 2√N}`
    * `i_center[v] = π( floor(centerRatios[v] * √N) )`
    * This guarantees Z-X actually targets **> √N**.

2. **Stride by expected gap, with Weyl jitter (prevents collisions):**

   ```java
   long gap = Math.max(1L, Math.round(Math.log(centerX.doubleValue()))); // ~avg prime gap
   for (int j = 0; j < baseSize; j++) {
     double w = (j * PHI) - Math.floor(j * PHI); // PHI = (1+√5)/2
     long idx = i_center[v] + Math.round((j - baseSize/2.0) * gap * mult[v] + w * gap);
     BigInteger x = pi.invertIndexSecant(idx, secantIters);
     if (!inThetaBand(x, centerX[v], band[v])) continue; // use v’s band
     if (x.isProbablePrime(32)) add(x);
   }
   ```

   Where `mult = {1, 9, 49}` (A, B, X) and `centerX[v] = floor(centerRatios[v] * √N)`.

3. **Kill the global clamp around √N:**
   If you still have something like `clampToWindow(sqrtN ± localWindow)`, replace it with **variant-local windows around `centerX[v]`**, or **no clamp** at all when you already pick by index. Clamping is why Z-X tops out at ratio 1.000.

4. **Scale window to target size (if you keep any windowing):**
   `localWindow ≥ baseSize * ceil(ln(centerX[v]))`. For 30k near 3.16e8, use **≥ 600k** indices. Small windows create repeats → high dedup.

5. **De-dup early across variants by index buckets:**
   Keep a `LongOpenHashSet seenBuckets`. Bucket = `idx / gap`. Skip if seen; this forces non-overlap with O(1) cost.

6. **Make θ a *weight* (optional), not a hard filter:**
   If θ filtering is still aggressive, move it to a scoring/priority step instead of discarding; that will keep coverage high for arbitrary moduli.

# Quick patch sketch (drop-in structure)

```java
final BigInteger sqrtN = isqrt(Nmax);
final double PHI = (1 + Math.sqrt(5.0)) / 2.0;
final double[] centerRatios = {0.5, 1.0, 2.0};     // A, B, X
final long[] mult = {1L, 9L, 49L};                 // spread factors
final double[][] bands = { {0.05,1.5}, {0.02,0.6}, {1.0,3.0} };

LongOpenHashSet buckets = new LongOpenHashSet(3L * baseSize);
for (int v = 0; v < 3; v++) {
  BigInteger centerX = sqrtN.multiply(BigInteger.valueOf((long)(centerRatios[v] * 1e6)))
                            .divide(BigInteger.valueOf(1_000_000L));
  long iCenter = pi.indexOfFloor(centerX);        // π(⌊center⌋)
  long gap = Math.max(1L, Math.round(Math.log(centerX.doubleValue())));
  for (int j = 0; j < baseSize; j++) {
    double w = (j * PHI) - Math.floor(j * PHI);
    long idx = iCenter + Math.round((j - baseSize/2.0) * gap * mult[v] + w * gap);
    long bucket = idx / gap;
    if (!buckets.add(bucket)) continue;           // enforce spread
    BigInteger x = pi.invertIndexSecant(idx, secantIters);
    if (!inThetaBand(x, centerX, bands[v])) continue;
    if (x.signum() > 0 && x.isProbablePrime(32)) add(x);
  }
}
```

# What you should see next run

* **Ratio to √N** should expand to roughly **[0.5, ~2.0–3.0]** (Z-X finally > √N).
* **Dedup** should drop **below ~60–80%** immediately (often <<50% with the bucket guard).
* **Total candidates** should jump from **1,852 → tens of thousands** (with baseSize=30k×3).
* **Runtime** stays ~sub-second to a few seconds (index inversion + MR(32) is cheap).

# Extra guardrails (nice-to-have)

* If `dedup > 0.95 || ratioMax < 1.05`, print:
  “**Collapse detected** — increase index spread (mult), remove clamps above √N, or expand localWindow.”
* Log per-variant coverage: `min/max ratio`, `unique count`, `avg gap`, `collisions`.

# TL;DR

You fixed the *speed* and widened to **0.5·√N…√N**, but the **clamp around √N** is still forcing the Z-X band to collapse. Move centers to `{0.5, 1.0, 2.0}·√N`, stride in **π-index space** with a Weyl jitter, kill the global clamp, and bucket de-dup. That will unlock **real** multi-variant coverage and give you the ~90k uniques you expected.
