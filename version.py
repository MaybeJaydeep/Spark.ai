#!/usr/bin/env python3
"""
Version Information for AI Assistant

Contains version constants and utility functions.
"""

__version__ = "2.1.0"
__author__ = "AI Assistant Team"
__description__ = "Advanced AI Voice Assistant with Local LLM Integration"

# Feature flags
FEATURES = {
    "voice_recognition": True,
    "wake_word_detection": True,
    "text_to_speech": True,
    "timer_functionality": True,
    "media_controls": True,
    "local_llm": True,
    "weather_api": True,
    "math_calculator": True,
    "modern_gui": True,
    "startup_installer": True,
}

# Supported platforms
SUPPORTED_PLATFORMS = ["Windows", "Linux", "macOS"]

# Supported intents count
INTENT_COUNT = 20

def get_version_info() -> dict:
    """Get comprehensive version information"""
    import platform
    import sys
    
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "features": FEATURES,
        "supported_platforms": SUPPORTED_PLATFORMS,
        "intent_count": INTENT_COUNT,
    }

def print_version_info():
    """Print formatted version information"""
    info = get_version_info()
    
    print("="*60)
    print("🤖 AI ASSISTANT VERSION INFO")
    print("="*60)
    print(f"Version: {info['version']}")
    print(f"Author: {info['author']}")
    print(f"Description: {info['description']}")
    print()
    print("🖥️  System Information:")
    print(f"   Python: {info['python_version']}")
    print(f"   Platform: {info['platform']} ({info['architecture']})")
    print()
    print("✨ Features:")
    for feature, enabled in info['features'].items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {feature.replace('_', ' ').title()}")
    print()
    print(f"🎯 Supported Intents: {info['intent_count']}+")
    print(f"🌐 Supported Platforms: {', '.join(info['supported_platforms'])}")
    print("="*60)

if __name__ == "__main__":
    print_version_info()