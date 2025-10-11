package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.stream.DoubleStream;
import org.junit.jupiter.api.Test;

public class TestZ5dParallel {
  @Test
  void parallel_predictions_noNaNs() {
    double[] ks = DoubleStream.iterate(1e3, x -> x * 1.3).limit(50).toArray();
    long bad =
        DoubleStream.of(ks)
            .parallel()
            .map(k -> Z5dPredictor.z5dPrime(k, 0, 0, 0, true))
            .filter(v -> !Double.isFinite(v) || v <= 0.0)
            .count();
    System.out.printf("Parallel test: ks length=%d, bad=%d%n", ks.length, bad);
    assertEquals(0, bad, "non-finite/≤0 values exist in parallel path");
  }

  @Test
  void concurrentLoad_threadSafety() throws InterruptedException, ExecutionException {
    int numThreads = 10;
    int tasksPerThread = 100;
    ExecutorService executor = Executors.newFixedThreadPool(numThreads);
    List<Future<Void>> futures = new ArrayList<>();

    System.out.printf(
        "Concurrent test: numThreads=%d, tasksPerThread=%d%n", numThreads, tasksPerThread);

    for (int i = 0; i < numThreads; i++) {
      futures.add(
          executor.submit(
              () -> {
                for (int j = 0; j < tasksPerThread; j++) {
                  double k = 1e3 + j * 1e2; // Vary k
                  double result = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
                  assertTrue(
                      Double.isFinite(result) && result > 0,
                      "Invalid result in concurrent execution");
                }
                return null;
              }));
    }

    for (Future<Void> future : futures) {
      future.get(); // Wait for completion
    }

    executor.shutdown();
    boolean terminated = executor.awaitTermination(10, TimeUnit.SECONDS);
    System.out.printf("Executor terminated: %b%n", terminated);
    assertTrue(terminated, "Executor did not terminate in time");
  }
}
