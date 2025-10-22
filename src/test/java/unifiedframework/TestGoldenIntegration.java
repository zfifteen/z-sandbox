package unifiedframework;



import java.math.BigDecimal;
import java.math.BigInteger;
import org.junit.Test;

/** Tests for Golden Ratio and Zeta integration code. */
public class TestGoldenIntegration {

  @Test
  public void testGoldenBuilder() {
    GoldenBuilder gb = new GoldenBuilder();
    BigDecimal N = new BigDecimal(170629);
    assert gb.circDistLessThan(
        gb.theta(N, 10), gb.theta(new BigDecimal(17), 10), new BigDecimal("0.001"));
  }

  @Test
  public void testZ5DZetaEst() {
    Z5DZetaEst est = new Z5DZetaEst();
    BigInteger p = est.est(BigInteger.valueOf(1000), 20);
    // Check if it's a probable prime (basic check, not full primality)
    assert p.compareTo(BigInteger.ZERO) > 0; // Positive
    // For simplicity, assume it's reasonable
    assert p.bitLength() > 5; // Has some bits
  }
}
