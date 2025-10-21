package tools;

import java.io.FileWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;
import gva.GVAFactorizer;
public class BenchLadder {

  // Provided code snippets
  static BigInteger randPrimeBits(int bits, Random rnd) {
    // Miller-Rabin with high certainty; ensure p ≡ 3 mod 4 to avoid tiny factors structure
    while (true) {
      BigInteger p = new BigInteger(bits, rnd).setBit(bits - 1).setBit(0);
      if (p.isProbablePrime(80)) return p;
    }
  }

  static BigInteger[] balancedSemiprimeDigits(int digits, long seed) {
    // Approx bits from digits
    int bits = (int) Math.ceil(digits * Math.log(10) / Math.log(2));
    int pBits = bits / 2, qBits = bits - pBits;
    Random rnd = new Random(seed);
    BigInteger p = randPrimeBits(pBits, rnd);
    BigInteger q = randPrimeBits(qBits, rnd);
    // Balance p and q (|log2 p - log2 q| small)
    while (p.bitLength() > q.bitLength() + 2 || q.bitLength() > p.bitLength() + 2)
      q = randPrimeBits(qBits, rnd);
    return new BigInteger[] {p, q};
  }

  // CandidateBuilder interface
  public interface CandidateBuilder {
    List<BigInteger> build(BigInteger N, int maxCands, long seed);

    String name();
  }

  // Golden ratio
  private static final BigDecimal PHI =
      BigDecimal.ONE
          .add(new BigDecimal(5).sqrt(new MathContext(160)))
          .divide(new BigDecimal(2), new MathContext(160));

  // Euclidean fractional part in [0, 1).
  static BigDecimal frac01(BigDecimal x) {
    BigDecimal flo = x.setScale(0, RoundingMode.FLOOR);
    BigDecimal r = x.subtract(flo);
    if (r.signum() < 0) r = r.add(BigDecimal.ONE);
    if (r.compareTo(BigDecimal.ONE) >= 0) r = r.subtract(BigDecimal.ONE);
    return r;
  }

  // thetaPrimeInt: θ′(n,k) = frac( PHI * ( frac(n/PHI) )^k )
  static BigDecimal thetaPrimeInt(BigDecimal n, BigDecimal k) {
    BigDecimal x = frac01(n.divide(PHI, new MathContext(160))); // x in [0,1)
    double xd = x.doubleValue();
    double kd = k.doubleValue();
    BigDecimal val = BigDecimal.valueOf(PHI.doubleValue() * Math.pow(xd, kd));
    return frac01(val);
  }

  // Sample Z-neighborhood implementation
  static class ZNeighborhood implements CandidateBuilder {
    @Override
    public List<BigInteger> build(BigInteger N, int maxCands, long seed) {
      BigInteger sqrtN = sqrtFloor(N);
      BigInteger start = sqrtN.subtract(BigInteger.valueOf(100000));
      List<BigInteger> cands = new ArrayList<>();
      for (int i = 0; i < maxCands; i++) {
        BigInteger cand = start.add(BigInteger.valueOf(i * 2));
        if (cand.compareTo(BigInteger.TWO) > 0) cands.add(cand);
      }
      return cands;
    }

    @Override
    public String name() {
      return "ZNeighborhood";
    }
  }

  // ResidueFilter: candidates around sqrt(N) that are 3 mod 4
  static class ResidueFilter implements CandidateBuilder {
    @Override
    public List<BigInteger> build(BigInteger N, int maxCands, long seed) {
      BigInteger sqrtN = sqrtFloor(N);
      List<BigInteger> cands = new ArrayList<>();
      Random rnd = new Random(seed);
      for (int i = 0; i < maxCands; i++) {
        BigInteger offset = BigInteger.valueOf(rnd.nextInt(200000) - 100000);
        BigInteger cand = sqrtN.add(offset);
        if (cand.mod(BigInteger.valueOf(4)).equals(BigInteger.valueOf(3))
            && cand.compareTo(BigInteger.TWO) > 0) {
          cands.add(cand);
        }
      }
      return cands;
    }

    @Override
    public String name() {
      return "ResidueFilter";
    }
  }

