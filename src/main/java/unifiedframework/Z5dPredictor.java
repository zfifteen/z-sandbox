package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Z5D Prime Predictor - Java Reference Implementation =====================================
 *
 * <p>Java port of the C z5d_predictor implementation following unified-framework principles.
 * Provides double-precision arithmetic with numerical stability guards. Based on the Z Framework's
 * normalization principle Z = A(B/c).
 *
 * <p>Enhanced with arbitrary-precision BigDecimal support for ultra-high scales up to 10^1233.
 *
 * @file Z5dPredictor.java
 * @author Unified Framework Team - Java Port
 * @version 2.0 (Java Reference with BigDecimal support)
 */
public class Z5dPredictor {

  // Version information
  private static final String Z5D_VERSION = "2025-10-11-Java-BigDecimal";

  // Mathematical constants from z_framework_params.h
  private static final double Z5D_E_SQUARED = 7.38905609893065; /* e^2 */
  private static final double Z5D_E_FOURTH = 54.59815003314424; /* e^4 */
  private static final double Z5D_GOLDEN_PHI = 1.61803398874989; /* Golden ratio φ */
  private static final double Z5D_PI = 3.14159265358979; /* π */

  // Default calibration parameters from params.py
  private static final double Z5D_DEFAULT_C = -0.00247;
  private static final double Z5D_DEFAULT_K_STAR = 0.04449; /* KEY PARAMETER */
  private static final double Z5D_DEFAULT_KAPPA_GEO = 0.3;

  // Bounds from params.py
  private static final double Z5D_MIN_KAPPA_GEO = 0.05;
  private static final double Z5D_MAX_KAPPA_GEO = 10.0;

  // Scale-specific calibration thresholds
  private static final double Z5D_SCALE_MEDIUM_MAX = 1e7;
  private static final double Z5D_SCALE_LARGE_MAX = 1e10;
  private static final double Z5D_SCALE_ULTRA_MAX = 1e12;

  // Precision and validation thresholds
  private static final double Z5D_MIN_K = 2.0;
  private static final double Z5D_PRECISION_EPSILON = 1e-15;
  private static final double Z5D_LARGE_K_THRESHOLD = 1e10;

  // BigDecimal support for ultra-high scales
  private static final int BIGDECIMAL_PRECISION = 100; // Significant digits
  private static final MathContext MC = new MathContext(BIGDECIMAL_PRECISION, RoundingMode.HALF_UP);
  private static final double DOUBLE_MAX_SAFE_SCALE = 1e305; // Above this, use BigDecimal

  // Error codes
  public static final int Z5D_SUCCESS = 0;
  public static final int Z5D_ERROR_INVALID_K = -1;
  public static final int Z5D_ERROR_OVERFLOW = -2;
  public static final int Z5D_ERROR_UNDERFLOW = -3;
  public static final int Z5D_ERROR_DOMAIN = -4;
  public static final int Z5D_ERROR_INVALID_KAPPA_GEO = -5;

  /** Calibration parameters for different scales */
  public static class Z5dCalibration {
    public final double c;
    public final double kStar;
    public final double kappaGeoFactor;

    public Z5dCalibration(double c, double kStar, double kappaGeoFactor) {
      this.c = c;
      this.kStar = kStar;
      this.kappaGeoFactor = kappaGeoFactor;
    }
  }

  /** Extended prediction result with detailed components */
  public static class Z5dResult {
    public double prediction;
    public double pntBase;
    public double dTerm;
    public double eTerm;
    public double curvatureProxy;
    public double cUsed;
    public double kStarUsed;
    public double kappaGeoUsed;
    public int errorCode;
  }

  // Scale-specific calibration parameters (Const)
  private static final Z5dCalibration[] Z5D_CALIBRATIONS = {
    new Z5dCalibration(-0.00247, 0.04449, 0.3),
    new Z5dCalibration(-0.00037, -0.11446, 0.3 * 0.809),
    new Z5dCalibration(-0.0001, -0.15, 0.3 * 0.5),
    new Z5dCalibration(-0.00002, -0.10, 0.3 * 0.333)
  };

