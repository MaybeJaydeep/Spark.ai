#!/usr/bin/env python3
"""
Microphone Test Utility

Tests microphone access using available methods.
"""

import logging
import sys

def test_pyaudio():
    """Test PyAudio availability"""
    try:
        import pyaudio
        print("✅ PyAudio is available")
        
        # Test audio device access
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✅ Found {device_count} audio devices")
        
        # List input devices
        input_devices = []
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
                print(f"   📱 Input device {i}: {device_info['name']}")
        
        p.terminate()
        return True
        
    except ImportError:
        print("❌ PyAudio not available")
        print("   Install with: pip install pyaudio")
        print("   (Requires C++ build tools and PortAudio)")
        return False
    except Exception as e:
        print(f"❌ PyAudio error: {e}")
        return False


def test_sounddevice():
    """Test sounddevice library"""
    try:
        import sounddevice as sd
        print("✅ sounddevice is available")
        
        # List devices
        devices = sd.query_devices()
        input_count = sum(1 for d in devices if d['max_input_channels'] > 0)
        print(f"✅ Found {input_count} input devices")
        
        return True
        
    except ImportError:
        print("❌ sounddevice not available")
        print("   Install with: pip install sounddevice")
        return False
    except Exception as e:
        print(f"❌ sounddevice error: {e}")
        return False


def test_speech_recognition():
    """Test SpeechRecognition library"""
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition is available")
        
        # Test microphone access
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("✅ Microphone access successful")
                print(f"   Energy threshold: {recognizer.energy_threshold}")
            return True
        except Exception as e:
            print(f"⚠️  Microphone access failed: {e}")
            return False
            
    except ImportError:
        print("❌ SpeechRecognition not available")
        print("   Install with: pip install SpeechRecognition")
        return False


def test_windows_speech():
    """Test Windows Speech API"""
    try:
        import win32com.client
        print("✅ Windows Speech API (pywin32) is available")
        
        try:
            recognizer = win32com.client.Dispatch("SAPI.SpInProcRecoContext")
            print("✅ Windows Speech Recognition initialized")
            return True
        except Exception as e:
            print(f"⚠️  Windows Speech initialization failed: {e}")
            return False
            
    except ImportError:
        print("❌ pywin32 not available")
        print("   Install with: pip install pywin32")
        return False


def test_webrtcvad():
    """Test WebRTC VAD"""
    try:
        import webrtcvad
        print("✅ WebRTC VAD is available")
        
        vad = webrtcvad.Vad(2)
        print("✅ VAD initialized")
        return True
        
    except ImportError:
        print("❌ WebRTC VAD not available")
        print("   Install with: pip install webrtcvad")
        print("   (Requires C++ build tools)")
        return False
    except Exception as e:
        print(f"❌ WebRTC VAD error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🎤 MICROPHONE & AUDIO LIBRARY TEST")
    print("="*60)
    print()
    
    results = {}
    
    print("Testing sounddevice...")
    results['sounddevice'] = test_sounddevice()
    print()
    
    print("Testing PyAudio...")
    results['pyaudio'] = test_pyaudio()
    print()
    
    print("Testing SpeechRecognition...")
    results['speech_recognition'] = test_speech_recognition()
    print()
    
    print("Testing Windows Speech API...")
    results['windows_speech'] = test_windows_speech()
    print()
    
    print("Testing WebRTC VAD...")
    results['webrtcvad'] = test_webrtcvad()
    print()
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    working = [k for k, v in results.items() if v]
    not_working = [k for k, v in results.items() if not v]
    
    if working:
        print(f"✅ Working: {', '.join(working)}")
    
    if not_working:
        print(f"❌ Not working: {', '.join(not_working)}")
    
    print()
    
    if results.get('speech_recognition') or results.get('sounddevice'):
        print("🎉 You can use the text-based assistant!")
        print("   Run: python test_assistant.py")
    
    if results.get('sounddevice') and results.get('speech_recognition'):
        print("🎉 Voice input is available with sounddevice!")
        print("   Test: python speech/stt_sounddevice.py")
    elif results.get('pyaudio') and results.get('webrtcvad'):
        print("🎉 Full voice assistant is available!")
        print("   Run: python main.py")
    elif results.get('speech_recognition'):
        print("⚠️  Voice input available but wake word detection needs pyaudio+webrtcvad")
        print("   You can still use speech recognition without wake words")
    else:
        print("💡 Install missing dependencies to enable voice features")
    
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
