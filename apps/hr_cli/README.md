# Hyper-Rotation Messenger

A PoC "hyper-rotating" end-to-end encrypted messenger with time-based automatic key rotation.

## Overview

Hyper-Rotation Messenger provides ultra-low latency encrypted messaging with keys that automatically rotate based on time windows (1s, 3s, 5s, or 10s). Both parties derive the same encryption keys from a shared secret and synchronized time, enabling message exchange without online key negotiation.

**Key Features:**
- ✅ **Time-based key rotation**: Automatic key changes every 1-10 seconds
- ✅ **XChaCha20-Poly1305 AEAD**: Strong symmetric encryption (256-bit keys)
- ✅ **Clock drift tolerance**: ±1 window drift handling (±750ms typical)
- ✅ **Replay protection**: Per-window monotonic counters
- ✅ **Low latency**: Sub-millisecond crypto operations, ~10-30ms end-to-end
- ✅ **Optional RSA demo**: Z5D-assisted prime generation (showcase mode)

## Quick Start

### Installation

```bash
# Install dependencies
pip install PyNaCl

# Or use requirements.txt
pip install -r python/requirements.txt
```

### Basic Usage

**Start receiver:**
```bash
python3 apps/hr_cli/recv.py --rotation 3
```

**Send messages (in another terminal):**
```bash
python3 apps/hr_cli/send.py --rotation 3
```

Type messages to send. Empty line sends a heartbeat. Press Ctrl+C to exit.

### Demo Script

Run a split-pane demo with tmux/screen:

```bash
bash apps/hr_cli/demo_two_panes.sh
```

## Architecture

### Core Modules (`hr_core/`)

- **`key_schedule.py`**: HKDF-based key derivation with time windows
- **`aead.py`**: XChaCha20-Poly1305 AEAD encryption wrappers
- **`wire.py`**: Message header format and wire protocol
- **`replay.py`**: Anti-replay protection with per-window counters
- **`rsa_demo.py`**: Z5D-assisted RSA keypair generation (demo only)

### CLI Applications (`apps/hr_cli/`)

- **`send.py`**: Interactive message sender with key rotation countdown
- **`recv.py`**: Message receiver with clock drift tolerance
- **`demo_two_panes.sh`**: Split-pane demonstration script

## Key Derivation

Keys are derived using HKDF (RFC 5869):

```
window_id = floor(time_seconds / rotation_seconds)
seed      = HMAC-SHA256(shared_secret, LE64(window_id))
PRK       = HKDF-Extract(salt = H(channel_id), IKM = seed)
OKM       = HKDF-Expand(PRK, info = context, L = 64)
K_enc     = OKM[0..31]   // Encryption key
K_mac     = OKM[32..63]  // MAC key material
```

**Domain separation** via context string:
```
context = "Z5D-HR:v1|" + channel_id + "|" + role
```

## Message Format

**Wire Format (56-byte header + ciphertext):**

```
Header (56 bytes):
  - version:         u32 (4 bytes)
  - alg_id:          u32 (4 bytes) - 0x01 = XChaCha20-Poly1305
  - window_id:       u64 (8 bytes)
  - channel_id_hash: u32 (4 bytes) - BLAKE2b truncated
  - msg_counter:     u32 (4 bytes) - per-window, monotonic
  - nonce:           u8[24] (24 bytes) - XChaCha20 nonce
  - reserved:        u64 (8 bytes)

Ciphertext:
  - encrypted_plaintext + Poly1305_tag (16 bytes)
```

Total overhead: 56 + 16 = 72 bytes

## Security Properties

### What We Provide (MVP)

✅ **Confidentiality**: XChaCha20-Poly1305 AEAD encryption (IND-CCA2)  
✅ **Authenticity**: Poly1305 MAC prevents tampering (EUF-CMA)  
✅ **Window-confined exposure**: Compromise of one window key doesn't reveal others  
✅ **Replay protection**: Per-window counters prevent replays  
✅ **Clock drift tolerance**: Messages decrypt with ±1 window skew  

### What We Do NOT Provide (MVP)

❌ **Forward Secrecy (PFS)**: Compromise of `shared_secret` reveals all past/future keys  
❌ **Post-Compromise Security (PCS)**: No self-healing mechanism  
❌ **Deniability**: AEAD provides strong authentication  

**See [docs/SECURITY_NOTES.md](docs/SECURITY_NOTES.md) for detailed security analysis.**

## Performance

Measured on Intel Core i7-9750H @ 2.6GHz:

| Operation | Time |
|-----------|------|
| Key derivation | 0.09ms |
| AEAD encryption | 0.012ms |
| AEAD decryption | 0.012ms |
| End-to-end latency (LAN) | ~15-20ms |
| RSA keygen (1024-bit) | ~70ms |

