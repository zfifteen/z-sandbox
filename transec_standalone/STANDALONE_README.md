# TRANSEC Standalone Repository

## Overview

This directory contains a complete, standalone implementation of TRANSEC (Time-Synchronized Encryption) extracted from the z-sandbox research framework. It is structured as an independent Python package ready for PyPI distribution.

## What is TRANSEC?

TRANSEC is a zero-handshake encrypted messaging protocol inspired by military frequency-hopping COMSEC systems (SINCGARS, HAVE QUICK). It provides true zero-RTT communication using time-synchronized key rotation with HKDF-SHA256 and ChaCha20-Poly1305 AEAD.

## Repository Structure

```
transec_standalone/
├── transec/              # Core package
│   ├── __init__.py       # Package exports
│   ├── core.py           # Base TransecCipher implementation
│   ├── prime_optimization.py  # Prime slot normalization
│   ├── adaptive.py       # Adaptive slot duration (NEW)
│   └── otar.py           # OTAR-Lite key refresh (NEW)
│
├── examples/             # Demonstration applications
│   ├── demo.py           # Feature showcase
│   ├── transec_messenger.py  # CLI messenger tool
│   └── transec_udp_demo.py   # UDP benchmark
│
├── tests/                # Test suite
│   ├── test_transec.py   # Core functionality tests (25 tests)
│   └── test_advanced.py  # Advanced features tests (15 tests)
│
├── docs/                 # Documentation
│   ├── TRANSEC.md        # Full protocol specification
│   ├── TRANSEC_USAGE.md  # API reference and usage
│   └── TRANSEC_PROTOCOL_COMPARISON.md  # vs TLS/QUIC/IPsec/Signal
│
├── setup.py              # PyPI package configuration
├── requirements.txt      # Dependencies
├── README.md             # Package overview and quick start
├── QUICKSTART.md         # 5-minute getting started guide
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # MIT License
├── MANIFEST.in           # Package manifest
└── .gitignore            # Git ignore rules
```

## Key Features Implemented

### Core TRANSEC (from z-sandbox)
- ✅ Zero-RTT encryption with time-sliced keys
- ✅ HKDF-SHA256 key derivation
- ✅ ChaCha20-Poly1305 AEAD
- ✅ Replay protection via sequence tracking
- ✅ Clock drift tolerance (configurable window)
- ✅ Prime optimization for enhanced stability

### New Enhancements (as suggested in issue)
- ✅ **Adaptive Slot Duration**: PRNG-based dynamic timing (2-10s jitter)
- ✅ **OTAR-Lite**: Over-the-air key refresh with hash-based ratcheting
- ✅ **Package Structure**: Ready for PyPI publication
- ✅ **CLI Tools**: Messenger and UDP demo applications
- ✅ **Comprehensive Tests**: 40 total tests (25 core + 15 advanced)
- ✅ **Documentation**: README, QUICKSTART, CONTRIBUTING guides

## Installation

### From Source
```bash
cd transec_standalone
pip install -e .
```

### For Development
```bash
cd transec_standalone
pip install -e ".[dev]"
```

## Quick Test

```bash
cd transec_standalone

# Run core tests (25 tests)
python3 tests/test_transec.py

# Run advanced tests (15 tests)
python3 tests/test_advanced.py

# Run feature demo
python3 examples/demo.py

# Test imports
python3 -c "from transec import TransecCipher, AdaptiveTransecCipher, OTARTransecCipher; print('✓ All imports successful')"
```

## Usage Example

```python
from transec import TransecCipher, generate_shared_secret

# Setup
secret = generate_shared_secret()
sender = TransecCipher(secret)
receiver = TransecCipher(secret)

# Communicate
packet = sender.seal(b"Hello, TRANSEC!", sequence=1)
plaintext = receiver.open(packet)
print(plaintext)  # b"Hello, TRANSEC!"
```

## Advanced Features

### Adaptive Slot Duration
```python
from transec import AdaptiveTransecCipher

cipher = AdaptiveTransecCipher(
    secret,
    jitter_range=(2, 10)  # Dynamic 2-10s slots
)
```

### OTAR Key Refresh
```python
from transec import OTARTransecCipher

cipher = OTARTransecCipher(
    secret,
    refresh_interval=3600,  # Rekey every hour
    auto_refresh=True
)
```

## Publishing to PyPI

To publish this as an independent package:

```bash
cd transec_standalone

# Build distributions
python3 setup.py sdist bdist_wheel

# Upload to PyPI (requires credentials)
python3 -m twine upload dist/*
```

## Relationship to z-sandbox

This standalone repository extracts TRANSEC from the larger z-sandbox research framework:

- **z-sandbox**: Multi-faceted research repo (factorization, QMC, TRANSEC, etc.)
- **transec_standalone**: Focused TRANSEC-only package for production use

The standalone version:
- Removes dependencies on z-sandbox research code
- Adds production-ready features (adaptive, OTAR)
- Provides clean package structure for PyPI
- Maintains backward compatibility with z-sandbox TRANSEC

## Future Roadmap

Planned enhancements:
- [ ] Hybrid FHSS emulation (UDP port rotation)
- [ ] Forward secrecy via ephemeral ECDH
- [ ] Post-quantum key derivation (CRYSTALS-Kyber)
- [ ] LoRaWAN and mesh network bindings
- [ ] Hardware acceleration (AES-NI, crypto offload)
- [ ] Streamlit metrics dashboard
- [ ] Integration with Briar/Cwtch/Matrix

## License

MIT License - see LICENSE file

## Credits

- Based on TRANSEC implementation from z-sandbox project
- Enhanced with suggestions from issue "Create a Stand Alone TRANSEC Repository"
- Inspired by Hedy Lamarr's frequency-hopping patent
- Military COMSEC: HAVE QUICK, SINCGARS, Milstar OTAR

## Contributing

See CONTRIBUTING.md for guidelines on:
- Setting up development environment
- Running tests
- Code style and standards
- Pull request process
- Security issue reporting

## Support

- Documentation: See docs/ directory
- Examples: See examples/ directory
- Issues: GitHub issue tracker
- Security: security@example.com
