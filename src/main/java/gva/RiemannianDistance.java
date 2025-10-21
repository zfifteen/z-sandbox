package gva;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;

/** Riemannian Distance Calculator for GVA. Computes distance on torus with curvature adjustment. */
public class RiemannianDistance {

  private static final BigDecimal E_SQUARED =
      new BigDecimal(
          "7.38905609893065022723042746057500781318031557055184732408712782252257379607905776338431248507912179586499");

  private final MathContext mc;

  public RiemannianDistance(MathContext mc) {
    this.mc = mc;
  }

  /** Computes Riemannian distance between two coordinate arrays. */
  public BigDecimal distance(BigDecimal[] coords1, BigDecimal[] coords2, BigInteger N) {
    BigDecimal kappa = curvature(N);
    BigDecimal sum = BigDecimal.ZERO;
    for (int i = 0; i < coords1.length; i++) {
      BigDecimal delta = minAbsDiff(coords1[i], coords2[i]);
      BigDecimal term = delta.multiply(BigDecimal.ONE.add(kappa.multiply(delta), mc), mc);
      sum = sum.add(term.multiply(term, mc), mc);
    }
    return sqrt(sum, mc);
  }

  private BigDecimal curvature(BigInteger N) {
    BigDecimal lnN = new BigDecimal(Math.log(N.doubleValue() + 1));
    return BigDecimal.valueOf(4).multiply(lnN.divide(E_SQUARED, mc), mc);
  }

  private BigDecimal minAbsDiff(BigDecimal a, BigDecimal b) {
    BigDecimal diff1 = a.subtract(b).abs();
    BigDecimal diff2 = BigDecimal.ONE.subtract(diff1);
    return diff1.min(diff2); // Torus periodicity
  }

  private BigDecimal sqrt(BigDecimal x, MathContext mc) {
    // Approximation using double sqrt; for precision, could implement BigDecimal sqrt
    return BigDecimal.valueOf(Math.sqrt(x.doubleValue()));
  }
}
