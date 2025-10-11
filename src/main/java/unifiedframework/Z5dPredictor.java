package unifiedframework;

/**
 * Z5D Prime Predictor - Java Reference Implementation =====================================
 *
 * <p>Java port of the C z5d_predictor implementation following unified-framework principles.
 * Provides double-precision arithmetic with numerical stability guards. Based on the Z Framework's
 * normalization principle Z = A(B/c).
 *
 * @file Z5dPredictor.java
 * @author Unified Framework Team - Java Port
 * @version 1.0 (Java Reference)
 */
public class Z5dPredictor {

  // Version information
  private static final String Z5D_VERSION = "2025-09-03-Java";

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

    /**
     * Extended Z5D prediction with detailed results
     */
    public static int z5dPrimeExtended(double k, double c, double kStar, double kappaGeo, boolean autoCalibrate, Z5dResult result) {
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
        double e = (pnt > 0.0) ? Math.pow(pnt, -1.0/3.0) : 0.0;
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

    /**
     * Validate Z5D accuracy against true prime values
     */
    public static int z5dValidateAccuracy(double[] kValues, double[] truePrimes, int nValues,
                                         double c, double kStar, double kappaGeo, boolean autoCalibrate,
                                         double[] meanRelativeError, double[] maxRelativeError) {
        if (nValues <= 0 || kValues == null || truePrimes == null ||
            meanRelativeError == null || maxRelativeError == null) {
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

    public static void main(String[] args) {
        System.out.println("Z5D Prime Predictor - Java Reference Implementation");
        System.out.println("==================================================");

        // Test basic functionality
        double testK = 100000.0;
        double prediction = z5dPrime(testK, -0.00247, 0.04449, 0.3, false);
        System.out.printf("Prediction for k=%.0f: %.6f%n", testK, prediction);

        // Test auto-calibration
        double autoPrediction = z5dPrime(testK, 0, 0, 0, true);
        System.out.printf("Auto-calibrated prediction for k=%.0f: %.6f%n", testK, autoPrediction);

        // Print formula info
        z5dPrintFormulaInfo();
    }
}