**See [docs/PERF.md](docs/PERF.md) for benchmark scripts and detailed results.**

## Configuration

### Command-Line Options

**Sender (`send.py`):**
```bash
python3 apps/hr_cli/send.py \
  --secret "your_shared_secret" \
  --channel "channel_name" \
  --role A \
  --rotation 3 \
  --host localhost \
  --port 9999 \
  --message "Optional single message"
```

**Receiver (`recv.py`):**
```bash
python3 apps/hr_cli/recv.py \
  --secret "your_shared_secret" \
  --channel "channel_name" \
  --role B \
  --rotation 3 \
  --port 9999 \
  --max-drift 1
```

### Rotation Windows

Choose based on your use case:

- **1s**: Ultra-fast rotation, maximum forward isolation, tight time sync required
- **3s**: Balanced (default), good for real-time comms
- **5s**: Moderate rotation, more tolerant of clock drift
- **10s**: Slow rotation, maximum drift tolerance

## Testing

Run comprehensive test suite:

```bash
python3 -m unittest tests.test_hyper_rotation -v
```

**Test coverage (27 tests):**
- Key schedule: HKDF derivation, role/window/channel separation
- AEAD: encryption/decryption, authentication, nonce handling
- Wire format: header serialization, message encoding
- Replay protection: counter tracking, window cleanup
- Clock skew: ±1 window drift tolerance
- RSA demo: keypair generation, primality tests
- End-to-end: complete message flow

All tests pass in ~0.2s.

## Examples

### Local LAN Demo

**Terminal 1 (Receiver):**
```bash
python3 apps/hr_cli/recv.py --rotation 3 --port 9999
```

**Terminal 2 (Sender):**
```bash
python3 apps/hr_cli/send.py --rotation 3 --port 9999
```

Type messages in Terminal 2. They appear instantly in Terminal 1 with key expiry countdown.

### Different Channels

Run multiple independent channels:

```bash
# Channel 1
python3 apps/hr_cli/recv.py --channel "team-alpha" --port 9001 &
python3 apps/hr_cli/send.py --channel "team-alpha" --port 9001

# Channel 2 (independent)
python3 apps/hr_cli/recv.py --channel "team-beta" --port 9002 &
python3 apps/hr_cli/send.py --channel "team-beta" --port 9002
```

### Custom Secrets

Use high-entropy secrets (>128 bits recommended):

```bash
SECRET=$(openssl rand -base64 32)
python3 apps/hr_cli/recv.py --secret "$SECRET" &
python3 apps/hr_cli/send.py --secret "$SECRET"
```

## Documentation

- **[HYPER_ROTATION_SPEC.md](docs/HYPER_ROTATION_SPEC.md)**: Complete specification
- **[SECURITY_NOTES.md](docs/SECURITY_NOTES.md)**: Security analysis and threat model
- **[PERF.md](docs/PERF.md)**: Performance benchmarks

## Roadmap

### Future Enhancements

1. **PFS Mode**: Add Double Ratchet-style ECDH for true forward secrecy
2. **Group Chat**: Integrate MLS TreeKEM for efficient group encryption
3. **QR Bootstrap**: Mobile app with QR code secret exchange
4. **Panic Mode**: Instant key rotation on demand
5. **UDP Transport**: Lower latency alternative to TCP

## FAQ

**Q: Is this secure for production use?**  
A: The MVP provides strong encryption but lacks forward secrecy. Use only when:
- Endpoints are physically secure
- Shared secret remains confidential
- Low latency is critical

For general-purpose messaging, use Signal or wait for PFS mode.

**Q: How does this compare to Signal?**  
A: Signal provides forward secrecy via Double Ratchet. Hyper-rotation trades PFS for ultra-low latency and time-based UX. See [SECURITY_NOTES.md](docs/SECURITY_NOTES.md).

**Q: What if clocks are out of sync?**  
A: Drift tolerance (±1 window) handles clock skew up to ~750ms. Beyond that, messages fail to decrypt. Use NTP for time sync.

**Q: Can I use this offline?**  
A: Yes, as long as both parties have synchronized clocks. No online key exchange required.

**Q: What's the RSA demo mode?**  
A: Demonstrates Z5D-assisted prime finding for fast RSA keypair generation. **Not recommended for production**—use AEAD mode instead.

## Contributing

Contributions welcome! Please ensure:
- All tests pass (`python3 -m unittest tests.test_hyper_rotation`)
- Code follows existing style
- Security implications documented

## License

[Specify license here]

## Acknowledgments

- Built on [PyNaCl](https://pynacl.readthedocs.io/) (libsodium bindings)
- HKDF spec: [RFC 5869](https://datatracker.ietf.org/doc/html/rfc5869)
- Inspired by Signal Protocol and WireGuard
- Z5D prime prediction framework for RSA demo mode
