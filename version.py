#!/usr/bin/env python3
"""
Version Information for AI Assistant

Contains version constants and utility functions.
"""

import os
import sys
import platform
from datetime import datetime
from typing import Dict, Any

__version__ = "2.1.1"  # Incremented version
__author__ = "AI Assistant Team"
__description__ = "Advanced AI Voice Assistant with Local LLM Integration"
__build_date__ = "2026-01-24"  # Added build date

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
    "exception_handling": True,  # New feature
    "configuration_management": True,  # New feature
    "advanced_logging": True,  # New feature
}

# Supported platforms
SUPPORTED_PLATFORMS = ["Windows", "Linux", "macOS"]

# Supported intents count
INTENT_COUNT = 20

# Dependencies
DEPENDENCIES = {
    "sounddevice": ">=0.4.6",
    "soundfile": ">=0.12.1",
    "SpeechRecognition": ">=3.10.0",
    "requests": ">=2.32.0",
    "numpy": ">=1.24.0",
    "customtkinter": ">=5.2.2",
}

def get_version_info() -> Dict[str, Any]:
    """Get comprehensive version information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "build_date": __build_date__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_version": platform.version(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "features": FEATURES,
        "supported_platforms": SUPPORTED_PLATFORMS,
        "intent_count": INTENT_COUNT,
        "dependencies": DEPENDENCIES,
        "timestamp": datetime.now().isoformat(),
    }

def get_system_requirements() -> Dict[str, str]:
    """Get system requirements information"""
    return {
        "python_minimum": "3.8+",
        "python_recommended": "3.11+",
        "memory_minimum": "512MB",
        "memory_recommended": "2GB",
        "disk_space": "100MB",
        "audio_device": "Microphone required for voice input",
        "network": "Internet connection for speech recognition and weather",
    }

def check_compatibility() -> Dict[str, bool]:
    """Check system compatibility"""
    checks = {}
    
    # Python version check
    py_version = sys.version_info
    checks["python_version"] = py_version >= (3, 8)
    
    # Platform check
    checks["supported_platform"] = platform.system() in SUPPORTED_PLATFORMS
    
    # Architecture check
    checks["64bit_architecture"] = platform.machine().endswith('64')
    
    # Memory check (basic)
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        checks["sufficient_memory"] = memory_gb >= 0.5
    except ImportError:
        checks["sufficient_memory"] = True  # Assume OK if can't check
    
    return checks

def print_version_info():
    """Print formatted version information"""
    info = get_version_info()
    
    print("="*60)
    print("🤖 AI ASSISTANT VERSION INFO")
    print("="*60)
    print(f"Version: {info['version']}")
    print(f"Build Date: {info['build_date']}")
    print(f"Author: {info['author']}")
    print(f"Description: {info['description']}")
    print()
    print("🖥️  System Information:")
    print(f"   Python: {info['python_version']}")
    print(f"   Platform: {info['platform']} {info['platform_release']}")
    print(f"   Architecture: {info['architecture']}")
    print(f"   Processor: {info['processor']}")
    print(f"   Hostname: {info['hostname']}")
    print()
    print("✨ Features:")
    for feature, enabled in info['features'].items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {feature.replace('_', ' ').title()}")
    print()
    print(f"🎯 Supported Intents: {info['intent_count']}+")
    print(f"🌐 Supported Platforms: {', '.join(info['supported_platforms'])}")
    print()
    print("📦 Dependencies:")
    for dep, version in info['dependencies'].items():
        print(f"   - {dep} {version}")
    print("="*60)

def print_system_requirements():
    """Print system requirements"""
    reqs = get_system_requirements()
    
    print("\n📋 SYSTEM REQUIREMENTS")
    print("="*40)
    for req, value in reqs.items():
        print(f"   {req.replace('_', ' ').title()}: {value}")

def print_compatibility_check():
    """Print compatibility check results"""
    checks = check_compatibility()
    
    print("\n🔍 COMPATIBILITY CHECK")
    print("="*40)
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check.replace('_', ' ').title()}")
    
    all_passed = all(checks.values())
    print(f"\nOverall: {'✅ Compatible' if all_passed else '❌ Issues detected'}")

if __name__ == "__main__":
    print_version_info()
    print_system_requirements()
    print_compatibility_check()