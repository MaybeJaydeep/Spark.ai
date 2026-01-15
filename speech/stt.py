"""
Speech-to-Text Module

Converts spoken audio into text using various speech recognition engines.
"""

import logging
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Speech recognition imports
try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Try sounddevice as alternative to pyaudio
try:
    from speech.stt_sounddevice import SoundDeviceSTT
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class RecognitionEngine(Enum):
    """Available speech recognition engines"""
    GOOGLE = "google"
    SPHINX = "sphinx"
    WHISPER = "whisper"
    AZURE = "azure"
    IBM = "ibm"


class RecognitionState(Enum):
    """States for speech recognition"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RecognitionResult:
    """Result from speech recognition"""
    text: str
    confidence: float
    language: str
    duration: float
    timestamp: float
    engine: str
    success: bool
    error: Optional[str] = None


@dataclass
class STTConfig:
    """Configuration for speech-to-text"""
    engine: RecognitionEngine = RecognitionEngine.GOOGLE
    language: str = "en-US"
    timeout: float = 5.0
    phrase_time_limit: float = 10.0
    energy_threshold: int = 4000
    dynamic_energy_threshold: bool = True
    pause_threshold: float = 0.8
    ambient_duration: float = 1.0


class SpeechToText:
    """
    Speech-to-Text conversion system
    
    Captures audio input and converts it to text using
    various speech recognition engines.
    """
    
    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or STTConfig()
        self.recognizer = None
        self.microphone = None
        self.state = RecognitionState.IDLE
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.result_callbacks: list[Callable[[RecognitionResult], None]] = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Try sounddevice first, fallback to pyaudio
        if SOUNDDEVICE_AVAILABLE:
            self.logger.info("Using sounddevice for audio input")
            self.sounddevice_stt = SoundDeviceSTT()
            self.use_sounddevice = True
        else:
            self.logger.info("Using pyaudio for audio input")
            self.use_sounddevice = False
            # Initialize recognizer
            self._initialize_recognizer()
    
    def _initialize_recognizer(self) -> bool:
        """Initialize speech recognizer"""
        if sr is None:
            self.logger.error("speech_recognition library not available")
            return False
        
        try:
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            self.recognizer.pause_threshold = self.config.pause_threshold
            
            self.logger.info("Speech recognizer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize recognizer: {e}")
            return False
    
    def add_result_callback(self, callback: Callable[[RecognitionResult], None]) -> None:
        """Register callback for recognition results"""
        if callback not in self.result_callbacks:
            self.result_callbacks.append(callback)
            self.logger.debug(f"Added result callback: {callback.__name__}")
    
    def remove_result_callback(self, callback: Callable[[RecognitionResult], None]) -> None:
        """Unregister callback"""
        if callback in self.result_callbacks:
            self.result_callbacks.remove(callback)
            self.logger.debug(f"Removed result callback: {callback.__name__}")
    
    def _notify_callbacks(self, result: RecognitionResult) -> None:
        """Notify all registered callbacks"""
        for callback in self.result_callbacks:
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in callback {callback.__name__}: {e}")
    
    def adjust_for_ambient_noise(self, duration: Optional[float] = None) -> bool:
        """Adjust recognizer for ambient noise"""
        duration = duration or self.config.ambient_duration
        
        # Use sounddevice if available
        if self.use_sounddevice and hasattr(self, 'sounddevice_stt'):
            return self.sounddevice_stt.adjust_for_ambient_noise(duration)
        
        if not self.recognizer:
            return False
        
        try:
            with sr.Microphone() as source:
                self.logger.info(f"Adjusting for ambient noise ({duration}s)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.logger.info(f"Energy threshold set to: {self.recognizer.energy_threshold}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to adjust for ambient noise: {e}")
            return False
    
    def listen_once(self, timeout: Optional[float] = None, 
                    phrase_time_limit: Optional[float] = None) -> Optional[RecognitionResult]:
        """
        Listen for a single utterance and convert to text
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time for the phrase
            
        Returns:
            RecognitionResult or None if failed
        """
        # Use sounddevice if available
        if self.use_sounddevice and hasattr(self, 'sounddevice_stt'):
            phrase_time_limit = phrase_time_limit or self.config.phrase_time_limit
            return self.sounddevice_stt.listen_once(duration=phrase_time_limit)
        
        if not self.recognizer:
            self.logger.error("Recognizer not initialized")
            return None
        
        timeout = timeout or self.config.timeout
        phrase_time_limit = phrase_time_limit or self.config.phrase_time_limit
        
        try:
            self.state = RecognitionState.LISTENING
            
            with sr.Microphone() as source:
                self.logger.info("Listening for speech...")
                start_time = time.time()
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                duration = time.time() - start_time
                
                # Process audio
                result = self._recognize_audio(audio, duration)
                
                self.state = RecognitionState.COMPLETED if result.success else RecognitionState.ERROR
                
                # Notify callbacks
                self._notify_callbacks(result)
                
                return result
                
        except sr.WaitTimeoutError:
            self.logger.warning("Listening timed out - no speech detected")
            result = RecognitionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                duration=timeout,
                timestamp=time.time(),
                engine=self.config.engine.value,
                success=False,
                error="Timeout - no speech detected"
            )
            self.state = RecognitionState.ERROR
            self._notify_callbacks(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error during listening: {e}")
            result = RecognitionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                duration=0.0,
                timestamp=time.time(),
                engine=self.config.engine.value,
                success=False,
                error=str(e)
            )
            self.state = RecognitionState.ERROR
            self._notify_callbacks(result)
            return result
        
        finally:
            self.state = RecognitionState.IDLE
    
    def _recognize_audio(self, audio: sr.AudioData, duration: float) -> RecognitionResult:
        """Recognize speech from audio data"""
        self.state = RecognitionState.PROCESSING
        start_time = time.time()
        
        try:
            # Select recognition engine
            if self.config.engine == RecognitionEngine.GOOGLE:
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.language
                )
                confidence = 0.9  # Google doesn't provide confidence
                
            elif self.config.engine == RecognitionEngine.SPHINX:
                text = self.recognizer.recognize_sphinx(audio)
                confidence = 0.8  # Sphinx doesn't provide confidence
                
            elif self.config.engine == RecognitionEngine.WHISPER:
                text = self.recognizer.recognize_whisper(audio)
                confidence = 0.85  # Whisper doesn't provide confidence directly
                
            else:
                raise ValueError(f"Unsupported engine: {self.config.engine}")
            
            self.logger.info(f"Recognized: '{text}'")
            
            return RecognitionResult(
                text=text,
                confidence=confidence,
                language=self.config.language,
                duration=duration,
                timestamp=start_time,
                engine=self.config.engine.value,
                success=True
            )
            
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                duration=duration,
                timestamp=start_time,
                engine=self.config.engine.value,
                success=False,
                error="Could not understand audio"
            )
            
        except sr.RequestError as e:
            self.logger.error(f"Recognition service error: {e}")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                duration=duration,
                timestamp=start_time,
                engine=self.config.engine.value,
                success=False,
                error=f"Service error: {e}"
            )
            
        except Exception as e:
            self.logger.error(f"Recognition error: {e}")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                duration=duration,
                timestamp=start_time,
                engine=self.config.engine.value,
                success=False,
                error=str(e)
            )
    
    def start_continuous_listening(self) -> bool:
        """Start continuous speech recognition in background"""
        if self.is_listening:
            self.logger.warning("Already listening")
            return True
        
        if not self.recognizer:
            self.logger.error("Recognizer not initialized")
            return False
        
        try:
            self.is_listening = True
            
            # Start background listening thread
            self.microphone = sr.Microphone()
            
            def callback(recognizer, audio):
                """Background callback for audio"""
                try:
                    result = self._recognize_audio(audio, 0.0)
                    self._notify_callbacks(result)
                except Exception as e:
                    self.logger.error(f"Error in background callback: {e}")
            
            # Start listening in background
            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone,
                callback,
                phrase_time_limit=self.config.phrase_time_limit
            )
            
            self.logger.info("Started continuous listening")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous listening: {e}")
            self.is_listening = False
            return False
    
    def stop_continuous_listening(self) -> None:
        """Stop continuous speech recognition"""
        if not self.is_listening:
            return
        
        try:
            if hasattr(self, 'stop_listening') and self.stop_listening:
                self.stop_listening(wait_for_stop=False)
            
            self.is_listening = False
            self.state = RecognitionState.IDLE
            self.logger.info("Stopped continuous listening")
            
        except Exception as e:
            self.logger.error(f"Error stopping continuous listening: {e}")
    
    def recognize_from_audio_data(self, audio_data: bytes, 
                                  sample_rate: int = 16000) -> Optional[RecognitionResult]:
        """
        Recognize speech from raw audio data
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            RecognitionResult or None
        """
        if not self.recognizer:
            return None
        
        try:
            # Convert raw audio to AudioData
            audio = sr.AudioData(audio_data, sample_rate, 2)
            
            # Recognize
            result = self._recognize_audio(audio, 0.0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error recognizing from audio data: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current STT status"""
        return {
            "state": self.state.value,
            "is_listening": self.is_listening,
            "engine": self.config.engine.value,
            "language": self.config.language,
            "energy_threshold": self.recognizer.energy_threshold if self.recognizer else None,
            "callbacks_count": len(self.result_callbacks)
        }
    
    def list_microphones(self) -> list[str]:
        """List available microphones"""
        if sr is None:
            return []
        
        try:
            mics = sr.Microphone.list_microphone_names()
            return mics
        except Exception as e:
            self.logger.error(f"Error listing microphones: {e}")
            return []


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_result(result: RecognitionResult):
        if result.success:
            print(f"✅ Recognized: '{result.text}' (confidence: {result.confidence:.2f})")
        else:
            print(f"❌ Recognition failed: {result.error}")
    
    # Create STT instance
    stt = SpeechToText()
    stt.add_result_callback(on_result)
    
    # List available microphones
    print("Available microphones:")
    for i, mic in enumerate(stt.list_microphones()):
        print(f"  {i}: {mic}")
    
    # Adjust for ambient noise
    print("\nAdjusting for ambient noise...")
    stt.adjust_for_ambient_noise()
    
    # Listen for speech
    print("\nSpeak now...")
    result = stt.listen_once()
    
    if result and result.success:
        print(f"\nFinal result: '{result.text}'")
    else:
        print("\nNo speech recognized")