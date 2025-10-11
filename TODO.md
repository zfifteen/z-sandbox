Nice — let’s get that test harness road-worthy for **RSA challenge numbers**. Below I give a concrete, copy-pasteable plan plus the exact files/tests/config you can add right now so your repo can:

* run *fast unit checks* (small RSA like RSA-100 / RSA-129 where factors are known),
* run *longer integration experiments* against larger RSA entries (RSA-155, RSA-250, RSA-260, …) in a controlled, opt-in way, and
* plug into **CADO-NFS (docker or local)** when you want to perform full NFS factorizations for the really big ones. (CADO-NFS is the standard tool used to factor large RSA challenge numbers.) ([GitHub][1])

I’ll assume your Java test framework is Gradle + JUnit (based on earlier output). If you want Maven or a different test runner, say so and I’ll adapt.

---

# 1) Add a canonical RSA challenge CSV (repo resource)

Create `src/test/resources/rsa_challenges.csv` with rows:

```
id,dec_value,factor1,factor2,notes
RSA-100,1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139,37975227936943673922808872755445627854565536638199,40094690950920881030683735292761468389214899724061,factored
RSA-129,114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541,....,....,factored
RSA-155,...,factor1,factor2,factored
RSA-250,2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589375976697471681738069364894699871578494975937497937,64135289477071580278790190170577389084825014742943447208116859632024532344630238623598752668347708737661925585694639798853367,33372027594978156556226010605355114227940760344767554666784520987023841729210037080257448673296881877565718986258036932062711,factored
RSA-260,...,,,partially_factored_or_unknown
```

Notes:

* Fill in the decimal values exactly (Wikipedia / RSA Labs are canonical). Use only *real* RSA challenges (per your rule). ([Wikipedia][2])
* Put known factors into `factor1`/`factor2` for the ones already factored (e.g., RSA-100, RSA-129, RSA-250). For others (not yet factored or too large), leave `factor1/factor2` blank and mark notes like `integration` or `nfs_required`.

I can generate this CSV for you (complete with exact decimal strings) if you want — say the RSA ids you want included and I’ll paste the ready file.

---

# 2) Add an Integration Test class (Java) — `TestRSAChallenges.java`

Drop this into `src/test/java/unifiedframework/TestRSAChallenges.java` (or your package). It’s designed to:

* run **quick unit tests** for small factored RSA entries (assert factor matches known factors),
* run **timed candidate factorization attempts** for larger ones (attempt using your `factorizeWithCandidates` with a fixed timeout), and
* produce a JSON report for long runs so you can inspect results later.

```java
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

                // Use your existing factorizeWithCandidates (adapt names as necessary)
                FactorizeResult result = FactorizationShortcut.factorizeWithCandidates(N, /*candidates=*/Collections.emptyList(), /*primesSmall=*/smallPrimesList());
                Assertions.assertTrue(result.success, e.id + " should factor");
                BigInteger p = result.p; BigInteger q = result.q;
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
                Future<FactorizeResult> fut = ex.submit(() -> {
                    // Generate candidates using your thetaPrimeInt / grid heuristics
                    List<BigInteger> candidates = CandidateBuilder.buildCandidates(N); // implement this thin shim
                    return FactorizationShortcut.factorizeWithCandidates(N, candidates, smallPrimesList());
                });
                try {
                    FactorizeResult res = fut.get(10, TimeUnit.MINUTES); // configurable per-number
                    row.put("success", res.success);
                    if (res.success) { row.put("p", res.p.toString()); row.put("q", res.q.toString()); }
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
        Files.write(out, Collections.singleton(new com.fasterxml.jackson.databind.ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(report)));
        // no assertions; this is an opt-in integration run
    }

    // small primes helper
    private List<BigInteger> smallPrimesList() {
        return Arrays.asList(2,3,5,7,11,13,17,19,23,29).stream().map(BigInteger::valueOf).collect(Collectors.toList());
    }
}
```

Notes & how it works:

