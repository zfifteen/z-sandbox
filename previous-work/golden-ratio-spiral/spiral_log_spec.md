# Spiral Log Specification

To enable proper parsing and regression, output per-candidate rows in one of the following formats. This ensures structured data for per-center OLS fits, avoiding parse failures from narrative text.

## Required Fields Per Candidate
- `center`: The starting integer (e.g., 1000000).
- `it`: Number of iterations (B in Z = A(B / c)).
- `value`: The final value after spiral (typically a bigint, but log it as string for precision).
- `area`: Geometric area proxy (e.g., scale_x * scale_y; if not tracked, estimate as radius^2 * pi or similar).

## Optional Fields
- `radius`: Spiral radius.
- `scale_x`: Secondary scale (e.g., 50).
- `scale_y`: Secondary scale (e.g., 30).
- `timestamp_ns`: Nanosecond timestamp for timing.

## Output Formats

### CSV Format (Preferred)
Header line: `center,it,value,area,radius,scale_x,scale_y,timestamp_ns`
Each row: comma-separated values (escape commas in strings if needed).
Example:
```
center,it,value,area,radius,scale_x,scale_y,timestamp_ns
1000000,11,1000151,1500,100.5,50,30,1234567890123456
271340807,13,271340820,800000,1000.0,1000,800,1234567890123457
```

### Key-Value Format (Alternative)
Each candidate on a new line, space-separated key=value pairs.
Example:
center=1000000 it=11 value=1000151 area=1500 radius=100.5 scale_x=50 scale_y=30 timestamp_ns=1234567890123456
center=271340807 it=13 value=271340820 area=800000 radius=1000.0 scale_x=1000 scale_y=800 timestamp_ns=1234567890123457

## Notes
- Output to stdout or a file like `golden_spiral_out.txt`.
- For regression, use B = it / area (rate-normalized).
- Ensure at least 5 rows per center for meaningful OLS.