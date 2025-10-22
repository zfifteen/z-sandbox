#!/usr/bin/env python3
"""
Wire Protocol

Defines message header format and serialization for hyper-rotation messenger.
"""

import struct
import hashlib
from typing import Tuple
from dataclasses import dataclass


# Algorithm identifiers
ALG_AEAD_XCHACHA20_POLY1305 = 0x01
ALG_RSA_DEMO = 0x02


@dataclass
class MessageHeader:
    """
    Message header structure (cleartext).
    
    Layout (56 bytes total):
    - version: u32 (4 bytes)
    - alg_id: u32 (4 bytes)
    - window_id: u64 (8 bytes)
    - channel_id_hash: u32 (4 bytes)
    - msg_counter: u32 (4 bytes)
    - nonce: 192 bits (24 bytes)
    - reserved: u64 (8 bytes, for future use)
    """
    version: int  # Protocol version
    alg_id: int  # Algorithm identifier
    window_id: int  # Time window ID
    channel_id_hash: int  # Truncated hash of channel_id for routing
    msg_counter: int  # Per-window message counter (anti-replay)
    nonce: bytes  # AEAD nonce (24 bytes for XChaCha20)
    reserved: int = 0  # Reserved for future use
    
    HEADER_SIZE = 56  # Total header size in bytes
    VERSION = 1
    
    def __post_init__(self):
        """Validate header fields."""
        if self.version != self.VERSION:
            raise ValueError(f"Unsupported version: {self.version}")
        if self.alg_id not in (ALG_AEAD_XCHACHA20_POLY1305, ALG_RSA_DEMO):
            raise ValueError(f"Unknown algorithm ID: {self.alg_id}")
        if len(self.nonce) != 24:
            raise ValueError(f"Nonce must be 24 bytes, got {len(self.nonce)}")
    
    @staticmethod
    def compute_channel_hash(channel_id: str) -> int:
        """
        Compute truncated hash of channel_id for routing.
        
        Args:
            channel_id: Channel identifier string
            
        Returns:
            32-bit hash value
        """
        hash_bytes = hashlib.blake2b(
            channel_id.encode(), 
            digest_size=4
        ).digest()
        return struct.unpack('<I', hash_bytes)[0]
    
    def encode(self) -> bytes:
        """
        Serialize header to bytes.
        
        Returns:
            56-byte header
        """
        return struct.pack(
            '<IIQII24sQ',
            self.version,
            self.alg_id,
            self.window_id,
            self.channel_id_hash,
            self.msg_counter,
            self.nonce,
            self.reserved
        )
    
    @staticmethod
    def decode(data: bytes) -> 'MessageHeader':
        """
        Deserialize header from bytes.
        
        Args:
            data: Raw header bytes (at least 56 bytes)
            
        Returns:
            MessageHeader instance
            
        Raises:
            ValueError: If data is malformed
        """
        if len(data) < MessageHeader.HEADER_SIZE:
            raise ValueError(
                f"Header too short: {len(data)} < {MessageHeader.HEADER_SIZE}"
            )
        
        try:
            version, alg_id, window_id, channel_hash, counter, nonce, reserved = struct.unpack(
                '<IIQII24sQ',
                data[:MessageHeader.HEADER_SIZE]
            )
        except struct.error as e:
            raise ValueError(f"Header decode error: {e}")
        
        return MessageHeader(
            version=version,
            alg_id=alg_id,
            window_id=window_id,
            channel_id_hash=channel_hash,
            msg_counter=counter,
            nonce=nonce,
            reserved=reserved
        )
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"MessageHeader(v={self.version}, alg=0x{self.alg_id:02x}, "
            f"window={self.window_id}, channel=0x{self.channel_id_hash:08x}, "
            f"counter={self.msg_counter}, nonce={self.nonce.hex()[:16]}...)"
        )


class WireMessage:
    """Complete wire-format message (header + ciphertext)."""
    
    def __init__(self, header: MessageHeader, ciphertext: bytes):
        """
        Initialize wire message.
        
        Args:
            header: Message header
            ciphertext: Encrypted payload with authentication tag
        """
        self.header = header
        self.ciphertext = ciphertext
    
    def encode(self) -> bytes:
        """
        Serialize message to wire format.
        
        Returns:
            Serialized message (header || ciphertext)
        """
        return self.header.encode() + self.ciphertext
    
    @staticmethod
    def decode(data: bytes) -> 'WireMessage':
        """
        Deserialize message from wire format.
        
        Args:
            data: Raw message bytes
            
        Returns:
            WireMessage instance
            
        Raises:
            ValueError: If data is malformed
        """
        if len(data) < MessageHeader.HEADER_SIZE:
            raise ValueError(f"Message too short: {len(data)} bytes")
        
        header = MessageHeader.decode(data[:MessageHeader.HEADER_SIZE])
        ciphertext = data[MessageHeader.HEADER_SIZE:]
        
        return WireMessage(header, ciphertext)
    
    def __len__(self) -> int:
        """Total message size."""
        return MessageHeader.HEADER_SIZE + len(self.ciphertext)
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"WireMessage({self.header}, "
            f"ciphertext_len={len(self.ciphertext)})"
        )


def test_wire_format():
    """Test wire format encoding/decoding."""
    import os
    
    # Create test header
    channel_id = "test_channel_123"
    header = MessageHeader(
        version=MessageHeader.VERSION,
        alg_id=ALG_AEAD_XCHACHA20_POLY1305,
        window_id=42,
        channel_id_hash=MessageHeader.compute_channel_hash(channel_id),
        msg_counter=7,
        nonce=os.urandom(24)
    )
    
    # Test header encoding/decoding
    header_bytes = header.encode()
    assert len(header_bytes) == MessageHeader.HEADER_SIZE
    
    decoded_header = MessageHeader.decode(header_bytes)
    assert decoded_header.version == header.version
    assert decoded_header.alg_id == header.alg_id
    assert decoded_header.window_id == header.window_id
    assert decoded_header.channel_id_hash == header.channel_id_hash
    assert decoded_header.msg_counter == header.msg_counter
    assert decoded_header.nonce == header.nonce
    
    # Test wire message
    ciphertext = b"encrypted_payload_with_authentication_tag"
    wire_msg = WireMessage(header, ciphertext)
    
    wire_bytes = wire_msg.encode()
    assert len(wire_bytes) == MessageHeader.HEADER_SIZE + len(ciphertext)
    
    decoded_msg = WireMessage.decode(wire_bytes)
    assert decoded_msg.header.window_id == header.window_id
    assert decoded_msg.ciphertext == ciphertext
    
    # Test channel hash determinism
    hash1 = MessageHeader.compute_channel_hash(channel_id)
    hash2 = MessageHeader.compute_channel_hash(channel_id)
    assert hash1 == hash2
    
    # Test different channels produce different hashes
    hash3 = MessageHeader.compute_channel_hash("different_channel")
    assert hash1 != hash3
    
    print("✓ Wire format tests passed")
    print(f"  Header size: {MessageHeader.HEADER_SIZE} bytes")
    print(f"  Channel hash: 0x{header.channel_id_hash:08x}")
    print(f"  Total message size: {len(wire_msg)} bytes")


if __name__ == "__main__":
    test_wire_format()