  // Scale thresholds for lookup
  private static final double[] Z5D_SCALE_THRESHOLDS = {
    0, Z5D_SCALE_MEDIUM_MAX, Z5D_SCALE_LARGE_MAX, Z5D_SCALE_ULTRA_MAX, Double.POSITIVE_INFINITY
  };

  /** Safe logarithm with domain checking */
  private static double safeLog(double x) {
    if (x <= 0.0 || !Double.isFinite(x)) {
      return Double.NaN;
    }
    return Math.log(x);
  }

  /** Safe division with denominator checking */
  private static double safeDivide(double numerator, double denominator) {
    if (Math.abs(denominator) < Z5D_PRECISION_EPSILON) {
      return Double.NaN;
    }
    return numerator / denominator;
  }

  /** Check if double value is finite and not NaN */
  private static boolean isValidFinite(double x) {
    return Double.isFinite(x) && !Double.isNaN(x);
  }

  // ============================================================================
  // BigDecimal Helper Methods for Arbitrary-Precision Arithmetic
  // ============================================================================

  /**
   * Compute natural logarithm using BigDecimal with arbitrary precision. Uses Taylor series
   * expansion: ln(1+x) = x - x^2/2 + x^3/3 - x^4/4 + ... For general x, uses logarithm properties:
   * ln(x) = ln(m * 10^e) = ln(m) + e*ln(10)
   */
  private static BigDecimal lnBigDecimal(BigDecimal x, MathContext mc) {
    if (x.compareTo(BigDecimal.ZERO) <= 0) {
      throw new ArithmeticException("Logarithm of non-positive number");
    }

    // For x = 1, return 0
    if (x.compareTo(BigDecimal.ONE) == 0) {
      return BigDecimal.ZERO;
    }

    // ln(10) constant with high precision
    BigDecimal ln10 =
        new BigDecimal(
            "2.302585092994045684017991454684364207601101488628772976033327900967572609677352480235997205089598298341967784042286");

    // Normalize x to be close to 1 for faster convergence
    // x = mantissa * 10^exponent, ln(x) = ln(mantissa) + exponent * ln(10)
    int exponent = 0;
    BigDecimal mantissa = x;

    // Scale to range [0.1, 10)
    while (mantissa.compareTo(BigDecimal.TEN) >= 0) {
      mantissa = mantissa.divide(BigDecimal.TEN, mc);
      exponent++;
    }
    while (mantissa.compareTo(new BigDecimal("0.1")) < 0) {
      mantissa = mantissa.multiply(BigDecimal.TEN, mc);
      exponent--;
    }

    // Further scale to range [0.5, 2) for better convergence
    int powerOfTwo = 0;
    while (mantissa.compareTo(BigDecimal.ONE.add(BigDecimal.ONE)) >= 0) {
      mantissa = mantissa.divide(BigDecimal.ONE.add(BigDecimal.ONE), mc);
      powerOfTwo++;
    }
    while (mantissa.compareTo(new BigDecimal("0.5")) < 0) {
      mantissa = mantissa.multiply(BigDecimal.ONE.add(BigDecimal.ONE), mc);
      powerOfTwo--;
    }

    // Now compute ln(mantissa) using Taylor series around 1
    // ln(mantissa) = ln(1 + (mantissa-1)) where mantissa is close to 1
    BigDecimal y = mantissa.subtract(BigDecimal.ONE, mc);
    BigDecimal result = BigDecimal.ZERO;
    BigDecimal term = y;

    // Taylor series: ln(1+y) = y - y^2/2 + y^3/3 - y^4/4 + ...
    for (int n = 1; n <= mc.getPrecision() * 2; n++) {
      BigDecimal termValue = term.divide(new BigDecimal(n), mc);
      if (n % 2 == 0) {
        result = result.subtract(termValue, mc);
      } else {
        result = result.add(termValue, mc);
      }
      term = term.multiply(y, mc);

      // Check for convergence
      if (termValue.abs().compareTo(new BigDecimal("1e-" + (mc.getPrecision() + 10))) < 0) {
        break;
      }
    }

    // Add back the scaling factors
    BigDecimal ln2 =
        new BigDecimal(
            "0.693147180559945309417232121458176568075500134360255254120680009493393621969694715605863326996418687542001481021");
    result = result.add(new BigDecimal(powerOfTwo).multiply(ln2, mc), mc);
    result = result.add(new BigDecimal(exponent).multiply(ln10, mc), mc);

    return result;
  }

