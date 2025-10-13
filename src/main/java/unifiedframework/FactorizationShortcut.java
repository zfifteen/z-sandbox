package unifiedframework;

import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;
import java.util.LinkedHashSet;
import java.util.stream.Collectors;

/**
 * Factorization Shortcut Demo (BigInteger/BigDecimal-safe, Z5D-only)
 *
 * <p>Key properties: - NO sieve. Prime pool is built by inverting pi(x) using a Z5D BigDecimal
 * oracle (secant), then a tiny local odd-step search to the nearest probable prime. - Sampling
 * uniformly without replacement from all (p <= q, p*q < Nmax) using an LCG permutation over the
 * implicit pair index space (no materialization). - Full BigInteger/BigDecimal safety for N, p, q,
 * comparisons, and sqrt(Nmax). - Theta banding uses BigDecimal; only bounded double is used for x^k
 * with x in [0,1).
 *
 * <p>Plug your BigDecimal Z5D oracle at: PiOracle pi = x -> Z5dPredictorBD.pi(x); If absent, we
 * fallback to a double-based adapter via Z5dPredictor.z5dPrime(...), which is NOT scale-safe for
 * huge N and is provided for compilation/demo only.
 */
public class FactorizationShortcut {

  // ======== Configuration ========
  // Precision for all BigDecimal computations (theta, secant steps, etc.).
  // 160 digits is plenty for theta and root-finding steering.
  private static final MathContext MC = new MathContext(160, RoundingMode.HALF_EVEN);

  // Golden ratio
  private static final BigDecimal PHI =
      BigDecimal.ONE.add(new BigDecimal(5).sqrt(MC)).divide(new BigDecimal(2), MC);

  // ======== A) BigDecimal / BigInteger helpers ========

  /** Euclidean fractional part in [0, 1). */
  static BigDecimal frac01(BigDecimal x) {
    BigDecimal flo = x.setScale(0, RoundingMode.FLOOR);
    BigDecimal r = x.subtract(flo, MC);
    if (r.signum() < 0) r = r.add(BigDecimal.ONE, MC);
    if (r.compareTo(BigDecimal.ONE) >= 0) r = r.subtract(BigDecimal.ONE, MC);
    return r;
  }

  /** Circular distance on unit circle in [0, 0.5]. */
  static BigDecimal circDist(BigDecimal a, BigDecimal b) {
    BigDecimal s = a.subtract(b, MC).add(new BigDecimal("0.5"), MC);
    BigDecimal m = frac01(s);
    return m.subtract(new BigDecimal("0.5"), MC).abs(MC);
  }

  /**
   * thetaPrimeInt: θ′(n,k) = frac( PHI * ( frac(n/PHI) )^k ) We compute pow in double over x in
   * [0,1) -- bounded and overflow-free. If pure BigDecimal pow is required, replace with a ln/exp
   * kernel.
   */
  static BigDecimal thetaPrimeInt(BigDecimal n, BigDecimal k) {
    BigDecimal x = frac01(n.divide(PHI, MC)); // x in [0,1)
    double xd = x.doubleValue();
    double kd = k.doubleValue();
    BigDecimal val = BigDecimal.valueOf(PHI.doubleValue() * Math.pow(xd, kd));
    return frac01(val);
  }

  /** Integer sqrt floor via Newton-Raphson. */
  static BigInteger sqrtFloor(BigInteger n) {
    if (n.signum() < 0) throw new ArithmeticException("sqrt of negative");
    if (n.signum() == 0) return BigInteger.ZERO;
    BigInteger x = BigInteger.ONE.shiftLeft((n.bitLength() + 1) >>> 1);
    while (true) {
      BigInteger xn = x.add(n.divide(x)).shiftRight(1);
      if (xn.equals(x) || xn.equals(x.subtract(BigInteger.ONE))) {
        if (xn.multiply(xn).compareTo(n) > 0) return xn.subtract(BigInteger.ONE);
        return xn;
      }
      x = xn;
    }
  }

  // ======== B) Deterministic no-replacement sampler (BigInteger) ========

