# TRANSEC Standalone Package

## What is This?

The `transec_standalone/` directory contains a complete, production-ready implementation of TRANSEC (Time-Synchronized Encryption) extracted from the z-sandbox research framework and enhanced with suggested features from the community.

This standalone package is ready for:
- PyPI distribution
- Independent repository extraction  
- Production deployment
- Community contributions

## Quick Overview

TRANSEC is a zero-handshake encrypted messaging protocol inspired by military frequency-hopping COMSEC systems (SINCGARS, HAVE QUICK). It provides true zero-RTT communication using time-synchronized key rotation.

### Key Features

**Core TRANSEC** (from z-sandbox):
- Zero-RTT encryption with time-sliced keys
- HKDF-SHA256 key derivation  
- ChaCha20-Poly1305 AEAD
- Built-in replay protection
- Clock drift tolerance
- Prime optimization for enhanced stability

**New Enhancements** (community-suggested):
- **Adaptive Slot Duration**: PRNG-based dynamic timing (2-10s jitter) for anti-timing-analysis
- **OTAR-Lite**: Over-the-air key refresh with hash-based ratcheting for reduced exposure
- **CLI Tools**: Messenger and benchmark applications
- **PyPI-ready**: Complete package structure for distribution

## Quick Start

### From This Directory

```bash
cd transec_standalone

# Install in development mode
pip install -e .

# Run tests (40 tests, all passing)
python3 tests/test_transec.py
python3 tests/test_advanced.py

# Try the demo
python3 examples/demo.py

# Use the CLI messenger
python3 examples/transec_messenger.py generate
```

### Basic Usage

```python
from transec import TransecCipher, generate_shared_secret

# Setup
secret = generate_shared_secret()
sender = TransecCipher(secret)
receiver = TransecCipher(secret)

# Communicate (zero handshake!)
packet = sender.seal(b"Hello!", sequence=1)
plaintext = receiver.open(packet)  # b"Hello!"
```

### Advanced Features

```python
from transec import AdaptiveTransecCipher, OTARTransecCipher

# Adaptive timing (2-10s jitter)
adaptive = AdaptiveTransecCipher(secret, jitter_range=(2, 10))

# Auto key refresh (every hour)
otar = OTARTransecCipher(secret, refresh_interval=3600, auto_refresh=True)
```

## Documentation

- **[README.md](transec_standalone/README.md)**: Package overview and features
- **[QUICKSTART.md](transec_standalone/QUICKSTART.md)**: 5-minute getting started guide
- **[STANDALONE_README.md](transec_standalone/STANDALONE_README.md)**: Repository structure explanation
- **[CONTRIBUTING.md](transec_standalone/CONTRIBUTING.md)**: Contribution guidelines
- **[docs/](transec_standalone/docs/)**: Full protocol specifications

## Structure

```
transec_standalone/
├── transec/              # Core package
│   ├── core.py           # Base TransecCipher
│   ├── adaptive.py       # Adaptive slot duration (NEW)
│   ├── otar.py           # OTAR-Lite key refresh (NEW)
│   └── prime_optimization.py
│
├── examples/             # Demo applications
│   ├── demo.py           # Feature showcase
│   ├── transec_messenger.py  # CLI tool
│   └── transec_udp_demo.py   # Benchmark
│
├── tests/                # Test suite (40 tests)
├── docs/                 # Documentation
├── setup.py              # PyPI packaging
└── README.md             # Package README
```

## Testing

All tests pass:
```bash
$ cd transec_standalone
$ python3 tests/test_transec.py
Ran 25 tests in 0.015s - OK

$ python3 tests/test_advanced.py  
Ran 15 tests in 0.004s - OK
```

## Performance

Benchmark results (from examples/transec_udp_demo.py):
- **Throughput**: 2,942 msg/sec
- **Latency**: 0.34ms RTT
- **Success Rate**: 100%
- **Overhead**: ~36 bytes per packet

## Extracting to Independent Repository

To create a standalone TRANSEC repository:

```bash
# From z-sandbox root
cp -r transec_standalone/ ../transec/
cd ../transec

# Initialize git
git init
git add .
git commit -m "Initial commit: TRANSEC standalone package"

# Create remote and push
git remote add origin https://github.com/YOUR_USERNAME/transec.git
git push -u origin main
```

## Publishing to PyPI

```bash
cd transec_standalone

# Build distributions
python3 setup.py sdist bdist_wheel

# Upload (requires PyPI credentials)
python3 -m twine upload dist/*
```

## Relationship to z-sandbox

- **z-sandbox**: Multi-faceted research repository (factorization, QMC, TRANSEC, geometric methods)
- **transec_standalone**: Focused TRANSEC package for production use

The standalone version:
- ✅ Removes research-specific dependencies
- ✅ Adds production features (adaptive, OTAR)
- ✅ Provides clean PyPI package structure
- ✅ Maintains backward compatibility

Original z-sandbox TRANSEC files remain in `python/transec*.py` for integration with research code.

## Use Cases

- **Tactical Communications**: Drone swarms, battlefield mesh networks
- **Critical Infrastructure**: SCADA/DER telemetry, power grid protection
- **Autonomous Systems**: V2V messaging, vehicle platoons
- **Edge Computing**: Low-latency IoT mesh networks
- **High-Frequency Trading**: Sub-millisecond encrypted data feeds

## License

MIT License - see [LICENSE](transec_standalone/LICENSE)

## Credits

- Based on TRANSEC implementation from z-sandbox
- Enhanced with community suggestions (issue: "Create a Stand Alone TRANSEC Repository")
- Inspired by Hedy Lamarr's frequency-hopping patent
- Military COMSEC: HAVE QUICK, SINCGARS, Milstar OTAR

## Security Notice

TRANSEC is experimental software designed for research and specific use cases. While implemented with security best practices, it has not undergone formal security audit. Production deployment requires careful review and threat modeling.

For security concerns: security@example.com

## Contributing

See [CONTRIBUTING.md](transec_standalone/CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process
- Security issue reporting

## Further Reading

- [Zero-Handshake Property Analysis](transec_standalone/docs/ZERO_HANDSHAKE_PROPERTY_ANALYSIS.md)
- [Protocol Comparison](transec_standalone/docs/TRANSEC_PROTOCOL_COMPARISON.md) (vs TLS/QUIC/IPsec/Signal)
- [Prime Optimization](transec_standalone/docs/TRANSEC_PRIME_OPTIMIZATION.md)
- [Usage Guide](transec_standalone/docs/TRANSEC_USAGE.md)
