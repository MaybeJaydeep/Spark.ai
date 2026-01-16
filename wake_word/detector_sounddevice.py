"""
Wake Word Detection using sounddevice

Alternative implementation that doesn't require PyAudio.
Uses simple keyword spotting with sounddevice for audio capture.
"""

import logging
import numpy as np
import time
import threading
from typing import Callable, List, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import sounddevice as sd
    import speech_recognition as sr
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class DetectionState(Enum):
    """States for wake word detection"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    DETECTED = "detected"
    ERROR = "error"


@dataclass
class WakeWordEvent:
    """Event generated when wake word is detected"""
    wake_word: str
    confidence: float
    timestamp: float


class SoundDeviceWakeWord:
    """
    Wake Word Detector using sounddevice
    
    Continuously monitors audio and detects wake words using
    speech recognition on audio chunks.
    """
    
    def __init__(self, wake_words: List[str] = None, 
                 sample_rate: int = 16000,
                 chunk_duration: float = 2.0,
                 confidence_threshold: float = 0.6):
        """
        Initialize wake word detector
        
        Args:
            wake_words: List of wake words to detect
            sample_rate: Audio sample rate
            chunk_duration: Duration of audio chunks to process
            confidence_threshold: Minimum confidence for detection
        """
        self.logger = logging.getLogger(__name__)
        self.wake_words = wake_words or ["hey assistant", "computer", "wake up"]
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.confidence_threshold = confidence_threshold
        
        self.state = DetectionState.IDLE
        self.is_running = False
        self.listeners: List[Callable[[WakeWordEvent], None]] = []
        self.recognizer = None
        self.detection_thread = None
        
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.error("sounddevice or speech_recognition not available")
            return
        
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.logger.info("Wake word detector initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
    
    def add_listener(self, callback: Callable[[WakeWordEvent], None]) -> None:
        """Register a callback for wake word events"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            self.logger.debug(f"Added wake word listener")
    
    def remove_listener(self, callback: Callable[[WakeWordEvent], None]) -> None:
        """Unregister a callback"""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def _notify_listeners(self, event: WakeWordEvent) -> None:
        """Notify all registered listeners"""
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error notifying listener: {e}")
    
    def start(self) -> bool:
        """Start wake word detection"""
        if self.is_running:
            self.logger.warning("Wake word detector already running")
            return True
        
        if not self.recognizer:
            self.logger.error("Recognizer not initialized")
            return False
        
        try:
            self.is_running = True
            self.state = DetectionState.LISTENING
            
            # Start detection thread
            self.detection_thread = threading.Thread(
                target=self._detection_loop,
                daemon=True
            )
            self.detection_thread.start()
            
            self.logger.info("Wake word detection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start wake word detection: {e}")
            self.is_running = False
            return False
    
    def stop(self) -> None:
        """Stop wake word detection"""
        self.is_running = False
        self.state = DetectionState.IDLE
        
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
        
        self.logger.info("Wake word detection stopped")
    
    def _detection_loop(self) -> None:
        """Main detection loop"""
        self.logger.info("Detection loop started")
        
        while self.is_running:
            try:
                # Record audio chunk
                audio_data = sd.rec(
                    self.chunk_size,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16'
                )
                sd.wait()
                
                # Check for wake word
                self.state = DetectionState.PROCESSING
                wake_word = self._check_for_wake_word(audio_data)
                
                if wake_word:
                    self.state = DetectionState.DETECTED
                    
                    # Create event
                    event = WakeWordEvent(
                        wake_word=wake_word,
                        confidence=0.8,  # Simplified confidence
                        timestamp=time.time()
                    )
                    
                    # Notify listeners
                    self._notify_listeners(event)
                    self.logger.info(f"Wake word detected: {wake_word}")
                    
                    # Brief pause after detection
                    time.sleep(1.0)
                
                self.state = DetectionState.LISTENING
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                self.state = DetectionState.ERROR
                time.sleep(0.5)
    
    def _check_for_wake_word(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Check if audio contains wake word
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Wake word if detected, None otherwise
        """
        try:
            # Convert to AudioData
            audio_bytes = audio_data.tobytes()
            audio = sr.AudioData(audio_bytes, self.sample_rate, 2)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language="en-US")
                text_lower = text.lower().strip()
                
                # Check if any wake word is in the text
                for wake_word in self.wake_words:
                    if wake_word.lower() in text_lower:
                        return wake_word
                
            except sr.UnknownValueError:
                # No speech detected
                pass
            except sr.RequestError as e:
                self.logger.warning(f"Recognition service error: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking for wake word: {e}")
            return None
    
    def get_status(self) -> dict:
        """Get current detector status"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "wake_words": self.wake_words,
            "listeners_count": len(self.listeners)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not SOUNDDEVICE_AVAILABLE:
        print("❌ sounddevice or speech_recognition not available")
        exit(1)
    
    def on_wake_word(event: WakeWordEvent):
        print(f"\n🎤 Wake word detected: '{event.wake_word}'")
        print(f"   Confidence: {event.confidence:.2f}")
        print(f"   Timestamp: {event.timestamp}")
    
    # Create detector
    detector = SoundDeviceWakeWord(
        wake_words=["hey assistant", "computer", "wake up"],
        chunk_duration=2.0
    )
    
    # Add listener
    detector.add_listener(on_wake_word)
    
    # Start detection
    print("Starting wake word detection...")
    print(f"Wake words: {', '.join(detector.wake_words)}")
    print("Speak a wake word to test...")
    print("Press Ctrl+C to stop\n")
    
    if detector.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
    
    detector.stop()
    print("Done!")
