package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

public class TestZ5dTruthPanels {

  @Test
  void k1e6_matchesTruth_tight() {
    double k = 1_000_000d;
    double truth = 15_485_863d;   // p_1,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }

  @Test
  void k1e7_matchesTruth_tight() {
    double k = 10_000_000d;
    double truth = 179_424_673d;  // p_10,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }
}