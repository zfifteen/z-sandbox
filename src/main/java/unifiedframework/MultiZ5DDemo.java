package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Demonstration of the multi-variant Z5D pool generator.
 *
 * <p>This class demonstrates the usage of multiZ5DPool with realistic parameters as specified in
 * the requirements: - Z5D-A: Baseline variant (theta band 0.05-1.5, epsilon 0.1) - 30k primes -
 * Z5D-B: Low-band variant (theta band 0.02-0.6, epsilon 0.05) - 30k primes - Z-X: High-band variant
 * (theta band 1.0-3.0, epsilon 0.2) - 30k primes - Total: ~80k unique candidates after
 * deduplication
 */
public class MultiZ5DDemo {

  public static void main(String[] args) {
    System.out.println("=".repeat(70));
    System.out.println("Multi-Variant Z5D Pool Generator Demonstration");
    System.out.println("=".repeat(70));
    System.out.println();

    // Parse arguments or use defaults
    String nmaxStr = args.length > 0 ? args[0] : "100000000000000000"; // 10^17
    int baseSize = args.length > 1 ? Integer.parseInt(args[1]) : 30000;
    boolean runFullDemo = args.length > 2 && args[2].equals("--full");

    BigInteger Nmax = new BigInteger(nmaxStr);
    BigInteger sqrtNmax = FactorizationShortcut.sqrtFloor(Nmax);

    System.out.println("Configuration:");
    System.out.printf("  Nmax: %s (%.2e)%n", Nmax, Nmax.doubleValue());
    System.out.printf("  sqrt(Nmax): %s (%.2e)%n", sqrtNmax, sqrtNmax.doubleValue());
    System.out.printf("  Base size per variant: %d%n", baseSize);
    System.out.printf("  Expected total (with dedup): ~%d%n", baseSize * 3);
    System.out.println();

    // Build the PiOracle
    System.out.println("Building Z5D π(x) oracle...");
    FactorizationShortcut.PiOracle pi = FactorizationShortcut.buildPiOracle();
    System.out.println("✓ Oracle ready");
    System.out.println();

    // Generate multi-variant pool
    System.out.println("Generating multi-variant Z5D pool...");
    System.out.println("  Variant Z5D-A: theta band [0.05, 1.5], target " + baseSize + " primes");
    System.out.println("  Variant Z5D-B: theta band [0.02, 0.6], target " + baseSize + " primes");
    System.out.println("  Variant Z-X:   theta band [1.0, 3.0], target " + baseSize + " primes");
    System.out.println();

    long startTime = System.currentTimeMillis();
    List<BigInteger> pool =
        FactorizationShortcut.multiZ5DPool(
            Nmax,
            baseSize,
            pi,
            20, // secantIters
            2048, // localWindow
            64 // mrIters
            );
    long endTime = System.currentTimeMillis();
    long generationTime = endTime - startTime;

    System.out.printf("✓ Pool generated in %.2f seconds%n", generationTime / 1000.0);
    System.out.println();

    // Analyze the pool
    System.out.println("Pool Statistics:");
    System.out.printf("  Total candidates: %d%n", pool.size());
    System.out.printf(
        "  Deduplication rate: %.2f%%%n", 100.0 * (1.0 - pool.size() / (double) (baseSize * 3)));

    // Check primality
    int primeCount = 0;
    for (BigInteger p : pool) {
      if (p.isProbablePrime(64)) primeCount++;
    }
    System.out.printf(
        "  Probable primes: %d / %d (%.2f%%)%n",
        primeCount, pool.size(), 100.0 * primeCount / pool.size());

    // Range statistics
    BigInteger minCandidate = pool.get(0);
    BigInteger maxCandidate = pool.get(pool.size() - 1);
    System.out.printf("  Candidate range: [%s, %s]%n", minCandidate, maxCandidate);

    BigDecimal minRatio =
        new BigDecimal(minCandidate)
            .divide(new BigDecimal(sqrtNmax), java.math.MathContext.DECIMAL128);
    BigDecimal maxRatio =
        new BigDecimal(maxCandidate)
            .divide(new BigDecimal(sqrtNmax), java.math.MathContext.DECIMAL128);
    System.out.printf(
        "  Ratio to sqrt(Nmax): [%.3f, %.3f]%n", minRatio.doubleValue(), maxRatio.doubleValue());
    System.out.println();

    if (runFullDemo) {
      // Compute theta distribution
      System.out.println("Computing theta distribution...");
      BigDecimal k = new BigDecimal("0.3");
      Map<BigInteger, BigDecimal> thetaMap = new HashMap<>();
      for (BigInteger p : pool) {
        BigDecimal theta = FactorizationShortcut.thetaPrimeInt(new BigDecimal(p), k);
        thetaMap.put(p, theta);
      }

      // Theta histogram
      int bins = 20;
      int[] thetaHistogram = new int[bins];
      for (BigDecimal theta : thetaMap.values()) {
        int bin = Math.min(bins - 1, (int) (theta.doubleValue() * bins));
        thetaHistogram[bin]++;
      }

      System.out.println("Theta distribution (20 bins, k=0.3):");
      int maxCount = 0;
      for (int c : thetaHistogram) {
        maxCount = Math.max(maxCount, c);
      }
      for (int i = 0; i < bins; i++) {
        double lo = i / (double) bins;
        double hi = (i + 1) / (double) bins;
        int count = thetaHistogram[i];
        int barLength = maxCount > 0 ? (count * 50 / maxCount) : 0;
        String bar = "█".repeat(Math.min(50, barLength));
        System.out.printf("  [%.2f, %.2f): %5d %s%n", lo, hi, count, bar);
      }
      System.out.println();

      // Test coverage with sample semiprimes
      System.out.println("Testing theta banding coverage...");
      int numSamples = Math.min(1000, pool.size() * pool.size() / 1000);
      System.out.printf("  Sampling %d semiprimes from pool%n", numSamples);

      List<BigInteger[]> testSemiprimes =
          FactorizationShortcut.sampleSemiprimesBalancedLCG(pool, numSamples, Nmax, 42L);

      // Test with different epsilon values
      for (double epsVal : new double[] {0.05, 0.1, 0.15, 0.2}) {
        BigDecimal eps = new BigDecimal(epsVal);
        int covered = 0;

        for (BigInteger[] semi : testSemiprimes) {
          BigInteger p = semi[0];
          BigInteger q = semi[1];
          BigInteger N = semi[2];

          BigDecimal thetaN = FactorizationShortcut.thetaPrimeInt(new BigDecimal(N), k);
          BigDecimal thetaP = thetaMap.get(p);
          BigDecimal thetaQ = thetaMap.get(q);

          if (thetaP != null && thetaQ != null) {
            BigDecimal distP = FactorizationShortcut.circDist(thetaP, thetaN);
            BigDecimal distQ = FactorizationShortcut.circDist(thetaQ, thetaN);

            if (distP.compareTo(eps) <= 0 || distQ.compareTo(eps) <= 0) {
              covered++;
            }
          }
        }

        double coverage = 100.0 * covered / testSemiprimes.size();
        System.out.printf(
            "  Epsilon %.2f: %d / %d (%.2f%% coverage)%n",
            epsVal, covered, testSemiprimes.size(), coverage);
      }
      System.out.println();
    }

    System.out.println("Summary:");
    System.out.println("  ✓ Multi-variant Z5D pool successfully generated");
    System.out.println("  ✓ All three variants (Z5D-A, Z5D-B, Z-X) combined");
    System.out.println("  ✓ Candidates deduplicated and sorted");
    System.out.printf("  ✓ Total generation time: %.2f seconds%n", generationTime / 1000.0);
    System.out.println();
    System.out.println("Usage:");
    System.out.println("  Default: java unifiedframework.MultiZ5DDemo");
    System.out.println("  Custom:  java unifiedframework.MultiZ5DDemo <Nmax> <baseSize> [--full]");
    System.out.println();
  }
}
