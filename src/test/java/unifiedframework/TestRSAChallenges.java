package unifiedframework;

import java.math.BigInteger;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class TestRSAChallenges {

  static class RSAEntry {
    public String id;
    public String dec;
    public String f1, f2;
    public String notes;
  }

  private List<RSAEntry> entries;

  @BeforeAll
  void loadCsv() throws Exception {
    Path p = Paths.get("src/test/resources/rsa_challenges.csv");
    System.err.println("Reading CSV from: " + p.toAbsolutePath()); // << add
    Assertions.assertTrue(Files.exists(p), "CSV not found: " + p.toAbsolutePath()); // << add
    entries =
        Files.lines(p)
            .filter(l -> !l.isBlank() && !l.startsWith("id,"))
            .map(
                l -> {
                  String[] a = l.split(",", -1);
                  if (a.length < 5) throw new IllegalArgumentException("Bad CSV row: " + l);
                  RSAEntry e = new RSAEntry();
                  e.id = a[0].trim();
                  e.dec = a[1].trim();
                  e.f1 = a[2].trim();
                  e.f2 = a[3].trim();
                  e.notes = a[4].trim();
                  return e;
                })
            .collect(Collectors.toList());
  }

  @Test
  @DisplayName("Quick: verify factored RSA entries (unit)")
  void quickFactoredRSA() {
    System.out.println("Testing quick factored RSA entries");
    for (RSAEntry e : entries) {
      if (!e.f1.isEmpty() && !e.f2.isEmpty()) {
        if (e.dec.length() > 250) continue; // keep unit fast
        BigInteger N = new BigInteger(e.dec);
        BigInteger expectedP = new BigInteger(e.f1);
        BigInteger expectedQ = new BigInteger(e.f2);

        // ---- Integrity gate (catches wrong N instantly) ----
        BigInteger prod = expectedP.multiply(expectedQ);
        if (!prod.equals(N)) {
          String sP = expectedP.toString(), sQ = expectedQ.toString();
          String sN = N.toString(), sProd = prod.toString();

          // show first differing index
          int diff = -1, L = Math.min(sN.length(), sProd.length());
          for (int i = 0; i < L; i++)
            if (sN.charAt(i) != sProd.charAt(i)) {
              diff = i;
              break;
            }

          System.err.printf("%s mismatch: p*q != N%n", e.id);
          System.err.printf("N   digits=%d, prod digits=%d%n", sN.length(), sProd.length());
          System.err.printf(
              "N mod 3=%d, p mod 3=%d, q mod 3=%d, (p*q) mod 3=%d%n",
              N.mod(BigInteger.valueOf(3)).intValue(),
              expectedP.mod(BigInteger.valueOf(3)).intValue(),
              expectedQ.mod(BigInteger.valueOf(3)).intValue(),
              prod.mod(BigInteger.valueOf(3)).intValue());
          if (diff >= 0)
            System.err.printf(
                "first diff @ index %d: N[%d]=%c, prod[%d]=%c%n",
                diff, diff, sN.charAt(diff), diff, sProd.charAt(diff));

          // also dump the exact CSV row being parsed
          System.err.println("CSV row (verbatim):");
          System.err.println("id=" + e.id);
          System.err.println("dec=" + e.dec);
          System.err.println("f1 =" + e.f1);
          System.err.println("f2 =" + e.f2);

          Assertions.fail(e.id + ": CSV dec does not equal f1*f2 (see logs above)");
        }

        System.out.printf("dec length: %d%n", e.dec.length());
        assertSaneRSA(e.id, N);
        Assertions.assertEquals(
            N, expectedP.multiply(expectedQ), e.id + ": known factors don't multiply to N");

        System.out.printf("Input RSA ID: %s%n", e.id);
        System.out.printf("Input N digits: %d%n", e.dec.length());
        System.out.printf("Expected p: %s%n", expectedP);
        System.out.printf("Expected q: %s%n", expectedQ);

        List<BigInteger> candidates = Arrays.asList(expectedP, expectedQ);
        FactorizationShortcut.Factor res =
            FactorizationShortcut.factorizeWithCandidatesBig(N, candidates, 64);

        System.out.printf("Factorization success: %b%n", res.success());
        Assertions.assertTrue(res.success(), e.id + " should factor");

        BigInteger p = res.p(), q = res.q();
        Assertions.assertTrue(validFactorization(N, p, q), e.id + ": invalid factorization");

        System.out.printf("Recovered p: %s%n", p);
        System.out.printf("Recovered q: %s%n", q);
        System.out.printf("p matches expected: %b%n", p.equals(expectedP) || p.equals(expectedQ));
        System.out.printf("q matches expected: %b%n", q.equals(expectedP) || q.equals(expectedQ));
        Assertions.assertTrue(p.equals(expectedP) || p.equals(expectedQ));
        Assertions.assertTrue(q.equals(expectedP) || q.equals(expectedQ));
        System.out.println();
      }
    }
  }

  @Test
  @Tag("integration")
  @EnabledIfSystemProperty(named = "integration", matches = "true")
  @DisplayName("RSA-260 must never false-positive (adversarial candidates)")
  void rsa260_neverSucceeds() throws Exception {
    RSAEntry e =
        entries.stream()
            .filter(x -> "RSA-260".equals(x.id))
            .findFirst()
            .orElseThrow(() -> new IllegalStateException("RSA-260 not found in CSV"));
    BigInteger N = new BigInteger(e.dec);
    System.out.printf("Integration attempt on %s, digits: %d%n", e.id, e.dec.length());
    assertSaneRSA(e.id, N);

    List<BigInteger> adversarial =
        Arrays.asList(
            BigInteger.ONE,
            BigInteger.TWO,
            BigInteger.valueOf(3),
            BigInteger.valueOf(5),
            N,
            N.subtract(BigInteger.ONE),
            N.add(BigInteger.ONE));
    List<BigInteger> candidates = sanitizeCandidates(N, adversarial);

    ExecutorService ex = Executors.newSingleThreadExecutor();
    Future<FactorizationShortcut.Factor> fut =
        ex.submit(() -> FactorizationShortcut.factorizeWithCandidatesBig(N, candidates, 64));

    try {
      FactorizationShortcut.Factor res = fut.get(15, TimeUnit.SECONDS);
      boolean ok = validFactorization(N, res.p(), res.q());
      System.out.printf("Result: success=%b, valid=%b%n", res.success(), ok);
      Assertions.assertFalse(ok, "RSA-260 must not be factored; any 'success' must be invalid");
    } catch (TimeoutException te) {
      System.out.println("Attempt timed out as expected");
    } finally {
      ex.shutdownNow();
    }
  }

  // ---------- helpers ----------

  private static final Map<String, Integer> EXPECTED_DIGITS =
      Map.of(
          "RSA-100", 100,
          "RSA-129", 129,
          "RSA-155", 155,
          "RSA-250", 250,
          "RSA-260", 260);

  static void assertSaneRSA(String id, BigInteger N) {
    int d = N.toString().length();
    System.out.printf("Preflight %s: d=%d%n", id, d);
    Integer expected = EXPECTED_DIGITS.get(id);
    Assertions.assertNotNull(expected, "Unknown RSA id: " + id);
    Assertions.assertEquals(expected.intValue(), d, id + ": digits mismatch");

    int[] small = {2, 3, 5, 7, 11, 13, 17, 19};
    for (int sp : small) {
      Assertions.assertNotEquals(
          0,
          N.mod(BigInteger.valueOf(sp)).intValue(),
          id + ": N divisible by " + sp + " (shouldn't be for RSA entries)");
    }
  }

  static boolean validFactorization(BigInteger N, BigInteger p, BigInteger q) {
    if (p == null || q == null) return false;
    if (p.signum() <= 0 || q.signum() <= 0) return false;
    if (p.equals(BigInteger.ONE) || q.equals(BigInteger.ONE)) return false;
    if (!p.multiply(q).equals(N)) return false;
    if (!p.isProbablePrime(64) || !q.isProbablePrime(64)) return false;
    return true;
  }

  static List<BigInteger> sanitizeCandidates(BigInteger N, Collection<BigInteger> in) {
    if (in == null) return List.of();
    BigInteger Nminus1 = N.subtract(BigInteger.ONE);
    return in.stream()
        .filter(Objects::nonNull)
        .map(BigInteger::abs)
        .filter(c -> c.compareTo(BigInteger.TWO) >= 0)
        .filter(c -> c.compareTo(Nminus1) <= 0)
        .distinct()
        .collect(Collectors.toList());
  }
}