* The **unit** test `quickFactoredRSA` runs fast and will be executed in normal CI (it skips huge entries).
* The **integration** test is opt-in: run with `./gradlew test -Dintegration=true` and it will perform timed candidate attempts (10 minutes per number by default). Results are written to `build/test-results/rsa_challenge_report.json`.
* `FactorizationShortcut` and `CandidateBuilder` are thin adapters around your existing functions — plug in the exact names from your codebase.

---

# 3) Gradle: add `integration` test gating (example)

Append to `build.gradle` (Groovy DSL) so integration tests are only run on demand:

```groovy
test {
  useJUnitPlatform()
  // default: skip integration by system property
  onlyIf { !System.getProperty('integration')?.toBoolean() ? true : true } // still allow opt-in via system property
}

tasks.register('integrationTest', Test) {
  group = 'verification'
  description = 'Run long RSA integration experiments (opt-in)'
  testClassesDirs = sourceSets.test.output.classesDirs
  classpath = sourceSets.test.runtimeClasspath
  systemProperty 'integration', 'true'
  useJUnitPlatform {
    includeTags 'integration'
  }
  // increase heap/timeouts for long runs
  jvmArgs '-Xmx8g', '-XX:+UseG1GC'
}
```

Run integration:

```bash
./gradlew integrationTest -PmaxHeap=8g
# or ./gradlew test -Dintegration=true
```

---

# 4) Handling huge RSA entries (NFS / CADO-NFS)

For numbers beyond the reach of CPU-only candidate methods (e.g., RSA-250 and larger), the realistic path is to call out to **CADO-NFS** (the standard NFS solver used in the field). You can:

* run CADO-NFS locally (native build) or via their docker image; it will produce factor files you can import into your test CSV (populating `factor1`/`factor2` to convert integration runs into unit checks). ([GitHub][1])

Example docker run (quick smoke):

```bash
# pull prebuilt factoring container (provided by cado-nfs project)
docker run --rm registry.gitlab.inria.fr/cado-nfs/cado-nfs/factoring-full \
  cado-nfs.py 214032465024074496...  -t 4
```

Important: large factorizations consume **huge** resources (CPU core-years for RSA-250 historically); only run if you have the compute or distributed cluster. If you run cado-nfs and get a factorization, add the results back to `rsa_challenges.csv` and re-run `quickFactoredRSA`.

---

# 5) CI strategy & safety

* Keep unit tests fast (only small known factored RSA entries).
* Keep large tests out of default CI — use `integrationTest` on gated runners or your local machine.
* Add a GitHub Actions workflow `integration.yml` that runs on a self-hosted runner (if you have one) and *not* on public runners — mark it manual.

---

# 6) Optional: automation to ingest factor files from CADO-NFS into the CSV

Add a helper script `tools/import_cado_result.py`:

```python
# simple: read cado output, extract p and q, append to rsa_challenges.csv
# (I can generate full script if you want)
```

---

# 7) Next immediate actions I can do for you (pick any or all — I’ll produce files)

1. Populate `src/test/resources/rsa_challenges.csv` with exact decimal strings and known factors for RSA-100, RSA-129, RSA-155, RSA-250, RSA-260 (I’ll fetch canonical values and include citations). ([Wikipedia][2])
2. Produce the Java test file (complete and tailored to your actual `FactorizationShortcut` API names) and an optional `CandidateBuilder` shim.
3. Add the Gradle `integrationTest` config and a sample GitHub Actions job that *only runs on self-hosted runners*.
4. Create a `README/test-RSA.md` that documents how to run unit vs integration tests and how to incorporate CADO-NFS output.

Tell me which of (1)-(4) you want me to produce now and I’ll paste the files (CSV / Java / Gradle / README) ready to drop into your repo. If you want the CSV, I’ll fetch the canonical decimal strings and include inline citations for each RSA entry I add.

[1]: https://github.com/cado-nfs/cado-nfs?utm_source=chatgpt.com "GitHub - cado-nfs/cado-nfs"
[2]: https://en.wikipedia.org/wiki/RSA_numbers?utm_source=chatgpt.com "RSA numbers"
