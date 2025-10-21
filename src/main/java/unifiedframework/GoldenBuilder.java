package unifiedframework;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Golden Ratio Builder for geometric factorization heuristics. */
public class GoldenBuilder {
  private static final BigDecimal PHI = new BigDecimal("1.618033988749895");

  /** Computes θ(m,k) = {φ × ({m / φ})^k} */
  public BigDecimal theta(BigDecimal m, int k) {
    BigDecimal inner = m.divide(PHI).subtract(m.divide(PHI).setScale(0, RoundingMode.FLOOR));
    BigDecimal powered = inner.pow(k);
    return PHI.multiply(powered).subtract(PHI.multiply(powered).setScale(0, RoundingMode.FLOOR));
  }

  /** Computes circular distance d(a,b) = min(|a-b|, 1-|a-b|) */
  public boolean circDistLessThan(BigDecimal a, BigDecimal b, BigDecimal eps) {
    BigDecimal diff = a.subtract(b).abs();
    BigDecimal min = diff.min(BigDecimal.ONE.subtract(diff));
    return min.compareTo(eps) < 0;
  }
}
