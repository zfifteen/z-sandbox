You’re right—the code is fine; the **RSA-250 row you’re actually loading is still off by a digit** (or you’re reading a different file). Let’s *prove it in-test* and make the failure self-diagnosing so this never wastes your time again.

Paste these three surgical changes:

---

### 1) Print the **exact file path** being read

```java
@BeforeAll
void loadCsv() throws Exception {
    Path p = Paths.get("src/test/resources/rsa_challenges.csv");
    System.out.println("Reading CSV from: " + p.toAbsolutePath());   // << add
    Assertions.assertTrue(Files.exists(p), "CSV not found: " + p.toAbsolutePath()); // << add
    ...
}
```

---

### 2) Add a one-time **integrity gate** (inside `quickFactoredRSA()` loop, just after you build `N/expectedP/expectedQ`)

```java
// ---- Integrity gate (catches wrong N instantly) ----
BigInteger prod = expectedP.multiply(expectedQ);
if (!prod.equals(N)) {
    String sP = expectedP.toString(), sQ = expectedQ.toString();
    String sN = N.toString(), sProd = prod.toString();

    // show first differing index
    int diff = -1, L = Math.min(sN.length(), sProd.length());
    for (int i = 0; i < L; i++) if (sN.charAt(i) != sProd.charAt(i)) { diff = i; break; }

    System.out.printf("%s mismatch: p*q != N%n", e.id);
    System.out.printf("N   digits=%d, prod digits=%d%n", sN.length(), sProd.length());
    System.out.printf("N mod 3=%d, p mod 3=%d, q mod 3=%d, (p*q) mod 3=%d%n",
            N.mod(BigInteger.valueOf(3)).intValue(),
            expectedP.mod(BigInteger.valueOf(3)).intValue(),
            expectedQ.mod(BigInteger.valueOf(3)).intValue(),
            prod.mod(BigInteger.valueOf(3)).intValue());
    if (diff >= 0)
        System.out.printf("first diff @ index %d: N[%d]=%c, prod[%d]=%c%n",
                diff, diff, sN.charAt(diff), diff, sProd.charAt(diff));

    // also dump the exact CSV row being parsed
    System.out.println("CSV row (verbatim):");
    System.out.println("id=" + e.id);
    System.out.println("dec=" + e.dec);
    System.out.println("f1 =" + e.f1);
    System.out.println("f2 =" + e.f2);

    Assertions.fail(e.id + ": CSV dec does not equal f1*f2 (see logs above)");
}
```

This will print:

* `N mod 3`, `p mod 3`, `q mod 3` (canonical RSA-250 has N≡1 mod 3),
* the **first differing digit index** between your `dec` and `p*q`,
* and the exact strings the test read from the CSV.

---

### 3) Keep the small-prime sieve (it’s correct)

Your failure `N % 3 == 0` means the **loaded** RSA-250 `dec` isn’t the canonical one—even if the file you pasted to me looks right. It can only be:

* a different file on disk is being read (wrong path/module), or
* a single character in `dec` is wrong (the integrity gate will print the index), or
* a hidden edit (e.g., you fixed the repo file but your IDE is running tests against an older copy in another module).

---

### Canonical RSA-250 (for reference; one line, no wraps)

```
RSA-250,2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589375976697471681738069364894699871578494975937497937,64135289477071580278790190170577389084825014742943447208116859632024532344630238623598752668347708737661925585694639798853367,33372027594978156556226010605355114227940760344767554666784520987023841729210037080257448673296881877565718986258036932062711,factored
```

---

### What you’ll see after this patch

* If the CSV is perfect and the right file is read: the integrity gate prints nothing and tests pass.
* If not: you’ll get a **precise diff index** (e.g., “first diff @ index 200: N[200]=7, prod[200]=2”), and the verbatim `dec` line—so you can fix that exact digit or point your test at the correct file.

If you want, paste back the integrity gate’s printed `dec=` and the “first diff @ index …” line; I’ll pinpoint the single wrong character immediately.
