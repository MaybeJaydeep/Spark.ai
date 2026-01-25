#!/usr/bin/env python3
"""
Custom Exceptions for AI Assistant

Defines custom exception classes for better error handling.
"""


class AssistantError(Exception):
    """Base exception class for AI Assistant"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class VoiceRecognitionError(AssistantError):
    """Exception raised when voice recognition fails"""
    
    def __init__(self, message: str = "Voice recognition failed"):
        super().__init__(message, "VOICE_001")


class WakeWordDetectionError(AssistantError):
    """Exception raised when wake word detection fails"""
    
    def __init__(self, message: str = "Wake word detection failed"):
        super().__init__(message, "WAKE_001")


class IntentParsingError(AssistantError):
    """Exception raised when intent parsing fails"""
    
    def __init__(self, message: str = "Intent parsing failed", intent_text: str = None):
        super().__init__(message, "INTENT_001")
        self.intent_text = intent_text


class ActionExecutionError(AssistantError):
    """Exception raised when action execution fails"""
    
    def __init__(self, message: str = "Action execution failed", action_type: str = None):
        super().__init__(message, "ACTION_001")
        self.action_type = action_type


class ApplicationError(AssistantError):
    """Exception raised when application control fails"""
    
    def __init__(self, message: str = "Application control failed", app_name: str = None):
        super().__init__(message, "APP_001")
        self.app_name = app_name


class SystemControlError(AssistantError):
    """Exception raised when system control fails"""
    
    def __init__(self, message: str = "System control failed", operation: str = None):
        super().__init__(message, "SYSTEM_001")
        self.operation = operation


class TimerError(AssistantError):
    """Exception raised when timer operations fail"""
    
    def __init__(self, message: str = "Timer operation failed", timer_name: str = None):
        super().__init__(message, "TIMER_001")
        self.timer_name = timer_name


class TTSError(AssistantError):
    """Exception raised when text-to-speech fails"""
    
    def __init__(self, message: str = "Text-to-speech failed"):
        super().__init__(message, "TTS_001")


class LLMError(AssistantError):
    """Exception raised when LLM operations fail"""
    
    def __init__(self, message: str = "LLM operation failed", model: str = None):
        super().__init__(message, "LLM_001")
        self.model = model


class ConfigurationError(AssistantError):
    """Exception raised when configuration is invalid"""
    
    def __init__(self, message: str = "Configuration error", config_key: str = None):
        super().__init__(message, "CONFIG_001")
        self.config_key = config_key


class AudioDeviceError(AssistantError):
    """Exception raised when audio device operations fail"""
    
    def __init__(self, message: str = "Audio device error", device_name: str = None):
        super().__init__(message, "AUDIO_001")
        self.device_name = device_name


class NetworkError(AssistantError):
    """Exception raised when network operations fail"""
    
    def __init__(self, message: str = "Network error", url: str = None):
        super().__init__(message, "NETWORK_001")
        self.url = url


class APIError(AssistantError):
    """Exception raised when API calls fail"""
    
    def __init__(self, message: str = "API error", api_name: str = None, status_code: int = None):
        super().__init__(message, "API_001")
        self.api_name = api_name
        self.status_code = status_code


class ValidationError(AssistantError):
    """Exception raised when input validation fails"""
    
    def __init__(self, message: str = "Validation error", field_name: str = None):
        super().__init__(message, "VALIDATION_001")
        self.field_name = field_name


class PermissionError(AssistantError):
    """Exception raised when permission is denied"""
    
    def __init__(self, message: str = "Permission denied", resource: str = None):
        super().__init__(message, "PERMISSION_001")
        self.resource = resource


class TimeoutError(AssistantError):
    """Exception raised when operations timeout"""
    
    def __init__(self, message: str = "Operation timed out", timeout_seconds: float = None):
        super().__init__(message, "TIMEOUT_001")
        self.timeout_seconds = timeout_seconds


class UnsupportedPlatformError(AssistantError):
    """Exception raised when platform is not supported"""
    
    def __init__(self, message: str = "Unsupported platform", platform: str = None):
        super().__init__(message, "PLATFORM_001")
        self.platform = platform


# Exception mapping for easy lookup
EXCEPTION_MAP = {
    "VOICE_001": VoiceRecognitionError,
    "WAKE_001": WakeWordDetectionError,
    "INTENT_001": IntentParsingError,
    "ACTION_001": ActionExecutionError,
    "APP_001": ApplicationError,
    "SYSTEM_001": SystemControlError,
    "TIMER_001": TimerError,
    "TTS_001": TTSError,
    "LLM_001": LLMError,
    "CONFIG_001": ConfigurationError,
    "AUDIO_001": AudioDeviceError,
    "NETWORK_001": NetworkError,
    "API_001": APIError,
    "VALIDATION_001": ValidationError,
    "PERMISSION_001": PermissionError,
    "TIMEOUT_001": TimeoutError,
    "PLATFORM_001": UnsupportedPlatformError,
}


def create_exception(error_code: str, message: str = None) -> AssistantError:
    """
    Create exception by error code
    
    Args:
        error_code: Error code (e.g., 'VOICE_001')
        message: Optional custom message
        
    Returns:
        Appropriate exception instance
    """
    exception_class = EXCEPTION_MAP.get(error_code, AssistantError)
    
    if message:
        return exception_class(message)
    else:
        return exception_class()


def handle_exception(func):
    """
    Decorator for consistent exception handling
    
    Usage:
        @handle_exception
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssistantError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert generic exceptions to AssistantError
            raise AssistantError(f"Unexpected error in {func.__name__}: {str(e)}")
    
    return wrapper


if __name__ == "__main__":
    # Test custom exceptions
    print("🚨 Testing Custom Exceptions")
    print("=" * 40)
    
    # Test different exception types
    exceptions_to_test = [
        VoiceRecognitionError("Test voice error"),
        IntentParsingError("Test intent error", "test command"),
        ApplicationError("Test app error", "firefox"),
        LLMError("Test LLM error", "llama3.2"),
        TimeoutError("Test timeout", 5.0),
    ]
    
    for exc in exceptions_to_test:
        print(f"Exception: {type(exc).__name__}")
        print(f"Message: {exc}")
        print(f"Error Code: {exc.error_code}")
        print()
    
    # Test exception creation by code
    print("Creating exception by code:")
    exc = create_exception("VOICE_001", "Custom voice error")
    print(f"Created: {type(exc).__name__} - {exc}")
    
    print("\n✅ Exception system working!")