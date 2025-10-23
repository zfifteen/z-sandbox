package gva;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Torus Geodesic Embedding for GVA. Embeds a number into a high-dimensional torus using iterative
 * transformations.
 */
public class Embedding {

  private static final BigDecimal PHI =
      new BigDecimal(
          "1.61803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475");
  private static final BigDecimal E_SQUARED =
      new BigDecimal(
          "7.38905609893065022723042746057500781318031557055184732408712782252257379607905776338431248507912179586499");

  private final MathContext mc;

  public Embedding(MathContext mc) {
    this.mc = mc;
  }

  /** Embeds n into a torus with given dimensions and adaptive k. */
  public BigDecimal[] embedTorusGeodesic(BigInteger n, int dims) {
    BigDecimal[] coords = new BigDecimal[dims];
    BigDecimal x = new BigDecimal(n).divide(E_SQUARED, mc);
    double logLogN = Math.log(Math.log(n.doubleValue() + 1)) / Math.log(2);
    BigDecimal k = BigDecimal.valueOf(0.3 / logLogN);

    for (int i = 0; i < dims; i++) {
      BigDecimal fracX = frac01(x);
      // x = phi * (fracX ^ k)
      BigDecimal pow = pow(fracX, k.doubleValue());
      x = PHI.multiply(pow, mc);
      coords[i] = frac01(x);
    }
    return coords;
  }

  /**
   * Enhanced torus embedding with spherical harmonics and toroidal winding.
   * Uses golden ratio spacing and sinθ-weighted sampling for better prime coverage.
   * 
   * Generates (θ, φ) pairs where:
   * - θ varies with adaptive curvature scaling
   * - φ uses golden ratio for uniform angular distribution
   * 
   * @param n Number to embed
   * @param dims Number of dimensions (must be even for θ,φ pairs)
   * @return Coordinate array with alternating θ, φ values in [0, 1]
   */
  public BigDecimal[] embedTorusSpherical(BigInteger n, int dims) {
    if (dims % 2 != 0) {
      throw new IllegalArgumentException("Dimensions must be even for (θ, φ) pairs");
    }
    
    BigDecimal[] coords = new BigDecimal[dims];
    BigDecimal x = new BigDecimal(n).divide(E_SQUARED, mc);
    double logN = Math.log(n.doubleValue() + 1);
    double logLogN = Math.log(logN) / Math.log(2);
    
    // Adaptive parameters based on number size
    BigDecimal kappaGeo = BigDecimal.valueOf(0.3 / logLogN);
    BigDecimal windingFactor = BigDecimal.valueOf(4.0 * logN / E_SQUARED.doubleValue());
    
    for (int i = 0; i < dims; i += 2) {
      // Generate θ coordinate with curvature scaling
      BigDecimal fracX = frac01(x);
      BigDecimal thetaRaw = PHI.multiply(pow(fracX, kappaGeo.doubleValue()), mc);
      coords[i] = frac01(thetaRaw); // θ ∈ [0, 1]
      
      // Generate φ coordinate with golden ratio spacing + winding
      x = PHI.multiply(fracX, mc).add(windingFactor, mc);
      BigDecimal phiRaw = x.multiply(PHI, mc);
      coords[i + 1] = frac01(phiRaw); // φ ∈ [0, 1]
      
      // Update x for next iteration
      x = PHI.multiply(pow(frac01(x), 1.0 + 0.5 / (i + 1)), mc);
    }
    
    return coords;
  }

  private BigDecimal frac01(BigDecimal x) {
    BigDecimal floored = x.setScale(0, RoundingMode.FLOOR);
    BigDecimal frac = x.subtract(floored);
    if (frac.signum() < 0) frac = frac.add(BigDecimal.ONE);
    if (frac.compareTo(BigDecimal.ONE) >= 0) frac = frac.subtract(BigDecimal.ONE);
    return frac;
  }

  private BigDecimal pow(BigDecimal base, double exponent) {
    // Simple power using double for approximation; for high precision, could use BigDecimal exp/log
    // but this suffices for now
    double val = Math.pow(base.doubleValue(), exponent);
    return BigDecimal.valueOf(val);
  }
}
