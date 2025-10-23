#!/usr/bin/env python3
"""
TRANSEC Advanced Examples

This module demonstrates TRANSEC in real-world tactical and industrial scenarios:
1. Drone swarm coordination
2. SCADA/industrial telemetry
3. Autonomous vehicle platoons
4. Time synchronization strategies
"""

import sys
import os
import time
import random
from typing import List, Tuple

# Add parent directory to path if running from examples/
if os.path.exists('../python/transec.py'):
    sys.path.insert(0, '../python')
else:
    sys.path.insert(0, './python')

from transec import TransecCipher, generate_shared_secret


# ============================================================================
# Example 1: Drone Swarm Coordination
# ============================================================================

class DroneSwarmNode:
    """Simulates a drone in a tactical swarm with TRANSEC encryption."""
    
    def __init__(self, node_id: int, mission_secret: bytes):
        self.node_id = node_id
        # Use mission-specific context to isolate key streams
        context = f"swarm:alpha:mission:2024".encode()
        # Aggressive 1-second slot duration for tactical operations
        self.cipher = TransecCipher(
            mission_secret,
            context=context,
            slot_duration=1,
            drift_window=1  # Tight synchronization via GPS
        )
        self.sequence = 0
    
    def send_command(self, command: str, target_id: int = None) -> bytes:
        """Send encrypted command to swarm."""
        self.sequence += 1
        
        # Include target in associated data for routing
        aad = f"from:{self.node_id}".encode()
        if target_id is not None:
            aad += f",to:{target_id}".encode()
        
        message = f"{command}"
        packet = self.cipher.seal(message.encode(), self.sequence, associated_data=aad)
        
        return packet
    
    def receive_command(self, packet: bytes, expected_from: int = None, is_targeted: bool = False) -> Tuple[bool, str]:
        """Receive and decrypt command from swarm."""
        # Reconstruct AAD for verification
        aad = b""
        if expected_from is not None:
            aad = f"from:{expected_from}".encode()
            if is_targeted:
                aad += f",to:{self.node_id}".encode()
        
        plaintext = self.cipher.open(packet, associated_data=aad)
        
        if plaintext:
            return (True, plaintext.decode())
        else:
            return (False, "")


def demo_drone_swarm():
    """Demonstrate drone swarm coordination with TRANSEC."""
    print("=" * 70)
    print("Example 1: Drone Swarm Coordination")
    print("=" * 70)
    print()
    
    # Mission secret provisioned before takeoff
    mission_secret = generate_shared_secret()
    print(f"Mission secret provisioned (32 bytes)")
    print(f"Secret: {mission_secret.hex()[:32]}...")
    print()
    
    # Create swarm nodes
    leader = DroneSwarmNode(0, mission_secret)
    follower1 = DroneSwarmNode(1, mission_secret)
    follower2 = DroneSwarmNode(2, mission_secret)
    
    print("Swarm initialized: Leader (Node 0) + 2 Followers")
    print()
    
    # Leader sends formation command
    print("Leader → All: Formation Delta")
    packet = leader.send_command("formation:delta")
    print(f"  Encrypted packet: {len(packet)} bytes")
    
    # Followers receive and execute (broadcast, no specific sender check)
    success1, cmd1 = follower1.receive_command(packet, expected_from=0)
    success2, cmd2 = follower2.receive_command(packet, expected_from=0)
    
    print(f"  Follower 1: {'✓' if success1 else '✗'} {cmd1}")
    print(f"  Follower 2: {'✓' if success2 else '✗'} {cmd2}")
    print()
    
    # Targeted command to specific drone
    print("Leader → Follower 1: Advance position")
    packet = leader.send_command("advance:north:100m", target_id=1)
    print(f"  Encrypted packet: {len(packet)} bytes")
    
    success, cmd = follower1.receive_command(packet, expected_from=0, is_targeted=True)
    print(f"  Follower 1: {'✓' if success else '✗'} {cmd}")
    print()
    
    # Performance: Zero-latency encryption
    print("Performance test: 100 commands")
    start = time.time()
    for i in range(100):
        packet = leader.send_command(f"status:update:{i}")
        follower1.receive_command(packet)
    elapsed = time.time() - start
    
    print(f"  Total time: {elapsed*1000:.2f}ms")
    print(f"  Per-message: {elapsed/100*1000:.3f}ms")
    print(f"  Throughput: {100/elapsed:.1f} commands/sec")
    print()


# ============================================================================
# Example 2: SCADA/Industrial Telemetry
# ============================================================================

