package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Factorization Shortcut Demo using Z5D for prime generation.
 * Ports the Python semiprime factorization demo, replacing sieve with Z5D-based prime estimation.
 * Uses BigDecimal for high-precision calculations consistent with Z5dPredictor.
 */
public class FactorizationShortcutDemo {

  private static final BigDecimal PHI = BigDecimal.valueOf(1).add(BigDecimal.valueOf(5).sqrt(MathContext.DECIMAL128)).divide(BigDecimal.valueOf(2), MathContext.DECIMAL128);
  private static final BigDecimal K_DEFAULT = BigDecimal.valueOf(0.3);
  private static final MathContext MC = MathContext.DECIMAL128;

  // Z5D-based prime generation
  static List<Integer> generatePrimesZ5D(int limit) {
    List<Integer> primes = new ArrayList<>();
    double piLimit = Z5dPredictor.z5dPrime(limit, 0, 0, 0, true);
    int maxK = (int) Math.ceil(piLimit);
    for (int k = 1; k <= maxK; k++) {
      long n = findNForPiK(k);
      if (n > limit) break;
      BigInteger candidate = BigInteger.valueOf(n);
      if (candidate.isProbablePrime(100)) {
        primes.add((int) n);
      }
    }
    return primes;
  }

  private static long findNForPiK(int k) {
    // Binary search for the smallest n where π(n) >= k
    long low = 2;
    long high = 1000000; // sufficient for k up to ~78k
    while (low < high) {
      long mid = (low + high) / 2;
      double pi = Z5dPredictor.z5dPrime(mid, 0, 0, 0, true);
      if (pi < k) {
        low = mid + 1;
      } else {
        high = mid;
      }
    }
    return low;
  }

  // === Utilities ===
  static BigDecimal frac01(BigDecimal x) {
    // Euclidean fractional part in [0,1)
    BigDecimal flo = x.setScale(0, RoundingMode.FLOOR);
    BigDecimal r = x.subtract(flo, MC);
    // Guard against 0.999999999999... due to doubles later:
    if (r.signum() < 0) r = r.add(BigDecimal.ONE, MC);
    if (r.compareTo(BigDecimal.ONE) >= 0) r = r.subtract(BigDecimal.ONE, MC);
    return r;
  }

  static BigDecimal circDist(BigDecimal a, BigDecimal b) {
    // d = | ((a - b + 0.5) mod 1) - 0.5 |  in [0, 0.5]
    BigDecimal s = a.subtract(b, MC).add(new BigDecimal("0.5"), MC);
    BigDecimal m = frac01(s);
    BigDecimal d = m.subtract(new BigDecimal("0.5"), MC).abs(MC);
    return d;
  }

  static BigDecimal thetaPrimeInt(BigDecimal n, BigDecimal k) {
    // θ'(n,k) = frac( PHI * ( frac(n/PHI) )^k )
    BigDecimal x = frac01(n.divide(PHI, MC));
    double xd = x.doubleValue();
    double kd = k.doubleValue();
    BigDecimal val = BigDecimal.valueOf(PHI.doubleValue() * Math.pow(xd, kd));
    return frac01(val);
  }

  static boolean isPrimeTrial(long n, List<Integer> primesSmall) {
    if (n < 2) return false;
    long r = (long) Math.sqrt(n);
    for (int p : primesSmall) {
      if ((long) p > r) break;
      if (n % p == 0) return n == p;
    }
    return true;
  }

  // === Balanced sampler: uniform over unique (p<=q, p*q<Nmax), without replacement ===
  static List<long[]> sampleSemiprimesBalanced(List<Integer> primes, int targetCount, long Nmax, long seed) {
    List<long[]> pairs = new ArrayList<>();
    int m = primes.size();
    for (int i = 0; i < m; i++) {
      long p = primes.get(i);
      for (int j = i; j < m; j++) {
        long q = primes.get(j);
        long N = p * q;
        if (N < Nmax) pairs.add(new long[] {p, q, N});
        else break; // primes are increasing; further q will only grow
      }
    }
    if (pairs.isEmpty()) throw new IllegalArgumentException("No valid (p,q) pairs under Nmax.");
    Random rng = new Random(seed);
    List<long[]> out = new ArrayList<>(targetCount);

    // Keep shuffling & emitting until targetCount reached (no duplicates before exhaustion)
    List<long[]> bag = new ArrayList<>(pairs);
    while (out.size() < targetCount) {
      Collections.shuffle(bag, rng);
      for (long[] t : bag) {
        out.add(t);
        if (out.size() >= targetCount) break;
      }
    }
    return out;
  }

