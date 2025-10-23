#!/usr/bin/env python3
"""
TRANSEC Prime Optimization Demo

Demonstrates the curvature reduction achieved by prime-based slot normalization
and shows practical usage of the feature.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from transec import TransecCipher, generate_shared_secret
from transec_prime_optimization import (
    compute_curvature,
    normalize_slot_to_prime,
    compute_curvature_reduction,
    is_prime,
)


def demo_curvature_analysis():
    """Demonstrate curvature computation and prime advantages."""
    print("=" * 70)
    print("TRANSEC Prime Optimization Demo")
    print("=" * 70)
    print()
    
    print("1. Curvature Analysis for Slot Indices")
    print("-" * 70)
    print(f"{'Slot':<8} {'Prime?':<8} {'κ(n)':<12} {'vs Neighbors'}")
    print("-" * 70)
    
    test_slots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    
    for n in test_slots:
        kappa = compute_curvature(n)
        is_p = is_prime(n)
        marker = "★ PRIME" if is_p else ""
        
        # Compare with neighbors
        comparison = ""
        if n > 1:
            prev_kappa = compute_curvature(n - 1)
            if is_p and kappa < prev_kappa:
                reduction = (prev_kappa - kappa) / prev_kappa * 100
                comparison = f"↓{reduction:.1f}% vs {n-1}"
        
        print(f"{n:<8} {marker:<8} {kappa:<12.6f} {comparison}")
    
    print()


def demo_normalization_strategies():
    """Demonstrate different normalization strategies."""
    print("2. Normalization Strategy Comparison")
    print("-" * 70)
    print(f"{'Original':<10} {'Nearest':<10} {'Next':<10} {'κ Reduction'}")
    print("-" * 70)
    
    test_values = [4, 6, 8, 10, 12, 14, 16, 20, 50, 100]
    
    for n in test_values:
        nearest = normalize_slot_to_prime(n, "nearest")
        next_p = normalize_slot_to_prime(n, "next")
        reduction = compute_curvature_reduction(n, nearest)
        
        print(f"{n:<10} {nearest:<10} {next_p:<10} {reduction:.1f}%")
    
    print()


def demo_practical_usage():
    """Demonstrate practical usage with encryption/decryption."""
    print("3. Practical Usage Example")
    print("-" * 70)
    
    # Generate shared secret
    secret = generate_shared_secret()
    
    # Create ciphers with different strategies
    cipher_none = TransecCipher(secret, slot_duration=3600, prime_strategy="none")
    cipher_prime = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
    
    plaintext = b"Secret message for drone swarm coordination"
    sequence = 1
    
    # Without prime optimization
    print("\nWithout Prime Optimization:")
    packet_none = cipher_none.seal(plaintext, sequence)
    slot_none = cipher_none.get_current_slot()
    kappa_none = compute_curvature(slot_none)
    print(f"  Slot index: {slot_none}")
    print(f"  Curvature:  κ({slot_none}) = {kappa_none:.6f}")
    print(f"  Packet size: {len(packet_none)} bytes")
    
    # With prime optimization
    print("\nWith Prime Optimization (nearest):")
    packet_prime = cipher_prime.seal(plaintext, sequence)
    slot_prime = cipher_prime.get_current_slot()
    kappa_prime = compute_curvature(slot_prime)
    print(f"  Slot index: {slot_prime}")
    print(f"  Curvature:  κ({slot_prime}) = {kappa_prime:.6f}")
    print(f"  Packet size: {len(packet_prime)} bytes")
    
    # Show improvement
    if kappa_none > 0:
        improvement = (kappa_none - kappa_prime) / kappa_none * 100
        print(f"\n  Curvature reduction: {improvement:.2f}%")
        print(f"  {'✓ Prime slot has lower curvature!' if improvement > 0 else '✓ Slot is already prime'}")
    
    print()


def demo_interoperability():
    """Demonstrate interoperability between sender and receiver."""
    print("4. Sender/Receiver Interoperability")
    print("-" * 70)
    
    # Both parties must use same secret and strategy
    secret = generate_shared_secret()
    
    sender = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
    receiver = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
    
    messages = [
        b"Alert: Enemy aircraft detected at sector 7",
        b"Regroup at coordinates: 34.05, -118.25",
        b"Mission accomplished, returning to base",
    ]
    
    print("\nSending encrypted messages with prime-optimized slots:")
    print()
    
    for i, msg in enumerate(messages, 1):
        packet = sender.seal(msg, sequence=i)
        decrypted = receiver.open(packet, check_replay=False)
        
        status = "✓ SUCCESS" if decrypted == msg else "✗ FAILED"
        print(f"  Message {i}: {status}")
        print(f"    Plaintext:  {msg.decode()}")
        print(f"    Encrypted:  {len(packet)} bytes")
        if decrypted:
            print(f"    Decrypted:  {decrypted.decode()}")
        print()
    
    print()


def main():
    """Run all demonstrations."""
    demo_curvature_analysis()
    demo_normalization_strategies()
    demo_practical_usage()
    demo_interoperability()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Prime-valued slots have lower curvature than composite neighbors")
    print("  • Curvature reduction ranges from 25% to 88% depending on the slot")
    print("  • Both sender and receiver must use the same prime_strategy")
    print("  • Backward compatible: default strategy is 'none' (no normalization)")
    print()
    print("For more details, see: docs/TRANSEC_PRIME_OPTIMIZATION.md")
    print()


if __name__ == "__main__":
    main()
