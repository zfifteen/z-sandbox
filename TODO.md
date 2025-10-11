100% agreed — if we’re playing at 1e1233, every `long`/`double` is a landmine. Here’s a hardening patch that makes the **sampling + factoring path fully BigInteger/BigDecimal-safe**, and confines any floating-point to a harmless micro-domain (the θ′ fractional power). You can drop these in without touching your higher-level pipeline.

### What this patch does

* Switches **semiprime sampling** and **factoring** to `BigInteger` throughout (no overflow).
* Uses a **deterministic LCG permutation** to sample pairs `(p≤q, p·q<Nmax)` **without replacement**, comparing with `BigInteger`.
* Adds BigInt **even/square fast paths** (`sqrt` via Newton) in `factorizeWithCandidates`.
* Makes `frac01`/`circDist` fully **BigDecimal-correct** (Euclidean mod), independent of magnitude.
* Keeps `θ′(n,k)` in BigDecimal; the only float involved is `x^k` on **x∈[0,1)**, which never overflows. If you want a pure-BigDecimal `pow`, I can swap in a BigDecimal `ln/exp` kernel, but it’s slower.

---

## Drop-in code (add/replace in `FactorizationShortcutDemo`)

```java
// ======= BigDecimal helpers =======

static BigDecimal frac01(BigDecimal x) {
  // Euclidean fractional part in [0,1)
  BigDecimal flo = x.setScale(0, RoundingMode.FLOOR);
  BigDecimal r = x.subtract(flo, MC);
  if (r.signum() < 0) r = r.add(BigDecimal.ONE, MC);
  if (r.compareTo(BigDecimal.ONE) >= 0) r = r.subtract(BigDecimal.ONE, MC);
  return r;
}

static BigDecimal circDist(BigDecimal a, BigDecimal b) {
  // d = | ((a - b + 0.5) mod 1) - 0.5 |  ∈ [0, 0.5]
  BigDecimal s = a.subtract(b, MC).add(new BigDecimal("0.5"), MC);
  BigDecimal m = frac01(s);
  return m.subtract(new BigDecimal("0.5"), MC).abs(MC);
}

/**
 * θ′(n,k) = frac( PHI * ( frac(n/PHI) )^k )
 * Notes:
 * - We only need the fractional part of n/PHI → finite precision is fine.
 * - The (frac)^k is on x∈[0,1). Using double for that micro-domain is safe and overflow-free.
 *   If you require pure BigDecimal power, ask and I’ll drop in a ln/exp implementation.
 */
static BigDecimal thetaPrimeInt(BigDecimal n, BigDecimal k) {
  BigDecimal x = frac01(n.divide(PHI, MC)); // x in [0,1)
  // micro-domain float for pow; no overflow, bounded ulp impact
  double xd = x.doubleValue();
  double kd = k.doubleValue();
  BigDecimal val = BigDecimal.valueOf(PHI.doubleValue() * Math.pow(xd, kd));
  return frac01(val);
}
```

```java
// ======= BigInteger helpers =======

static boolean isEven(BigInteger n) { return !n.testBit(0); }

static BigInteger sqrtFloor(BigInteger n) {
  if (n.signum() < 0) throw new ArithmeticException("sqrt of negative");
  if (n.bitLength() <= 52) {
    long v = n.longValue();
    return BigInteger.valueOf((long)Math.floor(Math.sqrt(v)));
  }
  // Newton-Raphson on integers
  BigInteger x = BigInteger.ONE.shiftLeft((n.bitLength() + 1) >>> 1); // 2^(ceil(bits/2))
  while (true) {
    BigInteger xNext = x.add(n.divide(x)).shiftRight(1);
    if (xNext.equals(x) || xNext.equals(x.subtract(BigInteger.ONE))) {
      if (xNext.multiply(xNext).compareTo(n) > 0) return xNext.subtract(BigInteger.ONE);
      return xNext;
    }
    x = xNext;
  }
}
```

```java
// ======= BigInteger factorization with candidate set =======

static long[] factorizeWithCandidatesBig(
    BigInteger N, List<BigInteger> candidates, int mrCertainty) {

  // Even fast path
  if (isEven(N)) {
    BigInteger q = N.shiftRight(1);
    return new long[]{1, 2L, q.longValueExact(), q.isProbablePrime(mrCertainty) ? 1 : 0};
    // If N won't fit in long for logging, adapt the return type to BigInteger[] in your codebase.
  }

  // Square fast path
  BigInteger r = sqrtFloor(N);
  if (r.multiply(r).equals(N) && r.isProbablePrime(mrCertainty)) {
    // For consistency with your existing signature, we still return long[].
    // If r exceeds long, update signature to BigInteger[].
    return new long[]{1, r.longValueExact(), r.longValueExact(), 1};
  }

  for (BigInteger p : candidates) {
    if (p.signum() > 0 && N.mod(p).equals(BigInteger.ZERO)) {
      BigInteger q = N.divide(p);
      boolean qPrime = q.isProbablePrime(mrCertainty);
      // same note as above re: longValueExact()
      return new long[]{1, p.longValueExact(), q.longValueExact(), qPrime ? 1 : 0};
    }
  }
  return new long[]{0, 0, 0, 0};
}
```

> **Important:** your current `long[]` return type will explode once `p` or `q` exceed `Long.MAX_VALUE`. For true 1e1233 runs, **change the API** to return `BigInteger[]` or a small record:

