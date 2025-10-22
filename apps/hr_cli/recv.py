#!/usr/bin/env python3
"""
Hyper-Rotation Messenger - Receive

CLI tool for receiving and decrypting messages with time-based key rotation
and clock drift tolerance.
"""

import sys
import os
import socket
import argparse
import time
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from hr_core import (
    KeySchedule, XChaCha20Poly1305, MessageHeader, WireMessage,
    ReplayProtection, ALG_AEAD_XCHACHA20_POLY1305
)
from nacl.exceptions import CryptoError


class HyperRotationReceiver:
    """Hyper-rotation message receiver."""
    
    def __init__(
        self,
        shared_secret: bytes,
        channel_id: str,
        role: str = 'B',  # Opposite of sender
        rotation_seconds: int = 3,
        port: int = 9999,
        max_drift: int = 1
    ):
        """
        Initialize receiver.
        
        Args:
            shared_secret: Shared secret key (>=16 bytes)
            channel_id: Channel identifier
            role: Role ('A' or 'B'), opposite of sender
            rotation_seconds: Key rotation window (1, 3, 5, or 10)
            port: Listen port
            max_drift: Maximum window drift tolerance (±1 recommended)
        """
        # Note: Receiver uses sender's role to derive same keys
        # In production, would have bidirectional channels with different roles
        self.sender_role = 'A' if role == 'B' else 'B'
        
        self.key_schedule = KeySchedule(
            shared_secret, channel_id, self.sender_role, rotation_seconds
        )
        self.replay_protection = ReplayProtection()
        self.channel_id = channel_id
        self.port = port
        self.max_drift = max_drift
        
        print(f"[Receiver] Initialized")
        print(f"  Channel: {channel_id}")
        print(f"  Sender Role: {self.sender_role}")
        print(f"  Rotation: {rotation_seconds}s")
        print(f"  Port: {port}")
        print(f"  Max drift: ±{max_drift} windows")
    
    def receive_and_decrypt(self, wire_bytes: bytes) -> tuple:
        """
        Receive and decrypt a message with drift tolerance.
        
        Args:
            wire_bytes: Raw wire-format message
            
        Returns:
            Tuple of (success: bool, plaintext: str or None, error: str or None)
        """
        try:
            # Decode wire message
            wire_msg = WireMessage.decode(wire_bytes)
            header = wire_msg.header
            ciphertext = wire_msg.ciphertext
            
            # Validate channel
            expected_hash = MessageHeader.compute_channel_hash(self.channel_id)
            if header.channel_id_hash != expected_hash:
                return False, None, "Wrong channel"
            
            # Validate algorithm
            if header.alg_id != ALG_AEAD_XCHACHA20_POLY1305:
                return False, None, f"Unsupported algorithm: 0x{header.alg_id:02x}"
            
            # Check replay
            if not self.replay_protection.check_and_update(
                header.window_id, header.msg_counter
            ):
                return False, None, "Replay detected"
            
            # Try decryption with drift tolerance
            keys_to_try = self.key_schedule.get_keys_with_drift(
                header.window_id, self.max_drift
            )
            
            last_error = None
            for wid, k_enc, k_mac in keys_to_try:
                cipher = XChaCha20Poly1305(k_enc)
                
                try:
                    plaintext_bytes = cipher.decrypt(
                        header.nonce, ciphertext
                    )
                    plaintext = plaintext_bytes.decode('utf-8')
                    
                    # Success!
                    drift = wid - header.window_id
                    drift_str = f" (drift: {drift:+d})" if drift != 0 else ""
                    
                    return True, plaintext, drift_str
                    
                except CryptoError as e:
                    last_error = str(e)
                    continue
                except UnicodeDecodeError:
                    last_error = "Invalid UTF-8"
                    continue
            
            # All attempts failed
            return False, None, f"Decryption failed: {last_error}"
            
        except Exception as e:
            return False, None, f"Error: {e}"
    
    def listen(self):
        """
        Listen for incoming messages.
        """
        print(f"\n=== Listening for messages on port {self.port} ===\n")
        
        # Create listening socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        try:
            while True:
                # Show current window status
                window_id = self.key_schedule.get_current_window()
                time_left = self.key_schedule.get_time_until_rotation()
                
                print(f"[Window {window_id}, expires in {time_left:.1f}s] Waiting for messages...")
                
                # Set timeout for status updates
                server.settimeout(1.0)
                
                try:
                    client, addr = server.accept()
                    
                    # Receive message
                    data = b""
                    while True:
                        chunk = client.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                        
                        # Check if we have a complete message
                        if len(data) >= MessageHeader.HEADER_SIZE:
                            # Try to parse header to get total size
                            try:
                                header = MessageHeader.decode(data)
                                # We have complete header, check if we have full message
                                # For simplicity, assume all data received
                                break
                            except:
                                # Keep receiving
                                continue
                    
                    client.close()
                    
                    if not data:
                        continue
                    
                    # Decrypt message
                    success, plaintext, info = self.receive_and_decrypt(data)
                    
                    if success:
                        print(f"\n[Received] {datetime.now().strftime('%H:%M:%S')}{info}")
                        print(f"  Message: {plaintext}")
                        print()
                    else:
                        print(f"\n[Error] Failed to decrypt: {info}\n")
                        
                except socket.timeout:
                    # Timeout for status update, continue
                    continue
                    
        except KeyboardInterrupt:
            print("\n[Receiver] Shutting down")
        finally:
            server.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Hyper-Rotation Messenger - Receive'
    )
    parser.add_argument(
        '--secret',
        default='default_shared_secret_change_me_12345',
        help='Shared secret (default: test secret)'
    )
    parser.add_argument(
        '--channel',
        default='demo_channel',
        help='Channel ID (default: demo_channel)'
    )
    parser.add_argument(
        '--role',
        choices=['A', 'B'],
        default='B',
        help='Role identifier (default: B, opposite of sender)'
    )
    parser.add_argument(
        '--rotation',
        type=int,
        choices=[1, 3, 5, 10],
        default=3,
        help='Key rotation window in seconds (default: 3)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9999,
        help='Listen port (default: 9999)'
    )
    parser.add_argument(
        '--max-drift',
        type=int,
        default=1,
        help='Maximum window drift tolerance (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Convert secret to bytes
    shared_secret = args.secret.encode('utf-8')
    
    # Create receiver
    receiver = HyperRotationReceiver(
        shared_secret=shared_secret,
        channel_id=args.channel,
        role=args.role,
        rotation_seconds=args.rotation,
        port=args.port,
        max_drift=args.max_drift
    )
    
    # Listen for messages
    receiver.listen()


if __name__ == "__main__":
    main()
