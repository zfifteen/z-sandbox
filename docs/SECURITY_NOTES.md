# Security Notes: Hyper-Rotation Messenger

## Executive Summary

This document clarifies the security properties of the Hyper-Rotation Messenger MVP and distinguishes them from full forward secrecy (PFS) protocols like Signal's Double Ratchet or MLS.

**Key Points:**
- ✅ MVP provides **window-confined exposure** and strong AEAD encryption
- ✅ Suitable for scenarios with trusted endpoints and high-entropy shared secrets
- ❌ MVP does **NOT** provide forward secrecy (PFS) or post-compromise security (PCS)
- ✅ Future "Secure Mode" will add asymmetric ratcheting for true PFS

## 1. What We Provide (MVP)

### 1.1 Confidentiality

**Mechanism:** XChaCha20-Poly1305 AEAD encryption

- **Strength:** 256-bit symmetric key, 128-bit authentication tag
- **Properties:** IND-CCA2 secure (indistinguishable under chosen ciphertext attack)
- **Nonce handling:** 192-bit nonce space, random nonces safe (collision probability negligible)

**Guarantee:** Adversary observing ciphertext cannot recover plaintext without the key.

### 1.2 Authenticity & Integrity

**Mechanism:** Poly1305 MAC (part of AEAD)

- **Properties:** Existentially unforgeable under chosen message attack (EUF-CMA)
- **Guarantee:** Adversary cannot forge valid ciphertexts or modify existing ones undetected

### 1.3 Window-Confined Exposure

**Mechanism:** Time-based key derivation

- **Property:** Each time window (1s, 3s, 5s, or 10s) has independent keys
- **Benefit:** Compromise of one window key does not reveal other windows' keys *as long as the shared secret remains secure*

**Guarantee:** If an attacker compromises `K_enc(window=1234)`, they can only decrypt messages from that specific window, not past or future windows.

### 1.4 Replay Protection

**Mechanism:** Per-window monotonic counters

- **Property:** Each message has a unique `(window_id, msg_counter)` pair
- **Detection:** Receiver rejects messages with counters ≤ highest_seen for that window

**Guarantee:** Adversary cannot replay previously sent messages.

### 1.5 Header Privacy (Partial)

**What's hidden:**
- Message content (encrypted)
- Exact timestamp (only window_id exposed, coarse granularity)
- Sender/receiver identities (no explicit fields)

**What's visible (cleartext header):**
- Protocol version
- Algorithm ID
- Window ID (coarse time bucket)
- Channel ID hash (for routing)
- Message counter
- Nonce

**Analysis:** Window ID leaks approximate time (within rotation window), but not exact millisecond timestamps.

## 2. What We Do NOT Provide (MVP)

### 2.1 Forward Secrecy (PFS)

**Definition:** Forward secrecy ensures that compromise of long-term secrets does not compromise past session keys.

**Why MVP lacks PFS:**

The MVP derives all keys from a static `shared_secret` and public time:

```
K_enc(window) = HKDF(shared_secret, window_id)
```

Since `window_id` is just `floor(time / rotation_seconds)`, which is public information, **if an attacker later compromises the `shared_secret`, they can recompute all past and future keys**.

**Example attack:**
1. Attacker records encrypted traffic from weeks ago
2. Attacker later compromises endpoint and extracts `shared_secret`
3. Attacker computes `K_enc(window)` for all recorded windows
4. Attacker decrypts all recorded traffic

**Contrast with Signal Double Ratchet:**
- Signal uses ephemeral Diffie-Hellman (ECDH) key exchanges per message or session
- Compromising current state doesn't reveal past ECDH private keys (they're deleted)
- Past messages remain secure

### 2.2 Post-Compromise Security (PCS)

**Definition:** PCS ensures that after a compromise, the system can recover security without manual intervention.

**Why MVP lacks PCS:**

Since keys are deterministically derived from `shared_secret`, compromise of the secret is permanent:
- No mechanism to "heal" from compromise
- Attacker can compute all future keys until `shared_secret` is manually changed

**Contrast with Signal Double Ratchet:**
- Signal's ratchet incorporates fresh randomness from each party
- After compromise, new ECDH exchanges introduce unknown secrets to attacker
- System "heals" after a few round-trips

### 2.3 Deniability

**Definition:** Deniability means a participant can plausibly deny having sent a message, even to someone who received it.

**Why MVP lacks deniability:**

AEAD authentication (Poly1305 MAC) provides strong authenticity:
- Only someone with `K_enc` can create valid ciphertexts
- Since both parties have `K_enc`, either could have sent any message
- But this is *weaker* deniability than OTR or Signal (which use MACs that can be forged post-conversation)

**Use case impact:**
- MVP suitable for mutually trusted parties
- Not suitable for scenarios requiring legal deniability