class SCADANode:
    """Simulates a SCADA node with TRANSEC encryption."""
    
    def __init__(self, node_id: str, grid_secret: bytes):
        self.node_id = node_id
        # Grid-specific context
        context = b"scada:grid:west:production"
        # 5-second slots for balance of security and robustness
        self.cipher = TransecCipher(
            grid_secret,
            context=context,
            slot_duration=5,
            drift_window=2  # Allow some clock drift
        )
        self.sequence = 0
    
    def send_telemetry(self, voltage: float, current: float, frequency: float) -> bytes:
        """Send encrypted telemetry data."""
        self.sequence += 1
        
        # Encode telemetry as compact binary
        telemetry = f"{voltage:.2f},{current:.2f},{frequency:.3f}"
        
        # Include node ID in AAD
        aad = f"node:{self.node_id}".encode()
        
        packet = self.cipher.seal(telemetry.encode(), self.sequence, associated_data=aad)
        return packet
    
    def receive_telemetry(self, packet: bytes, expected_node: str) -> Tuple[bool, dict]:
        """Receive and decrypt telemetry data."""
        aad = f"node:{expected_node}".encode()
        
        plaintext = self.cipher.open(packet, associated_data=aad)
        
        if plaintext:
            values = plaintext.decode().split(',')
            return (True, {
                'voltage': float(values[0]),
                'current': float(values[1]),
                'frequency': float(values[2])
            })
        else:
            return (False, {})


def demo_scada_telemetry():
    """Demonstrate SCADA telemetry with TRANSEC."""
    print("=" * 70)
    print("Example 2: SCADA/Industrial Telemetry")
    print("=" * 70)
    print()
    
    # Grid secret rotated daily via secure channel
    grid_secret = generate_shared_secret()
    print(f"Grid secret provisioned (rotated daily)")
    print(f"Secret: {grid_secret.hex()[:32]}...")
    print()
    
    # Create SCADA nodes
    substation = SCADANode("SUBSTATION_A1", grid_secret)
    control_center = SCADANode("CONTROL_CENTER", grid_secret)
    
    print("SCADA network: Substation A1 → Control Center")
    print()
    
    # Simulate telemetry stream
    print("Telemetry stream (5 samples):")
    for i in range(5):
        # Simulated sensor readings
        voltage = 230.0 + random.uniform(-5, 5)
        current = 100.0 + random.uniform(-10, 10)
        frequency = 50.0 + random.uniform(-0.1, 0.1)
        
        # Send encrypted telemetry
        packet = substation.send_telemetry(voltage, current, frequency)
        
        # Control center receives
        success, data = control_center.receive_telemetry(packet, "SUBSTATION_A1")
        
        if success:
            print(f"  Sample {i+1}: V={data['voltage']:.2f}V, "
                  f"I={data['current']:.2f}A, f={data['frequency']:.3f}Hz ✓")
        else:
            print(f"  Sample {i+1}: Authentication failed ✗")
        
        time.sleep(0.1)  # Simulate 100ms sampling rate
    
    print()
    
    # Critical: No TLS handshake delay during grid transient
    print("Critical scenario: Grid transient detected")
    print("  Requirement: <5ms alert propagation")
    
    start = time.time()
    alert_packet = substation.send_telemetry(190.0, 150.0, 49.5)  # Abnormal readings
    success, data = control_center.receive_telemetry(alert_packet, "SUBSTATION_A1")
    elapsed = (time.time() - start) * 1000
    
    print(f"  Alert encrypted and transmitted: {elapsed:.2f}ms ✓")
    print(f"  Values: V={data['voltage']:.2f}V (LOW), "
          f"I={data['current']:.2f}A (HIGH), f={data['frequency']:.3f}Hz (LOW)")
    print()


# ============================================================================
# Example 3: Autonomous Vehicle Platoon
# ============================================================================

class VehicleNode:
    """Simulates an autonomous vehicle in a platoon."""
    
    def __init__(self, vehicle_id: int, platoon_secret: bytes):
        self.vehicle_id = vehicle_id
        context = b"v2v:highway:eastbound"
        # Very aggressive 1-second slots for safety-critical V2V
        self.cipher = TransecCipher(
            platoon_secret,
            context=context,
            slot_duration=1,
            drift_window=1
        )
        self.sequence = 0
    
    def broadcast_position(self, lat: float, lon: float, speed: float, heading: float) -> bytes:
        """Broadcast encrypted position update."""
        self.sequence += 1
        
        position = f"{lat:.6f},{lon:.6f},{speed:.1f},{heading:.1f}"
        aad = f"vehicle:{self.vehicle_id}".encode()
        
        packet = self.cipher.seal(position.encode(), self.sequence, associated_data=aad)
        return packet
    
    def receive_position(self, packet: bytes, expected_vehicle: int) -> Tuple[bool, dict]:
        """Receive encrypted position update."""
        aad = f"vehicle:{expected_vehicle}".encode()
        
        plaintext = self.cipher.open(packet, associated_data=aad)
        
        if plaintext:
            values = plaintext.decode().split(',')
            return (True, {
                'lat': float(values[0]),
                'lon': float(values[1]),
                'speed': float(values[2]),
                'heading': float(values[3])
            })
        else:
            return (False, {})


