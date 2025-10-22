#!/usr/bin/env python3
"""
Hyper-Rotation Messenger - Send

CLI tool for sending encrypted messages with time-based key rotation.
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
    MessageCounter, ALG_AEAD_XCHACHA20_POLY1305
)


class HyperRotationSender:
    """Hyper-rotation message sender."""
    
    def __init__(
        self,
        shared_secret: bytes,
        channel_id: str,
        role: str = 'A',
        rotation_seconds: int = 3,
        host: str = 'localhost',
        port: int = 9999
    ):
        """
        Initialize sender.
        
        Args:
            shared_secret: Shared secret key (>=16 bytes)
            channel_id: Channel identifier
            role: Role ('A' or 'B')
            rotation_seconds: Key rotation window (1, 3, 5, or 10)
            host: Receiver host
            port: Receiver port
        """
        self.key_schedule = KeySchedule(
            shared_secret, channel_id, role, rotation_seconds
        )
        self.message_counter = MessageCounter()
        self.channel_id = channel_id
        self.host = host
        self.port = port
        
        print(f"[Sender] Initialized")
        print(f"  Channel: {channel_id}")
        print(f"  Role: {role}")
        print(f"  Rotation: {rotation_seconds}s")
        print(f"  Target: {host}:{port}")
    
    def send_message(self, plaintext: str, sock: socket.socket = None) -> bool:
        """
        Encrypt and send a message.
        
        Args:
            plaintext: Message to send
            sock: Optional existing socket connection
            
        Returns:
            True if successful
        """
        # Get current window keys
        window_id, k_enc, k_mac = self.key_schedule.get_current_keys()
        
        # Get next message counter for this window
        msg_counter = self.message_counter.next_counter(window_id)
        
        # Create cipher
        cipher = XChaCha20Poly1305(k_enc)
        
        # Encrypt message
        plaintext_bytes = plaintext.encode('utf-8')
        nonce, ciphertext = cipher.encrypt(plaintext_bytes)
        
        # Build header
        header = MessageHeader(
            version=MessageHeader.VERSION,
            alg_id=ALG_AEAD_XCHACHA20_POLY1305,
            window_id=window_id,
            channel_id_hash=MessageHeader.compute_channel_hash(self.channel_id),
            msg_counter=msg_counter,
            nonce=nonce
        )
        
        # Create wire message
        wire_msg = WireMessage(header, ciphertext)
        wire_bytes = wire_msg.encode()
        
        # Send message
        close_after = False
        if sock is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                close_after = True
            except Exception as e:
                print(f"[Error] Failed to connect: {e}")
                return False
        
        try:
            sock.sendall(wire_bytes)
            
            # Display info
            time_left = self.key_schedule.get_time_until_rotation()
            print(f"\n[Sent] Window {window_id}, Counter {msg_counter}")
            print(f"  Message: {plaintext[:50]}{'...' if len(plaintext) > 50 else ''}")
            print(f"  Size: {len(wire_bytes)} bytes")
            print(f"  Key expires in: {time_left:.1f}s")
            
            return True
        except Exception as e:
            print(f"[Error] Failed to send: {e}")
            return False
        finally:
            if close_after:
                sock.close()
    
    def interactive_mode(self):
        """
        Run interactive send mode with key rotation countdown.
        """
        print("\n=== Interactive Send Mode ===")
        print("Type messages to send (Ctrl+C to exit)")
        print("Empty line sends a heartbeat message\n")
        
        try:
            while True:
                # Show key rotation status
                window_id = self.key_schedule.get_current_window()
                time_left = self.key_schedule.get_time_until_rotation()
                
                prompt = f"[Window {window_id}, expires in {time_left:.1f}s] > "
                
                try:
                    message = input(prompt)
                    
                    if not message:
                        message = f"Heartbeat at {datetime.now().strftime('%H:%M:%S')}"
                    
                    self.send_message(message)
                    
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            print("\n[Sender] Shutting down")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Hyper-Rotation Messenger - Send'
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
        default='A',
        help='Role identifier (default: A)'
    )
    parser.add_argument(
        '--rotation',
        type=int,
        choices=[1, 3, 5, 10],
        default=3,
        help='Key rotation window in seconds (default: 3)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Receiver host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9999,
        help='Receiver port (default: 9999)'
    )
    parser.add_argument(
        '--message',
        help='Single message to send (interactive if not specified)'
    )
    
    args = parser.parse_args()
    
    # Convert secret to bytes
    shared_secret = args.secret.encode('utf-8')
    
    # Create sender
    sender = HyperRotationSender(
        shared_secret=shared_secret,
        channel_id=args.channel,
        role=args.role,
        rotation_seconds=args.rotation,
        host=args.host,
        port=args.port
    )
    
    # Send single message or enter interactive mode
    if args.message:
        success = sender.send_message(args.message)
        sys.exit(0 if success else 1)
    else:
        sender.interactive_mode()


if __name__ == "__main__":
    main()
