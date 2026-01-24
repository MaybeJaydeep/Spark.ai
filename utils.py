#!/usr/bin/env python3
"""
Utility Functions for AI Assistant

Common utility functions used across the application.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    import platform
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat(),
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path to ensure
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


def safe_filename(filename: str) -> str:
    """
    Convert string to safe filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename string
    """
    import re
    
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Trim underscores from ends
    safe_name = safe_name.strip('_')
    
    return safe_name or "unnamed"


def get_config_dir() -> str:
    """Get the configuration directory path"""
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    ensure_directory(config_dir)
    return config_dir


def get_logs_dir() -> str:
    """Get the logs directory path"""
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    ensure_directory(logs_dir)
    return logs_dir


def performance_timer(func):
    """
    Decorator to measure function execution time
    
    Usage:
        @performance_timer
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logging.debug(f"{func.__name__} executed in {duration:.4f} seconds")
        
        return result
    return wrapper


class PerformanceMonitor:
    """Simple performance monitoring utility"""
    
    def __init__(self):
        self.timers = {}
        self.counters = {}
    
    def start_timer(self, name: str):
        """Start a named timer"""
        self.timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """Stop a named timer and return duration"""
        if name not in self.timers:
            return 0.0
        
        duration = time.time() - self.timers[name]
        del self.timers[name]
        return duration
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a named counter"""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            "active_timers": list(self.timers.keys()),
            "counters": self.counters.copy(),
            "timestamp": datetime.now().isoformat(),
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


if __name__ == "__main__":
    # Test utilities
    print("🔧 AI Assistant Utilities")
    print("=" * 40)
    
    # Test system info
    info = get_system_info()
    print("\n🖥️  System Information:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test performance monitor
    print("\n⏱️  Performance Monitor Test:")
    performance_monitor.start_timer("test")
    time.sleep(0.1)
    duration = performance_monitor.stop_timer("test")
    print(f"   Test timer: {duration:.4f} seconds")
    
    # Test filename safety
    print("\n📁 Filename Safety Test:")
    unsafe = "test<>file|name?.txt"
    safe = safe_filename(unsafe)
    print(f"   Unsafe: {unsafe}")
    print(f"   Safe: {safe}")
    
    print("\n✅ All utilities working!")