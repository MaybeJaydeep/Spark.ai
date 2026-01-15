#!/usr/bin/env python3
"""
Quick Voice Test - Single command test
"""

import logging
from speech.stt_sounddevice import SoundDeviceSTT
from nlp.intent_parser import IntentParser
from toc.dispatcher import CommandDispatcher

logging.basicConfig(level=logging.WARNING)

print("="*60)
print("🎤 QUICK VOICE TEST")
print("="*60)
print()

# Initialize
print("Initializing...")
stt = SoundDeviceSTT()
parser = IntentParser()
dispatcher = CommandDispatcher()

# Adjust for noise
print("Adjusting for ambient noise (stay quiet)...")
stt.adjust_for_ambient_noise(1.0)

print()
print("🎤 Speak a command now (5 seconds)...")
print("   Try: 'open firefox' or 'what time is it'")
print()

# Listen
result = stt.listen_once(duration=5.0)

print()
if result and result.success:
    print(f"✅ Heard: '{result.text}'")
    print()
    
    # Parse
    intent = parser.parse(result.text)
    print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
    
    if intent.entities:
        for entity in intent.entities:
            print(f"   - {entity.type}: '{entity.value}'")
    
    print()
    
    # Execute
    print("🚀 Executing...")
    exec_result = dispatcher.dispatch(intent)
    
    if exec_result['success']:
        print(f"✅ {exec_result['message']}")
    else:
        print(f"❌ {exec_result['message']}")
else:
    print("❌ Could not recognize speech")
    if result:
        print(f"   Error: {result.error}")

print()
print("="*60)
