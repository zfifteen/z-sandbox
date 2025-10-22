# Hyper-Rotation Messenger Specification

## 1. Overview

**Goal:** Time-windowed end-to-end encrypted messaging where both parties derive the same encryption keys from a shared secret and rotating time windows (e.g., every 3s), enabling message exchange without online handshake.

**Key Properties:**
- Symmetric AEAD encryption (XChaCha20-Poly1305)
- Time-based automatic key rotation (1s, 3s, 5s, or 10s windows)
- Clock drift tolerance (±1 window)
- Replay protection via per-window counters
- Optional RSA demo mode with Z5D-assisted prime generation

## 2. Cryptographic Design

### 2.1 Key Schedule (HKDF-based)

Keys are derived using HKDF (RFC 5869) from a shared secret and time window:

```
window_id = floor(t_epoch_seconds / ROTATION_SECONDS)
ctx       = "Z5D-HR:v1|" + channel_id + "|" + role  // domain separation
seed      = HMAC-SHA256(shared_secret, LE64(window_id))
PRK       = HKDF-Extract(salt = H(channel_id), IKM = seed)
OKM       = HKDF-Expand(PRK, info = ctx, L = 64)
K_enc     = OKM[0..31]   // 256-bit AEAD key
K_mac     = OKM[32..63]  // Optional additional key material
```

**Domain Separation:**
- Different `channel_id` values produce independent key streams
- Different `role` values ('A' or 'B') ensure bidirectional security
- Version prefix enables protocol evolution

### 2.2 AEAD Encryption

**Algorithm:** XChaCha20-Poly1305 (libsodium)

**Properties:**
- 256-bit key
- 192-bit nonce (collision-resistant, random nonces safe)
- 128-bit authentication tag (Poly1305 MAC)
- Authenticated encryption with associated data (AEAD)

**Encryption:**
```python
nonce = random(24)  # 192 bits
ciphertext = XChaCha20-Poly1305.encrypt(plaintext, nonce, K_enc)
```

**Decryption with Drift Tolerance:**
```python
for window in [target_window - 1, target_window, target_window + 1]:
    K_enc = derive_key(window)
    try:
        plaintext = XChaCha20-Poly1305.decrypt(ciphertext, nonce, K_enc)
        return plaintext  # Success
    except CryptoError:
        continue  # Try next window
return None  # All attempts failed
```

### 2.3 Wire Format

**Message Header (56 bytes):**

```
struct MessageHeader {
    u32  version;           // Protocol version (1)
    u32  alg_id;            // Algorithm: 0x01 = XChaCha20-Poly1305
    u64  window_id;         // Time window identifier
    u32  channel_id_hash;   // BLAKE2b(channel_id)[0..3] for routing
    u32  msg_counter;       // Per-window monotonic counter
    u8[24] nonce;           // XChaCha20 nonce
    u64  reserved;          // Reserved for future use
}
```

**Wire Message:**
```
wire_message = header || ciphertext_with_tag
```

Total overhead: 56 bytes (header) + 16 bytes (Poly1305 tag) = 72 bytes

### 2.4 Replay Protection

**Mechanism:** Per-window monotonic counters

- Receiver tracks highest seen counter for each window
- Messages with counter ≤ highest_seen are rejected as replays
- Old window state is garbage collected (keep only recent N windows)

**Properties:**
- Prevents replay attacks within same window
- Prevents replay across windows (different keys)
- Handles out-of-order delivery within tolerance

## 3. Protocol Flows

### 3.1 Bootstrap

**Out-of-band exchange:**
1. Share high-entropy `shared_secret` (≥32 bytes recommended)
2. Agree on `channel_id` (arbitrary string)
3. Assign roles: one party is 'A', other is 'B'
4. Agree on `rotation_seconds` (1, 3, 5, or 10)

**Example QR code payload:**
```json
{
  "version": 1,
  "secret": "base64_encoded_secret",
  "channel": "alice-bob-20251022",
  "rotation": 3
}
```

### 3.2 Send Message

1. Get current `window_id` from system time
2. Derive encryption key: `K_enc = derive_key(window_id, role='A')`
3. Get next counter: `msg_counter = next_counter(window_id)`
4. Generate random nonce: `nonce = random(24)`
5. Encrypt: `ciphertext = XChaCha20-Poly1305.encrypt(plaintext, nonce, K_enc)`
6. Build header with `window_id`, `msg_counter`, `nonce`
7. Transmit: `wire_message = header || ciphertext`