  // HybridGcd: candidates around sqrt(N) that are 1 mod 4
  static class HybridGcd implements CandidateBuilder {
    @Override
    public List<BigInteger> build(BigInteger N, int maxCands, long seed) {
      BigInteger sqrtN = sqrtFloor(N);
      List<BigInteger> cands = new ArrayList<>();
      Random rnd = new Random(seed);
      for (int i = 0; i < maxCands; i++) {
        BigInteger offset = BigInteger.valueOf(rnd.nextInt(200000) - 100000);
        BigInteger cand = sqrtN.add(offset);
        if (cand.mod(BigInteger.valueOf(4)).equals(BigInteger.ONE)
            && cand.compareTo(BigInteger.TWO) > 0) {
          cands.add(cand);
        }
      }
      return cands;
    }

    @Override
    public String name() {
      return "HybridGcd";
    }
  }

  // MetaSelection: combines multiple builders
  static class MetaSelection implements CandidateBuilder {
    List<CandidateBuilder> builders = Arrays.asList(new ZNeighborhood(), new ResidueFilter(), new GVAFactorizer(new MathContext(200)));

    @Override
    public List<BigInteger> build(BigInteger N, int maxCands, long seed) {
      List<BigInteger> all = new ArrayList<>();
      for (CandidateBuilder b : builders) {
        all.addAll(b.build(N, maxCands / builders.size(), seed));
      }
      Collections.shuffle(all, new Random(seed));
      return all.subList(0, Math.min(maxCands, all.size()));
    }

    @Override
    public String name() {
      return "MetaSelection";
    }
  }

  // Factorization method (adapted from FactorizationShortcut)
  static class Factor {
    BigInteger p, q;
    boolean qPrime, success;

    Factor(BigInteger p, BigInteger q, boolean qPrime, boolean success) {
      this.p = p;
      this.q = q;
      this.qPrime = qPrime;
      this.success = success;
    }
  }

  static Factor factorizeWithCandidatesBig(
      BigInteger N, List<BigInteger> candidates, int mrCertainty) {
    if (!N.testBit(0)) { // even
      BigInteger q = N.shiftRight(1);
      return new Factor(BigInteger.TWO, q, q.isProbablePrime(mrCertainty), true);
    }
    BigInteger r = sqrtFloor(N);
    if (r.multiply(r).equals(N) && r.isProbablePrime(mrCertainty))
      return new Factor(r, r, true, true);

    for (BigInteger p : candidates) {
      if (p.signum() > 0 && N.mod(p).equals(BigInteger.ZERO)) {
        BigInteger q = N.divide(p);
        return new Factor(p, q, q.isProbablePrime(mrCertainty), true);
      }
    }
    return new Factor(BigInteger.ZERO, BigInteger.ZERO, false, false);
  }

  static BigInteger sqrtFloor(BigInteger n) {
    if (n.signum() < 0) throw new ArithmeticException("sqrt of negative");
    if (n.signum() == 0) return BigInteger.ZERO;
    BigInteger x = BigInteger.ONE.shiftLeft((n.bitLength() + 1) >>> 1);
    while (true) {
      BigInteger xn = x.add(n.divide(x)).shiftRight(1);
      if (xn.equals(x) || xn.equals(x.subtract(BigInteger.ONE))) {
        if (xn.multiply(xn).compareTo(n) > 0) return xn.subtract(BigInteger.ONE);
        return xn;
      }
      x = xn;
    }
  }

