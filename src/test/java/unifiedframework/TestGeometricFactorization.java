package unifiedframework;

import static org.junit.Assert.*;

import gva.GaussLegendreQuadrature;
import gva.SphericalFluxDistance;
import gva.Embedding;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import org.junit.Test;

/**
 * Tests for Geometric Factorization Design improvements.
 * Validates Gauss-Legendre quadrature, spherical flux distance, and enhanced embeddings.
 */
public class TestGeometricFactorization {

  private static final MathContext MC = new MathContext(100);

  @Test
  public void testGaussLegendreNodes() {
    // Test 8-point quadrature
    double[] nodes8 = GaussLegendreQuadrature.getNodes(8);
    assertEquals("8-point quadrature should have 8 nodes", 8, nodes8.length);
    
    // Nodes should be symmetric around 0
    assertEquals("First and last nodes should be symmetric", 
                 nodes8[0], -nodes8[7], 1e-15);
    
    // All nodes should be in [-1, 1]
    for (double node : nodes8) {
      assertTrue("Node should be >= -1", node >= -1.0);
      assertTrue("Node should be <= 1", node <= 1.0);
    }
  }

  @Test
  public void testGaussLegendreWeights() {
    // Test that weights sum to 2.0 (integral over [-1, 1])
    double[] weights8 = GaussLegendreQuadrature.getWeights(8);
    double sum = 0.0;
    for (double w : weights8) {
      sum += w;
      assertTrue("Weight should be positive", w > 0);
    }
    assertEquals("Weights should sum to 2.0", 2.0, sum, 1e-12);
  }

  @Test
  public void testGaussLegendre16Point() {
    double[] nodes16 = GaussLegendreQuadrature.getNodes(16);
    double[] weights16 = GaussLegendreQuadrature.getWeights(16);
    
    assertEquals("16-point quadrature", 16, nodes16.length);
    assertEquals("16 weights", 16, weights16.length);
    
    // Check symmetry
    for (int i = 0; i < 8; i++) {
      assertEquals("Nodes should be symmetric", 
                   nodes16[i], -nodes16[15-i], 1e-15);
      assertEquals("Weights should be symmetric", 
                   weights16[i], weights16[15-i], 1e-15);
    }
  }

  @Test
  public void testMapToTheta() {
    // Node -1 should map to 0
    double theta0 = GaussLegendreQuadrature.mapToTheta(-1.0);
    assertEquals("Node -1 maps to θ=0", 0.0, theta0, 1e-15);
    
    // Node 1 should map to π
    double thetaPi = GaussLegendreQuadrature.mapToTheta(1.0);
    assertEquals("Node 1 maps to θ=π", Math.PI, thetaPi, 1e-15);
    
    // Node 0 should map to π/2
    double thetaHalf = GaussLegendreQuadrature.mapToTheta(0.0);
    assertEquals("Node 0 maps to θ=π/2", Math.PI / 2.0, thetaHalf, 1e-15);
  }

  @Test
  public void testComputePhi() {
    // Test golden ratio spacing
    double phi0 = GaussLegendreQuadrature.computePhi(0);
    double phi1 = GaussLegendreQuadrature.computePhi(1);
    
    assertTrue("φ should be in [0, 2π]", phi0 >= 0 && phi0 <= 2 * Math.PI);
    assertTrue("φ should be in [0, 2π]", phi1 >= 0 && phi1 <= 2 * Math.PI);
    
    // Should not be equal (golden ratio spacing)
    assertNotEquals("φ values should differ", phi0, phi1, 1e-10);
  }

  @Test
  public void testSphericalFluxDistanceSymmetry() {
    SphericalFluxDistance fluxDist = new SphericalFluxDistance(MC);
    
    // Create two simple embeddings (4D: 2 θ,φ pairs)
    BigDecimal[] coords1 = {
      new BigDecimal("0.25"), new BigDecimal("0.5"),  // θ₁=π/4, φ₁=π
      new BigDecimal("0.75"), new BigDecimal("0.25")  // θ₂=3π/4, φ₂=π/2
    };
    
    BigDecimal[] coords2 = {
      new BigDecimal("0.3"), new BigDecimal("0.6"),
      new BigDecimal("0.7"), new BigDecimal("0.3")
    };
    
    BigInteger N = new BigInteger("10007"); // Small prime
    
    // Distance should be symmetric
    BigDecimal dist12 = fluxDist.distance(coords1, coords2, N);
    BigDecimal dist21 = fluxDist.distance(coords2, coords1, N);
    
    assertEquals("Distance should be symmetric", 
                 dist12.doubleValue(), dist21.doubleValue(), 1e-10);
    
    // Distance to self should be zero
    BigDecimal dist11 = fluxDist.distance(coords1, coords1, N);
    assertTrue("Distance to self should be zero", 
               dist11.compareTo(new BigDecimal("0.001")) < 0);
  }

  @Test
  public void testSphericalFluxDistanceNonNegative() {
    SphericalFluxDistance fluxDist = new SphericalFluxDistance(MC);
    
    BigDecimal[] coords1 = {
      new BigDecimal("0.1"), new BigDecimal("0.2"),
      new BigDecimal("0.8"), new BigDecimal("0.9")
    };
    
    BigDecimal[] coords2 = {
      new BigDecimal("0.4"), new BigDecimal("0.5"),
      new BigDecimal("0.6"), new BigDecimal("0.7")
    };
    
    BigInteger N = new BigInteger("100003");
    
    BigDecimal dist = fluxDist.distance(coords1, coords2, N);
    
    assertTrue("Distance should be non-negative", 
               dist.compareTo(BigDecimal.ZERO) >= 0);
  }