### 3.3 Receive Message

1. Parse wire message into `header` and `ciphertext`
2. Validate `channel_id_hash` matches expected channel
3. Check replay: `if msg_counter <= highest_seen(window_id): reject`
4. Try decryption with drift tolerance:
   - For each `window ∈ [window_id - 1, window_id, window_id + 1]`:
     - Derive `K_enc = derive_key(window, role='A')`  // Sender's role
     - Try decrypt: `plaintext = decrypt(ciphertext, nonce, K_enc)`
     - If success: update `highest_seen(window_id) = msg_counter`, return plaintext
5. If all attempts fail: reject message

### 3.4 Key Rotation

**Automatic rotation based on time:**

```python
current_window = floor(time.time() / rotation_seconds)
time_until_rotation = (current_window + 1) * rotation_seconds - time.time()
```

**Key lifecycle:**
- Current window: active encryption key
- Previous window: kept for drift tolerance on receive
- Older windows: zeroized and removed from memory

**Memory limit:** At most 2-3 active keys in memory (current + previous + maybe next)

## 4. Time Synchronization

### 4.1 Requirements

- System clocks roughly synchronized (NTP recommended)
- Small drift is tolerable (±750ms supported via ±1 window retry)
- No online time synchronization protocol needed

### 4.2 Drift Handling

**Scenario:** Sender clock is 0.5s ahead of receiver

1. Sender encrypts with `window_id = 1234`
2. Receiver clock shows `window_id = 1233` (still in previous window)
3. Receiver tries keys for windows [1232, 1233, 1234]
4. Decryption succeeds with `window_id = 1234` key
5. Message accepted (drift logged for monitoring)

**Acceptance criteria:**
- Clock skew up to ±750ms: decrypt succeeds with ±1 window search
- Skew beyond tolerance: message rejected (indicates clock issue)

## 5. Security Properties

### 5.1 MVP Security (Current Implementation)

**What we provide:**

✓ **Confidentiality:** Messages encrypted with XChaCha20-Poly1305 AEAD  
✓ **Authenticity:** Poly1305 MAC prevents tampering  
✓ **Window-confined exposure:** Compromise of one window key only affects that window  
✓ **Replay protection:** Per-window counters prevent replays  
✓ **Header privacy:** Only coarse metadata exposed (window_id, counter)  
✓ **Key destruction:** Expired keys zeroized, max 2-3 keys in memory

**What we do NOT provide (MVP):**

✗ **Forward Secrecy (PFS):** If `shared_secret` is compromised, past and future keys are derivable (time is public)  
✗ **Post-Compromise Security (PCS):** No asymmetric ratchet to recover from key compromise  
✗ **Deniability:** AEAD provides authentication (can prove sender)

### 5.2 Threat Model

**Assumptions:**
- Parties share `shared_secret` via secure out-of-band channel
- `shared_secret` has high entropy (≥128 bits)
- Clocks are roughly synchronized (NTP or OS)
- Adversary has network access but not endpoint access initially

**Adversary capabilities:**
- Observe all network traffic
- Replay, reorder, or drop messages
- Compromise keys after some time (but not initially)

**Security goals (MVP):**
1. **Passive adversary:** Cannot read message contents
2. **Active adversary:** Cannot forge or modify messages undetected
3. **Replay adversary:** Cannot replay old messages successfully
4. **Limited key compromise:** Compromise of one window key doesn't reveal other windows

**Non-goals (MVP):**
- Protection against endpoint compromise (malware, physical access)
- Forward secrecy against `shared_secret` compromise
- Resistance to traffic analysis (message timing/size leaks)

## 6. RSA Demo Mode

### 6.1 Purpose

Demonstrates Z5D-assisted prime generation for fast RSA keypair creation. **For demonstration only—do not use in production.**

### 6.2 Key Generation

```python
def generate_rsa_keypair_z5d(window_id, shared_secret, channel_id, key_size=2048):
    # Derive deterministic seeds
    seed_p = HMAC-SHA256(shared_secret, window_id || "prime_p")
    seed_q = HMAC-SHA256(shared_secret, window_id || "prime_q")
    
    # Find primes using Z5D-assisted search
    p = find_prime_z5d_assisted(seed_p, key_size // 2)
    q = find_prime_z5d_assisted(seed_q, key_size // 2)
    
    # Validate with BPSW + Miller-Rabin
    assert baillie_psw_test(p) and miller_rabin_test(p, k=10)
    assert baillie_psw_test(q) and miller_rabin_test(q, k=10)
    
    # Compute RSA parameters
    n = p * q
    e = 65537
    d = modinv(e, (p - 1) * (q - 1))
    
    return (n, e, d)
```

