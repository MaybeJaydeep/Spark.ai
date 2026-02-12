#!/usr/bin/env python3
"""
AI Assistant - Main Entry Point

This is the main entry point for the AI assistant application.
Currently demonstrates wake word detection functionality.
"""

import logging
import time
import signal
import sys
from typing import Optional

from wake_word.detector_sounddevice import SoundDeviceWakeWord, WakeWordEvent
from speech.stt_sounddevice import SoundDeviceSTT, SOUNDDEVICE_AVAILABLE
from nlp.intent_parser import IntentParser, Intent
from toc.dispatcher import CommandDispatcher


class AIAssistant:
    """Main AI Assistant application"""
    
    def __init__(self, use_gui: bool = False, use_wake_word: bool = False):
        self.wake_word_detector: Optional[SoundDeviceWakeWord] = None
        self.stt: Optional[SoundDeviceSTT] = None
        self.intent_parser: Optional[IntentParser] = None
        self.dispatcher: Optional[CommandDispatcher] = None
        self.use_gui = use_gui
        self.use_wake_word = use_wake_word
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def on_wake_word_detected(self, event: WakeWordEvent) -> None:
        """Handle wake word detection events"""
        self.logger.info(
            f"🎤 Wake word detected: '{event.wake_word}' "
            f"(confidence: {event.confidence:.2f}) at {event.timestamp}"
        )
        
        if self.ui:
            self.ui.log_wake_word(event.wake_word, event.confidence)
            self.ui.set_state("Listening for command")
        else:
            print(f"\n✨ Assistant activated by '{event.wake_word}'!")
            print("🔊 Listening for your command...")
        
        # Use STT to capture the command
        if self.stt:
            result = self.stt.listen_once(duration=5.0)
        else:
            if not self.ui:
                print("(STT not initialized)\n")
            return
        
        if result and result.success:
            if self.ui:
                self.ui.log_command(result.text)
                self.ui.set_state("Processing command")
            else:
                print(f"📝 You said: '{result.text}'")
            
            # Parse intent
            if self.intent_parser:
                intent = self.intent_parser.parse(result.text)
                
                if self.ui:
                    self.ui.log_intent(intent.type.value, intent.confidence)
                else:
                    print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
                
                if intent.entities:
                    if not self.ui:
                        print(f"📦 Entities:")
                        for entity in intent.entities:
                            print(f"   - {entity.type}: '{entity.value}'")
                
                # Execute action using dispatcher
                if self.dispatcher:
                    result = self.dispatcher.dispatch(intent)
                    if self.ui:
                        self.ui.log_action(result['message'], result['success'])
                        self.ui.set_state("Listening")
                    else:
                        icon = '✅' if result['success'] else '❌'
                        print(f"{icon} {result['message']}")
                else:
                    self.execute_intent(intent)
            else:
                if not self.ui:
                    print("(Intent parser not initialized)")
        else:
            if self.ui:
                self.ui.log_error("Could not understand the command")
                self.ui.set_state("Listening")
            else:
                print("❌ Could not understand the command")
    
    def initialize_wake_word_detection(self) -> bool:
        """Initialize wake word detection system"""
        try:
            self.logger.info("Initializing wake word detection...")
            
            # Create wake word detector
            self.wake_word_detector = SoundDeviceWakeWord(
                wake_words=["hey assistant", "computer", "wake up"],
                chunk_duration=2.0
            )
            
            # Register our callback
            self.wake_word_detector.add_listener(self.on_wake_word_detected)
            
            # Start detection
            if self.wake_word_detector.start():
                self.logger.info("✅ Wake word detection started successfully")
                return True
            else:
                self.logger.error("❌ Failed to start wake word detection")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing wake word detection: {e}")
            return False
    
    def initialize_speech_to_text(self) -> bool:
        """Initialize speech-to-text system"""
        try:
            self.logger.info("Initializing speech-to-text...")
            
            # Use sounddevice STT
            self.stt = SoundDeviceSTT()
            
            # Adjust for ambient noise
            self.logger.info("Adjusting for ambient noise...")
            self.stt.adjust_for_ambient_noise(duration=1.0)
            
            self.logger.info("✅ Speech-to-text initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing speech-to-text: {e}")
            return False
    
    def initialize_intent_parser(self) -> bool:
        """Initialize intent parser"""
        try:
            self.logger.info("Initializing intent parser...")
            
            self.intent_parser = IntentParser()
            
            self.logger.info("✅ Intent parser initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing intent parser: {e}")
            return False
    
    def initialize_dispatcher(self) -> bool:
        """Initialize command dispatcher"""
        try:
            self.logger.info("Initializing command dispatcher...")
            
            self.dispatcher = CommandDispatcher()
            
            self.logger.info("✅ Command dispatcher initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing dispatcher: {e}")
            return False
    
    def execute_intent(self, intent: Intent) -> None:
        """Execute action based on parsed intent"""
        print(f"\n🚀 Executing: {intent.type.value}")
        
        # Execute the intent using the dispatcher
        if self.dispatcher:
            result = self.dispatcher.dispatch(intent)
            if result.get('success'):
                print(f"   ✅ {result.get('message', 'Success')}")
            else:
                print(f"   ❌ {result.get('message', 'Failed')}")
        else:
            print("   ❌ Dispatcher not initialized")
        print("-" * 60)
    
    def run(self) -> None:
        """Main application loop"""
        self.logger.info("🚀 Starting AI Assistant...")
        
        # Initialize UI if requested
        if self.use_gui:
            self.ui = AssistantUI()
            self.ui.set_start_callback(self._start_assistant)
            self.ui.set_stop_callback(self.shutdown)
            self.ui.run()
        else:
            self._start_assistant()
    
    def _start_assistant(self):
        """Start the assistant components"""
        # Initialize dispatcher
        if not self.initialize_dispatcher():
            self.logger.warning("⚠️  Dispatcher initialization failed, continuing without it")
        
        # Initialize intent parser
        if not self.initialize_intent_parser():
            self.logger.warning("⚠️  Intent parser initialization failed, continuing without it")
        
        # Initialize speech-to-text
        if not self.initialize_speech_to_text():
            self.logger.warning("⚠️  STT initialization failed, continuing without it")
        
        # Initialize wake word detection
        if not self.initialize_wake_word_detection():
            self.logger.error("Failed to initialize wake word detection. Exiting.")
            return
        
        self.is_running = True
        
        # Update UI if present
        if self.ui:
            self.ui.set_wake_word_active(True)
            self.ui.set_stt_active(True)
            self.ui.set_state("Listening")
            return  # UI will handle the main loop
        
        # Display status and instructions
        self._display_startup_info()
        
        try:
            # Main loop
            while self.is_running:
                # Display periodic status
                if hasattr(self, '_last_status_time'):
                    if time.time() - self._last_status_time > 30:  # Every 30 seconds
                        self._display_status()
                else:
                    self._last_status_time = time.time()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()
    
    def _display_startup_info(self) -> None:
        """Display startup information and instructions"""
        print("\n" + "="*60)
        print("🤖 AI ASSISTANT - WAKE WORD DETECTION DEMO")
        print("="*60)
        
        if self.wake_word_detector:
            config = self.wake_word_detector.config
            print(f"📋 Configured wake words: {', '.join(config.wake_words)}")
            print(f"🎯 Confidence threshold: {config.confidence_threshold}")
            print(f"🔊 Sample rate: {config.sample_rate} Hz")
        
        print("\n💡 Instructions:")
        print("   • Speak one of the wake words to activate the assistant")
        print("   • The system is continuously listening")
        print("   • Press Ctrl+C to exit")
        print("\n🎤 Listening for wake words...")
        print("-" * 60)
    
    def _display_status(self) -> None:
        """Display current system status"""
        if self.wake_word_detector:
            status = self.wake_word_detector.get_status()
            self.logger.info(f"Status: {status['state']} | Listeners: {status['listeners_count']}")
            self._last_status_time = time.time()
    
    def shutdown(self) -> None:
        """Graceful shutdown of all components"""
        self.logger.info("🛑 Shutting down AI Assistant...")
        self.is_running = False
        
        # Stop wake word detection
        if self.wake_word_detector:
            self.wake_word_detector.stop()
            self.logger.info("✅ Wake word detection stopped")
        
        # Stop STT if in continuous mode
        if self.stt and self.stt.is_listening:
            self.stt.stop_continuous_listening()
            self.logger.info("✅ Speech-to-text stopped")
        
        self.logger.info("👋 AI Assistant shutdown complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Voice Assistant')
    parser.add_argument('--gui', action='store_true', help='Launch exceptional graphical interface')
    parser.add_argument('--mode', type=str, choices=['interactive', 'continuous'], 
                       default='interactive', help='Voice assistant mode')
    args = parser.parse_args()
    
    try:
        if args.gui:
            # Launch exceptional UI
            from ui.exceptional_ui import main as exceptional_main
            exceptional_main()
        else:
            assistant = AIAssistant(use_gui=False)
            assistant.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()