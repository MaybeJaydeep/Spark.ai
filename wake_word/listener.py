"""
Wake Word Detection Module

This module provides continuous audio monitoring and wake word detection
functionality for the AI assistant.
"""

import threading
import time
import logging
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json
import os

# Audio processing imports (will be added to requirements)
try:
    import pyaudio
    import numpy as np
    import webrtcvad
except ImportError:
    pyaudio = None
    np = None
    webrtcvad = None


class DetectionState(Enum):
    """States for wake word detection"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    DETECTED = "detected"
    ERROR = "error"


@dataclass
class ActivationEvent:
    """Event generated when wake word is detected"""
    timestamp: float
    confidence: float
    wake_word: str
    audio_context: Optional[bytes] = None


@dataclass
class WakeWordConfig:
    """Configuration for wake word detection"""
    wake_words: List[str]
    confidence_threshold: float = 0.7
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    audio_format: int = pyaudio.paInt16 if pyaudio else 16
    buffer_duration: float = 2.0  # seconds
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive


class WakeWordDetector:
    """
    Continuous wake word detection system
    
    Monitors audio input and detects configured wake words,
    generating activation events for downstream processing.
    """
    
    def __init__(self, config_path: str = "config/wake_word_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.state = DetectionState.IDLE
        self.is_running = False
        self.audio_stream = None
        self.audio_interface = None
        self.listeners: List[Callable[[ActivationEvent], None]] = []
        self.audio_buffer = []
        self.processing_thread = None
        self.vad = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize VAD if available
        if webrtcvad:
            self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)
    
    def _load_config(self) -> WakeWordConfig:
        """Load configuration from file or use defaults"""
        default_config = {
            "wake_words": ["hey assistant", "computer", "wake up"],
            "confidence_threshold": 0.7,
            "sample_rate": 16000,
            "chunk_size": 1024,
            "channels": 1,
            "buffer_duration": 2.0,
            "vad_aggressiveness": 2
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    # Merge with defaults
                    default_config.update(config_data)
            else:
                self.logger.info(f"Config file not found at {self.config_path}, using defaults")
                
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
        
        return WakeWordConfig(**default_config)
    
    def reload_config(self) -> bool:
        """Reload configuration without restarting"""
        try:
            old_config = self.config
            self.config = self._load_config()
            self.logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload config: {e}")
            self.config = old_config
            return False
    
    def add_listener(self, callback: Callable[[ActivationEvent], None]) -> None:
        """Register a callback for activation events"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            self.logger.debug(f"Added activation listener: {callback.__name__}")
    
    def remove_listener(self, callback: Callable[[ActivationEvent], None]) -> None:
        """Unregister a callback"""
        if callback in self.listeners:
            self.listeners.remove(callback)
            self.logger.debug(f"Removed activation listener: {callback.__name__}")
    
    def _notify_listeners(self, event: ActivationEvent) -> None:
        """Notify all registered listeners of activation event"""
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error notifying listener {listener.__name__}: {e}")
    
    def start(self) -> bool:
        """Start continuous wake word detection"""
        if self.is_running:
            self.logger.warning("Wake word detector already running")
            return True
        
        if not self._check_dependencies():
            return False
        
        try:
            self._initialize_audio()
            self.is_running = True
            self.state = DetectionState.LISTENING
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._audio_processing_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.logger.info("Wake word detector started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start wake word detector: {e}")
            self.state = DetectionState.ERROR
            return False
    
    def stop(self) -> None:
        """Stop wake word detection and cleanup resources"""
        self.is_running = False
        self.state = DetectionState.IDLE
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Cleanup audio resources
        self._cleanup_audio()
        
        self.logger.info("Wake word detector stopped")
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        missing_deps = []
        
        if pyaudio is None:
            missing_deps.append("pyaudio")
        if np is None:
            missing_deps.append("numpy")
        if webrtcvad is None:
            missing_deps.append("webrtcvad")
        
        if missing_deps:
            self.logger.error(f"Missing required dependencies: {missing_deps}")
            return False
        
        return True
    
    def _initialize_audio(self) -> None:
        """Initialize audio input stream"""
        self.audio_interface = pyaudio.PyAudio()
        
        # Find suitable audio device
        device_index = self._find_audio_device()
        
        self.audio_stream = self.audio_interface.open(
            format=self.config.audio_format,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.config.chunk_size,
            stream_callback=self._audio_callback
        )
        
        self.audio_stream.start_stream()
        self.logger.debug("Audio stream initialized")
    
    def _find_audio_device(self) -> Optional[int]:
        """Find suitable audio input device"""
        device_count = self.audio_interface.get_device_count()
        
        for i in range(device_count):
            device_info = self.audio_interface.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.logger.debug(f"Using audio device: {device_info['name']}")
                return i
        
        self.logger.warning("No suitable audio input device found, using default")
        return None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream data"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        # Add to buffer for processing
        self.audio_buffer.append(in_data)
        
        # Maintain buffer size
        max_buffer_size = int(self.config.buffer_duration * self.config.sample_rate / self.config.chunk_size)
        if len(self.audio_buffer) > max_buffer_size:
            self.audio_buffer.pop(0)
        
        return (None, pyaudio.paContinue)
    
    def _audio_processing_loop(self) -> None:
        """Main audio processing loop"""
        self.logger.debug("Audio processing loop started")
        
        while self.is_running:
            try:
                if len(self.audio_buffer) > 0:
                    self.state = DetectionState.PROCESSING
                    
                    # Get audio data
                    audio_data = self.audio_buffer.copy()
                    
                    # Process for wake word detection
                    if self._process_audio_chunk(audio_data):
                        self.state = DetectionState.DETECTED
                        # Reset buffer after detection
                        self.audio_buffer.clear()
                    else:
                        self.state = DetectionState.LISTENING
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                self.logger.error(f"Error in audio processing loop: {e}")
                self.state = DetectionState.ERROR
                time.sleep(0.1)
    
    def _process_audio_chunk(self, audio_chunks: List[bytes]) -> bool:
        """Process audio chunks for wake word detection"""
        if not audio_chunks:
            return False
        
        try:
            # Combine audio chunks
            combined_audio = b''.join(audio_chunks)
            
            # Convert to numpy array for processing
            audio_array = np.frombuffer(combined_audio, dtype=np.int16)
            
            # Voice Activity Detection
            if self.vad and not self._has_voice_activity(combined_audio):
                return False
            
            # Simple keyword matching (placeholder for more sophisticated detection)
            detected_word, confidence = self._detect_wake_word(audio_array)
            
            if detected_word and confidence >= self.config.confidence_threshold:
                # Generate activation event
                event = ActivationEvent(
                    timestamp=time.time(),
                    confidence=confidence,
                    wake_word=detected_word,
                    audio_context=combined_audio
                )
                
                self._notify_listeners(event)
                self.logger.info(f"Wake word detected: {detected_word} (confidence: {confidence:.2f})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
            return False
    
    def _has_voice_activity(self, audio_data: bytes) -> bool:
        """Check if audio contains voice activity using VAD"""
        try:
            # VAD requires specific frame sizes (10, 20, or 30ms)
            frame_duration = 30  # ms
            frame_size = int(self.config.sample_rate * frame_duration / 1000)
            
            # Process in frames
            for i in range(0, len(audio_data), frame_size * 2):  # *2 for 16-bit samples
                frame = audio_data[i:i + frame_size * 2]
                if len(frame) == frame_size * 2:
                    if self.vad.is_speech(frame, self.config.sample_rate):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"VAD processing error: {e}")
            return True  # Assume voice activity on error
    
    def _detect_wake_word(self, audio_array: np.ndarray) -> tuple[Optional[str], float]:
        """
        Detect wake words in audio array
        
        This is a placeholder implementation. In a production system,
        this would use a trained wake word detection model.
        """
        # Placeholder: Simple energy-based detection
        # In reality, this would use a trained neural network or keyword spotting model
        
        # Calculate audio energy
        energy = np.mean(np.abs(audio_array))
        
        # Simple threshold-based detection (placeholder)
        if energy > 1000:  # Arbitrary threshold
            # Return first configured wake word with mock confidence
            if self.config.wake_words:
                confidence = min(0.9, energy / 2000)  # Mock confidence calculation
                return self.config.wake_words[0], confidence
        
        return None, 0.0
    
    def _cleanup_audio(self) -> None:
        """Cleanup audio resources"""
        try:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None
                
            self.logger.debug("Audio resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up audio resources: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current detector status"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "config": {
                "wake_words": self.config.wake_words,
                "confidence_threshold": self.config.confidence_threshold,
                "sample_rate": self.config.sample_rate
            },
            "listeners_count": len(self.listeners)
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    def on_wake_word_detected(event: ActivationEvent):
        print(f"Wake word detected: {event.wake_word} at {event.timestamp} with confidence {event.confidence}")
    
    # Create detector
    detector = WakeWordDetector()
    detector.add_listener(on_wake_word_detected)
    
    try:
        print("Starting wake word detection...")
        if detector.start():
            print("Detector started. Say a wake word to test.")
            print("Press Ctrl+C to stop.")
            
            while True:
                time.sleep(1)
                status = detector.get_status()
                print(f"Status: {status['state']}")
                
    except KeyboardInterrupt:
        print("\nStopping detector...")
    finally:
        detector.stop()