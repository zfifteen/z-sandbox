package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class TestFactorizationShortcut {

  @BeforeAll
  static void printSystemInfo() {
    System.out.println("==========================================");
    System.out.println("   Test Environment Configuration");
    System.out.println("==========================================");

    // OS and Java Info
    System.out.printf(
        "OS: %s %s (%s)%n",
        System.getProperty("os.name"),
        System.getProperty("os.version"),
        System.getProperty("os.arch"));
    System.out.printf("Java Version: %s%n", System.getProperty("java.version"));
    System.out.printf("Java Vendor: %s%n", System.getProperty("java.vendor"));
    System.out.printf("JVM: %s%n", System.getProperty("java.vm.name"));

    // Hardware Info
    String cpuModel = getSystemCommandOutput("sysctl", "-n", "machdep.cpu.brand_string");
    String totalRam = getSystemCommandOutput("sysctl", "-n", "hw.memsize");
    long totalRamBytes = totalRam.isEmpty() ? 0 : Long.parseLong(totalRam.trim());
    double totalRamGB = totalRamBytes / (1024.0 * 1024.0 * 1024.0);

    Runtime runtime = Runtime.getRuntime();
    int availableProcessors = runtime.availableProcessors();
    long jvmTotalMemory = runtime.totalMemory();
    long jvmFreeMemory = runtime.freeMemory();
    long jvmMaxMemory = runtime.maxMemory();

    System.out.printf("CPU Model: %s%n", cpuModel.isEmpty() ? "Unknown" : cpuModel.trim());
    System.out.printf("Total RAM: %.2f GB%n", totalRamGB);
    System.out.printf("Logical Cores: %d%n", availableProcessors);
    System.out.printf("JVM Total Memory: %.2f MB%n", jvmTotalMemory / (1024.0 * 1024.0));
    System.out.printf("JVM Free Memory: %.2f MB%n", jvmFreeMemory / (1024.0 * 1024.0));
    System.out.printf("JVM Max Memory: %.2f MB%n", jvmMaxMemory / (1024.0 * 1024.0));
    System.out.printf(
        "JVM Used Memory: %.2f MB%n", (jvmTotalMemory - jvmFreeMemory) / (1024.0 * 1024.0));

    System.out.println("==========================================");
    System.out.println();
  }

  private static String getSystemCommandOutput(String... command) {
    try {
      ProcessBuilder pb = new ProcessBuilder(command);
      Process p = pb.start();
      BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
      String line = reader.readLine();
      p.waitFor();
      return line != null ? line : "";
    } catch (Exception e) {
      return "";
    }
  }

  @Test
  public void testThetaPrimeInt() {
    System.out.println("Testing thetaPrimeInt functionality");
    BigDecimal n = BigDecimal.valueOf(100);
    BigDecimal k = BigDecimal.valueOf(0.3);
    BigDecimal theta = FactorizationShortcut.thetaPrimeInt(n, k);

    System.out.printf("Input n: %s%n", n);
    System.out.printf("Input k: %s%n", k);
    System.out.printf("Result theta: %s%n", theta);
    System.out.printf(
        "Is in [0,1): %b%n",
        theta.compareTo(BigDecimal.ZERO) >= 0 && theta.compareTo(BigDecimal.ONE) < 0);

    assertTrue(theta.compareTo(BigDecimal.ZERO) >= 0 && theta.compareTo(BigDecimal.ONE) < 0);
  }

  @Test
  public void testSampleSemiprimesBalanced() {
    System.out.println("Testing sampleSemiprimesBalanced functionality");
    List<Integer> primes = List.of(2, 3, 5, 7, 11, 13, 17, 19);
    int targetCount = 10;
    long Nmax = 1000;
    long seed = 42;
    List<long[]> semis =
        FactorizationShortcut.sampleSemiprimesBalanced(primes, targetCount, Nmax, seed);

    System.out.printf("Input primes: %s%n", primes);
    System.out.printf("Target count: %d%n", targetCount);
    System.out.printf("Nmax: %d%n", Nmax);
    System.out.printf("Seed: %d%n", seed);
    System.out.printf("Generated semiprimes count: %d%n", semis.size());
    for (int i = 0; i < semis.size(); i++) {
      long[] s = semis.get(i);
      System.out.printf(
          "Semiprime %d: p=%d, q=%d, N=%d, N < Nmax: %b, p*q==N: %b%n",
          i + 1, s[0], s[1], s[2], s[2] < Nmax, s[0] * s[1] == s[2]);
    }

    assertEquals(10, semis.size());
    for (long[] s : semis) {
      assertTrue(s[2] < 1000);
      assertTrue(s[0] * s[1] == s[2]);
    }
  }

  @Test
  public void testWilsonCi() {
    System.out.println("Testing wilsonCi functionality");
    int successes = 50;
    int n = 100;
    double z = 1.96;
    double[] ci = FactorizationShortcut.wilsonCi(successes, n, z);

    System.out.printf("Input successes: %d%n", successes);
    System.out.printf("Input n: %d%n", n);
    System.out.printf("Input z: %.2f%n", z);
    System.out.printf("Result CI: [%.4f, %.4f, %.4f]%n", ci[0], ci[1], ci[2]);
    System.out.printf("Center == 0.5: %b%n", ci[0] == 0.5);
    System.out.printf("Lower < Center < Upper: %b%n", ci[1] < ci[0] && ci[0] < ci[2]);

    assertTrue(ci[0] == 0.5);
    assertTrue(ci[1] < ci[0] && ci[0] < ci[2]);
  }

  @Test
  public void testFactorizeWithCandidates() {
    System.out.println("Testing factorizeWithCandidates functionality");
    long N = 6;
    List<Integer> cands = List.of(2, 3);
    List<Integer> primesSmall = List.of(2, 3, 5, 7);
    long[] res = FactorizationShortcut.factorizeWithCandidates(N, cands, primesSmall);

    System.out.printf("Input N: %d%n", N);
    System.out.printf("Input candidates: %s%n", cands);
    System.out.printf("Input primesSmall: %s%n", primesSmall);
    System.out.printf(
        "Result: success=%d, p=%d, q=%d, q_prime=%d%n", res[0], res[1], res[2], res[3]);
    System.out.printf("Success: %b%n", res[0] == 1);
    System.out.printf("p correct: %b%n", res[1] == 2);
    System.out.printf("q correct: %b%n", res[2] == 3);
    System.out.printf("q is prime: %b%n", res[3] == 1);

    assertEquals(1, res[0]); // success
    assertEquals(2, res[1]); // p
    assertEquals(3, res[2]); // q
    assertEquals(1, res[3]); // q prime
  }

  @Test
  public void testMultiZ5DPool() {
    System.out.println("Testing multiZ5DPool functionality");
    
    // Use a smaller Nmax for faster testing
    BigInteger Nmax = new BigInteger("10000000000000000"); // 10^16 for better band separation
    int baseSize = 50; // Smaller size for testing (instead of 30k)
    
    // Build the PiOracle
    FactorizationShortcut.PiOracle pi = FactorizationShortcut.buildPiOracle();
    
    System.out.printf("Input Nmax: %s%n", Nmax);
    System.out.printf("Base size per variant: %d%n", baseSize);
    System.out.printf("Expected total candidates: ~%d (with deduplication)%n", baseSize * 3);
    
    // Generate multi-variant pool
    long startTime = System.currentTimeMillis();
    List<BigInteger> pool = FactorizationShortcut.multiZ5DPool(
        Nmax,
        baseSize,
        pi,
        20,    // secantIters
        2048,  // localWindow
        64     // mrIters
    );
    long endTime = System.currentTimeMillis();
    
    System.out.printf("Generated pool size: %d%n", pool.size());
    System.out.printf("Generation time: %d ms%n", (endTime - startTime));
    
    // Verify pool properties
    assertNotNull(pool);
    assertTrue(pool.size() > 0, "Pool should contain candidates");
    assertTrue(pool.size() <= baseSize * 3, "Pool should not exceed 3x base size");
    
    // Verify all candidates are prime (probabilistic test)
    int primeCount = 0;
    for (BigInteger p : pool) {
      assertTrue(p.signum() > 0, "All candidates should be positive");
      if (p.isProbablePrime(64)) {
        primeCount++;
      }
    }
    System.out.printf("Probable primes: %d / %d (%.2f%%)%n", 
        primeCount, pool.size(), 100.0 * primeCount / pool.size());
    assertTrue(primeCount > pool.size() * 0.95, 
        "At least 95% of candidates should be probable primes");
    
    // Verify sorted order
    for (int i = 1; i < pool.size(); i++) {
      assertTrue(pool.get(i).compareTo(pool.get(i - 1)) > 0, 
          "Pool should be sorted in ascending order");
    }
    System.out.println("✓ Pool is sorted");
    
    // Verify no duplicates
    Set<BigInteger> uniqueSet = new HashSet<>(pool);
    assertEquals(pool.size(), uniqueSet.size(), "Pool should contain no duplicates");
    System.out.println("✓ Pool contains no duplicates");
    
    // Verify candidates are in reasonable range relative to sqrt(Nmax)
    BigInteger sqrtNmax = FactorizationShortcut.sqrtFloor(Nmax);
    System.out.printf("sqrt(Nmax): %s%n", sqrtNmax);
    
    // Check that candidates cover different bands
    BigInteger minCandidate = pool.get(0);
    BigInteger maxCandidate = pool.get(pool.size() - 1);
    System.out.printf("Candidate range: [%s, %s]%n", minCandidate, maxCandidate);
    
    BigDecimal minRatio = new BigDecimal(minCandidate).divide(new BigDecimal(sqrtNmax), 
        java.math.MathContext.DECIMAL128);
    BigDecimal maxRatio = new BigDecimal(maxCandidate).divide(new BigDecimal(sqrtNmax), 
        java.math.MathContext.DECIMAL128);
    System.out.printf("Ratio to sqrt(Nmax): [%.3f, %.3f]%n", 
        minRatio.doubleValue(), maxRatio.doubleValue());
    
    // Verify that we have coverage across the bands
    // The bands in multiZ5DPool are: Z5D-A (0.05-1.5), Z5D-B (0.02-0.6), Z-X (1.0-3.0)
    // The algorithm searches around sqrt(Nmax), so candidates will be in the overlapping regions
    // For now, just verify we have some reasonable spread
    assertTrue(minRatio.doubleValue() > 0.0 && minRatio.doubleValue() <= 2.0, 
        "Minimum candidate should be in reasonable range");
    assertTrue(maxRatio.doubleValue() >= 0.5 && maxRatio.doubleValue() <= 3.5, 
        "Maximum candidate should be in reasonable range");
    
    System.out.println("✓ Multi-variant Z5D pool test passed");
  }
}