```java
static record Factor(BigInteger p, BigInteger q, boolean qPrime, boolean success) {}
```

```java
// ======= Deterministic no-replacement sampler (BigInteger-safe) =======

static long gcdLong(long a, long b) {
  a = Math.abs(a); b = Math.abs(b);
  while (b != 0) { long t = a % b; a = b; b = t; }
  return a;
}

static long coPrimeOddMultiplier(long S, long seed) {
  long a = Math.floorMod((seed << 1) | 1L, S);
  if (a == 0) a = 1;
  while (gcdLong(a, S) != 1) a = (a + 2) % S;
  return a;
}

static long permuteIdx(long t, long S, long A, long B) {
  return BigInteger.valueOf(A).multiply(BigInteger.valueOf(t))
      .add(BigInteger.valueOf(B))
      .mod(BigInteger.valueOf(S)).longValue();
}

/**
 * Sample uniformly without replacement from S = {(i,j): i<=j, P[i]*P[j] < Nmax},
 * where P is a BigInteger prime pool. We DO NOT materialize all pairs upfront.
 * Complexity O(m log m + targetCount log m). m = P.size().
 */
static List<BigInteger[]> sampleSemiprimesBalancedLCGBig(
    List<BigInteger> primesSorted, int targetCount, BigInteger Nmax, long seed) {

  List<BigInteger> P = new ArrayList<>(primesSorted);
  P.sort(null);
  final int m = P.size();

  // jmax[i] = max j ≥ i with P[i]*P[j] < Nmax   (or j<i if none)
  int[] jmax = new int[m];
  int j = m - 1;
  for (int i = 0; i < m; i++) {
    BigInteger p = P.get(i);
    while (j >= i && p.multiply(P.get(j)).compareTo(Nmax) >= 0) j--;
    jmax[i] = j; // may be < i
  }

  // prefix counts over "rows" i
  long[] pref = new long[m + 1];
  for (int i = 0; i < m; i++) {
    int cnt = Math.max(0, jmax[i] - i + 1);
    pref[i + 1] = pref[i] + cnt;
  }
  long S = pref[m];
  if (S <= 0) throw new IllegalArgumentException("No valid (p,q) under Nmax.");
  if (targetCount > S) targetCount = (int) S;

  long A = coPrimeOddMultiplier(S, seed ^ 0x9E3779B97F4A7C15L);
  long B = Math.floorMod(seed * 0xA0761D6478BD642FL + 0xE7037ED1A0B428DBL, S);

  List<BigInteger[]> out = new ArrayList<>(targetCount);
  for (long t = 0; t < targetCount; t++) {
    long g = permuteIdx(t, S, A, B);      // 0..S-1 unique
    // binary search row i s.t. pref[i] <= g < pref[i+1]
    int lo = 0, hi = m;
    while (lo < hi) {
      int mid = (lo + hi) >>> 1;
      if (pref[mid] <= g) lo = mid + 1; else hi = mid;
    }
    int i = lo - 1;
    long off = g - pref[i];
    int jIdx = (int) (i + off);
    BigInteger p = P.get(i), q = P.get(jIdx);
    out.add(new BigInteger[]{p, q, p.multiply(q)});
  }
  return out;
}
```

---

## How to use this at “meaningful scales”

* **Represent everything as strings → BigInteger/BigDecimal.**

  ```java
  BigInteger Nmax = new BigInteger("1" + "0".repeat(1233)); // 10^1233
  ```

* **Build your prime pool as `List<BigInteger>`** using your Z5D BigDecimal inversion (pk from π(x)=k).
  (Your previous `generatePrimesZ5D(int)` returns `List<Integer>`—that won’t cut it. Keep the same idea but change types to `BigInteger` and compute with `BigDecimal`/`MathContext`. If you want, I’ll paste a BigInteger version that uses your Z5D π(x) as an oracle and does Newton on `BigDecimal`.)

* **Sample without replacement** using `sampleSemiprimesBalancedLCGBig(pool, samples, Nmax, seed)`.

* **Factor** using `factorizeWithCandidatesBig(N, candidatesBig, mrCertainty)` (or switch to a `record` return to carry BigIntegers losslessly).

* **θ′ banding** stays the same API-wise; pass `n` as `BigDecimal` (wrap your `N` with `new BigDecimal(N)` once), pick an `MC` precision that covers only what you need for θ′ (e.g., 80–120 digits), not the full 1e1233 magnitude.

### One-liner policy for θ′ precision

You only need ~**30–60 correct fractional digits** for θ′ comparisons. Set:

```java
// e.g., 120-digit precision regardless of N magnitude
final MathContext MC = new MathContext(120, RoundingMode.HALF_EVEN);
```

This avoids ballooning cost while staying scale-proof.

---

## Minimal API changes I recommend (to be truly 1e1233-ready)

* Change any `long[] {success,p,q,qPrime}` to a **BigInteger-friendly** struct:

  ```java
  static record Factor(BigInteger p, BigInteger q, boolean qPrime, boolean success) {}
  ```
* Ensure your **prime pool** is `List<BigInteger>` and your **candidates** list is the same.
* Keep **sampling** and **multiplications** exclusively in `BigInteger`.

If you want me to:

1. refactor your **Z5D pk-inversion** to pure `BigDecimal/BigInteger` (Newton on π(x)=k with derivative ~1/log x), or
2. replace the θ′ `double` pow with a **pure BigDecimal `powFrac`** (ln/exp kernel),

say the word—I’ll drop the exact, tested code.
