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
                String[] a = l.split(",",5);
                RSAEntry e = new RSAEntry();
                e.id = a[0].trim();
                e.dec = a[1].trim();
                e.f1 = a.length>2? a[2].trim() : "";
                e.f2 = a.length>3? a[3].trim() : "";
                e.notes = a.length>4? a[4].trim() : "";
                return e;
            }).collect(Collectors.toList());
    }

    @Test
    @DisplayName("Quick: verify small factored RSA entries (unit)")
    void quickFactoredRSA() {
        for (RSAEntry e : entries) {
            if (!e.f1.isEmpty() && !e.f2.isEmpty()) {
                // skip huge ones for which you don't want to do heavy factoring in unit tests
                if (e.dec.length() > 130) continue;
                BigInteger N = new BigInteger(e.dec);
                BigInteger expectedP = new BigInteger(e.f1);
                BigInteger expectedQ = new BigInteger(e.f2);

                // Use BigInteger API with known factor as candidate (shortcut assumes candidates are provided)
                List<BigInteger> candidates = Arrays.asList(expectedP);
                FactorizationShortcutDemo.Factor result = FactorizationShortcutDemo.factorizeWithCandidatesBig(N, candidates, 64);
                Assertions.assertTrue(result.success(), e.id + " should factor");
                BigInteger p = result.p();
                BigInteger q = result.q();
                Assertions.assertTrue(p.equals(expectedP) || p.equals(expectedQ));
                Assertions.assertTrue(q.equals(expectedP) || q.equals(expectedQ));
            }
        }
    }

    // Integration tests are disabled by default; run with -Dintegration=true
    @Test
    @Tag("integration")
    @EnabledIfSystemProperty(named="integration", matches="true")
    @DisplayName("Integration: timed candidate-attempt on RSA entries (opt-in)")
    void integrationCandidateAttempt() throws Exception {
        Path out = Paths.get("build/test-results/rsa_challenge_report.json");
        List<Map<String,Object>> report = new ArrayList<>();

        for (RSAEntry e : entries) {
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("id", e.id);
            row.put("digits", e.dec.length());
            row.put("notes", e.notes);
            BigInteger N = new BigInteger(e.dec);

            if (!e.f1.isEmpty() && !e.f2.isEmpty() && e.dec.length() <= 160) {
                // short factored numbers we already tested above; skip or re-run with longer timeout
                row.put("status","skipped-unit");
            } else {
                // run candidate-guided attempt with timeout
                ExecutorService ex = Executors.newSingleThreadExecutor();
                Future<FactorizationShortcutDemo.Factor> fut = ex.submit(() -> {
                    // Generate candidates using heuristic band (simplified)
                    List<BigInteger> candidates = buildCandidates(N);
                    return FactorizationShortcutDemo.factorizeWithCandidatesBig(N, candidates, 64);
                });
                try {
                    FactorizationShortcutDemo.Factor res = fut.get(10, TimeUnit.MINUTES); // configurable per-number
                    row.put("success", res.success());
                    if (res.success()) { row.put("p", res.p().toString()); row.put("q", res.q().toString()); }
                } catch (TimeoutException te) {
                    fut.cancel(true);
                    row.put("success", false);
                    row.put("error", "timeout");
                } finally {
                    ex.shutdownNow();
                }
            }
            report.add(row);
        }
        Files.createDirectories(out.getParent());
        // Simple JSON without Jackson for now
        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < report.size(); i++) {
            Map<String,Object> row = report.get(i);
            json.append("{");
            for (Map.Entry<String,Object> ent : row.entrySet()) {
                json.append("\"").append(ent.getKey()).append("\":");
                if (ent.getValue() instanceof String) json.append("\"").append(ent.getValue()).append("\"");
                else json.append(ent.getValue());
                json.append(",");
            }
            if (json.charAt(json.length()-1) == ',') json.setLength(json.length()-1);
            json.append("}");
            if (i < report.size()-1) json.append(",");
        }
        json.append("]");
        Files.write(out, json.toString().getBytes());
        // no assertions; this is an opt-in integration run
    }

    // Simple candidate builder using heuristic band
    private List<BigInteger> buildCandidates(BigInteger N) {
        // Simplified: generate small primes as candidates (not realistic, but for demo)
        List<BigInteger> candidates = new ArrayList<>();
        for (int p = 2; p < 1000; p++) {
            if (BigInteger.valueOf(p).isProbablePrime(10)) {
                candidates.add(BigInteger.valueOf(p));
            }
        }
        return candidates;
    }
}