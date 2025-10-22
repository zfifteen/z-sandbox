#!/usr/bin/env python3
"""
Hyper-Rotation Core (hr_core)

Core cryptographic modules for time-windowed hyper-rotation encryption.

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
