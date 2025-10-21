package unifiedframework;

import static org.junit.Assert.*;

import gva.GVAFactorizer;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.List;
import org.junit.Test;

/** Tests for GVA Factorizer. */
public class TestGVA {

  private final GVAFactorizer gva = new GVAFactorizer(new MathContext(200));

  @Test
  public void testSmallSemiprime() {
    // Known semiprime: 15 = 3 * 5
    BigInteger N = BigInteger.valueOf(15);
    List<BigInteger> factors = gva.build(N, 10, 42);
    assertTrue(
        "Should find factor 3 or 5",
        factors.contains(BigInteger.valueOf(3)) || factors.contains(BigInteger.valueOf(5)));
  }

  @Test
  public void test64BitBenchmark() {
    // Generate a 64-bit semiprime
    BigInteger p =
        new BigInteger(32, java.util.Random.from(java.util.concurrent.ThreadLocalRandom.current()));
    BigInteger q =
        new BigInteger(32, java.util.Random.from(java.util.concurrent.ThreadLocalRandom.current()));
    BigInteger N = p.multiply(q);

    List<BigInteger> factors = gva.build(N, 10, 42);
    // Check if any candidate is a factor
    boolean hasFactor = factors.stream().anyMatch(f -> N.mod(f).equals(BigInteger.ZERO));
    assertTrue("Should find at least one factor", hasFactor);
  }

  @Test
  public void testNoFactorsForPrime() {
    BigInteger prime = BigInteger.valueOf(17);
    List<BigInteger> factors = gva.build(prime, 10, 42);
    assertTrue("Prime should have no factors", factors.isEmpty());
  }
}
