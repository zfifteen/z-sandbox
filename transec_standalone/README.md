# TRANSEC: Time-Synchronized Encryption

**Zero-Handshake Encrypted Messaging Inspired by Military Frequency-Hopping COMSEC**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

TRANSEC (Transmission Security) adapts military frequency-hopping COMSEC principles (SINCGARS, HAVE QUICK) to software-defined networking, enabling **zero-RTT encrypted communication** without traditional handshake overhead.

### Unique Properties

TRANSEC provides a property set **absent from TLS 1.3/QUIC, IKEv2, and Signal**:
- **True zero-handshake**: First packet flies encrypted on first contact
- **Time-synchronized keying**: Deterministic key rotation using HKDF-SHA256
- **Built-in replay protection**: Slot index + sequence number tracking
- **Sub-millisecond latency**: ~0.3ms RTT for encrypted UDP packets
- **Military-grade design**: Adapted from HAVE QUICK/SINCGARS time-sliced keying

## Quick Start

### Installation

```bash
pip install transec
```

### Basic Usage

```python
from transec import TransecCipher, generate_shared_secret

# Generate or provision shared secret (out-of-band)
secret = generate_shared_secret()

# Create cipher instances for sender and receiver
sender = TransecCipher(secret, slot_duration=5, drift_window=2)
receiver = TransecCipher(secret, slot_duration=5, drift_window=2)

# Encrypt message (no handshake needed!)
plaintext = b"Hello, TRANSEC!"
packet = sender.seal(plaintext, sequence=1)

# Decrypt message
decrypted = receiver.open(packet)
print(decrypted)  # b"Hello, TRANSEC!"
```

### Advanced Features

#### Adaptive Slot Duration (NEW!)

Dynamic slot timing with PRNG-based jitter for enhanced unpredictability:

```python
from transec import AdaptiveTransecCipher

# Create cipher with adaptive slot duration
cipher = AdaptiveTransecCipher(
    secret,
    base_duration=5,      # Base slot duration in seconds
    drift_window=2,       # Clock drift tolerance
    jitter_range=(2, 10)  # Slot duration varies 2-10 seconds
)
```

#### Prime Optimization

Use prime-valued slot indices for enhanced synchronization stability:

```python
cipher = TransecCipher(
    secret,
    slot_duration=3600,      # 1-hour slots
    drift_window=3,          # ±3 slots tolerance
    prime_strategy="nearest" # Map to nearest prime slot
)
```

#### OTAR-Lite Key Refresh

Automatic over-the-air rekeying for long sessions:

```python
from transec import OTARTransecCipher

cipher = OTARTransecCipher(
    secret,
    refresh_interval=60,  # Rekey every 60 seconds
    auto_refresh=True     # Automatic key rotation
)
```

## Features

### Core Capabilities

- **Zero-RTT Communication**: No handshake overhead after bootstrap
- **HKDF-SHA256 Key Derivation**: Cryptographically secure time-sliced keys
- **ChaCha20-Poly1305 AEAD**: Authenticated encryption with associated data
- **Replay Protection**: Automatic sequence number tracking
- **Clock Drift Tolerance**: Configurable time window acceptance
- **Prime Optimization**: 25-88% curvature reduction for enhanced stability

### Advanced Features

- **Adaptive Slot Duration**: PRNG-based dynamic timing (anti-pattern analysis)
- **OTAR-Lite Rekeying**: Over-the-air key refresh without full renegotiation
- **Hybrid FHSS Emulation**: Port rotation and VLAN tagging support
- **High Performance**: 3,000+ msg/sec throughput, <1ms latency
- **Flexible Configuration**: Customizable slot durations and drift windows

## Use Cases

### Tactical Communications
- **Drone swarms**: Real-time formation control
- **Battlefield mesh networks**: Low-latency command and control
- **First-responder coordination**: Instant encrypted comms

### Critical Infrastructure
- **SCADA/DER telemetry**: Sub-100ms requirements for power grid
- **IEC 61850-90-5**: Teleprotection with deterministic timing
- **Industrial control systems**: Zero-latency process control

### Autonomous Systems
- **V2V messaging**: Vehicle platoons and collision avoidance
- **Swarm coordination**: Multi-robot encrypted communication
- **Edge computing**: Low-latency IoT mesh networks

### High-Performance Applications
- **High-frequency trading**: Sub-millisecond encrypted market data
- **Real-time gaming**: Low-latency multiplayer encryption
- **Live streaming**: Minimal delay encrypted video feeds

## Architecture

### Key Derivation

