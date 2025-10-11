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

  static BigDecimal frac(BigDecimal x) {
    return x.subtract(x.setScale(0, RoundingMode.FLOOR));
  }

  static BigDecimal thetaPrimeInt(BigDecimal n, BigDecimal k) {
    BigDecimal nModPhi = n.remainder(PHI);
    BigDecimal x = nModPhi.divide(PHI, MC);
    // Use double for pow since BigDecimal pow is integer
    double xDouble = x.doubleValue();
    double kDouble = k.doubleValue();
    double valDouble = PHI.doubleValue() * Math.pow(xDouble, kDouble);
    BigDecimal val = BigDecimal.valueOf(valDouble);
    return frac(val);
  }

  static BigDecimal circDist(BigDecimal a, BigDecimal b) {
    BigDecimal diff = a.subtract(b, MC);
    BigDecimal shifted = diff.add(BigDecimal.valueOf(0.5), MC);
    BigDecimal mod = shifted.remainder(BigDecimal.ONE, MC);
    BigDecimal d = mod.subtract(BigDecimal.valueOf(0.5), MC);
    return d.abs(MC);
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

  static List<long[]> sampleSemiprimesBalanced(
      List<Integer> primes, int targetCount, long Nmax, long seed) {
    Random rand = new Random(seed);
    List<long[]> out = new ArrayList<>();
    long sqrtNmax = (long) Math.sqrt(Nmax);
    long bandLo = Math.max(2, sqrtNmax / 2);
    long bandHi = Math.max(bandLo + 1, sqrtNmax * 2);
    List<Integer> primesBal =
        primes.stream().filter(p -> p >= bandLo && p <= bandHi).collect(Collectors.toList());
    if (primesBal.isEmpty()) {
      throw new IllegalArgumentException("No primes in balanced band; increase Nmax.");
    }
    while (out.size() < targetCount) {
      int p = primesBal.get(rand.nextInt(primesBal.size()));
      int q = primesBal.get(rand.nextInt(primesBal.size()));
      if (p > q) {
        int temp = p;
        p = q;
        q = temp;
      }
      long N = (long) p * q;
      if (N < Nmax) {
        out.add(new long[] {p, q, N});
      }
    }
    return out;
  }

  static List<long[]> sampleSemiprimesUnbalanced(
      List<Integer> primes, int targetCount, long Nmax, long seed) {
    Random rand = new Random(seed);
    List<long[]> out = new ArrayList<>();
    long sqrtNmax = (long) Math.sqrt(Nmax);
    long smallHi = Math.max(7, sqrtNmax / 5);
    long largeHi = sqrtNmax * 3;
    List<Integer> primesSmall =
        primes.stream().filter(p -> p >= 2 && p <= smallHi).collect(Collectors.toList());
    List<Integer> primesLarge =
        primes.stream().filter(p -> p > smallHi && p <= largeHi).collect(Collectors.toList());
    if (primesSmall.isEmpty() || primesLarge.isEmpty()) {
      throw new IllegalArgumentException("Insufficient primes for unbalanced sampling.");
    }
    while (out.size() < targetCount) {
      int p = primesSmall.get(rand.nextInt(primesSmall.size()));
      int q = primesLarge.get(rand.nextInt(primesLarge.size()));
      if (p > q) {
        int temp = p;
        p = q;
        q = temp;
      }
      long N = (long) p * q;
      if (N < Nmax) {
        out.add(new long[] {p, q, N});
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

  static double[] wilsonCi(int successes, int n, double z) {
    if (n == 0) return new double[] {Double.NaN, Double.NaN, Double.NaN};
    double p = (double) successes / n;
    double denom = 1.0 + (z * z) / n;
    double center = (p + (z * z) / (2 * n)) / denom;
    double half = z * Math.sqrt((p * (1 - p) / n) + (z * z) / (4 * n * n)) / denom;
    return new double[] {p, Math.max(0.0, center - half), Math.min(1.0, center + half)};
  }

  static long[] factorizeWithCandidates(
      long N, List<Integer> candidates, List<Integer> primesSmall) {
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