## 3. Threat Model

### 3.1 Adversary Capabilities

**Network adversary (always assumed):**
- Observe all network traffic (passive)
- Inject, modify, replay, reorder, or drop messages (active)
- Cannot break cryptographic primitives (XChaCha20, Poly1305, HMAC-SHA256)

**Endpoint compromise (time-dependent):**
- **Before compromise:** Adversary cannot access `shared_secret` or keys
- **After compromise:** Adversary gains access to:
  - `shared_secret` (stored in memory or on disk)
  - Current and recent window keys
  - Replay protection state

### 3.2 Security Goals

**Against network adversary:**
- ✅ Confidentiality: Cannot read message contents
- ✅ Authenticity: Cannot forge or modify messages
- ✅ Replay protection: Cannot replay old messages

**Against endpoint compromise:**
- ✅ Window isolation: Compromise of one window key doesn't reveal others (short-term)
- ❌ Forward secrecy: Compromise of `shared_secret` reveals all past keys
- ❌ Post-compromise security: Compromise of `shared_secret` reveals all future keys

### 3.3 Out-of-Scope Threats (MVP)

The following are explicitly **not addressed** in the MVP:

**Traffic analysis:**
- Message timing, size, and frequency are visible
- No padding or traffic shaping
- Adversary can infer communication patterns

**Endpoint security:**
- No protection against malware, keyloggers, or physical access
- `shared_secret` stored unencrypted in memory
- No secure enclave or hardware security module (HSM) integration

**Denial of service:**
- Adversary can drop all messages (network-level DoS)
- No retry or reliability mechanism

**Compromise of PRNG:**
- System depends on secure random number generation for nonces
- Weak PRNG could lead to nonce reuse (catastrophic for stream ciphers)

## 4. Accurate Security Claims

### 4.1 What to Say ✅

**Acceptable claims:**

1. "Hyper-rotation provides **window-confined exposure**: compromise of a single time window key only affects that window."

2. "Messages are encrypted with **XChaCha20-Poly1305 AEAD**, providing strong confidentiality and authenticity."

3. "The system uses **time-based key rotation** (1-10 seconds) to limit the impact of key compromise."

4. "For scenarios where the `shared_secret` remains secure, hyper-rotation provides **efficient, low-latency encryption** without online key exchange."

5. "The MVP is suitable for **trusted endpoints** with out-of-band secret sharing (e.g., in-person QR exchange)."

### 4.2 What NOT to Say ❌

**Inaccurate/misleading claims to avoid:**

1. ❌ "Hyper-rotation provides **forward secrecy**."
   - **Truth:** Only if using future "Secure Mode" with asymmetric ratchet

2. ❌ "Past messages are safe even if your device is compromised."
   - **Truth:** Compromise of `shared_secret` allows decryption of all recorded traffic

3. ❌ "Hyper-rotation is **as secure as Signal**."
   - **Truth:** Signal provides PFS/PCS via Double Ratchet; we don't (MVP)

4. ❌ "Automatically recover from key compromise."
   - **Truth:** No PCS mechanism; must manually change `shared_secret`

5. ❌ "Protection against traffic analysis."
   - **Truth:** Message timing and size are visible

## 5. Comparison to Other Protocols

### 5.1 vs. Signal Protocol

| Feature | Hyper-Rotation MVP | Signal Double Ratchet |
|---------|-------------------|----------------------|
| Forward Secrecy | ❌ No | ✅ Yes (ECDH per session) |
| Post-Compromise Security | ❌ No | ✅ Yes (self-healing) |
| Key Exchange | Static (out-of-band) | Dynamic (in-band DH) |
| Latency | Very low (~10-30ms) | Low (~50-100ms) |
| Metadata Leakage | Window ID | More (handshake messages) |
| Offline Messages | ✅ Yes (if time-synced) | ✅ Yes (with server storage) |
| Setup Complexity | Low (QR code) | Medium (key verification) |

**Use case fit:**
- **Hyper-rotation:** Real-time, low-latency, trusted devices (e.g., team comms, IoT)
- **Signal:** General-purpose messaging, untrusted networks, long-term conversations

### 5.2 vs. TLS 1.3

| Feature | Hyper-Rotation MVP | TLS 1.3 |
|---------|-------------------|---------|
| Forward Secrecy | ❌ No | ✅ Yes (ephemeral ECDHE) |
| Session Resumption | N/A | ✅ Yes (0-RTT, PSK) |
| Certificate Auth | No (pre-shared secret) | ✅ Yes (X.509 certs) |
| Key Rotation | ✅ Automatic (time-based) | Manual (rekey) |
| Latency | Very low | Low (1-RTT handshake) |

**Use case fit:**
- **Hyper-rotation:** Symmetric, pre-shared secret, embedded systems
- **TLS:** Client-server, public-key infrastructure, web/API security

