#!/usr/bin/env python3
"""
Hyper-Rotation Core (hr_core)

⚠️ RESEARCH PROOF OF CONCEPT ONLY ⚠️

This is a research prototype for exploring mathematical concepts in cryptographic
protocol design. NOT suitable for production use or real-world applications.

Do NOT use this code for:
- Real communications requiring security
- Production environments
- Protecting sensitive data
- Any scenario where security matters

Research Purpose: Academic exploration of time-based key derivation concepts,
experimental protocol design, and mathematical research into cryptographic primitives.

Core cryptographic modules for time-windowed hyper-rotation encryption research.

Modules:
- key_schedule: HKDF-based key derivation with time windows
- aead: XChaCha20-Poly1305 AEAD encryption
- wire: Message header format and wire protocol
- replay: Anti-replay protection with per-window counters
- rsa_demo: Z5D-assisted RSA keypair generation (demo only)
"""

__version__ = "0.1.0"

from .key_schedule import KeySchedule
from .aead import XChaCha20Poly1305, AEADCipher
from .wire import MessageHeader, WireMessage, ALG_AEAD_XCHACHA20_POLY1305, ALG_RSA_DEMO
from .replay import ReplayProtection, MessageCounter

__all__ = [
    'KeySchedule',
    'XChaCha20Poly1305',
    'AEADCipher',
    'MessageHeader',
    'WireMessage',
    'ALG_AEAD_XCHACHA20_POLY1305',
    'ALG_RSA_DEMO',
    'ReplayProtection',
    'MessageCounter',
]