  /** Sample uniformly without replacement from S = {(i,j): i<=j, P[i]*P[j] < Nmax}. */
  static List<BigInteger[]> sampleSemiprimesBalancedLCG(
      List<BigInteger> primesSorted, int targetCount, BigInteger Nmax, long seed) {

    List<BigInteger> P = new ArrayList<>(primesSorted);
    P.sort(null);
    final int m = P.size();

    int[] jmax = new int[m];
    int j = m - 1;
    for (int i = 0; i < m; i++) {
      BigInteger p = P.get(i);
      while (j >= i && p.multiply(P.get(j)).compareTo(Nmax) >= 0) j--;
      jmax[i] = j; // may be < i => no pairs for row i
    }

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
      long g = permuteIdx(t, S, A, B); // 0..S-1 unique
      int i = upperBound(pref, g) - 1; // pref[i] <= g < pref[i+1]
      long off = g - pref[i];
      int jj = (int) (i + off);
      BigInteger p = P.get(i), q = P.get(jj);
      out.add(new BigInteger[] {p, q, p.multiply(q)});
    }
    return out;
  }

  static int upperBound(long[] a, long x) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
      int mid = (lo + hi) >>> 1;
      if (a[mid] <= x) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }

  static long gcdLong(long a, long b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b != 0) {
      long t = a % b;
      a = b;
      b = t;
    }
    return a;
  }

  static long coPrimeOddMultiplier(long S, long seed) {
    long a = Math.floorMod((seed << 1) | 1L, S);
    if (a == 0) a = 1;
    while (gcdLong(a, S) != 1) a = (a + 2) % S;
    return a;
  }

  static long permuteIdx(long t, long S, long A, long B) {
    return BigInteger.valueOf(A)
        .multiply(BigInteger.valueOf(t))
        .add(BigInteger.valueOf(B))
        .mod(BigInteger.valueOf(S))
        .longValue();
  }

  // ======== C) Big-safe factorization with fast paths ========

  public static record Factor(BigInteger p, BigInteger q, boolean qPrime, boolean success) {}

  static Factor factorizeWithCandidatesBig(
      BigInteger N, List<BigInteger> candidates, int mrCertainty) {

    if (!N.testBit(0)) { // even
      BigInteger q = N.shiftRight(1);
      return new Factor(BigInteger.TWO, q, q.isProbablePrime(mrCertainty), true);
    }
    BigInteger r = sqrtFloor(N);
    if (r.multiply(r).equals(N) && r.isProbablePrime(mrCertainty))
      return new Factor(r, r, true, true);

    for (BigInteger p : candidates) {
      if (p.signum() > 0 && N.mod(p).equals(BigInteger.ZERO)) {
        BigInteger q = N.divide(p);
        return new Factor(p, q, q.isProbablePrime(mrCertainty), true);
      }
    }
    return new Factor(BigInteger.ZERO, BigInteger.ZERO, false, false);
  }

  // ======== D) Z5D-only prime pool around √Nmax (secant on π(x)) ========

  @FunctionalInterface
  interface PiOracle {
    BigDecimal pi(BigDecimal x);
  }

  /** Build a PiOracle from available predictors. Prefers BigDecimal Z5dPredictorBD.pi(x). */
  static PiOracle buildPiOracle() {
    try {
      // Try: unifiedframework.Z5dPredictorBD.pi(BigDecimal) : BigDecimal
      Class<?> cls = Class.forName("unifiedframework.Z5dPredictorBD");
      Method m = cls.getMethod("pi", BigDecimal.class);
      return x -> {
        try {
          return (BigDecimal) m.invoke(null, x);
        } catch (Throwable t) {
          throw new RuntimeException("Z5dPredictorBD.pi call failed", t);
        }
      };
    } catch (Throwable ignored) {
      // Fallback: use double z5dPrime(long) adapter (NOT scale-safe; demo only).
      return x -> {
        double xd = x.doubleValue();
        if (xd < 2.0) return BigDecimal.ZERO;
        try {
          double pi = Z5dPredictor.z5dPrime((long) Math.floor(xd), 0, 0, 0, true);
          return new BigDecimal(pi, MC);
        } catch (Throwable t) {
          throw new UnsupportedOperationException(
              "No BigDecimal Z5D oracle found. Provide unifiedframework.Z5dPredictorBD.pi(BigDecimal).",
              t);
        }
      };
    }
  }

  /** Secant inversion: find x with pi(x) ≈ k. */
  static BigInteger invertPiSecant(
      BigInteger k, PiOracle pi, BigInteger x0, BigInteger x1, int iters) {
    BigDecimal kBD = new BigDecimal(k);
    BigDecimal xPrev = new BigDecimal(x0);
    BigDecimal xCurr = new BigDecimal(x1);

    for (int i = 0; i < iters; i++) {
      BigDecimal fPrev = pi.pi(xPrev).subtract(kBD, MC);
      BigDecimal fCurr = pi.pi(xCurr).subtract(kBD, MC);
      BigDecimal denom = fCurr.subtract(fPrev, MC);
      if (denom.signum() == 0) break;
      BigDecimal step = fCurr.multiply(xCurr.subtract(xPrev, MC), MC).divide(denom, MC);
      BigDecimal xNext = xCurr.subtract(step, MC);
      if (xNext.compareTo(new BigDecimal(2)) < 0) xNext = new BigDecimal(2);
      xPrev = xCurr;
      xCurr = xNext;
      if (xCurr.subtract(xPrev, MC).abs().compareTo(BigDecimal.ONE) <= 0) break;
    }
    return xCurr.toBigInteger(); // prime refinement next
  }

  /** Local odd-step search to nearest probable prime within ±window steps of 2. */
  static BigInteger findPrimeNear(BigInteger x0, int window, int certainty) {
    BigInteger x = x0.testBit(0) ? x0 : x0.add(BigInteger.ONE);
    if (x.isProbablePrime(certainty)) return x;
    for (int d = 1; d <= window; d++) {
      BigInteger up = x.add(BigInteger.valueOf(2L * d));
      if (up.isProbablePrime(certainty)) return up;
      BigInteger dn = x.subtract(BigInteger.valueOf(2L * d));
      if (dn.compareTo(BigInteger.TWO) > 0 && dn.isProbablePrime(certainty)) return dn;
    }
    return BigInteger.valueOf(-1);
  }

  /** Build prime pool in [bandLo*√Nmax, bandHi*√Nmax] using ONLY Z5D π(x) oracle. */
  static List<BigInteger> generatePrimePoolBandZ5D(
      BigInteger Nmax,
      double bandLo,
      double bandHi,
      int poolTarget,
      PiOracle pi,
      int secantIters,
      int localWindow,
      int mrIters) {

    if (!(bandLo > 0 && bandHi > bandLo)) throw new IllegalArgumentException("bad band");
    BigInteger s = sqrtFloor(Nmax); // √Nmax
    BigDecimal sBD = new BigDecimal(s);
    BigInteger pLo = new BigDecimal(bandLo, MC).multiply(sBD, MC).toBigInteger();
    BigInteger pHi = new BigDecimal(bandHi, MC).multiply(sBD, MC).toBigInteger();

    BigInteger kS = pi.pi(sBD).toBigInteger(); // π(√Nmax)

    LinkedHashSet<BigInteger> pool = new LinkedHashSet<>(Math.max(16, poolTarget * 11 / 10));
    BigInteger x0 = pLo.max(BigInteger.TWO);
    BigInteger x1 = pHi;

    int step = 0;
    while (pool.size() < poolTarget) {
      for (int sign : new int[] {+1, -1}) {
        BigInteger k = kS.add(BigInteger.valueOf((long) sign * step));
        if (k.compareTo(BigInteger.TWO) < 0) continue;
        BigInteger xApprox = invertPiSecant(k, pi, x0, x1, secantIters);
        BigInteger p = findPrimeNear(xApprox, localWindow, mrIters);
        if (p.signum() > 0 && p.compareTo(pLo) >= 0 && p.compareTo(pHi) <= 0) {
          pool.add(p);
          if (pool.size() >= poolTarget) break;
        }
      }
      step++;
      if (step > poolTarget * 4) break; // safety valve
    }

    List<BigInteger> out = new ArrayList<>(pool);
    out.sort(null);
    if (out.size() > poolTarget) out = out.subList(0, poolTarget);
    return out;
  }

  // ======== D) Multi-variant Z5D Pool Generation ========

  /**
   * Generates a combined pool of prime candidates using three tuned Z5D variants.
   *
   * <p>Variants: - Z5D-A: Baseline for balanced semiprimes (theta band 0.05–1.5, epsilon 0.1) -
   * Z5D-B: Stretch low-band for skinny factors (theta band 0.02–0.6, epsilon 0.05) - Z-X:
   * High-offset-band for primes significantly above √N (theta band 1.0–3.0, epsilon 0.2)
   *
   * @param Nmax The maximum N value (used to compute √Nmax for band calculations)
   * @param baseSize The base size for prime generation per variant (target: 30k per variant)
   * @param pi The Z5D π(x) oracle for prime prediction
   * @param secantIters Number of secant iterations for pi inversion
   * @param localWindow Window size for local prime search
   * @param mrIters Miller-Rabin iterations for primality testing
   * @return A merged and distinct list of prime candidates (~80k total)
   */
  public static List<BigInteger> multiZ5DPool(
      BigInteger Nmax, int baseSize, PiOracle pi, int secantIters, int localWindow, int mrIters) {

    BigInteger sqrtN = sqrtFloor(Nmax);
    double lnS = Math.log(sqrtN.doubleValue());
    long gap = Math.max(1L, Math.round(lnS));

    // Scale localWindow if too small
    int scaledLocalWindow = Math.max(localWindow, (int) (baseSize * Math.ceil(lnS)));

    double phi = (1 + Math.sqrt(5.0)) / 2.0;

    double[][] thetaBands = {{0.05, 1.5}, {0.02, 0.6}, {1.0, 3.0}};
    double[] scaleFactors = {0.5, 1.0, 1.5}; // Different scales for i0

    LinkedHashSet<BigInteger> merged = new LinkedHashSet<>(baseSize * 3);

    for (int v = 0; v < 3; v++) {
      BigDecimal scaledSqrt = new BigDecimal(sqrtN).multiply(new BigDecimal(scaleFactors[v]), MC);
      BigInteger i0 = pi.pi(scaledSqrt).toBigInteger();
      for (int j = 0; j < baseSize; j++) {
        double w = (j * phi) - Math.floor(j * phi); // Weyl phase
        long offset = Math.round((j - baseSize / 2.0) * gap + w * gap);
        long idx = i0.longValue() + offset;
        if (idx < 2) continue;
        BigInteger x0 = scaledSqrt.toBigInteger();
        BigInteger x1 = x0.add(BigInteger.valueOf(scaledLocalWindow));
        BigInteger x = invertPiSecant(BigInteger.valueOf(idx), pi, x0, x1, secantIters);
        if (inThetaBand(x, sqrtN, thetaBands[v][0], thetaBands[v][1])
            && x.isProbablePrime(mrIters)) {
          merged.add(x);
        }
      }
    }

    // Collapse sentinel
    int totalBeforeDedup = baseSize * 3;
    double dedupRate = 1.0 - (double) merged.size() / totalBeforeDedup;
    BigInteger min = merged.stream().min(BigInteger::compareTo).orElse(BigInteger.ZERO);
    BigInteger max = merged.stream().max(BigInteger::compareTo).orElse(BigInteger.ZERO);
    BigInteger rangeWidth = max.subtract(min);
    long expectedGap = (long) (baseSize * gap / 5.0);
    if (dedupRate > 0.98 && rangeWidth.compareTo(BigInteger.valueOf(expectedGap)) < 0) {
      System.err.println(
          "WARNING: Variants collapsed—high dedup ("
              + String.format("%.2f%%", dedupRate * 100)
              + ") and narrow range ("
              + rangeWidth
              + " < "
              + expectedGap
              + "). Increase localWindow or diversify indices.");
    }

    // Convert to sorted list
    List<BigInteger> result = new ArrayList<>(merged);
    result.sort(null);
    return result;
  }

  private static boolean inThetaBand(
      BigInteger p, BigInteger sqrtN, double thetaMin, double thetaMax) {
    BigDecimal theta = thetaPrimeInt(new BigDecimal(p), new BigDecimal("0.3"));
    double t = theta.doubleValue();
    return t >= thetaMin && t < thetaMax;
  }

  // ======== E) Heuristic banding (BigInteger) ========

  /** Return candidate primes whose θ′ are within eps of θ′(N). */
  static List<BigInteger> heuristicBand(BigInteger N, Map<String, Object> ctx) {
    BigDecimal eps = (BigDecimal) ctx.getOrDefault("eps", new BigDecimal("0.05"));
    int maxCandidates = (Integer) ctx.getOrDefault("maxCandidates", 1000);
    BigDecimal k = (BigDecimal) ctx.getOrDefault("k", new BigDecimal("0.3"));

    @SuppressWarnings("unchecked")
    Map<BigInteger, BigDecimal> thetaPool = (Map<BigInteger, BigDecimal>) ctx.get("thetaPool");
    @SuppressWarnings("unchecked")
    List<BigInteger> pool = (List<BigInteger>) ctx.get("pool");

    BigDecimal thetaN = thetaPrimeInt(new BigDecimal(N), k);

    List<BigInteger> cands = new ArrayList<>();
    for (BigInteger p : pool) {
      if (circDist(thetaPool.get(p), thetaN).compareTo(eps) <= 0) {
        cands.add(p);
        if (cands.size() >= maxCandidates) break;
      }
    }
    if (cands.size() > maxCandidates) cands = cands.subList(0, maxCandidates);
    return cands;
  }

  // ======== F) Stats helpers ========

  static double[] wilsonCi(int successes, int n, double z) {
    if (n == 0) return new double[] {Double.NaN, Double.NaN, Double.NaN};
    double p = (double) successes / n;
    double z2 = z * z;
    double denom = 1.0 + z2 / n;
    double center = (p + z2 / (2.0 * n)) / denom;
    double half = z * Math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n))) / denom;
    double lo = Math.max(0.0, center - half);
    double hi = Math.min(1.0, center + half);
    return new double[] {p, lo, hi};
  }

  static double quantileInt(List<Integer> xs, double q) {
    if (xs.isEmpty()) return 0.0;
    List<Integer> s = new ArrayList<>(xs);
    Collections.sort(s);
    double pos = q * (s.size() - 1);
    int lo = (int) Math.floor(pos), hi = (int) Math.ceil(pos);
    if (lo == hi) return s.get(lo);
    double w = pos - lo;
    return s.get(lo) * (1 - w) + s.get(hi) * w;
  }

  // ======== Pollard's Rho ========

  public static BigInteger pollardRho(BigInteger n) {
    if (n.equals(BigInteger.ONE)) return n;
    if (n.mod(BigInteger.TWO).equals(BigInteger.ZERO)) return BigInteger.TWO;

    java.util.Random rand = new java.util.Random();
    for (int tries = 0; tries < 10; tries++) {
      BigInteger x =
          new BigInteger(n.bitLength(), rand).mod(n.subtract(BigInteger.TWO)).add(BigInteger.TWO);
      BigInteger y = x;
      BigInteger c =
          new BigInteger(n.bitLength(), rand).mod(n.subtract(BigInteger.ONE)).add(BigInteger.ONE);
      BigInteger d = BigInteger.ONE;

      int steps = 0;
      while (d.equals(BigInteger.ONE) && steps < 1000000) {
        x = x.modPow(BigInteger.TWO, n).add(c).mod(n);
        y = y.modPow(BigInteger.TWO, n).add(c).mod(n);
        y = y.modPow(BigInteger.TWO, n).add(c).mod(n);
        BigInteger diff = x.subtract(y).abs();
        d = diff.gcd(n);
        steps++;
      }
      if (!d.equals(BigInteger.ONE) && !d.equals(n)) return d;
    }
    return n; // failed
  }

  // ======== Factor single N ========

  public static Factor factorSingleN(BigInteger N) {
    // Check even
    if (!N.testBit(0)) {
      BigInteger q = N.shiftRight(1);
      return new Factor(BigInteger.TWO, q, q.isProbablePrime(64), true);
    }

    BigInteger r = sqrtFloor(N);
    if (r.multiply(r).equals(N) && r.isProbablePrime(64)) {
      return new Factor(r, r, true, true);
    }

    // Trial division with small primes
    List<BigInteger> smallPrimes = generateSmallPrimes(100000);
    for (BigInteger p : smallPrimes) {
      if (N.mod(p).equals(BigInteger.ZERO)) {
        BigInteger q = N.divide(p);
        return new Factor(p, q, q.isProbablePrime(64), true);
      }
    }

    // Use Pollard's Rho to find a factor
    BigInteger p = pollardRho(N);
    if (p.equals(N)) {
      return new Factor(BigInteger.ZERO, BigInteger.ZERO, false, false); // prime?
    }
    BigInteger q = N.divide(p);
    return new Factor(p, q, q.isProbablePrime(64), true);
  }

  private static List<BigInteger> generateSmallPrimes(int limit) {
    List<BigInteger> primes = new ArrayList<>();
    boolean[] isComposite = new boolean[limit + 1];
    for (int i = 2; i <= limit; i++) {
      if (!isComposite[i]) {
        primes.add(BigInteger.valueOf(i));
        for (int j = i * 2; j <= limit; j += i) {
          isComposite[j] = true;
        }
      }
    }
    return primes;
  }

  // ======== G) CLI / Main ========

  public static void main(String[] args) {
    // Defaults geared for a "meaningful" run; override via CLI flags below.
    BigInteger Nmax = new BigInteger("281474976710656"); // 2^48
    BigInteger singleN = null;
    int samples = 200_000;
    String mode = "balanced-lcg"; // only mode implemented at scale
    double bandLo = 0.85, bandHi = 0.98;
    int poolTarget = 120_000;
    BigDecimal kTheta = new BigDecimal("0.3");
    double epsVal = 0.03;
    int maxCandidates = 1000;
    long seed = 42L;
    int secantIters = 20, localWindow = 2048, mrIters = 64;
    int examples = 5;

    // Parse args
    for (int i = 0; i < args.length; i++) {
      switch (args[i]) {
        case "--Nmax":
          Nmax = new BigInteger(args[++i]);
          break;
        case "--Nmax-pow10":
          int pow = Integer.parseInt(args[++i]);
          Nmax = new BigInteger("1" + "0".repeat(Math.max(0, pow)));
          break;
        case "--samples":
          samples = Integer.parseInt(args[++i]);
          break;
        case "--mode":
          mode = args[++i];
          break;
        case "--band-lo":
          bandLo = Double.parseDouble(args[++i]);
          break;
        case "--band-hi":
          bandHi = Double.parseDouble(args[++i]);
          break;
        case "--pool-target":
          poolTarget = Integer.parseInt(args[++i]);
          break;
        case "--k":
          kTheta = new BigDecimal(args[++i], MC);
          break;
        case "--eps":
          epsVal = Double.parseDouble(args[++i]);
          break;
        case "--max-candidates":
          maxCandidates = Integer.parseInt(args[++i]);
          break;
        case "--seed":
          seed = Long.parseLong(args[++i]);
          break;
        case "--secant-iters":
          secantIters = Integer.parseInt(args[++i]);
          break;
        case "--local-window":
          localWindow = Integer.parseInt(args[++i]);
          break;
        case "--mr-iters":
          mrIters = Integer.parseInt(args[++i]);
          break;
        case "--examples":
          examples = Integer.parseInt(args[++i]);
          break;
        case "--factor-single":
          singleN = new BigInteger(args[++i]);
          break;
        default:
          System.err.println("Unknown arg: " + args[i]);
      }
    }

    if (singleN != null) {
      Factor res = factorSingleN(singleN);
      if (res.success()) {
        System.out.println("N=" + singleN + " = " + res.p() + " * " + res.q());
        if (res.qPrime()) {
          System.out.println("q is prime");
        } else {
          System.out.println("q is composite");
        }
      } else {
        System.out.println("Failed to factor " + singleN);
      }
      return;
    }

    // Build π oracle (prefers BigDecimal Z5dPredictorBD if present)
    PiOracle pi = buildPiOracle();

    // Build Z5D-only prime pool near sqrt(Nmax)
    List<BigInteger> pool =
        generatePrimePoolBandZ5D(
            Nmax, bandLo, bandHi, poolTarget, pi, secantIters, localWindow, mrIters);

    // primesSmall up to sqrt(Nmax) (for trial/fast checks if desired)
    BigInteger sqrt = sqrtFloor(Nmax);
    final BigInteger finalSqrt = sqrt;
    List<BigInteger> primesSmall =
        pool.stream()
            .filter(p -> p.multiply(p).compareTo(finalSqrt) <= 0)
            .collect(Collectors.toList());

    // Precompute theta for pool
    Map<BigInteger, BigDecimal> thetaPool = new HashMap<>(pool.size() * 2);
    for (BigInteger p : pool) {
      thetaPool.put(p, thetaPrimeInt(new BigDecimal(p), kTheta));
    }

    // Sample semiprimes uniformly without replacement
    List<BigInteger[]> semis;
    if ("balanced-lcg".equals(mode)) {
      semis = sampleSemiprimesBalancedLCG(pool, samples, Nmax, seed);
    } else {
      throw new IllegalArgumentException("Unsupported mode at scale: " + mode);
    }

    // Examples
    System.out.println("\n=== Factorization Shortcut Examples (BigInteger/Z5D-only) ===");
    int printed = 0;
    for (BigInteger[] semi : semis) {
      BigInteger p = semi[0], q = semi[1], N = semi[2];

      List<BigInteger> cands =
          heuristicBand(
              N,
              Map.of(
                  "eps", new BigDecimal(epsVal, MC),
                  "maxCandidates", maxCandidates,
                  "k", kTheta,
                  "thetaPool", thetaPool,
                  "pool", pool));
      Factor res = factorizeWithCandidatesBig(N, cands, mrIters);
      if (res.success()) {
        System.out.println(
            "N="
                + N
                + " -> recovered p="
                + res.p()
                + "; q=N/p="
                + res.q()
                + "; q is prime? "
                + res.qPrime()
                + "; candidates="
                + cands.size());
        printed++;
        if (printed >= examples) break;
      }
    }

    // Aggregate
    double[] epsSweep = new double[] {epsVal, Math.max(1e-4, epsVal * 0.75), epsVal * 1.25};
    for (double eps : epsSweep) {
      int partial = 0;
      int full = 0;
      List<Integer> candSizes = new ArrayList<>(semis.size());
      for (BigInteger[] semi : semis) {
        BigInteger p = semi[0], q = semi[1], N = semi[2];
        List<BigInteger> cands =
            heuristicBand(
                N,
                Map.of(
                    "eps", new BigDecimal(eps, MC),
                    "maxCandidates", maxCandidates,
                    "k", kTheta,
                    "thetaPool", thetaPool,
                    "pool", pool));
        candSizes.add(cands.size());
        Factor res = factorizeWithCandidatesBig(N, cands, mrIters);
        if (res.success()) partial++;
        if (cands.contains(p) && cands.contains(q)) full++;
      }
      double[] ci = wilsonCi(partial, samples, 1.96);
      double avg = candSizes.stream().mapToInt(Integer::intValue).average().orElse(0);
      double p50 = quantileInt(candSizes, 0.50);
      double p90 = quantileInt(candSizes, 0.90);
      double p99 = quantileInt(candSizes, 0.99);
      System.out.println(
          String.format(
              Locale.ROOT,
              "eps=%.5f: partial=%.4f [%.4f, %.4f]; full=%d/%d; cand avg=%.1f | p50=%.0f p90=%.0f p99=%.0f | pool=%d",
              eps,
              ci[0],
              ci[1],
              ci[2],
              full,
              samples,
              avg,
              p50,
              p90,
              p99,
              pool.size()));
    }
  }

  // ======== H) Backward-compatibility shims (small-scale only) ========
  /**
   * Legacy API: small-scale balanced sampler returning List<long[]>. Converts to BigInteger
   * pipeline and back. For large N, prefer sampleSemiprimesBalancedLCG(...).
   */
  public static List<long[]> sampleSemiprimesBalanced(
      List<Integer> primes, int targetCount, long Nmax, long seed) {
    List<BigInteger> P = new ArrayList<>();
    for (int v : primes) P.add(BigInteger.valueOf(v));
    List<BigInteger[]> big =
        sampleSemiprimesBalancedLCG(P, targetCount, BigInteger.valueOf(Nmax), seed);
    List<long[]> out = new ArrayList<>(big.size());
    for (BigInteger[] t : big) {
      long p = t[0].longValueExact(); // safe only if values fit in long
      long q = t[1].longValueExact();
      long N = t[2].longValueExact();
      out.add(new long[] {p, q, N});
    }
    return out;
  }

  /**
   * Legacy API: small-scale factorization using candidates (long-based result). Wraps the
   * BigInteger version. "primesSmall" parameter is ignored here.
   */
  public static long[] factorizeWithCandidates(
      long N, List<Integer> candidates, List<Integer> primesSmall) {
    List<BigInteger> cands = new ArrayList<>(candidates.size());
    for (int v : candidates) cands.add(BigInteger.valueOf(v));
    Factor f = factorizeWithCandidatesBig(BigInteger.valueOf(N), cands, 64);
    if (!f.success()) return new long[] {0, 0, 0, 0};
    long p = f.p().longValueExact();
    long q = f.q().longValueExact();
    return new long[] {1, p, q, f.qPrime() ? 1 : 0};
  }
}
