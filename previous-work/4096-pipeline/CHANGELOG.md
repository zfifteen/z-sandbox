# Changelog

## Unreleased

- Harden seed generation: require `/dev/urandom` and mix in host entropy via OpenSSL EVP.
- Introduce `--debug` and `--quiet` flags; keep legacy verbose output behind `--debug` while default runs are non-sensitive.
- Prime search telemetry now respects logging flags and OpenMP banner only appears in debug mode.
- Added OpenMP-aware parallel search helper, ensuring deterministic fallback when OpenMP is disabled.
- Enforced private key permissions (`0600`) via `umask(0077)` and `fchmod`; certificate serials now sourced from fresh entropy instead of the seed.
- Zeroize temporary entropy buffers before free; suppressed OpenSSL deprecation warnings with `-Wno-deprecated-declarations`.
- Documented new logging options in CLI usage and README references.
