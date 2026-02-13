#!/usr/bin/env python3
"""
Hands-Free Voice Assistant

Complete voice assistant with wake word detection.
No button press needed - just say the wake word!
"""

import logging
import sys
import time
from typing import Optional

from wake_word.detector_sounddevice import SoundDeviceWakeWord, WakeWordEvent
from speech.stt_sounddevice import SoundDeviceSTT
from speech.tts import get_tts
from nlp.intent_parser import IntentParser
from toc.dispatcher import CommandDispatcher


class HandsFreeAssistant:
    """
    Hands-Free Voice Assistant
    
    Always listening for wake words, then processes voice commands.
    """
    
    def __init__(self, wake_words: list = None, enable_tts: bool = True):
        self.wake_word_detector: Optional[SoundDeviceWakeWord] = None
        self.stt: Optional[SoundDeviceSTT] = None
        self.parser: Optional[IntentParser] = None
        self.dispatcher: Optional[CommandDispatcher] = None
        self.tts = get_tts() if enable_tts else None
        self.enable_tts = enable_tts
        self.is_running = False
        self.wake_words = wake_words or ["hey spark", "spark"]
        self.activation_count = 0  # Track wake word activations
        self.session_start_time = time.time()  # Track session duration
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            self.logger.info("Initializing Hands-Free Assistant...")
            
            # Initialize wake word detector
            self.logger.info("Initializing wake word detection...")
            self.wake_word_detector = SoundDeviceWakeWord(
                wake_words=self.wake_words,
                chunk_duration=2.0,
                confidence_threshold=0.6
            )
            self.wake_word_detector.add_listener(self.on_wake_word_detected)
            
            # Initialize STT
            self.logger.info("Initializing speech recognition...")
            self.stt = SoundDeviceSTT()
            
            # Initialize intent parser
            self.logger.info("Initializing intent parser...")
            self.parser = IntentParser()
            
            # Initialize command dispatcher
            self.logger.info("Initializing command dispatcher...")
            self.dispatcher = CommandDispatcher()
            
            self.logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def on_wake_word_detected(self, event: WakeWordEvent) -> None:
        """Handle wake word detection"""
        print(f"\n🎤 Wake word detected: '{event.wake_word}'")
        
        if self.enable_tts:
            self.tts.speak("Yes?")
        
        print("🔊 Listening for your command...")
        
        try:
            # Listen for command
            result = self.stt.listen_once(duration=5.0)
            
            if not result or not result.success:
                print("❌ Could not understand command")
                if self.enable_tts:
                    self.tts.speak("Sorry, I didn't catch that")
                print("💡 Waiting for wake word...\n")
                return
            
            # Display recognized text
            print(f"📝 You said: '{result.text}'")
            
            # Parse intent
            intent = self.parser.parse(result.text)
            print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            if intent.entities:
                print(f"📦 Entities:")
                for entity in intent.entities:
                    print(f"   - {entity.type}: '{entity.value}'")
            
            # Execute command
            print(f"🚀 Executing...")
            exec_result = self.dispatcher.dispatch(intent)
            
            if exec_result['success']:
                print(f"✅ {exec_result['message']}")
                if self.enable_tts:
                    self.tts.speak(exec_result['message'])
            else:
                print(f"❌ {exec_result['message']}")
                if self.enable_tts:
                    self.tts.speak(exec_result['message'])
            
            print("\n💡 Waiting for wake word...\n")
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            print(f"❌ Error: {e}")
            if self.enable_tts:
                self.tts.speak("Sorry, an error occurred")
            print("💡 Waiting for wake word...\n")
    
    def run(self):
        """Run the hands-free assistant"""
        self.is_running = True
        
        print("\n" + "="*60)
        print("🤖 HANDS-FREE VOICE ASSISTANT")
        print("="*60)
        print(f"\n🎤 Wake words: {', '.join(self.wake_words)}")
        print("\n💡 Instructions:")
        print("   1. Say a wake word to activate")
        print("   2. Speak your command")
        print("   3. Wait for execution")
        print("   4. Repeat!")
        print("\n📋 Example:")
        print("   You: 'Hey assistant'")
        print("   Assistant: 'Listening...'")
        print("   You: 'Open firefox'")
        print("   Assistant: 'Opening firefox...'")
        print("\n⚠️  Press Ctrl+C to stop")
        print("\n" + "-"*60)
        print("💡 Waiting for wake word...")
        print()
        
        # Start wake word detection
        if not self.wake_word_detector.start():
            print("❌ Failed to start wake word detection")
            return
        
        try:
            # Keep running
            while self.is_running:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopping...")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the assistant"""
        self.is_running = False
        
        if self.wake_word_detector:
            self.wake_word_detector.stop()
        
        # Calculate session duration
        session_duration = time.time() - self.session_start_time
        
        print(f"\n📊 Session Summary:")
        print(f"   Duration: {session_duration/60:.1f} minutes")
        print(f"   Wake word activations: {self.activation_count}")
        if self.activation_count > 0:
            avg_time = session_duration / self.activation_count / 60
            print(f"   Average time between activations: {avg_time:.1f} minutes")
        
        print("\n👋 Goodbye!")
        self.logger.info("Hands-free assistant shutdown")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hands-Free Voice Assistant')
    parser.add_argument(
        '--wake-words',
        nargs='+',
        default=["hey assistant", "computer"],
        help='Wake words to detect (default: "hey assistant" "computer")'
    )
    parser.add_argument(
        '--no-tts',
        action='store_true',
        help='Disable text-to-speech responses'
    )
    
    args = parser.parse_args()
    
    # Create assistant
    assistant = HandsFreeAssistant(
        wake_words=args.wake_words,
        enable_tts=not args.no_tts
    )
    
    # Initialize
    if not assistant.initialize():
        print("\n❌ Failed to initialize assistant")
        sys.exit(1)
    
    # Run
    try:
        assistant.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
