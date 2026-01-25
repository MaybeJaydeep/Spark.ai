#!/usr/bin/env python3
"""
Constants for AI Assistant

Centralized constants and configuration values.
"""

# Application metadata
APP_NAME = "AI Voice Assistant"
APP_VERSION = "2.1.0"
APP_DESCRIPTION = "Advanced AI Voice Assistant with Local LLM Integration"
APP_AUTHOR = "AI Assistant Team"

# Default wake words
DEFAULT_WAKE_WORDS = [
    "hey assistant",
    "spark",
    "computer",
    "wake up",
    "hello assistant"
]

# Audio configuration
AUDIO_CONFIG = {
    "SAMPLE_RATE": 16000,
    "CHUNK_SIZE": 1024,
    "CHANNELS": 1,
    "BUFFER_DURATION": 2.0,
    "CONFIDENCE_THRESHOLD": 0.7,
    "TIMEOUT_SECONDS": 5.0,
}

# Intent confidence thresholds
INTENT_THRESHOLDS = {
    "HIGH_CONFIDENCE": 0.8,
    "MEDIUM_CONFIDENCE": 0.6,
    "LOW_CONFIDENCE": 0.4,
    "MINIMUM_CONFIDENCE": 0.3,
}

# File paths and directories
PATHS = {
    "CONFIG_DIR": "config",
    "LOGS_DIR": "logs",
    "SCREENSHOTS_DIR": "screenshots",
    "TEMP_DIR": "temp",
}

# Supported file extensions
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".flac", ".ogg"]
SUPPORTED_CONFIG_FORMATS = [".json", ".yaml", ".yml"]

# API endpoints and timeouts
API_CONFIG = {
    "OPENWEATHER_BASE_URL": "https://api.openweathermap.org/data/2.5",
    "DEFAULT_TIMEOUT": 10.0,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 1.0,
}

# LLM configuration
LLM_CONFIG = {
    "DEFAULT_BASE_URL": "http://localhost:11434",
    "DEFAULT_MODEL": "llama3.2",
    "DEFAULT_TIMEOUT": 20.0,
    "MAX_TOKENS": 2048,
    "TEMPERATURE": 0.7,
}

# System limits
SYSTEM_LIMITS = {
    "MAX_COMMAND_LENGTH": 500,
    "MAX_RESPONSE_LENGTH": 1000,
    "MAX_TIMER_DURATION": 86400,  # 24 hours in seconds
    "MAX_LOG_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
    "MAX_LOG_FILES": 10,
}

# Error messages
ERROR_MESSAGES = {
    "MICROPHONE_NOT_FOUND": "No microphone detected. Please check your audio setup.",
    "SPEECH_RECOGNITION_FAILED": "Could not understand speech. Please try again.",
    "INTENT_NOT_RECOGNIZED": "I didn't understand that command. Try saying 'help' for options.",
    "APP_NOT_FOUND": "Application not found or could not be launched.",
    "SYSTEM_COMMAND_FAILED": "System command failed to execute.",
    "LLM_CONNECTION_FAILED": "Could not connect to local LLM server.",
    "API_REQUEST_FAILED": "API request failed. Please check your connection.",
}

# Success messages
SUCCESS_MESSAGES = {
    "COMMAND_EXECUTED": "Command executed successfully.",
    "APP_LAUNCHED": "Application launched successfully.",
    "TIMER_SET": "Timer set successfully.",
    "SCREENSHOT_TAKEN": "Screenshot saved successfully.",
    "VOLUME_CHANGED": "Volume adjusted successfully.",
}

# Color codes for console output
COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
}

# Emoji constants for better UX
EMOJIS = {
    "MICROPHONE": "🎤",
    "SPEAKER": "🔊",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "WARNING": "⚠️",
    "INFO": "ℹ️",
    "ROBOT": "🤖",
    "TIMER": "⏰",
    "SCREENSHOT": "📸",
    "VOLUME": "🔊",
    "SEARCH": "🔍",
    "APP": "📱",
    "SYSTEM": "🖥️",
}

# Platform-specific constants
PLATFORM_CONSTANTS = {
    "WINDOWS": {
        "EXECUTABLE_EXTENSION": ".exe",
        "PATH_SEPARATOR": "\\",
        "LINE_ENDING": "\r\n",
    },
    "LINUX": {
        "EXECUTABLE_EXTENSION": "",
        "PATH_SEPARATOR": "/",
        "LINE_ENDING": "\n",
    },
    "DARWIN": {  # macOS
        "EXECUTABLE_EXTENSION": ".app",
        "PATH_SEPARATOR": "/",
        "LINE_ENDING": "\n",
    },
}

# Regular expressions for common patterns
REGEX_PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "URL": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    "TIME": r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\b',
    "NUMBER": r'\b\d+(?:\.\d+)?\b',
    "PHONE": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
}

# Feature flags
FEATURES = {
    "VOICE_RECOGNITION": True,
    "WAKE_WORD_DETECTION": True,
    "TEXT_TO_SPEECH": True,
    "TIMER_FUNCTIONALITY": True,
    "MEDIA_CONTROLS": True,
    "LOCAL_LLM": True,
    "WEATHER_API": True,
    "MATH_CALCULATOR": True,
    "MODERN_GUI": True,
    "STARTUP_INSTALLER": True,
    "ANALYTICS": True,
    "PERFORMANCE_MONITORING": True,
}

def get_platform_constant(platform: str, key: str, default=None):
    """Get platform-specific constant"""
    return PLATFORM_CONSTANTS.get(platform.upper(), {}).get(key, default)

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature.upper(), False)

if __name__ == "__main__":
    print(f"🤖 {APP_NAME} v{APP_VERSION}")
    print(f"📝 {APP_DESCRIPTION}")
    print(f"👨‍💻 By {APP_AUTHOR}")
    print()
    print("🎤 Default wake words:")
    for word in DEFAULT_WAKE_WORDS:
        print(f"   - {word}")
    print()
    print("✨ Enabled features:")
    for feature, enabled in FEATURES.items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {feature.replace('_', ' ').title()}")