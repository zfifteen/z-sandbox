#!/usr/bin/env python3
"""
Replay Protection

Manages per-window message counters to prevent replay attacks.
"""

from typing import Dict, Optional
from collections import defaultdict
import threading


class ReplayProtection:
    """
    Thread-safe replay protection using per-window message counters.
    
    Tracks the highest seen counter for each window to detect replays
    and out-of-order messages.
    """
    
    def __init__(self, max_windows: int = 10):
        """
        Initialize replay protection.
        
        Args:
            max_windows: Maximum number of windows to track (for memory limiting)
        """
        self.max_windows = max_windows
        self.window_counters: Dict[int, int] = {}  # window_id -> highest_counter
        self.lock = threading.Lock()
    
    def check_and_update(self, window_id: int, msg_counter: int) -> bool:
        """
        Check if message is a replay and update counter if valid.
        
        Args:
            window_id: Window identifier
            msg_counter: Message counter from header
            
        Returns:
            True if message is valid (not a replay), False if replay detected
        """
        with self.lock:
            highest_seen = self.window_counters.get(window_id, -1)
            
            if msg_counter <= highest_seen:
                # Replay or out-of-order (reject)
                return False
            
            # Update highest seen counter
            self.window_counters[window_id] = msg_counter
            
            # Enforce memory limit by removing oldest windows
            if len(self.window_counters) > self.max_windows:
                self._cleanup_old_windows(window_id)
            
            return True
    
    def _cleanup_old_windows(self, current_window: int):
        """
        Remove tracking for old windows to limit memory usage.
        
        Keeps only the most recent max_windows entries.
        
        Args:
            current_window: Current window ID for reference
        """
        # Keep windows close to current_window
        min_window = current_window - self.max_windows
        windows_to_remove = [
            wid for wid in self.window_counters
            if wid < min_window
        ]
        
        for wid in windows_to_remove:
            del self.window_counters[wid]
    
    def get_highest_counter(self, window_id: int) -> Optional[int]:
        """
        Get the highest seen counter for a window.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Highest counter seen, or None if window not tracked
        """
        with self.lock:
            return self.window_counters.get(window_id)
    
    def reset(self):
        """Reset all counter state (for testing)."""
        with self.lock:
            self.window_counters.clear()
    
    def get_stats(self) -> dict:
        """
        Get replay protection statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                'tracked_windows': len(self.window_counters),
                'windows': dict(self.window_counters)
            }


class MessageCounter:
    """
    Per-window message counter for sending messages.
    
    Maintains a monotonically increasing counter for each window to ensure
    unique counters and enable replay detection at receiver.
    """
    
    def __init__(self):
        """Initialize message counter."""
        self.counters: Dict[int, int] = defaultdict(int)
        self.lock = threading.Lock()
    
    def next_counter(self, window_id: int) -> int:
        """
        Get the next counter value for a window.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Next counter value (starts at 0)
        """
        with self.lock:
            counter = self.counters[window_id]
            self.counters[window_id] += 1
            return counter
    
    def reset(self):
        """Reset all counters (for testing)."""
        with self.lock:
            self.counters.clear()
    
    def cleanup_old_windows(self, current_window: int, max_windows: int = 10):
        """
        Remove counters for old windows.
        
        Args:
            current_window: Current window ID
            max_windows: Number of recent windows to keep
        """
        with self.lock:
            min_window = current_window - max_windows
            windows_to_remove = [
                wid for wid in self.counters
                if wid < min_window
            ]
            
            for wid in windows_to_remove:
                del self.counters[wid]


def test_replay_protection():
    """Test replay protection functionality."""
    rp = ReplayProtection(max_windows=5)
    
    # Test: First message should be accepted
    assert rp.check_and_update(100, 0) == True
    assert rp.get_highest_counter(100) == 0
    
    # Test: Higher counter should be accepted
    assert rp.check_and_update(100, 1) == True
    assert rp.check_and_update(100, 2) == True
    assert rp.get_highest_counter(100) == 2
    
    # Test: Replay should be rejected
    assert rp.check_and_update(100, 2) == False
    assert rp.check_and_update(100, 1) == False
    assert rp.check_and_update(100, 0) == False
    
    # Test: Different windows are independent
    assert rp.check_and_update(101, 0) == True
    assert rp.check_and_update(101, 1) == True
    
    # Test: Out-of-order messages are rejected
    assert rp.check_and_update(100, 5) == True
    assert rp.check_and_update(100, 3) == False
    
    # Test: Window cleanup
    for wid in range(102, 115):
        rp.check_and_update(wid, 0)
    
    stats = rp.get_stats()
    # Should have cleaned up old windows
    assert stats['tracked_windows'] <= rp.max_windows + 2  # Allow small buffer
    
    # Test message counter
    mc = MessageCounter()
    assert mc.next_counter(100) == 0
    assert mc.next_counter(100) == 1
    assert mc.next_counter(100) == 2
    assert mc.next_counter(101) == 0  # Different window
    
    print("✓ Replay protection tests passed")
    print(f"  Tracked windows: {stats['tracked_windows']}")
    print(f"  Window 100 highest counter: {rp.get_highest_counter(100)}")


if __name__ == "__main__":
    test_replay_protection()