### 5.3 vs. WireGuard

| Feature | Hyper-Rotation MVP | WireGuard |
|---------|-------------------|-----------|
| Forward Secrecy | ❌ No | ✅ Yes (rekeying) |
| Key Rotation | ✅ Every 1-10s | Every 2 min (rekey) |
| Transport | Application-layer | Network-layer (VPN) |
| Latency | Very low (~10ms) | Very low (~15ms) |
| Setup | QR code | Config files |

**Use case fit:**
- **Hyper-rotation:** Application messaging, flexible rotation
- **WireGuard:** VPN, network-level encryption

## 6. Future: Secure Mode (PFS-enabled)

### 6.1 Design Sketch

To add true forward secrecy, we'll integrate **periodic ECDH ratcheting**:

```
# Every N windows (e.g., N=10, so every 30 seconds for 3s rotation):
(eph_pub, eph_priv) = ECDH.generate()
send_public_key(eph_pub)

# Upon receiving peer's eph_pub_peer:
shared_dh = ECDH.agree(eph_priv, eph_pub_peer)
shared_secret_new = HKDF(shared_secret_old || shared_dh || "ratchet")

# Zeroize old keys
zeroize(eph_priv)
zeroize(shared_secret_old)
```

**Properties gained:**
- ✅ Forward secrecy: Compromise at time T doesn't reveal pre-T keys
- ✅ Post-compromise security: System heals after N windows
- ✅ Backward compatible: Can detect and upgrade based on protocol version

**Trade-offs:**
- Slightly higher latency (periodic ECDH)
- Requires online presence for ratchet messages (can't be fully offline)

### 6.2 Roadmap

1. **MVP (current):** Time-based derivation only, no PFS
2. **Secure Mode v1:** Add optional ECDH ratchet (user-configurable)
3. **Secure Mode v2:** Integrate MLS for group chats with TreeKEM
4. **Secure Mode v3:** Add deniability via post-conversation MAC disclosure

## 7. Best Practices

### 7.1 Deployment Recommendations

**For the MVP, only use in scenarios where:**
1. ✅ Endpoints are physically secure (no malware, no theft)
2. ✅ `shared_secret` is high-entropy (≥128 bits, preferably ≥256 bits)
3. ✅ Secret bootstrapping is out-of-band and secure (in-person QR, hardware token)
4. ✅ Parties mutually trust each other (no deniability needed)
5. ✅ Low latency is critical (real-time comms)

**Do NOT use MVP if:**
- ❌ Endpoints may be compromised (use Signal or Secure Mode)
- ❌ Long-term archival of encrypted messages (PFS is critical)
- ❌ Parties don't trust each other (need deniability)
- ❌ Regulatory compliance requires PFS (e.g., some financial standards)

### 7.2 Operational Security

**Key management:**
- Store `shared_secret` encrypted at rest (OS keychain, hardware token)
- Rotate `shared_secret` periodically (e.g., every 30 days) via secure channel
- Use unique secrets per channel (don't reuse)

**Monitoring:**
- Log clock drift events (if drift > 1 window, investigate NTP issues)
- Monitor replay protection rejections (could indicate replay attacks)
- Alert on crypto failures (authentication errors, invalid headers)

**Incident response:**
- If compromise suspected: immediately change `shared_secret` out-of-band
- If compromise confirmed: assume all past messages compromised (no PFS)
- Consider switching to "Secure Mode" for future communications

## 8. Responsible Disclosure

**When discussing Hyper-Rotation Messenger:**

1. **Always mention MVP limitations:**
   - "This is an MVP without forward secrecy."
   - "Compromise of the shared secret reveals all past and future messages."

2. **Explain the trade-off:**
   - "We prioritize ultra-low latency and time-based UX over PFS for this use case."
   - "For PFS, use Signal Protocol or wait for our Secure Mode."

3. **Point to this document:**
   - Link to `SECURITY_NOTES.md` in README
   - Include in release notes

4. **Future-proof:**
   - "Secure Mode with PFS is planned for Q2 2025 (example date)."

## 9. Conclusion

The Hyper-Rotation Messenger MVP provides **strong encryption and window-confined security** but **does not offer forward secrecy** due to its deterministic key derivation from a static shared secret.

**This is a deliberate design choice** to achieve:
- Ultra-low latency (no online key exchange)
- Time-based UX (keys rotate automatically)
- Simplicity (no complex ratchet state)

**For applications requiring PFS**, either:
1. Use Signal Protocol, MLS, or similar (now)
2. Wait for our "Secure Mode" with ECDH ratcheting (future)

**Transparency is critical:** Always clearly communicate these limitations to users and developers.

---

**Document version:** 1.0  
**Last updated:** 2025-10-22  
**Status:** MVP specification
