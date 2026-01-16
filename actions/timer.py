"""
Timer Module

Handles timer and alarm functionality.
"""

import logging
import threading
import time
from typing import Optional, Callable
from datetime import datetime, timedelta


class Timer:
    """
    Simple timer implementation
    
    Supports countdown timers with callback notifications.
    """
    
    def __init__(self, duration_seconds: int, callback: Optional[Callable] = None, name: str = "Timer"):
        self.duration_seconds = duration_seconds
        self.callback = callback
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.is_running = False
        self.is_finished = False
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> bool:
        """Start the timer"""
        if self.is_running:
            self.logger.warning(f"Timer '{self.name}' is already running")
            return False
        
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(seconds=self.duration_seconds)
        self.is_running = True
        self.is_finished = False
        
        # Start timer thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        self.logger.info(f"Timer '{self.name}' started for {self.duration_seconds} seconds")
        return True
    
    def _run(self):
        """Internal timer loop"""
        time.sleep(self.duration_seconds)
        
        self.is_running = False
        self.is_finished = True
        
        self.logger.info(f"Timer '{self.name}' finished!")
        
        # Call callback if provided
        if self.callback:
            try:
                self.callback(self)
            except Exception as e:
                self.logger.error(f"Timer callback error: {e}")
    
    def cancel(self) -> bool:
        """Cancel the timer"""
        if not self.is_running:
            return False
        
        self.is_running = False
        self.logger.info(f"Timer '{self.name}' cancelled")
        return True
    
    def get_remaining_seconds(self) -> int:
        """Get remaining seconds"""
        if not self.is_running or not self.end_time:
            return 0
        
        remaining = (self.end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def get_status(self) -> dict:
        """Get timer status"""
        return {
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "is_running": self.is_running,
            "is_finished": self.is_finished,
            "remaining_seconds": self.get_remaining_seconds(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class TimerManager:
    """
    Timer Manager
    
    Manages multiple timers and provides timer operations.
    """
    
    def __init__(self):
        self.timers: dict[str, Timer] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_timer(self, duration_seconds: int, name: Optional[str] = None, 
                    callback: Optional[Callable] = None) -> Timer:
        """
        Create and start a new timer
        
        Args:
            duration_seconds: Timer duration in seconds
            name: Optional timer name
            callback: Optional callback function when timer finishes
            
        Returns:
            Timer instance
        """
        if name is None:
            name = f"Timer_{len(self.timers) + 1}"
        
        # Create timer
        timer = Timer(duration_seconds, callback, name)
        
        # Start timer
        timer.start()
        
        # Store timer
        self.timers[name] = timer
        
        self.logger.info(f"Created timer '{name}' for {duration_seconds} seconds")
        return timer
    
    def cancel_timer(self, name: str) -> bool:
        """Cancel a timer by name"""
        if name not in self.timers:
            self.logger.warning(f"Timer '{name}' not found")
            return False
        
        timer = self.timers[name]
        success = timer.cancel()
        
        if success:
            del self.timers[name]
        
        return success
    
    def get_timer(self, name: str) -> Optional[Timer]:
        """Get a timer by name"""
        return self.timers.get(name)
    
    def list_timers(self) -> list[dict]:
        """List all active timers"""
        return [timer.get_status() for timer in self.timers.values() if timer.is_running]
    
    def cleanup_finished(self):
        """Remove finished timers"""
        finished = [name for name, timer in self.timers.items() if timer.is_finished]
        for name in finished:
            del self.timers[name]
        
        if finished:
            self.logger.info(f"Cleaned up {len(finished)} finished timers")


# Global timer manager instance
_timer_manager = TimerManager()


def get_timer_manager() -> TimerManager:
    """Get the global timer manager instance"""
    return _timer_manager


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_timer_finished(timer: Timer):
        print(f"\n⏰ Timer '{timer.name}' finished!")
    
    manager = TimerManager()
    
    print("Creating 5-second timer...")
    timer = manager.create_timer(5, "Test Timer", on_timer_finished)
    
    print(f"Timer status: {timer.get_status()}")
    
    # Wait for timer
    while timer.is_running:
        remaining = timer.get_remaining_seconds()
        print(f"Remaining: {remaining} seconds", end="\r")
        time.sleep(1)
    
    print("\nTimer completed!")