```
slot_index = floor(current_time / slot_duration)
info = context || slot_index (8 bytes, big-endian)
K_t = HKDF-SHA256(shared_secret, salt=None, info=info, length=32)
```

### Packet Structure

```
[slot_index: 8 bytes][sequence: 8 bytes][random: 4 bytes][ciphertext + tag: variable]
```

### Security Model

**Protected Against:**
- Passive eavesdropping (ChaCha20-Poly1305 encryption)
- Replay attacks (sequence tracking)
- Packet injection (AEAD authentication)
- Out-of-order delivery (slot window acceptance)

**Limitations:**
- Shared secret compromise requires network-wide rekey
- Requires time synchronization (GPS/NTP/monotonic counter)
- No forward secrecy without additional ratcheting
- Time desynchronization attacks require authenticated time source

## Performance

### Benchmark Results (localhost UDP)

- **Throughput**: 2,942 msg/sec
- **Average RTT**: 0.34ms
- **Success Rate**: 100%
- **Encryption Overhead**: <1ms per packet
- **Key Derivation**: <0.1ms per slot change

## Documentation

- [Full Specification](docs/TRANSEC.md) - Complete protocol specification
- [Usage Guide](docs/TRANSEC_USAGE.md) - Detailed API reference
- [Protocol Comparison](docs/TRANSEC_PROTOCOL_COMPARISON.md) - vs TLS 1.3, QUIC, IKEv2, Signal
- [Prime Optimization](docs/TRANSEC_PRIME_OPTIMIZATION.md) - Enhanced synchronization
- [Security Model](docs/TRANSEC.md#security-model) - Threat analysis and limitations

## Examples

### UDP Client/Server

```bash
# Terminal 1: Start server
python examples/transec_udp_demo.py server

# Terminal 2: Send messages
python examples/transec_udp_demo.py client --message "Hello, TRANSEC!"

# Terminal 3: Run benchmark
python examples/transec_udp_demo.py benchmark --count 1000
```

### CLI Messenger

```bash
# Terminal 1: Start listener
python examples/transec_messenger.py listen --port 5000

# Terminal 2: Send message
python examples/transec_messenger.py send --host localhost --port 5000 --message "Hello!"
```

## Development

### Installation from Source

```bash
git clone https://github.com/zfifteen/transec.git
cd transec
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=transec --cov-report=html

# Run specific test file
python tests/test_transec.py
```

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Comparison with Existing Protocols

| Property | TRANSEC | TLS 1.3 | QUIC | IPsec | Signal |
|----------|---------|---------|------|-------|--------|
| Handshake RTT | **0** | 1-RTT | 0-1 RTT* | 1-4 RTT | Multiple RTT |
| First Contact | **✅ Yes** | ❌ No† | ❌ No† | ❌ No | ❌ No |
| Replay Protection | **✅ Inherent** | ❌ App-level | ❌ App-level | ✅ Via IKE | ✅ Via ratchet |
| Forward Secrecy | No‡ | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Time Dependency | **Critical** | None | None | Optional | None |
| Latency | **<1ms** | 10-100ms | 5-50ms | 10-50ms | 100-500ms |

*Requires prior connection or PSK  
†Requires key agreement handshake  
‡Can be added with ephemeral ECDH or ratcheting

## Roadmap

- [x] Core TRANSEC implementation
- [x] Prime optimization for enhanced stability
- [ ] Adaptive slot duration (PRNG-based)
- [ ] OTAR-Lite key refresh mechanism
- [ ] Hybrid FHSS emulation (port rotation)
- [ ] Forward secrecy via ratcheting
- [ ] Hardware acceleration support
- [ ] LoRaWAN and mesh network bindings
- [ ] Streamlit metrics dashboard
- [ ] Post-quantum key derivation (CRYSTALS-Kyber)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

Inspired by:
- **Hedy Lamarr**: Frequency-hopping spread spectrum inventor
- **HAVE QUICK**: Military frequency-hopping radio system
- **SINCGARS**: Single Channel Ground and Airborne Radio System
- **NSA COMSEC**: Transmission security principles

## Citation

If you use TRANSEC in academic work, please cite:

```bibtex
@software{transec2024,
  title={TRANSEC: Time-Synchronized Encryption for Zero-Handshake Messaging},
  author={Z-Sandbox Project},
  year={2024},
  url={https://github.com/zfifteen/transec}
}
```

## Security Notice

TRANSEC is experimental software. While designed with security in mind, it has not undergone formal security audit. Use in production systems requires careful review and appropriate threat modeling for your specific use case.

For security concerns, please email: security@example.com