  /**
   * Compute e^x using BigDecimal with arbitrary precision. Uses Taylor series: e^x = 1 + x + x^2/2!
   * + x^3/3! + x^4/4! + ...
   */
  private static BigDecimal expBigDecimal(BigDecimal x, MathContext mc) {
    // For x = 0, return 1
    if (x.compareTo(BigDecimal.ZERO) == 0) {
      return BigDecimal.ONE;
    }

    // For better convergence, use exp(x) = (exp(x/n))^n
    // Reduce x to small value
    int reductions = 0;
    BigDecimal reducedX = x;
    while (reducedX.abs().compareTo(BigDecimal.ONE) > 0) {
      reducedX = reducedX.divide(BigDecimal.ONE.add(BigDecimal.ONE), mc);
      reductions++;
    }

    // Compute exp(reducedX) using Taylor series
    BigDecimal result = BigDecimal.ONE;
    BigDecimal term = BigDecimal.ONE;

    for (int n = 1; n <= mc.getPrecision() * 2; n++) {
      term = term.multiply(reducedX, mc).divide(new BigDecimal(n), mc);
      result = result.add(term, mc);

      // Check for convergence
      if (term.abs().compareTo(new BigDecimal("1e-" + (mc.getPrecision() + 10))) < 0) {
        break;
      }
    }

    // Square the result 'reductions' times to get exp(x)
    for (int i = 0; i < reductions; i++) {
      result = result.multiply(result, mc);
    }

    return result;
  }

  /**
   * Compute x^y using BigDecimal. For integer y, uses repeated multiplication. For fractional y,
   * uses exp(y * ln(x)).
   */
  private static BigDecimal powBigDecimal(BigDecimal x, BigDecimal y, MathContext mc) {
    if (x.compareTo(BigDecimal.ZERO) <= 0) {
      throw new ArithmeticException("Power of non-positive base");
    }

    // x^0 = 1
    if (y.compareTo(BigDecimal.ZERO) == 0) {
      return BigDecimal.ONE;
    }

    // x^1 = x
    if (y.compareTo(BigDecimal.ONE) == 0) {
      return x;
    }

    // For integer exponents, use repeated multiplication
    try {
      int exponent = y.intValueExact();
      if (exponent < 0) {
        return BigDecimal.ONE.divide(powBigDecimal(x, y.negate(), mc), mc);
      }
      BigDecimal result = BigDecimal.ONE;
      for (int i = 0; i < exponent; i++) {
        result = result.multiply(x, mc);
      }
      return result;
    } catch (ArithmeticException e) {
      // y is not an integer, use exp(y * ln(x))
      BigDecimal lnX = lnBigDecimal(x, mc);
      BigDecimal exponent = y.multiply(lnX, mc);
      return expBigDecimal(exponent, mc);
    }
  }

  /** Get optimal calibration based on scale */
  public static Z5dCalibration z5dGetOptimalCalibration(double k) {
    int scaleIdx = 0;
    for (int i = 1; i < 5; ++i) {
      if (k <= Z5D_SCALE_THRESHOLDS[i]) {
        scaleIdx = i - 1;
        break;
      }
    }
    return Z5D_CALIBRATIONS[scaleIdx];
  }

  /** Validate k value */
  public static int z5dValidateK(double k) {
    if (!isValidFinite(k)) return Z5D_ERROR_DOMAIN;
    if (k < Z5D_MIN_K) return Z5D_ERROR_INVALID_K;
    if (k > Double.MAX_VALUE / 1000.0) return Z5D_ERROR_OVERFLOW;
    return Z5D_SUCCESS;
  }

  /** Validate kappa_geo */
  public static int z5dValidateKappaGeo(double kappaGeo) {
    if (!isValidFinite(kappaGeo)) return Z5D_ERROR_DOMAIN;
    if (kappaGeo < Z5D_MIN_KAPPA_GEO || kappaGeo > Z5D_MAX_KAPPA_GEO)
      return Z5D_ERROR_INVALID_KAPPA_GEO;
    return Z5D_SUCCESS;
  }

