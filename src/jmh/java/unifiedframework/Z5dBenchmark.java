package unifiedframework;

import org.openjdk.jmh.annotations.*;
import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1, timeUnit = TimeUnit.SECONDS)
@Measurement(iterations = 10, time = 1, timeUnit = TimeUnit.SECONDS)
@Fork(1)
@State(Scope.Benchmark)
public class Z5dBenchmark {

    @Param({"1000", "10000", "100000", "1000000"})
    public double k;

    @Benchmark
    public double benchmarkZ5dPrime() {
        return Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    }

    @Benchmark
    public double benchmarkZ5dPrimeNoCalibrate() {
        return Z5dPredictor.z5dPrime(k, 0, 0, 0, false);
    }
}