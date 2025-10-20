package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;

/** Z5D Zeta Estimator for prime prediction with zeta function corrections. */
public class Z5DZetaEst {

  /** Estimates \hat p_k with zeta radii corrections. */
  public BigInteger est(BigInteger k, int zeros) {
    double kDouble = k.doubleValue();
    double logK = Math.log(kDouble);
    BigDecimal piInv = new BigDecimal(kDouble * logK);
    BigDecimal dK = new BigDecimal(logK);
    BigDecimal zetaCorr = BigDecimal.ZERO;
    for (int n = 1; n <= zeros; n++) {
      zetaCorr = zetaCorr.add(BigDecimal.ONE.divide(new BigDecimal(n * n)));
    }
    BigDecimal eK =
        zetaCorr.multiply(new BigDecimal(Math.sqrt(kDouble))).divide(new BigDecimal(logK));
    return piInv.add(dK).add(eK).toBigInteger();
  }
}
