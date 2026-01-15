#!/usr/bin/env python3
"""
Voice Input Test

Test voice recognition with sounddevice.
"""

import logging
from speech.stt_sounddevice import SoundDeviceSTT

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("🎤 VOICE INPUT TEST")
    print("="*60)
    print()
    
    # Create STT
    stt = SoundDeviceSTT()
    
    # List devices
    print("📱 Available microphones:")
    devices = stt.list_devices()
    for device in devices[:5]:  # Show first 5
        print(f"   {device['index']}: {device['name']}")
    print()
    
    # Adjust for noise
    print("🔇 Adjusting for ambient noise (stay quiet)...")
    stt.adjust_for_ambient_noise(1.0)
    print()
    
    # Test recognition
    print("🎤 Speak a command (5 seconds)...")
    print("   Try: 'open firefox' or 'search for cats'")
    print()
    
    result = stt.listen_once(duration=5.0)
    
    print()
    if result and result.success:
        print(f"✅ Recognized: '{result.text}'")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Duration: {result.duration:.2f}s")
        print()
        
        # Parse intent
        from nlp.intent_parser import IntentParser
        parser = IntentParser()
        intent = parser.parse(result.text)
        
        print(f"🎯 Intent: {intent.type.value}")
        print(f"   Confidence: {intent.confidence:.2f}")
        
        if intent.entities:
            print(f"📦 Entities:")
            for entity in intent.entities:
                print(f"   - {entity.type}: '{entity.value}'")
    else:
        print(f"❌ Recognition failed")
        if result:
            print(f"   Error: {result.error}")
    
    print()
    print("="*60)


if __name__ == "__main__":
    main()
