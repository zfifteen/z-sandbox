package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import java.util.stream.DoubleStream;

public class TestZ5dParallel {
  @Test
  void parallel_predictions_noNaNs() {
    double[] ks = DoubleStream.iterate(1e3, x -> x*1.3).limit(50).toArray();
    long bad = DoubleStream.of(ks).parallel()
      .map(k -> Z5dPredictor.z5dPrime(k, 0, 0, 0, true))
      .filter(v -> !Double.isFinite(v) || v <= 0.0)
      .count();
    assertEquals(0, bad, "non-finite/≤0 values exist in parallel path");
  }
}