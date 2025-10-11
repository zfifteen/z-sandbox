package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

public class TestDomain {
  @Test
  public void testGetters() {
    Domain d = new Domain(1);
    double relTol = 1e-14; // Relative tolerance for floating-point comparisons

    // Test existing getters with relative error
    double expectedD = d.getB() / d.getC();
    double actualD = d.getD();
    System.out.printf(
        "getD(): expected=%.20f, actual=%.20f, diff=%.2e%n",
        expectedD, actualD, Math.abs(expectedD - actualD));
    assertRelativeEquals(expectedD, actualD, relTol);
    assertRelativeEquals(d.getC() / d.getD(), d.getE(), relTol);
    assertRelativeEquals(d.getD() / d.getE(), d.getF(), relTol);
  }

  private void assertRelativeEquals(double expected, double actual, double relTol) {
    double relError = Math.abs((expected - actual) / expected);
    assertTrue(
        relError <= relTol,
        String.format(
            "Relative error too large: expected=%.20f, actual=%.20f, relError=%.2e, relTol=%.2e",
            expected, actual, relError, relTol));
  }
}
