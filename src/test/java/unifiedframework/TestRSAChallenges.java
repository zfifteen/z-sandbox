package unifiedframework;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;



import java.io.*;
import java.math.BigInteger;
import java.nio.file.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class TestRSAChallenges {

    static class RSAEntry {
        String id;
        String dec;
        String f1, f2;
        String notes;
    }

    List<RSAEntry> entries;

    @BeforeAll
    void loadCsv() throws Exception {
        Path p = Paths.get("src/test/resources/rsa_challenges.csv");
        entries = Files.lines(p)
            .filter(l -> !l.isBlank() && !l.startsWith("id,"))
            .map(l -> {
                // Simple split, since numbers have no commas
                String[] a = l.split(",", -1); // -1 to include empty
                RSAEntry e = new RSAEntry();
                e.id = a[0].trim();
                e.dec = a[1].trim();
                e.f1 = a[2].trim();
                e.f2 = a[3].trim();
                e.notes = a[4].trim();
                return e;
            }).collect(Collectors.toList());
    }

    @Test
    @DisplayName("Quick: verify small factored RSA entries (unit)")
    void quickFactoredRSA() {
        System.out.println("Testing quick factored RSA entries");
        for (RSAEntry e : entries) {
            if (!e.f1.isEmpty() && !e.f2.isEmpty()) {
                // skip huge ones for which you don't want to do heavy factoring in unit tests
                if (e.dec.length() > 130) continue;
                BigInteger N = new BigInteger(e.dec);
                BigInteger expectedP = new BigInteger(e.f1);
                BigInteger expectedQ = new BigInteger(e.f2);

                System.out.printf("dec length: %d%n", e.dec.length());

                // Preflight checks
                assertSaneRSA(e.id, N);
                Assertions.assertTrue(expectedP.multiply(expectedQ).equals(N), e.id + ": known factors don't multiply to N");

                System.out.printf("Input RSA ID: %s%n", e.id);
                System.out.printf("Input N digits: %d%n", e.dec.length());
                System.out.printf("Expected p: %s%n", expectedP);
                System.out.printf("Expected q: %s%n", expectedQ);

                // Use BigInteger API with known factor as candidate (shortcut assumes candidates are provided)
                List<BigInteger> candidates = Arrays.asList(expectedP);
                FactorizationShortcutDemo.Factor result = FactorizationShortcutDemo.factorizeWithCandidatesBig(N, candidates, 64);
                System.out.printf("Factorization success: %b%n", result.success());
                Assertions.assertTrue(result.success(), e.id + " should factor");
                BigInteger p = result.p();
                BigInteger q = result.q();
                // Validate result
                Assertions.assertTrue(isValidFactorization(N, p, q), e.id + ": invalid factorization");
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

    // Preflight validator
    static void assertSaneRSA(String id, BigInteger N) {
        int d = N.toString().length();
        System.out.printf("Preflight %s: d=%d%n", id, d);
        Map<String, Integer> exp = Map.of("RSA-100", 100, "RSA-129", 129, "RSA-250", 250);
        Assertions.assertEquals(exp.get(id), d, id + ": digits mismatch");
        Assertions.assertNotEquals(0, N.mod(BigInteger.TWO).intValue(), id + ": N is even");
        int[] small = {3, 5, 7, 11, 13, 17, 19};
        for (int sp : small) {
            Assertions.assertNotEquals(0, N.mod(BigInteger.valueOf(sp)).intValue(), id + ": divisible by " + sp);
        }
    }

    // Result validation
    static boolean isValidFactorization(BigInteger N, BigInteger p, BigInteger q) {
        if (p == null || q == null) return false;
        if (p.signum() <= 0 || q.signum() <= 0) return false;
        if (!p.multiply(q).equals(N)) return false;
        if (!p.isProbablePrime(64) || !q.isProbablePrime(64)) return false;
        return true;
    }
}