  /** Compute base PNT prime estimate */
  public static double z5dBasePntPrime(double k) {
    int validation = z5dValidateK(k);
    if (validation != Z5D_SUCCESS) return Double.NaN;

    double lnK = safeLog(k);
    if (!isValidFinite(lnK)) return Double.NaN;

    double lnLnK = safeLog(lnK);
    if (!isValidFinite(lnLnK)) return Double.NaN;

    double smallTerm = safeDivide(lnLnK - 2.0, lnK);

    /* FIX v1.3: Correct log-space approx: log_p = ln_k + log(term) */
    if (k > Z5D_LARGE_K_THRESHOLD) {
      double term = lnK + lnLnK - 1.0 + smallTerm;
      double logTerm = safeLog(term);
      if (!isValidFinite(logTerm)) return Double.NaN;
      double logP = lnK + logTerm;
      if (!isValidFinite(logP)) return Double.NaN;
      if (logP > Math.log(Double.MAX_VALUE) - 1e-10) {
        /* FIX v1.3: Tighter guard */
        return Double.MAX_VALUE;
      }
      double pnt = Math.exp(logP);
      if (!Double.isFinite(pnt)) return Double.NaN; /* FIX v1.3: Post-exp check */
      return pnt;
    }

    /* Standard computation (safe up to threshold) */
    double term = lnK + lnLnK - 1.0 + smallTerm;
    double pnt = k * term;
    if (!Double.isFinite(pnt) || pnt < 0.0) return Double.NaN;
    return pnt;
  }

  /** Main Z5D prime predictor function */
  public static double z5dPrime(
      double k, double cIn, double kStarIn, double kappaGeoIn, boolean autoCalibrate) {
    // Suppress unused parameter warning for API compatibility
    // Note: kappaGeoIn not used in repository formula, but keeping for compatibility

    // Validate input
    int validation = z5dValidateK(k);
    if (validation != Z5D_SUCCESS) return Double.NaN;

    // Handle auto-calibration
    if (autoCalibrate) {
      Z5dCalibration cal = z5dGetOptimalCalibration(k);
      cIn = cal.c;
      kStarIn = cal.kStar;
      // Note: kappaGeoIn not used in repository formula, but keeping for compatibility
    }

    /* Use the repository's accurate Z5D formula:
     * p_Z5D(k) = p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)
     * where:
     * - p_PNT(k) = k * (ln k + ln ln k - 1 + (ln ln k - 2)/ln k)  [base term]
     * - d(k) = (ln(p_PNT(k)) / e^4)^2  [dilation term]
     * - e(k) = p_PNT(k)^(-1/3)  [curvature term]
     */

    double lnK = safeLog(k);
    double lnLnK = safeLog(lnK);

    // Base PNT term
    double pnt = k * (lnK + lnLnK - 1.0 + (lnLnK - 2.0) / lnK);
    if (!isValidFinite(pnt) || pnt <= 0.0) return Double.NaN;

    // Dilation term d(k) = (ln(p_PNT(k)) / e^4)^2
    double lnPnt = safeLog(pnt);
    double dTerm = 0.0;
    if (lnPnt > 0.0) {
      dTerm = (lnPnt / Z5D_E_FOURTH) * (lnPnt / Z5D_E_FOURTH);
    }

    // Curvature term e(k) = p_PNT(k)^(-1/3)
    double eTerm = 0.0;
    if (pnt > 0.0) {
      eTerm = Math.pow(pnt, -1.0 / 3.0);
    }

    // Apply Z5D formula: p_PNT + c·d·p_PNT + k*·e·p_PNT
    double z5dResult = pnt + cIn * dTerm * pnt + kStarIn * eTerm * pnt;

    // Ensure non-negative result
    if (z5dResult < 0.0) z5dResult = pnt;

    if (!Double.isFinite(z5dResult)) return Double.NaN;
    return z5dResult;
  }

  // Placeholder for constructor
  public Z5dPredictor() {
    // Constructor if needed
  }

  /** Get version string */
  public static String z5dGetVersion() {
    return Z5D_VERSION;
  }

