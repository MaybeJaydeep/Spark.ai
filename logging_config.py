#!/usr/bin/env python3
"""
Logging Configuration for AI Assistant

Centralized logging setup with file rotation and formatting.
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "assistant.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        log_file: Log file name
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
        
    Returns:
        Configured root logger
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Simpler format for console
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Log startup message
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log level: {level}")
    root_logger.info(f"Log file: {log_path / log_file}")
    
    return root_logger


def get_session_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific session/component
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_system_info():
    """Log system information for debugging"""
    import platform
    
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("AI ASSISTANT SESSION START")
    logger.info("=" * 50)
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Hostname: {platform.node()}")
    logger.info(f"Session time: {datetime.now().isoformat()}")
    logger.info("=" * 50)


def log_performance_metrics(metrics: dict):
    """
    Log performance metrics
    
    Args:
        metrics: Dictionary of performance metrics
    """
    logger = logging.getLogger("performance")
    
    logger.info("Performance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            logger.info(f"  {key}: {value:.4f}")
        else:
            logger.info(f"  {key}: {value}")


class PerformanceLogger:
    """Context manager for performance logging"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.logger = logging.getLogger("performance")
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} ({duration:.4f}s)")
        else:
            self.logger.error(f"Failed: {self.operation_name} ({duration:.4f}s) - {exc_val}")


def setup_component_loggers():
    """Setup specific loggers for different components"""
    
    # Voice recognition logger
    voice_logger = logging.getLogger("voice")
    voice_logger.setLevel(logging.INFO)
    
    # Intent parser logger
    intent_logger = logging.getLogger("intent")
    intent_logger.setLevel(logging.INFO)
    
    # Action execution logger
    action_logger = logging.getLogger("actions")
    action_logger.setLevel(logging.INFO)
    
    # LLM logger
    llm_logger = logging.getLogger("llm")
    llm_logger.setLevel(logging.INFO)
    
    # Performance logger
    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    # Test logging setup
    print("🔧 Testing Logging Configuration")
    print("=" * 40)
    
    # Setup logging
    logger = setup_logging(level="DEBUG", console_output=True)
    
    # Setup component loggers
    setup_component_loggers()
    
    # Log system info
    log_system_info()
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test component loggers
    voice_logger = logging.getLogger("voice")
    voice_logger.info("Voice recognition test")
    
    intent_logger = logging.getLogger("intent")
    intent_logger.info("Intent parsing test")
    
    # Test performance logging
    with PerformanceLogger("test_operation"):
        import time
        time.sleep(0.1)
    
    print("\n✅ Logging system test complete!")
    print("📁 Check logs/ directory for log files")