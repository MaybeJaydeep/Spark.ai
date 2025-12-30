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

from wake_word.listener import WakeWordDetector, ActivationEvent


class AIAssistant:
    """Main AI Assistant application"""
    
    def __init__(self):
        self.wake_word_detector: Optional[WakeWordDetector] = None
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
    
    def on_wake_word_detected(self, event: ActivationEvent) -> None:
        """Handle wake word detection events"""
        self.logger.info(
            f"🎤 Wake word detected: '{event.wake_word}' "
            f"(confidence: {event.confidence:.2f}) at {event.timestamp}"
        )
        
        # TODO: Integrate with speech-to-text and NLP processing
        print(f"\n✨ Assistant activated by '{event.wake_word}'!")
        print("🔊 Listening for your command...")
        print("(This is where speech-to-text would take over)\n")
    
    def initialize_wake_word_detection(self) -> bool:
        """Initialize wake word detection system"""
        try:
            self.logger.info("Initializing wake word detection...")
            
            # Create wake word detector
            self.wake_word_detector = WakeWordDetector()
            
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
    
    def run(self) -> None:
        """Main application loop"""
        self.logger.info("🚀 Starting AI Assistant...")
        
        # Initialize wake word detection
        if not self.initialize_wake_word_detection():
            self.logger.error("Failed to initialize wake word detection. Exiting.")
            return
        
        self.is_running = True
        
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
        
        self.logger.info("👋 AI Assistant shutdown complete")


def main():
    """Main entry point"""
    try:
        assistant = AIAssistant()
        assistant.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()