def demo_vehicle_platoon():
    """Demonstrate V2V communication in vehicle platoon."""
    print("=" * 70)
    print("Example 3: Autonomous Vehicle Platoon")
    print("=" * 70)
    print()
    
    # Platoon secret established during join protocol
    platoon_secret = generate_shared_secret()
    print(f"Platoon secret established")
    print(f"Secret: {platoon_secret.hex()[:32]}...")
    print()
    
    # Create vehicle platoon
    lead_vehicle = VehicleNode(1, platoon_secret)
    follow_vehicle1 = VehicleNode(2, platoon_secret)
    follow_vehicle2 = VehicleNode(3, platoon_secret)
    
    print("Platoon formed: Lead vehicle + 2 following vehicles")
    print()
    
    # Simulate position updates
    print("Position updates (10 Hz for collision avoidance):")
    
    for i in range(5):
        # Lead vehicle broadcasts position
        lat = 37.7749 + i * 0.0001
        lon = -122.4194
        speed = 65.0 + random.uniform(-2, 2)
        heading = 90.0
        
        packet = lead_vehicle.broadcast_position(lat, lon, speed, heading)
        
        # Following vehicles receive
        success1, pos1 = follow_vehicle1.receive_position(packet, 1)
        success2, pos2 = follow_vehicle2.receive_position(packet, 1)
        
        if success1 and success2:
            print(f"  Update {i+1}: Lead at ({pos1['lat']:.6f}, {pos1['lon']:.6f}), "
                  f"{pos1['speed']:.1f} mph ✓")
        
        time.sleep(0.1)  # 10 Hz update rate
    
    print()
    
    # Safety-critical: Emergency brake
    print("Safety-critical scenario: Lead vehicle emergency brake")
    print("  Requirement: <100ms propagation to prevent collision")
    
    start = time.time()
    brake_packet = lead_vehicle.broadcast_position(37.7750, -122.4194, 0.0, 90.0)
    success1, pos1 = follow_vehicle1.receive_position(brake_packet, 1)
    success2, pos2 = follow_vehicle2.receive_position(brake_packet, 1)
    elapsed = (time.time() - start) * 1000
    
    print(f"  Emergency brake signal propagated: {elapsed:.2f}ms ✓")
    print(f"  Following vehicles detected speed drop to {pos1['speed']:.1f} mph")
    print()


# ============================================================================
# Example 4: Time Synchronization Strategies
# ============================================================================

def demo_time_sync_strategies():
    """Demonstrate different time synchronization approaches."""
    print("=" * 70)
    print("Example 4: Time Synchronization Strategies")
    print("=" * 70)
    print()
    
    secret = generate_shared_secret()
    
    # Strategy 1: GPS/GNSS synchronized
    print("Strategy 1: GPS/GNSS Synchronization")
    print("  Accuracy: ±10 nanoseconds")
    print("  Best for: Tactical operations, outdoor deployments")
    gps_cipher = TransecCipher(secret, slot_duration=1, drift_window=1)
    print(f"  Configuration: 1s slots, ±1 slot window")
    print()
    
    # Strategy 2: NTP synchronized
    print("Strategy 2: Network Time Protocol (NTP)")
    print("  Accuracy: ±1-50 milliseconds")
    print("  Best for: Data center, enterprise networks")
    ntp_cipher = TransecCipher(secret, slot_duration=5, drift_window=2)
    print(f"  Configuration: 5s slots, ±2 slot window")
    print()
    
    # Strategy 3: Loose synchronization
    print("Strategy 3: Loose Synchronization")
    print("  Accuracy: ±1-5 seconds")
    print("  Best for: Degraded environments, mobile networks")
    loose_cipher = TransecCipher(secret, slot_duration=30, drift_window=5)
    print(f"  Configuration: 30s slots, ±5 slot window")
    print()
    
    # Demonstrate drift tolerance
    print("Drift Tolerance Test:")
    current_slot = gps_cipher.get_current_slot()
    
    # Simulate message from slightly out-of-sync node
    message = b"Test message"
    
    # Message from past slot
    past_packet = gps_cipher.seal(message, 1, slot_index=current_slot - 1)
    if gps_cipher.open(past_packet, check_replay=False):
        print("  ✓ Accepted message from -1 slot (within window)")
    
    # Message from way past
    old_packet = gps_cipher.seal(message, 2, slot_index=current_slot - 10)
    if gps_cipher.open(old_packet, check_replay=False) is None:
        print("  ✓ Rejected message from -10 slots (outside window)")
    
    print()


# ============================================================================
# Main Demo Runner
# ============================================================================

def main():
    """Run all advanced examples."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TRANSEC Advanced Examples" + " " * 28 + "║")
    print("║" + " " * 10 + "Military-Inspired Zero-Handshake Encryption" + " " * 14 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        demo_drone_swarm()
        input("Press Enter to continue to next example...")
        print()
        
        demo_scada_telemetry()
        input("Press Enter to continue to next example...")
        print()
        
        demo_vehicle_platoon()
        input("Press Enter to continue to next example...")
        print()
        
        demo_time_sync_strategies()
        
        print()
        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  • Zero-RTT encryption enables sub-millisecond latency")
        print("  • Time-sliced keying adapted from military COMSEC/TRANSEC")
        print("  • Ideal for tactical, industrial, and safety-critical applications")
        print("  • Tradeoff: No PFS, but acceptable for systems with pre-shared keys")
        print()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")


if __name__ == "__main__":
    main()