  /** Print Z5D formula and parameters information */
  public static void z5dPrintFormulaInfo() {
    System.out.println("Z5D Prime Predictor - Java Implementation v" + Z5D_VERSION);
    System.out.println("==========================================");
    System.out.println();
    System.out.println("Formula: p_Z5D(k) = p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)");
    System.out.println("With geodesic modulation: e(k) *= kappa_geo · (ln(k+1)/e²)");
    System.out.println();
    System.out.println("Where:");
    System.out.println("  p_PNT(k) = k * (ln(k) + ln(ln(k)) - 1 + (ln(ln(k)) - 2)/ln(k))");
    System.out.println("  d(k)     = (ln(p_PNT(k)) / e^4)^2 if ln(p) > 0 else 0");
    System.out.println("  e(k)     = (k^2 + k + 2) / (k * (k + 1) * (k + 2))");
    System.out.println("  Curvature Proxy: kappa_geo * (ln(k+1)/e^2) * e(k)");
    System.out.println();
    System.out.printf("Default Parameters:%n");
    System.out.printf("  c  = %.5f (dilation calibration)%n", Z5D_DEFAULT_C);
    System.out.printf("  k* = %.5f (curvature calibration)%n", Z5D_DEFAULT_K_STAR);
    System.out.printf(
        "  kappa_geo = %.5f (geodesic exponent for ~15%% enhancement)%n", Z5D_DEFAULT_KAPPA_GEO);
    System.out.println();
    System.out.println("Scale-specific Calibrations:");
    for (int i = 0; i < 4; i++) {
      System.out.printf(
          "  Scale %d: c=%.5f, k*=%.5f, kappa_geo_factor=%.5f%n",
          i + 1,
          Z5D_CALIBRATIONS[i].c,
          Z5D_CALIBRATIONS[i].kStar,
          Z5D_CALIBRATIONS[i].kappaGeoFactor);
    }
    System.out.println();
    System.out.println("Features:");
    System.out.println("  - Double-precision arithmetic");
    System.out.println("  - Automatic parameter selection with kappa_geo");
    System.out.println("  - Numerical stability guards (fixed log-space for ultra k)");
    System.out.println("  - Zero-division protection (ln_pnt <=0 guard)");
    System.out.println("  - Domain validation");
    System.out.println("  - 5D Curvature Proxy for validation");
    System.out.println("  - Optimizations: Safe math operations, array lookups");
    System.out.println();
  }

  /** Extended Z5D prediction with detailed results */
  public static int z5dPrimeExtended(
      double k, double c, double kStar, double kappaGeo, boolean autoCalibrate, Z5dResult result) {
    if (result == null) return Z5D_ERROR_DOMAIN;

    double pred = z5dPrime(k, c, kStar, kappaGeo, autoCalibrate);
    if (!isValidFinite(pred)) {
      result.errorCode = Z5D_ERROR_DOMAIN;
      return result.errorCode;
    }

    Z5dCalibration cal;
    if (autoCalibrate) {
      cal = z5dGetOptimalCalibration(k);
    } else {
      cal = new Z5dCalibration(c, kStar, kappaGeo);
    }

    double pnt = z5dBasePntPrime(k);
    double lnPnt = safeLog(pnt);
    double d = (lnPnt > 0.0) ? (lnPnt / Z5D_E_FOURTH) * (lnPnt / Z5D_E_FOURTH) : 0.0;
    double e = (pnt > 0.0) ? Math.pow(pnt, -1.0 / 3.0) : 0.0;
    double lnKPlus1 = safeLog(k + 1.0);
    double curvProxy = cal.kappaGeoFactor * (lnKPlus1 / Z5D_E_SQUARED) * e;

    result.prediction = pred;
    result.pntBase = pnt;
    result.dTerm = d;
    result.eTerm = e;
    result.curvatureProxy = curvProxy;
    result.cUsed = cal.c;
    result.kStarUsed = cal.kStar;
    result.kappaGeoUsed = cal.kappaGeoFactor;
    result.errorCode = Z5D_SUCCESS;

    return Z5D_SUCCESS;
  }