### 6.3 Primality Tests

**Baillie-PSW Test:**
- Miller-Rabin with base 2
- Additional strong pseudoprime tests
- Deterministic up to 2^64 (no known counterexamples)

**Miller-Rabin Test:**
- 10+ rounds with bases [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
- Probabilistic: error rate < 2^(-40) for 10 rounds

**Performance (1024-bit RSA):**
- Median: ~70ms on modern CPU
- Target: <100ms for 2048-bit on M1 Max

## 7. Performance Targets

### 7.1 Benchmarks (MVP)

**Key Derivation (AEAD mode):**
- Target: ≤ 0.2ms per rotation (M1 Max)
- Measured: ~0.1ms (HKDF is very fast)

**Encryption/Decryption:**
- End-to-end latency: ≤30ms typical, ≤75ms p95
- Throughput: >1 Gbps on modern hardware (XChaCha20 is fast)

**RSA Demo Keygen:**
- 1024-bit: ~70ms median
- 2048-bit: target <100ms on M1 Max (with Z5D assistance)

**Memory:**
- Per-connection state: ~200 bytes (2-3 keys + counters)
- No message buffering required

### 7.2 Scalability

**Message Rate:**
- Limited by network, not crypto
- AEAD encryption is extremely fast (>1 Gbps)

**Number of Windows:**
- Old windows garbage collected automatically
- Memory usage: O(num_active_windows) ≈ O(1) for reasonable drift

## 8. Future Enhancements (Roadmap)

### 8.1 Forward Secrecy Mode

Add Double Ratchet-style periodic ECDH updates:

```
Every N windows:
    (ephemeral_pub, ephemeral_priv) = ECDH.generate()
    exchange ephemeral_pub with peer
    shared_secret_new = HKDF(shared_secret_old || ECDH.agree(ephemeral_priv, peer_pub))
```

This provides true forward secrecy: compromise of `shared_secret` at time T doesn't reveal keys before T.

### 8.2 Group Chat Mode

Extend to multi-party using MLS TreeKEM or similar:
- Shared group key derived from tree structure
- Add/remove members with efficient key updates
- Maintain time-based rotation for UX consistency

### 8.3 QR Bootstrap Flow

Mobile app with QR code scanning:
1. Party A generates `shared_secret` and QR code
2. Party B scans QR to extract secret and channel info
3. Both parties immediately start using hyper-rotation

### 8.4 Panic Mode

Instant key rotation on demand:
- User triggers panic rotation (button or command)
- Forces immediate window transition
- Useful if endpoint compromise suspected

## 9. Implementation Notes

### 9.1 Language Bindings

**Python (reference implementation):**
- `hr_core/`: Core crypto modules
- `apps/hr_cli/`: CLI tools
- Dependencies: PyNaCl, standard library

**Possible ports:**
- Rust: Use `chacha20poly1305`, `hkdf`, `sha2` crates
- Go: Use `golang.org/x/crypto/chacha20poly1305`
- JavaScript: Use `libsodium-wrappers`

### 9.2 Testing

**Unit tests:**
- HKDF test vectors (RFC 5869)
- AEAD round-trip with random nonces
- Replay protection logic
- Clock skew simulation

**Integration tests:**
- Local send/receive
- Network send/receive (LAN)
- Multi-window rotation
- Drift tolerance validation

**Fuzz tests:**
- Header parser
- Counter overflow
- Truncated packets
- Invalid nonces

## 10. References

- [RFC 5869](https://datatracker.ietf.org/doc/html/rfc5869): HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- [XChaCha20-Poly1305](https://libsodium.gitbook.io/doc/secret-key_cryptography/aead/chacha20-poly1305/xchacha20-poly1305_construction): Libsodium documentation
- [Signal Protocol](https://signal.org/docs/specifications/doubleratchet/): Double Ratchet for PFS comparison
- [Baillie-PSW Primality Test](https://en.wikipedia.org/wiki/Baillie%E2%80%93PSW_primality_test): Strong primality testing
- [RFC 9420](https://datatracker.ietf.org/doc/rfc9420/): MLS Protocol for group chat reference