  // === Unbalanced sampler: p small, q large, still no replacement until exhaustion ===
  static List<long[]> sampleSemiprimesUnbalanced(List<Integer> primes, int targetCount, long Nmax, long seed) {
    long sqrtN = (long) Math.sqrt(Nmax);
    long smallHi = Math.max(7, sqrtN / 5);
    long largeHi = sqrtN * 3;

    List<Integer> primesSmall = primes.stream().filter(p -> p >= 2 && p <= smallHi).collect(Collectors.toList());
    List<Integer> primesLarge = primes.stream().filter(p -> p > smallHi && p <= largeHi).collect(Collectors.toList());
    if (primesSmall.isEmpty() || primesLarge.isEmpty())
      throw new IllegalArgumentException("Insufficient primes for unbalanced sampling.");

    // Build unique candidate set S = {(p,q): p small, q large, p<=q, p*q<Nmax}
    List<long[]> pairs = new ArrayList<>();
    for (int p : primesSmall) {
      for (int q : primesLarge) {
        int pp = Math.min(p, q), qq = Math.max(p, q);
        long N = 1L * pp * qq;
        if (N < Nmax) pairs.add(new long[] {pp, qq, N});
      }
    }
    if (pairs.isEmpty()) throw new IllegalArgumentException("No valid unbalanced pairs under Nmax.");
    Random rng = new Random(seed);
    List<long[]> out = new ArrayList<>(targetCount);
    List<long[]> bag = new ArrayList<>(pairs);

    while (out.size() < targetCount) {
      Collections.shuffle(bag, rng);
      for (long[] t : bag) {
        out.add(t);
        if (out.size() >= targetCount) break;
      }
    }
    return out;
  }

  static List<Integer> heuristicBand(long N, Map<String, Object> ctx) {
    BigDecimal eps = BigDecimal.valueOf((Double) ctx.getOrDefault("eps", 0.05));
    int maxCandidates = (Integer) ctx.getOrDefault("maxCandidates", 1000);
    BigDecimal k = (BigDecimal) ctx.getOrDefault("k", K_DEFAULT);
    @SuppressWarnings("unchecked")
    Map<Integer, BigDecimal> thetaPool = (Map<Integer, BigDecimal>) ctx.get("thetaPool");
    @SuppressWarnings("unchecked")
    List<Integer> pool = (List<Integer>) ctx.get("pool");
    BigDecimal thetaN = thetaPrimeInt(BigDecimal.valueOf(N), k);
    List<Integer> cands = new ArrayList<>();
    for (int p : pool) {
      if (circDist(thetaPool.get(p), thetaN).compareTo(eps) <= 0) {
        cands.add(p);
      }
    }
    if (cands.size() > maxCandidates) {
      cands.sort(Comparator.comparing(p -> circDist(thetaPool.get(p), thetaN)));
      cands = cands.subList(0, maxCandidates);
    }
    return cands;
  }

    // === Wilson CI (clamped) ===
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

  // === Factorization (add fast paths) ===
  static long[] factorizeWithCandidates(
      long N, List<Integer> candidates, List<Integer> primesSmall) {
    if ((N & 1L) == 0L) {
      long q = N / 2L;
      return new long[] {1, 2L, q, isPrimeTrial(q, primesSmall) ? 1 : 0};
    }
    long r = (long) Math.sqrt(N);
    if (r * r == N && isPrimeTrial(r, primesSmall)) {
      return new long[] {1, r, r, 1};
    }
    for (int p : candidates) {
      if (p > 1 && N % p == 0) {
        long q = N / p;
        boolean qPrime = isPrimeTrial(q, primesSmall);
        return new long[] {1, p, q, qPrime ? 1 : 0};
      }
    }
    return new long[] {0, 0, 0, 0};
  }

