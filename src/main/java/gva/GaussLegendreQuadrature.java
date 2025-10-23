package gva;

/**
 * Gauss-Legendre Quadrature for numerical integration.
 * Provides nodes and weights for high-precision integration on [-1, 1].
 * 
 * Used for optimal sampling in geometric factorization where prime density
 * is higher near the "equator" (sinθ ≈ 1) of the torus manifold.
 */
public class GaussLegendreQuadrature {

  /**
   * Get Gauss-Legendre quadrature nodes for n-point rule.
   * Nodes are roots of Legendre polynomials on [-1, 1].
   * 
   * @param n Number of quadrature points (supported: 8, 16, 32)
   * @return Array of quadrature nodes
   */
  public static double[] getNodes(int n) {
    switch (n) {
      case 8:
        return NODES_8;
      case 16:
        return NODES_16;
      case 32:
        return NODES_32;
      default:
        throw new IllegalArgumentException("Unsupported quadrature order: " + n + ". Supported: 8, 16, 32");
    }
  }

  /**
   * Get Gauss-Legendre quadrature weights for n-point rule.
   * Weights sum to 2.0 over [-1, 1].
   * 
   * @param n Number of quadrature points (supported: 8, 16, 32)
   * @return Array of quadrature weights
   */
  public static double[] getWeights(int n) {
    switch (n) {
      case 8:
        return WEIGHTS_8;
      case 16:
        return WEIGHTS_16;
      case 32:
        return WEIGHTS_32;
      default:
        throw new IllegalArgumentException("Unsupported quadrature order: " + n + ". Supported: 8, 16, 32");
    }
  }

  /**
   * Map quadrature node from [-1, 1] to [0, π] for spherical coordinates.
   * Uses transformation: θ = π/2 * (node + 1)
   * 
   * @param node Gauss-Legendre node in [-1, 1]
   * @return Angle θ in [0, π]
   */
  public static double mapToTheta(double node) {
    return Math.PI * 0.5 * (node + 1.0);
  }

  /**
   * Compute φ angle using golden ratio spacing for uniform coverage.
   * φ = 2π * goldenRatioFrac(i) where goldenRatioFrac = frac(i * φ)
   * 
   * @param index Sample index
   * @return Angle φ in [0, 2π]
   */
  public static double computePhi(int index) {
    double goldenRatio = (1.0 + Math.sqrt(5.0)) / 2.0;
    double frac = (index * goldenRatio) % 1.0;
    return 2.0 * Math.PI * frac;
  }

  // 8-point Gauss-Legendre quadrature (precision: integrates polynomials up to degree 15)
  private static final double[] NODES_8 = {
    -0.9602898564975362,
    -0.7966664774136267,
    -0.5255324099163290,
    -0.1834346424956498,
     0.1834346424956498,
     0.5255324099163290,
     0.7966664774136267,
     0.9602898564975362
  };

  private static final double[] WEIGHTS_8 = {
    0.1012285362903763,
    0.2223810344533745,
    0.3137066458778873,
    0.3626837833783620,
    0.3626837833783620,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763
  };

  // 16-point Gauss-Legendre quadrature (precision: integrates polynomials up to degree 31)
  private static final double[] NODES_16 = {
    -0.9894009349916499,
    -0.9445750230732326,
    -0.8656312023878318,
    -0.7554044083550030,
    -0.6178762444026438,
    -0.4580167776572274,
    -0.2816035507792589,
    -0.0950125098376374,
     0.0950125098376374,
     0.2816035507792589,
     0.4580167776572274,
     0.6178762444026438,
     0.7554044083550030,
     0.8656312023878318,
     0.9445750230732326,
     0.9894009349916499
  };

  private static final double[] WEIGHTS_16 = {
    0.0271524594117541,
    0.0622535239386479,
    0.0951585116824928,
    0.1246289712555339,
    0.1495959888165767,
    0.1691565193950025,
    0.1826034150449236,
    0.1894506104550685,
    0.1894506104550685,
    0.1826034150449236,
    0.1691565193950025,
    0.1495959888165767,
    0.1246289712555339,
    0.0951585116824928,
    0.0622535239386479,
    0.0271524594117541
  };

  // 32-point Gauss-Legendre quadrature (precision: integrates polynomials up to degree 63)
  private static final double[] NODES_32 = {
    -0.9972638618494816,
    -0.9856115115452684,
    -0.9647622555875064,
    -0.9349060759377397,
    -0.8963211557660521,
    -0.8493676137325700,
    -0.7944837959679424,
    -0.7321821187402897,
    -0.6630442669302152,
    -0.5877157572407623,
    -0.5068999089322294,
    -0.4213512761306353,
    -0.3318686022821277,
    -0.2392873622521371,
    -0.1444719615827965,
    -0.0483076656877383,
     0.0483076656877383,
     0.1444719615827965,
     0.2392873622521371,
     0.3318686022821277,
     0.4213512761306353,
     0.5068999089322294,
     0.5877157572407623,
     0.6630442669302152,
     0.7321821187402897,
     0.7944837959679424,
     0.8493676137325700,
     0.8963211557660521,
     0.9349060759377397,
     0.9647622555875064,
     0.9856115115452684,
     0.9972638618494816
  };

  private static final double[] WEIGHTS_32 = {
    0.0070186100094701,
    0.0162743947309057,
    0.0253920653092621,
    0.0342738629130214,
    0.0428358980222267,
    0.0509980592623762,
    0.0586840934785355,
    0.0658222227763618,
    0.0723457941088485,
    0.0781938957870703,
    0.0833119242269467,
    0.0876520930044038,
    0.0911738786957639,
    0.0938443990808046,
    0.0956387200792749,
    0.0965400885147278,
    0.0965400885147278,
    0.0956387200792749,
    0.0938443990808046,
    0.0911738786957639,
    0.0876520930044038,
    0.0833119242269467,
    0.0781938957870703,
    0.0723457941088485,
    0.0658222227763618,
    0.0586840934785355,
    0.0509980592623762,
    0.0428358980222267,
    0.0342738629130214,
    0.0253920653092621,
    0.0162743947309057,
    0.0070186100094701
  };

  private GaussLegendreQuadrature() {
    // Utility class - prevent instantiation
  }
}