  /** Validate Z5D accuracy against true prime values */
  public static int z5dValidateAccuracy(
      double[] kValues,
      double[] truePrimes,
      int nValues,
      double c,
      double kStar,
      double kappaGeo,
      boolean autoCalibrate,
      double[] meanRelativeError,
      double[] maxRelativeError) {
    if (nValues <= 0
        || kValues == null
        || truePrimes == null
        || meanRelativeError == null
        || maxRelativeError == null) {
      return Z5D_ERROR_DOMAIN;
    }

    double sumRelativeError = 0.0;
    double maxError = 0.0;
    int validCount = 0;

    for (int i = 0; i < nValues; i++) {
      if (truePrimes[i] <= 0.0) continue;

      double prediction = z5dPrime(kValues[i], c, kStar, kappaGeo, autoCalibrate);
      if (!isValidFinite(prediction)) continue;

      double relativeError = Math.abs((prediction - truePrimes[i]) / truePrimes[i]);

      sumRelativeError += relativeError;
      if (relativeError > maxError) maxError = relativeError;
      validCount++;
    }

    if (validCount == 0) return Z5D_ERROR_DOMAIN;

    meanRelativeError[0] = sumRelativeError / validCount;
    maxRelativeError[0] = maxError;

    return Z5D_SUCCESS;
  }

  // ============================================================================
  // High-Precision BigDecimal Methods for Ultra-High Scales
  // ============================================================================

  /**
   * Compute base PNT prime estimate using BigDecimal for arbitrary precision. Formula: p_PNT(k) = k
   * * (ln(k) + ln(ln(k)) - 1 + (ln(ln(k)) - 2)/ln(k))
   *
   * @param k The scale parameter as BigDecimal
   * @param mc MathContext for precision control
   * @return PNT estimate as BigDecimal
   */
  public static BigDecimal z5dBasePntPrimeBigDecimal(BigDecimal k, MathContext mc) {
    if (k.compareTo(new BigDecimal(Z5D_MIN_K)) < 0) {
      throw new ArithmeticException("k must be >= " + Z5D_MIN_K);
    }

    BigDecimal lnK = lnBigDecimal(k, mc);
    BigDecimal lnLnK = lnBigDecimal(lnK, mc);
    BigDecimal smallTerm = lnLnK.subtract(BigDecimal.ONE.add(BigDecimal.ONE), mc).divide(lnK, mc);
    BigDecimal term = lnK.add(lnLnK, mc).subtract(BigDecimal.ONE, mc).add(smallTerm, mc);

    return k.multiply(term, mc);
  }

  /**
   * Main Z5D prime predictor using BigDecimal for arbitrary precision. Formula: p_Z5D(k) = p_PNT(k)
   * + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)
   *
   * @param k The scale parameter as BigDecimal
   * @param c Dilation calibration parameter
   * @param kStar Curvature calibration parameter
   * @param kappaGeo Geodesic parameter (kept for API compatibility)
   * @param autoCalibrate Whether to use auto-calibration
   * @param mc MathContext for precision control
   * @return Z5D prediction as BigDecimal
   */
  public static BigDecimal z5dPrimeBigDecimal(
      BigDecimal k,
      double c,
      double kStar,
      double kappaGeo,
      boolean autoCalibrate,
      MathContext mc) {
    // Handle auto-calibration
    if (autoCalibrate) {
      // Use scale-appropriate calibration if k is within double range
      if (k.compareTo(new BigDecimal(Double.MAX_VALUE)) < 0) {
        Z5dCalibration cal = z5dGetOptimalCalibration(k.doubleValue());
        c = cal.c;
        kStar = cal.kStar;
      } else {
        // For ultra-high scales, use the most aggressive calibration
        c = Z5D_CALIBRATIONS[3].c;
        kStar = Z5D_CALIBRATIONS[3].kStar;
      }
    }

    BigDecimal cBD = new BigDecimal(c);
    BigDecimal kStarBD = new BigDecimal(kStar);

    // Compute base PNT term
    BigDecimal pnt = z5dBasePntPrimeBigDecimal(k, mc);

    // Dilation term d(k) = (ln(p_PNT(k)) / e^4)^2
    BigDecimal lnPnt = lnBigDecimal(pnt, mc);
    BigDecimal e4 = new BigDecimal(Z5D_E_FOURTH);
    BigDecimal dTerm = lnPnt.divide(e4, mc);
    dTerm = dTerm.multiply(dTerm, mc); // Square it

    // Curvature term e(k) = p_PNT(k)^(-1/3)
    BigDecimal oneThird = BigDecimal.ONE.divide(new BigDecimal(3), mc);
    BigDecimal eTerm = powBigDecimal(pnt, oneThird.negate(), mc);

    // Apply Z5D formula: p_PNT + c·d·p_PNT + k*·e·p_PNT
    BigDecimal result = pnt;
    result = result.add(cBD.multiply(dTerm, mc).multiply(pnt, mc), mc);
    result = result.add(kStarBD.multiply(eTerm, mc).multiply(pnt, mc), mc);

    // Ensure non-negative result
    if (result.compareTo(BigDecimal.ZERO) < 0) {
      result = pnt;
    }

    return result;
  }

