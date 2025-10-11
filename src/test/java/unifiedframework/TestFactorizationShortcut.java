package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.util.List;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class TestFactorizationShortcut {

  @BeforeAll
  static void printSystemInfo() {
    System.out.println("==========================================");
    System.out.println("   Test Environment Configuration");
    System.out.println("==========================================");

    // OS and Java Info
    System.out.printf("OS: %s %s (%s)%n", System.getProperty("os.name"), System.getProperty("os.version"), System.getProperty("os.arch"));
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
    System.out.printf("JVM Used Memory: %.2f MB%n", (jvmTotalMemory - jvmFreeMemory) / (1024.0 * 1024.0));

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
    System.out.printf("Is in [0,1): %b%n", theta.compareTo(BigDecimal.ZERO) >= 0 && theta.compareTo(BigDecimal.ONE) < 0);

    assertTrue(theta.compareTo(BigDecimal.ZERO) >= 0 && theta.compareTo(BigDecimal.ONE) < 0);
  }



  @Test
  public void testSampleSemiprimesBalanced() {
    System.out.println("Testing sampleSemiprimesBalanced functionality");
    List<Integer> primes = List.of(2, 3, 5, 7, 11, 13, 17, 19);
    int targetCount = 10;
    long Nmax = 1000;
    long seed = 42;
    List<long[]> semis = FactorizationShortcut.sampleSemiprimesBalanced(primes, targetCount, Nmax, seed);

    System.out.printf("Input primes: %s%n", primes);
    System.out.printf("Target count: %d%n", targetCount);
    System.out.printf("Nmax: %d%n", Nmax);
    System.out.printf("Seed: %d%n", seed);
    System.out.printf("Generated semiprimes count: %d%n", semis.size());
    for (int i = 0; i < semis.size(); i++) {
      long[] s = semis.get(i);
      System.out.printf("Semiprime %d: p=%d, q=%d, N=%d, N < Nmax: %b, p*q==N: %b%n", i+1, s[0], s[1], s[2], s[2] < Nmax, s[0] * s[1] == s[2]);
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
    System.out.printf("Result: success=%d, p=%d, q=%d, q_prime=%d%n", res[0], res[1], res[2], res[3]);
    System.out.printf("Success: %b%n", res[0] == 1);
    System.out.printf("p correct: %b%n", res[1] == 2);
    System.out.printf("q correct: %b%n", res[2] == 3);
    System.out.printf("q is prime: %b%n", res[3] == 1);

    assertEquals(1, res[0]); // success
    assertEquals(2, res[1]); // p
    assertEquals(3, res[2]); // q
    assertEquals(1, res[3]); // q prime
  }
}