  public static void main(String[] args) {
    // Simple CLI parsing
    long Nmax = 1000000;
    int samples = 100;
    String mode = "balanced";
    double[] epsValues = {0.02, 0.03, 0.04, 0.05};
    BigDecimal k = K_DEFAULT;
    int maxCandidates = 1000;
    long seed = 42;

    // Parse args if provided
    for (int i = 0; i < args.length; i++) {
      switch (args[i]) {
        case "--Nmax":
          Nmax = Long.parseLong(args[++i]);
          break;
        case "--samples":
          samples = Integer.parseInt(args[++i]);
          break;
        case "--mode":
          mode = args[++i];
          break;
        case "--eps": // simple, take first
          epsValues = new double[] {Double.parseDouble(args[++i])};
          break;
        case "--k":
          k = BigDecimal.valueOf(Double.parseDouble(args[++i]));
          break;
        case "--max-candidates":
          maxCandidates = Integer.parseInt(args[++i]);
          break;
        case "--seed":
          seed = Long.parseLong(args[++i]);
          break;
      }
    }

    // Generate primes using Z5D
    int limit = Math.max(100, 3 * (int) Math.sqrt(Nmax) + 100);
    List<Integer> pool = generatePrimesZ5D(limit);
    final long finalNmax = Nmax;
    List<Integer> primesSmall =
        pool.stream().filter(p -> (long) p * p <= finalNmax).collect(Collectors.toList());

    // Sample semiprimes
    List<long[]> semis;
    if ("balanced".equals(mode)) {
      semis = sampleSemiprimesBalanced(pool, samples, Nmax, seed);
    } else {
      semis = sampleSemiprimesUnbalanced(pool, samples, Nmax, seed);
    }

    // Theta pool
    Map<Integer, BigDecimal> thetaPool = new HashMap<>();
    for (int p : pool) {
      thetaPool.put(p, thetaPrimeInt(BigDecimal.valueOf(p), k));
    }

    int examples = 5;

    // Evaluate
    System.out.println("\n=== Factorization Shortcut Examples ===");
    int printed = 0;
    for (long[] semi : semis) {
      long p = semi[0], q = semi[1], N = semi[2];
      List<Integer> cands =
          heuristicBand(
              N,
              Map.of(
                  "eps",
                  0.05,
                  "maxCandidates",
                  maxCandidates,
                  "k",
                  k,
                  "thetaPool",
                  thetaPool,
                  "pool",
                  pool));
      long[] res = factorizeWithCandidates(N, cands, primesSmall);
      if (res[0] == 1) {
        System.out.println(
            "N="
                + N
                + " -> recovered p="
                + res[1]
                + "; shortcut q=N//p="
                + res[2]
                + "; q is prime? "
                + (res[3] == 1)
                + "; candidates="
                + cands.size());
        printed++;
        if (printed >= examples) break;
      }
    }

    // Aggregate
    for (double eps : epsValues) {
      int partial = 0;
      int full = 0;
      List<Integer> candSizes = new ArrayList<>();
      for (long[] semi : semis) {
        long p = semi[0], q = semi[1], N = semi[2];
        List<Integer> cands =
            heuristicBand(
                N,
                Map.of(
                    "eps",
                    eps,
                    "maxCandidates",
                    maxCandidates,
                    "k",
                    k,
                    "thetaPool",
                    thetaPool,
                    "pool",
                    pool));
        candSizes.add(cands.size());
        long[] res = factorizeWithCandidates(N, cands, primesSmall);
        if (res[0] == 1) partial++;
        if (cands.contains((int) p) && cands.contains((int) q)) full++;
      }
      double[] ci = wilsonCi(partial, samples, 1.96);
      double avgCand = candSizes.stream().mapToInt(Integer::intValue).average().orElse(0);
      System.out.println(
          "eps="
              + eps
              + ": partial_rate="
              + String.format("%.4f", ci[0])
              + " ["
              + String.format("%.4f", ci[1])
              + ", "
              + String.format("%.4f", ci[2])
              + "]; avg_candidates="
              + String.format("%.1f", avgCand));
    }
  }
}