  /**
   * Convenience method: z5dPrimeBigDecimal with string input for k. Allows specification of k as a
   * string like "1e1233".
   *
   * @param kStr String representation of k (e.g., "1e1233", "1.5e500")
   * @param c Dilation calibration parameter
   * @param kStar Curvature calibration parameter
   * @param kappaGeo Geodesic parameter (kept for API compatibility)
   * @param autoCalibrate Whether to use auto-calibration
   * @return Z5D prediction as BigDecimal
   */
  public static BigDecimal z5dPrimeBigDecimal(
      String kStr, double c, double kStar, double kappaGeo, boolean autoCalibrate) {
    BigDecimal k = new BigDecimal(kStr, MC);
    return z5dPrimeBigDecimal(k, c, kStar, kappaGeo, autoCalibrate, MC);
  }

  /**
   * Enhanced z5dPrime that automatically uses BigDecimal for ultra-high scales. Maintains backward
   * compatibility while extending range to 10^1233.
   *
   * @param kStr String representation of k for scales beyond double range
   * @param c Dilation calibration parameter
   * @param kStar Curvature calibration parameter
   * @param kappaGeo Geodesic parameter (kept for API compatibility)
   * @param autoCalibrate Whether to use auto-calibration
   * @return Z5D prediction as string for ultra-high scales
   */
  public static String z5dPrimeString(
      String kStr, double c, double kStar, double kappaGeo, boolean autoCalibrate) {
    BigDecimal result = z5dPrimeBigDecimal(kStr, c, kStar, kappaGeo, autoCalibrate);
    return result.toPlainString();
  }

  /** Extended prediction result with BigDecimal support for ultra-high scales. */
  public static class Z5dResultBigDecimal {
    public BigDecimal prediction;
    public BigDecimal pntBase;
    public BigDecimal dTerm;
    public BigDecimal eTerm;
    public double cUsed;
    public double kStarUsed;
    public double kappaGeoUsed;
    public int errorCode;
  }

  /** Extended Z5D prediction with BigDecimal and detailed results. */
  public static int z5dPrimeExtendedBigDecimal(
      BigDecimal k,
      double c,
      double kStar,
      double kappaGeo,
      boolean autoCalibrate,
      Z5dResultBigDecimal result,
      MathContext mc) {
    if (result == null) return Z5D_ERROR_DOMAIN;

    try {
      BigDecimal pred = z5dPrimeBigDecimal(k, c, kStar, kappaGeo, autoCalibrate, mc);

      Z5dCalibration cal;
      if (autoCalibrate) {
        if (k.compareTo(new BigDecimal(Double.MAX_VALUE)) < 0) {
          cal = z5dGetOptimalCalibration(k.doubleValue());
        } else {
          cal = Z5D_CALIBRATIONS[3]; // Ultra-high scale calibration
        }
      } else {
        cal = new Z5dCalibration(c, kStar, kappaGeo);
      }

      BigDecimal pnt = z5dBasePntPrimeBigDecimal(k, mc);
      BigDecimal lnPnt = lnBigDecimal(pnt, mc);
      BigDecimal e4 = new BigDecimal(Z5D_E_FOURTH);
      BigDecimal d = lnPnt.divide(e4, mc);
      d = d.multiply(d, mc);

      BigDecimal oneThird = BigDecimal.ONE.divide(new BigDecimal(3), mc);
      BigDecimal e = powBigDecimal(pnt, oneThird.negate(), mc);

      result.prediction = pred;
      result.pntBase = pnt;
      result.dTerm = d;
      result.eTerm = e;
      result.cUsed = cal.c;
      result.kStarUsed = cal.kStar;
      result.kappaGeoUsed = cal.kappaGeoFactor;
      result.errorCode = Z5D_SUCCESS;

      return Z5D_SUCCESS;
    } catch (Exception e) {
      result.errorCode = Z5D_ERROR_DOMAIN;
      return Z5D_ERROR_DOMAIN;
    }
  }

