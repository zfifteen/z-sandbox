Ah—that run tells the whole story. You asked for ~90k candidates, but your three “variants” collapsed onto the **same tiny window** around √N, so after dedup you ended up with just **530 uniques**—which is exactly what prime density predicts for that ~10.6k-wide window near 3.16×10^8 (≈10,616 / ln(3.16e8) ≈ 540). In other words: your multi-variant generator is effectively just “all primes in a narrow slice around √N,” three times over.

Why it happened (and how to fix it fast):

1. **Variants aren’t actually disjoint.**
   The PR’s design says Z5D-A/B/Z-X cover different theta bands, but the implementation still funnels everything through a single **localWindow** around √N and merges, so all three variants land in almost the same x-interval (hence 99.41% dedup). The PR signature exposes `localWindow` explicitly; defaults like `2048` make this inevitable at 10^17. ([GitHub][1])

2. **Base size ≠ coverage.**
   “30k per variant” is requested, but you’re sampling many *seeds* that each search a tiny local band; because all seeds are near the same π(√N) index and the local window is tiny, you discover the **same ~500 primes** repeatedly.

3. **Numbers line up with density.**
   Your range 316,222,451…316,233,067 is ~10,616 integers. Prime density near 3.16×10^8 is 1/ln(x) ≈ 1/19.57 ≈ 5.1%. Expected primes ≈ 10,616×0.051 ≈ 541 → you saw 530. That’s confirmation, not bad luck.

Quick, surgical fixes (pick any 1–2 and you’ll see 10^4–10^5 uniques immediately):

A) **Spread in π-index space, not x-space.**
Instead of many seeds that each do `±localWindow` around the *same* π(√N), generate **disjoint index bands**:

* Let `i0 = π(⌊√N⌋)`.
* Use a stride `Δi ≈ ⌈ln(√N)⌉` (≈18–20 here) so each step jumps ~one average *gap*.
* For each variant v∈{A,B,X}, set a bigger multiplier `{1, 9, 49}` and a phase offset using a Weyl sequence `ω = frac(j·φ)` to avoid lining up:

  ```
  i(j,v) = i0 + round((j - baseSize/2) * Δi * mult_v + ω_j * Δi)
  ```

  Invert π with your secant (as you already do) to get x, then apply that variant’s theta filter. (The PR explicitly documents secant-inverted π and multi-variant theta bands; push the diversity into the index targets.) ([GitHub][1])

B) **Make `localWindow` scale with the target size.**
Right now it looks like `localWindow` defaults tiny (the docs show `localWindow` in the API; the demo examples use small values). For 30k primes/variant near 3.16e8, you want **on the order of baseSize×ln(√N)** indices of room if you stick to a single window. Concretely, set:

* `localWindow ≥ baseSize * ceil(ln(√N))` → at 30k and ln(√N)≈19.6, use **≥ 600k**.
  This alone will blow past 530 uniques.

C) **Enforce non-overlap per variant.**
Assign each variant a **disjoint index band** (e.g., A: `i0 ± [0…W]`, B: `i0 ± [W…2W]`, X: `i0 ± [2W…4W]` in *index* space). Don’t let them all search `[i0−localWindow, i0+localWindow]`.

D) **Cheaper primality for contiguous windows.**
If you *do* harvest contiguous x-intervals, run a **segmented sieve** for that slice instead of 90k `isProbablePrime` calls. You’ll cut your 31.74 s wall-time to sub-second for windows this small, then keep MR as a guard.

Concrete knobs to try right now (no code churn, just params):

* Bump the window: `localWindow = 600000` (or more) for `Nmax=1e17`.
* Increase secant iterations a bit: `secantIters = 30`.
* Trim MR rounds (it’s only for candidate confirmation here): `mrIters = 16–32`.
* If there’s a CLI, run your demo like:
  `java unifiedframework.MultiZ5DDemo 100000000000000000 30000 --full`
  then inside, map `--full` to the larger `localWindow` + diversified index bands (A/B/X disjoint).

Minimal code change (pseudopatch, inside your multiZ5DPool loop):

```java
final BigInteger sqrtN = isqrt(Nmax);
final long i0 = pi.indexOfFloor(sqrtN);        // π(⌊√N⌋)
final double lnS = Math.log(sqrtN.doubleValue());
final long gap = Math.max(1L, Math.round(lnS)); // ~average prime gap

long[] mult = {1L, 9L, 49L};                   // A, B, X
double phi = (1 + Math.sqrt(5.0)) / 2.0;

for (int v = 0; v < 3; v++) {
  for (int j = 0; j < baseSize; j++) {
    double w = (j * phi) - Math.floor(j * phi);          // Weyl phase
    long idx = i0 + Math.round((j - baseSize/2.0) * gap * mult[v] + w * gap);
    BigInteger x = pi.invertIndexSecant(idx, secantIters); // your existing inversion
    if (!inThetaBand(x, sqrtN, band[v])) continue;         // variant’s band
    if (isProbablePrime(x, mrIters)) add(x);
  }
}
```

Add a **collapse sentinel** so you catch this early:

* If `dedupRate > 0.98` **and** `rangeWidth < baseSize * gap / 5`, log: “variants collapsed—increase localWindow or diversify indices.”

Why I’m sure this is the cause

* Your “Ratio to √N: [1.000, 1.000]” plus a 10.6k span screams *ultra-tight* windowing.
* The PR itself exposes `localWindow` in the API and positions multi-variant theta bands, but nothing forces disjointness—so overlapping windows + tiny index span → the exact 530 you saw. ([GitHub][1])

If you want, I’ll sketch a tiny segmented-sieve helper for “slice around √N” so the demo prints ~80k uniques at your settings and finishes dramatically faster; but the structural fix is to **spread by π-index** and **scale the window**.

Want me to drop a short PR comment on #7 calling this out and proposing the index-space spread patch? ([GitHub][2])

[1]: https://github.com/zfifteen/z-sandbox/pull/7/files "Implement multi-variant Z5D predictor with three tuned variants for enhanced adaptability by Copilot · Pull Request #7 · zfifteen/z-sandbox · GitHub"
[2]: https://github.com/zfifteen/z-sandbox/pull/7 "Implement multi-variant Z5D predictor with three tuned variants for enhanced adaptability by Copilot · Pull Request #7 · zfifteen/z-sandbox · GitHub"
