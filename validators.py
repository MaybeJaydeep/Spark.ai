#!/usr/bin/env python3
"""
Input Validation Module for AI Assistant

Provides validation functions for user inputs and system parameters.
"""

import re
import os
import platform
from typing import Any, List, Dict, Optional, Tuple
from pathlib import Path


def validate_wake_words(wake_words: List[str]) -> Tuple[bool, str]:
    """
    Validate wake words list
    
    Args:
        wake_words: List of wake words to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(wake_words, list):
        return False, "Wake words must be a list"
    
    if not wake_words:
        return False, "At least one wake word is required"
    
    if len(wake_words) > 10:
        return False, "Maximum 10 wake words allowed"
    
    for word in wake_words:
        if not isinstance(word, str):
            return False, "All wake words must be strings"
        
        if len(word.strip()) < 2:
            return False, "Wake words must be at least 2 characters long"
        
        if len(word.strip()) > 50:
            return False, "Wake words must be less than 50 characters"
        
        # Check for valid characters (letters, spaces, hyphens)
        if not re.match(r'^[a-zA-Z\s\-]+$', word.strip()):
            return False, f"Invalid characters in wake word: '{word}'"
    
    return True, ""


def validate_audio_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate audio configuration
    
    Args:
        config: Audio configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ['sample_rate', 'chunk_size', 'channels']
    
    for key in required_keys:
        if key not in config:
            return False, f"Missing required audio config key: {key}"
    
    # Validate sample rate
    sample_rate = config['sample_rate']
    if not isinstance(sample_rate, int) or sample_rate < 8000 or sample_rate > 48000:
        return False, "Sample rate must be between 8000 and 48000 Hz"
    
    # Validate chunk size
    chunk_size = config['chunk_size']
    if not isinstance(chunk_size, int) or chunk_size < 256 or chunk_size > 8192:
        return False, "Chunk size must be between 256 and 8192"
    
    # Validate channels
    channels = config['channels']
    if not isinstance(channels, int) or channels < 1 or channels > 2:
        return False, "Channels must be 1 (mono) or 2 (stereo)"
    
    # Validate confidence threshold if present
    if 'confidence_threshold' in config:
        threshold = config['confidence_threshold']
        if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
            return False, "Confidence threshold must be between 0.0 and 1.0"
    
    return True, ""


def validate_timer_duration(duration: str, unit: str) -> Tuple[bool, str, int]:
    """
    Validate timer duration and convert to seconds
    
    Args:
        duration: Duration as string
        unit: Time unit (seconds, minutes, hours)
        
    Returns:
        Tuple of (is_valid, error_message, duration_in_seconds)
    """
    try:
        duration_num = int(duration)
    except ValueError:
        return False, "Duration must be a number", 0
    
    if duration_num <= 0:
        return False, "Duration must be positive", 0
    
    unit_lower = unit.lower()
    
    if 'second' in unit_lower:
        seconds = duration_num
        max_seconds = 3600  # 1 hour max for seconds
    elif 'minute' in unit_lower:
        seconds = duration_num * 60
        max_seconds = 86400  # 24 hours max for minutes
    elif 'hour' in unit_lower:
        seconds = duration_num * 3600
        max_seconds = 604800  # 7 days max for hours
    else:
        return False, f"Invalid time unit: {unit}", 0
    
    if seconds > max_seconds:
        return False, f"Duration too long for {unit_lower}", 0
    
    return True, "", seconds


def validate_app_name(app_name: str) -> Tuple[bool, str]:
    """
    Validate application name
    
    Args:
        app_name: Application name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(app_name, str):
        return False, "App name must be a string"
    
    app_name = app_name.strip()
    
    if not app_name:
        return False, "App name cannot be empty"
    
    if len(app_name) > 100:
        return False, "App name too long (max 100 characters)"
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', '|', '&', ';', '`', '$']
    if any(char in app_name for char in dangerous_chars):
        return False, "App name contains invalid characters"
    
    return True, ""


def validate_file_path(file_path: str, must_exist: bool = False) -> Tuple[bool, str]:
    """
    Validate file path
    
    Args:
        file_path: File path to validate
        must_exist: Whether file must exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(file_path, str):
        return False, "File path must be a string"
    
    if not file_path.strip():
        return False, "File path cannot be empty"
    
    try:
        path = Path(file_path)
        
        # Check for invalid characters
        if platform.system() == "Windows":
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in str(path) for char in invalid_chars):
                return False, "File path contains invalid characters"
        
        # Check if file exists (if required)
        if must_exist and not path.exists():
            return False, f"File does not exist: {file_path}"
        
        # Check if parent directory is writable (for new files)
        if not must_exist:
            parent = path.parent
            if parent.exists() and not os.access(parent, os.W_OK):
                return False, f"Directory not writable: {parent}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(url, str):
        return False, "URL must be a string"
    
    url = url.strip()
    
    if not url:
        return False, "URL cannot be empty"
    
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Invalid URL format"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(email, str):
        return False, "Email must be a string"
    
    email = email.strip()
    
    if not email:
        return False, "Email cannot be empty"
    
    # Email pattern
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if not email_pattern.match(email):
        return False, "Invalid email format"
    
    return True, ""


def validate_math_expression(expression: str) -> Tuple[bool, str]:
    """
    Validate mathematical expression for safety
    
    Args:
        expression: Math expression to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(expression, str):
        return False, "Expression must be a string"
    
    expression = expression.strip()
    
    if not expression:
        return False, "Expression cannot be empty"
    
    if len(expression) > 200:
        return False, "Expression too long (max 200 characters)"
    
    # Check for dangerous patterns
    dangerous_patterns = [
        r'__',  # Double underscore (Python internals)
        r'import',  # Import statements
        r'exec',  # Code execution
        r'eval',  # Code evaluation
        r'open',  # File operations
        r'file',  # File operations
        r'input',  # User input
        r'raw_input',  # User input (Python 2)
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            return False, f"Expression contains forbidden pattern: {pattern}"
    
    # Allow only safe characters
    safe_pattern = re.compile(r'^[0-9+\-*/().\s]+$')
    if not safe_pattern.match(expression):
        return False, "Expression contains invalid characters"
    
    return True, ""


def validate_volume_level(level: Any) -> Tuple[bool, str, int]:
    """
    Validate volume level
    
    Args:
        level: Volume level to validate
        
    Returns:
        Tuple of (is_valid, error_message, normalized_level)
    """
    try:
        level_int = int(level)
    except (ValueError, TypeError):
        return False, "Volume level must be a number", 0
    
    if level_int < 0 or level_int > 100:
        return False, "Volume level must be between 0 and 100", 0
    
    return True, "", level_int


def validate_config_dict(config: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, str]:
    """
    Validate configuration dictionary
    
    Args:
        config: Configuration dictionary to validate
        required_keys: List of required keys
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary"
    
    # Check required keys
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    # Check for empty values in required keys
    empty_keys = [key for key in required_keys if not config[key]]
    if empty_keys:
        return False, f"Empty values for required keys: {', '.join(empty_keys)}"
    
    return True, ""


if __name__ == "__main__":
    # Test validators
    print("🔍 Testing Input Validators")
    print("=" * 40)
    
    # Test wake words validation
    print("\n🎤 Wake Words Validation:")
    valid_words = ["hey assistant", "computer"]
    invalid_words = ["", "a", "x" * 60]
    
    is_valid, msg = validate_wake_words(valid_words)
    print(f"Valid words: {is_valid} - {msg}")
    
    is_valid, msg = validate_wake_words(invalid_words)
    print(f"Invalid words: {is_valid} - {msg}")
    
    # Test timer validation
    print("\n⏰ Timer Validation:")
    is_valid, msg, seconds = validate_timer_duration("5", "minutes")
    print(f"5 minutes: {is_valid} - {seconds} seconds - {msg}")
    
    # Test URL validation
    print("\n🌐 URL Validation:")
    is_valid, msg = validate_url("https://example.com")
    print(f"Valid URL: {is_valid} - {msg}")
    
    is_valid, msg = validate_url("not-a-url")
    print(f"Invalid URL: {is_valid} - {msg}")
    
    print("\n✅ Validation system working!")