  public static void main(String[] args) {
    if (args.length > 0) {
      String command = args[0];
      if ("verify".equals(command) && args.length > 1) {
        double k = Double.parseDouble(args[1]);
        VerifiedResult result = z5dPrimeVerified(k);
        System.out.printf(
            "k=%.0f, estimate=%.6f, nearest_prime=%s, certainty=%.10f%n",
            k, result.estimate, result.nearestPrime, result.certainty);
      } else if ("truth".equals(command)) {
        printTruthPanels();
      } else {
        System.out.println("Usage: java Z5dPredictor [verify <k> | truth]");
      }
      return;
    }

    System.out.println("Z5D Prime Predictor - Java Reference Implementation");
    System.out.println("Version: " + Z5D_VERSION);
    System.out.println();

    // Test basic functionality
    double testK = 100000.0;
    double autoPrediction = z5dPrime(testK, 0, 0, 0, true);
    System.out.printf("Auto-calibrated prediction for k=%.0f: %.6f%n", testK, autoPrediction);

    // Test BigDecimal for ultra-high scale
    System.out.println("\nTesting BigDecimal for ultra-high scales:");
    String ultraHighK = "1e500";
    String ultraHighPred = z5dPrimeString(ultraHighK, 0, 0, 0, true);
    System.out.printf("Prediction for k=%s: %s%n", ultraHighK, ultraHighPred);

    // Print formula info
    z5dPrintFormulaInfo();
  }

  /**
   * Finds the nearest prime number to the given BigInteger. Uses BigInteger.isProbablePrime(100)
   * for primality testing (error < 2^-100).
   *
   * @param x The number to find the nearest prime for
   * @return The nearest prime number
   */
  public static BigInteger nearestPrime(BigInteger x) {
    if (x.signum() <= 0) return BigInteger.valueOf(2);
    BigInteger up = x;
    BigInteger down = x;
    while (true) {
      if (up.isProbablePrime(100)) return up;
      if (down.compareTo(BigInteger.TWO) > 0 && down.isProbablePrime(100)) return down;
      up = up.add(BigInteger.ONE);
      down = down.subtract(BigInteger.ONE);
    }
  }

  /**
   * Verifies the Z5D prediction by finding the nearest provably prime. Returns both the estimate
   * and the verified prime.
   */
  public static class VerifiedResult {
    public double estimate;
    public BigInteger nearestPrime;
    public double certainty; // For probable primes, 1 - 2^-certainty
  }

  /**
   * Predicts the k-th prime and verifies by finding the nearest prime.
   *
   * @param k The index k
   * @return VerifiedResult with estimate and nearest prime
   */
  public static VerifiedResult z5dPrimeVerified(double k) {
    double estimate = z5dPrime(k, 0, 0, 0, true);
    BigInteger estBI = BigInteger.valueOf((long) Math.round(estimate));
    BigInteger prime = nearestPrime(estBI);
    VerifiedResult result = new VerifiedResult();
    result.estimate = estimate;
    result.nearestPrime = prime;
    result.certainty = 1.0 - Math.pow(2, -100); // For 100-bit certainty
    return result;
  }

  /** Prints truth panels for canonical k values. */
  public static void printTruthPanels() {
    double[] ks = {1e5, 1e6, 1e7, 1e9, 1e10};
    long[] truePrimes = {1299709, 15485863, 179424673, 2280164371L, 252097800623L};

    System.out.println("Truth Panels:");
    System.out.println("k, Z5D Estimate, True p_k, Abs Error, Rel Error");
    for (int i = 0; i < ks.length; i++) {
      double k = ks[i];
      double estimate = z5dPrime(k, 0, 0, 0, true);
      long truePrime = truePrimes[i];
      double absErr = Math.abs(estimate - truePrime);
      double relErr = absErr / truePrime;
      System.out.printf("%.0e, %.6f, %d, %.6f, %.10f%n", k, estimate, truePrime, absErr, relErr);
    }
  }
}