  @Test
  public void testEnhancedTorusSphericalEmbedding() {
    Embedding embedding = new Embedding(MC);
    
    BigInteger n = new BigInteger("1000000007"); // Large prime
    int dims = 8; // 4 (θ,φ) pairs
    
    BigDecimal[] coords = embedding.embedTorusSpherical(n, dims);
    
    assertEquals("Should have correct dimensions", dims, coords.length);
    
    // All coordinates should be in [0, 1]
    for (int i = 0; i < coords.length; i++) {
      assertTrue("Coord should be >= 0", coords[i].compareTo(BigDecimal.ZERO) >= 0);
      assertTrue("Coord should be <= 1", coords[i].compareTo(BigDecimal.ONE) <= 0);
    }
  }

  @Test
  public void testEnhancedEmbeddingDeterministic() {
    Embedding embedding = new Embedding(MC);
    
    BigInteger n = new BigInteger("987654321");
    int dims = 6;
    
    BigDecimal[] coords1 = embedding.embedTorusSpherical(n, dims);
    BigDecimal[] coords2 = embedding.embedTorusSpherical(n, dims);
    
    // Should be deterministic
    for (int i = 0; i < dims; i++) {
      assertEquals("Embedding should be deterministic",
                   coords1[i].doubleValue(), coords2[i].doubleValue(), 1e-10);
    }
  }

  @Test
  public void testFluxWeightedDistance() {
    SphericalFluxDistance fluxDist = new SphericalFluxDistance(MC);
    
    BigDecimal[] coords1 = {
      new BigDecimal("0.5"), new BigDecimal("0.5"),  // Near equator (θ≈π/2)
      new BigDecimal("0.5"), new BigDecimal("0.0")
    };
    
    BigDecimal[] coords2 = {
      new BigDecimal("0.55"), new BigDecimal("0.55"),
      new BigDecimal("0.55"), new BigDecimal("0.1")
    };
    
    BigInteger N = new BigInteger("1000003");
    
    BigDecimal dist = fluxDist.fluxWeightedDistance(coords1, coords2, N);
    
    assertTrue("Flux-weighted distance should be positive", 
               dist.compareTo(BigDecimal.ZERO) > 0);
  }

  @Test
  public void testGaussLegendreIntegrationAccuracy() {
    // Test that Gauss-Legendre can accurately integrate polynomials
    // For 8-point rule: integrates exactly up to degree 15
    
    double[] nodes = GaussLegendreQuadrature.getNodes(8);
    double[] weights = GaussLegendreQuadrature.getWeights(8);
    
    // Integrate f(x) = x^2 over [-1, 1]
    // Exact integral: ∫_{-1}^{1} x^2 dx = 2/3
    double integral = 0.0;
    for (int i = 0; i < nodes.length; i++) {
      double x = nodes[i];
      double fx = x * x; // f(x) = x^2
      integral += weights[i] * fx;
    }
    
    double expected = 2.0 / 3.0;
    assertEquals("Should integrate x^2 exactly", expected, integral, 1e-14);
  }

  @Test
  public void testSphericalEmbeddingDifferentNumbers() {
    Embedding embedding = new Embedding(MC);
    
    BigInteger n1 = new BigInteger("1009");
    BigInteger n2 = new BigInteger("1013");
    int dims = 4;
    
    BigDecimal[] coords1 = embedding.embedTorusSpherical(n1, dims);
    BigDecimal[] coords2 = embedding.embedTorusSpherical(n2, dims);
    
    // Different numbers should have different embeddings
    boolean allSame = true;
    for (int i = 0; i < dims; i++) {
      if (Math.abs(coords1[i].doubleValue() - coords2[i].doubleValue()) > 1e-6) {
        allSame = false;
        break;
      }
    }
    
    assertFalse("Different numbers should have different embeddings", allSame);
  }

  @Test(expected = IllegalArgumentException.class)
  public void testSphericalEmbeddingOddDimensions() {
    Embedding embedding = new Embedding(MC);
    BigInteger n = new BigInteger("12345");
    
    // Should throw exception for odd dimensions
    embedding.embedTorusSpherical(n, 5);
  }

  @Test(expected = IllegalArgumentException.class)
  public void testGaussLegendreUnsupportedOrder() {
    // Should throw exception for unsupported order
    GaussLegendreQuadrature.getNodes(10);
  }

  @Test
  public void testFluxDistanceScalesWithN() {
    SphericalFluxDistance fluxDist = new SphericalFluxDistance(MC);
    
    BigDecimal[] coords1 = {
      new BigDecimal("0.3"), new BigDecimal("0.4"),
      new BigDecimal("0.6"), new BigDecimal("0.7")
    };
    
    BigDecimal[] coords2 = {
      new BigDecimal("0.35"), new BigDecimal("0.45"),
      new BigDecimal("0.65"), new BigDecimal("0.75")
    };
    
    BigInteger N_small = new BigInteger("1000");
    BigInteger N_large = new BigInteger("1000000000");
    
    BigDecimal distSmall = fluxDist.distance(coords1, coords2, N_small);
    BigDecimal distLarge = fluxDist.distance(coords1, coords2, N_large);
    
    // Distance should scale with log²N (larger N → smaller normalized distance)
    assertTrue("Distance should scale with N", 
               distSmall.compareTo(distLarge) > 0);
  }
}