  public static void main(String[] args) {
    int digits = 200; // default
    String builderName = "ZNeighborhood";
    boolean rsa260 = false;
    long seed = 42L;
    int K = 5;
    boolean ladder = false;
    boolean factorMode = false;
    BigInteger factorN = null;

    for (int i = 0; i < args.length; i++) {
      switch (args[i]) {
        case "--digits":
          digits = Integer.parseInt(args[++i]);
          break;
        case "--builder":
          builderName = args[++i];
          break;
        case "--rsa260":
          rsa260 = true;
          break;
        case "--ladder":
          ladder = true;
          break;
        case "--seed":
          seed = Long.parseLong(args[++i]);
          break;
        case "--K":
          K = Integer.parseInt(args[++i]);
          break;
        case "--factor":
          factorMode = true;
          factorN = new BigInteger(args[++i]);
          break;
      }
    }

    CandidateBuilder builder;
    switch (builderName) {
      case "ZNeighborhood":
        builder = new ZNeighborhood();
        break;
      case "ResidueFilter":
        builder = new ResidueFilter();
        break;
      case "HybridGcd":
        builder = new HybridGcd();
        break;
        break;
      default:
        builder = new ZNeighborhood();
        break;
    }

    if (factorMode) {
      if (factorN.isProbablePrime(100)) {
        System.out.println("The number " + factorN + " is probably prime.");
        return;
      }
      List<BigInteger> cands = builder.build(factorN, 10000, seed);
      long start = System.currentTimeMillis();
      Factor f = factorizeWithCandidatesBig(factorN, cands, 64);
      long time = System.currentTimeMillis() - start;
      if (f.success) {
        System.out.println("Factored: " + factorN + " = " + f.p + " * " + f.q);
        System.out.println("Time: " + time + " ms");
        System.out.println("Candidates checked: " + (cands.indexOf(f.p) + 1));
      } else {
        System.out.println(
            "Failed to factor: " + factorN + " (not factored with current builders)");
      }
      return;
    }

    try (FileWriter fw = new FileWriter("ladder_results.csv", true)) {
      fw.write("id,digits,builder,cand_count,time_ms,success,tries_to_hit,reduction_pct\n");
      if (ladder) {
        int[] rungs = {200, 210, 220, 230, 240, 245, 248, 250, 252, 254, 256, 258, 260};
        for (int d : rungs) {
          for (int i = 0; i < K; i++) {
            BigInteger[] pq = balancedSemiprimeDigits(d, seed + i);
            BigInteger N = pq[0].multiply(pq[1]);
            List<BigInteger> cands = builder.build(N, 10000, seed + i);
            Collections.shuffle(cands, new Random(seed + i));
            long start = System.currentTimeMillis();
            Factor f = factorizeWithCandidatesBig(N, cands, 64);
            long time = System.currentTimeMillis() - start;
            int tries = f.success ? cands.indexOf(f.p) + 1 : cands.size();
            double reduction = (double) cands.size() / (N.bitLength() / 2.0);
            fw.write(
                String.format(
                    "%d,%d,%s,%d,%d,%b,%d,%.2f\n",
                    i, d, builder.name(), cands.size(), time, f.success, tries, reduction));
          }
        }
      } else if (rsa260) {
        // RSA-260
        BigInteger N =
            new BigInteger(
                "22112825529529666435281085255026230927612089502470015394413748319128822941402001986512729726569746599085900330031400051170742204560859276357953757185954298838958709229238491006703034124620545784566413664540684214361293017694020846391065875914794251435144458199");
        // Use MetaSelection for best results
        builder = new MetaSelection();
        int maxCands = 10000;
        List<BigInteger> cands = builder.build(N, maxCands, seed);
        long start = System.currentTimeMillis();
        Factor f = factorizeWithCandidatesBig(N, cands, 64);
        long time = System.currentTimeMillis() - start;
        fw.write(
            String.format(
                "%d,%d,%s,%d,%d,%b,%d,%.2f\n",
                0, 260, builder.name(), cands.size(), time, f.success, f.success ? 1 : 0, 0.0));
      } else {
        for (int i = 0; i < K; i++) {
          BigInteger[] pq = balancedSemiprimeDigits(digits, seed + i);
          BigInteger N = pq[0].multiply(pq[1]);
          List<BigInteger> cands = builder.build(N, 10000, seed + i);
          Collections.shuffle(cands, new Random(seed + i));
          long start = System.currentTimeMillis();
          Factor f = factorizeWithCandidatesBig(N, cands, 64);
          long time = System.currentTimeMillis() - start;
          int tries = f.success ? cands.indexOf(f.p) + 1 : cands.size();
          double reduction = (double) cands.size() / (N.bitLength() / 2.0);
          fw.write(
              String.format(
                  "%d,%d,%s,%d,%d,%b,%d,%.2f\n",
                  i, digits, builder.name(), cands.size(), time, f.success, tries, reduction));
        }
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
  }
}
