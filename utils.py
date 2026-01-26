#!/usr/bin/env python3
"""
Comprehensive Utility Functions for AI Assistant

Enhanced utility functions used across the application.
"""

import os
import sys
import time
import json
import hashlib
import platform
import subprocess
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    import logging
    
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


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human readable string
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted bytes string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


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
        import logging
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


def get_data_dir() -> str:
    """Get the data directory path"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    ensure_directory(data_dir)
    return data_dir


def load_json_file(file_path: str, default: Any = None) -> Any:
    """
    Load JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
        
    Returns:
        Loaded JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return default


def save_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Save data to JSON file with error handling
    
    Args:
        file_path: Path to save JSON file
        data: Data to save
        indent: JSON indentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        import logging
        logging.error(f"Failed to save JSON file {file_path}: {e}")
        return False


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
    """
    Calculate hash of a file
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256, etc.)
        
    Returns:
        File hash or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None


def is_process_running(process_name: str) -> bool:
    """
    Check if a process is running
    
    Args:
        process_name: Name of the process
        
    Returns:
        True if process is running
    """
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                creationflags=subprocess.CREATE_NO_WINDOW
            ).decode()
            return process_name.lower() in output.lower()
        else:
            output = subprocess.check_output(["pgrep", "-f", process_name]).decode()
            return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False


def get_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
    """
    Find an available port starting from start_port
    
    Args:
        start_port: Starting port number
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number or None
    """
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None


def retry_operation(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry an operation with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
        
    Returns:
        Function result or raises last exception
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay * (backoff ** attempt))
            else:
                raise last_exception


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_time_string(time_str: str) -> Optional[float]:
    """
    Parse time string to seconds
    
    Args:
        time_str: Time string like "5m", "30s", "2h"
        
    Returns:
        Time in seconds or None if invalid
    """
    import re
    
    pattern = r'^(\d+(?:\.\d+)?)\s*([smhd]?)$'
    match = re.match(pattern, time_str.lower().strip())
    
    if not match:
        return None
    
    value, unit = match.groups()
    value = float(value)
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        '': 1  # Default to seconds
    }
    
    return value * multipliers.get(unit, 1)


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
        import logging
        logging.debug(f"{func.__name__} executed in {duration:.4f} seconds")
        
        return result
    return wrapper


class PerformanceMonitor:
    """Enhanced performance monitoring utility"""
    
    def __init__(self):
        self.timers = {}
        self.counters = {}
        self.metrics = {}
    
    def start_timer(self, name: str):
        """Start a named timer"""
        self.timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """Stop a named timer and return duration"""
        if name not in self.timers:
            return 0.0
        
        duration = time.time() - self.timers[name]
        del self.timers[name]
        
        # Store in metrics
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        return duration
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a named counter"""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def record_metric(self, name: str, value: float):
        """Record a metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        stats = {
            "active_timers": list(self.timers.keys()),
            "counters": self.counters.copy(),
            "metrics": {},
            "timestamp": datetime.now().isoformat(),
        }
        
        # Calculate metric statistics
        for name, values in self.metrics.items():
            if values:
                stats["metrics"][name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "total": sum(values)
                }
        
        return stats


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


if __name__ == "__main__":
    # Test utilities
    print("🔧 AI Assistant Enhanced Utilities")
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
    
    # Test time parsing
    print("\n⏰ Time Parsing Test:")
    time_strings = ["5m", "30s", "2h", "1.5h"]
    for ts in time_strings:
        seconds = parse_time_string(ts)
        print(f"   {ts} = {seconds} seconds")
    
    # Test byte formatting
    print("\n💾 Byte Formatting Test:")
    sizes = [1024, 1048576, 1073741824]
    for size in sizes:
        formatted = format_bytes(size)
        print(f"   {size} bytes = {formatted}")
    
    print("\n✅ All enhanced utilities working!")