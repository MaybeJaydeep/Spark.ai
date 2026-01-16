#!/usr/bin/env python3
"""
Complete Voice Assistant Application

Integrated voice assistant with speech recognition, intent parsing,
and action execution.
"""

import logging
import sys
import time
from typing import Optional

from speech.stt_sounddevice import SoundDeviceSTT
from speech.tts import get_tts
from nlp.intent_parser import IntentParser
from toc.dispatcher import CommandDispatcher


class VoiceAssistant:
    """
    Complete Voice Assistant
    
    Integrates speech recognition, intent parsing, and action execution
    into a unified voice-controlled assistant.
    """
    
    def __init__(self, enable_tts: bool = False):
        self.stt: Optional[SoundDeviceSTT] = None
        self.parser: Optional[IntentParser] = None
        self.dispatcher: Optional[CommandDispatcher] = None
        self.tts = get_tts() if enable_tts else None
        self.enable_tts = enable_tts
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            self.logger.info("Initializing Voice Assistant...")
            
            # Initialize STT
            self.logger.info("Initializing speech recognition...")
            self.stt = SoundDeviceSTT()
            
            # List available devices
            devices = self.stt.list_devices()
            if not devices:
                self.logger.error("No microphone devices found")
                return False
            
            self.logger.info(f"Found {len(devices)} input devices")
            
            # Adjust for ambient noise
            self.logger.info("Adjusting for ambient noise...")
            self.stt.adjust_for_ambient_noise(1.0)
            
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
    
    def listen_and_execute(self, duration: float = 5.0) -> bool:
        """
        Listen for a voice command and execute it
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            True if command was executed successfully
        """
        try:
            # Listen for speech
            print("\n🎤 Listening... (speak your command)")
            result = self.stt.listen_once(duration=duration)
            
            if not result or not result.success:
                print(f"❌ Could not recognize speech")
                if result and result.error:
                    print(f"   Error: {result.error}")
                return False
            
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
            dispatch_result = self.dispatcher.dispatch(intent)
            
            if dispatch_result['success']:
                print(f"✅ {dispatch_result['message']}")
                if self.enable_tts:
                    self.tts.speak(dispatch_result['message'])
            else:
                print(f"❌ {dispatch_result['message']}")
                if self.enable_tts:
                    self.tts.speak(dispatch_result['message'])
            
            return dispatch_result['success']
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def run_interactive(self):
        """Run in interactive mode"""
        self.is_running = True
        
        print("\n" + "="*60)
        print("🤖 VOICE ASSISTANT - INTERACTIVE MODE")
        print("="*60)
        print("\n💡 Instructions:")
        print("   • Press ENTER to start listening")
        print("   • Speak your command clearly")
        print("   • Type 'quit' or 'exit' to stop")
        print("\n📋 Example commands:")
        print("   • 'open firefox'")
        print("   • 'search for python tutorials'")
        print("   • 'what time is it'")
        print("   • 'volume up'")
        print("   • 'take a screenshot'")
        print("\n" + "-"*60)
        
        command_count = 0
        success_count = 0
        
        try:
            while self.is_running:
                # Wait for user to press enter
                user_input = input("\n🎤 Press ENTER to speak (or type 'quit'): ").strip().lower()
                
                if user_input in ['quit', 'exit', 'q']:
                    break
                
                # Listen and execute
                command_count += 1
                if self.listen_and_execute(duration=5.0):
                    success_count += 1
                
                print("-"*60)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        
        finally:
            print("\n" + "="*60)
            print("📊 SESSION SUMMARY")
            print("="*60)
            print(f"   Commands processed: {command_count}")
            print(f"   Successful: {success_count}")
            if command_count > 0:
                print(f"   Success rate: {success_count/command_count*100:.1f}%")
            print("\n👋 Goodbye!")
    
    def run_continuous(self, interval: float = 2.0):
        """
        Run in continuous mode (always listening)
        
        Args:
            interval: Pause between listening cycles
        """
        self.is_running = True
        
        print("\n" + "="*60)
        print("🤖 VOICE ASSISTANT - CONTINUOUS MODE")
        print("="*60)
        print("\n⚠️  Assistant is always listening!")
        print("   Speak commands naturally")
        print("   Press Ctrl+C to stop")
        print("\n" + "-"*60)
        
        try:
            while self.is_running:
                self.listen_and_execute(duration=5.0)
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        
        finally:
            print("\n👋 Goodbye!")
    
    def shutdown(self):
        """Shutdown the assistant"""
        self.is_running = False
        self.logger.info("Voice Assistant shutdown")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Voice Assistant')
    parser.add_argument(
        '--mode',
        choices=['interactive', 'continuous'],
        default='interactive',
        help='Operating mode (default: interactive)'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=5.0,
        help='Recording duration in seconds (default: 5.0)'
    )
    parser.add_argument(
        '--tts',
        action='store_true',
        help='Enable text-to-speech responses'
    )
    
    args = parser.parse_args()
    
    # Create assistant
    assistant = VoiceAssistant(enable_tts=args.tts)
    
    # Initialize
    if not assistant.initialize():
        print("\n❌ Failed to initialize assistant")
        print("💡 Run 'python test_microphone.py' to check your setup")
        sys.exit(1)
    
    # Run in selected mode
    try:
        if args.mode == 'interactive':
            assistant.run_interactive()
        else:
            assistant.run_continuous(interval=2.0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        assistant.shutdown()


if __name__ == "__main__":
    main()
