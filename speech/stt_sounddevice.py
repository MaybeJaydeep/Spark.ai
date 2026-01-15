"""
Speech-to-Text using sounddevice

Alternative implementation using sounddevice instead of pyaudio.
"""

import logging
import time
import numpy as np
from typing import Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

try:
    import sounddevice as sd
    import speech_recognition as sr
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


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


class SoundDeviceSTT:
    """
    Speech-to-Text using sounddevice
    
    Alternative to PyAudio-based STT that uses sounddevice library.
    """
    
    def __init__(self, sample_rate: int = 16000, language: str = "en-US"):
        self.logger = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.language = language
        self.state = RecognitionState.IDLE
        self.recognizer = None
        
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.error("sounddevice or speech_recognition not available")
            return
        
        try:
            self.recognizer = sr.Recognizer()
            self.logger.info("SoundDevice STT initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
    
    def list_devices(self) -> List[dict]:
        """List available audio input devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            return input_devices
        except Exception as e:
            self.logger.error(f"Error listing devices: {e}")
            return []
    
    def record_audio(self, duration: float = 5.0) -> Optional[np.ndarray]:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array or None
        """
        try:
            self.logger.info(f"Recording for {duration} seconds...")
            self.state = RecognitionState.LISTENING
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()  # Wait for recording to complete
            
            self.logger.info("Recording complete")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            self.state = RecognitionState.ERROR
            return None
    
    def recognize_from_audio(self, audio_data: np.ndarray) -> RecognitionResult:
        """
        Recognize speech from audio data
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            RecognitionResult
        """
        if not self.recognizer:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration=0.0,
                timestamp=time.time(),
                engine="sounddevice",
                success=False,
                error="Recognizer not initialized"
            )
        
        try:
            self.state = RecognitionState.PROCESSING
            start_time = time.time()
            
            # Convert numpy array to AudioData
            audio_bytes = audio_data.tobytes()
            audio = sr.AudioData(audio_bytes, self.sample_rate, 2)
            
            # Recognize using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            
            self.logger.info(f"Recognized: '{text}'")
            self.state = RecognitionState.COMPLETED
            
            return RecognitionResult(
                text=text,
                confidence=0.9,  # Google doesn't provide confidence
                language=self.language,
                duration=time.time() - start_time,
                timestamp=start_time,
                engine="sounddevice_google",
                success=True
            )
            
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration=0.0,
                timestamp=time.time(),
                engine="sounddevice_google",
                success=False,
                error="Could not understand audio"
            )
            
        except sr.RequestError as e:
            self.logger.error(f"Recognition service error: {e}")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration=0.0,
                timestamp=time.time(),
                engine="sounddevice_google",
                success=False,
                error=f"Service error: {e}"
            )
            
        except Exception as e:
            self.logger.error(f"Recognition error: {e}")
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration=0.0,
                timestamp=time.time(),
                engine="sounddevice_google",
                success=False,
                error=str(e)
            )
    
    def listen_once(self, duration: float = 5.0) -> Optional[RecognitionResult]:
        """
        Listen for speech and recognize
        
        Args:
            duration: Maximum recording duration
            
        Returns:
            RecognitionResult or None
        """
        # Record audio
        audio_data = self.record_audio(duration)
        
        if audio_data is None:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration=0.0,
                timestamp=time.time(),
                engine="sounddevice",
                success=False,
                error="Failed to record audio"
            )
        
        # Recognize speech
        return self.recognize_from_audio(audio_data)
    
    def adjust_for_ambient_noise(self, duration: float = 1.0) -> bool:
        """
        Adjust for ambient noise
        
        Args:
            duration: Duration to sample ambient noise
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Adjusting for ambient noise ({duration}s)...")
            
            # Record ambient noise
            noise_sample = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()
            
            # Calculate energy threshold
            if self.recognizer:
                energy = np.mean(np.abs(noise_sample))
                self.recognizer.energy_threshold = energy * 1.5
                self.logger.info(f"Energy threshold set to: {self.recognizer.energy_threshold}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adjusting for ambient noise: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not SOUNDDEVICE_AVAILABLE:
        print("❌ sounddevice or speech_recognition not available")
        print("Install with: pip install sounddevice SpeechRecognition")
        exit(1)
    
    # Create STT instance
    stt = SoundDeviceSTT()
    
    # List devices
    print("\n📱 Available input devices:")
    devices = stt.list_devices()
    for device in devices:
        print(f"  {device['index']}: {device['name']}")
    
    if not devices:
        print("❌ No input devices found")
        exit(1)
    
    # Adjust for ambient noise
    print("\n🔇 Adjusting for ambient noise...")
    stt.adjust_for_ambient_noise(1.0)
    
    # Test recording and recognition
    print("\n🎤 Speak now (5 seconds)...")
    result = stt.listen_once(duration=5.0)
    
    if result and result.success:
        print(f"\n✅ Recognized: '{result.text}'")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Duration: {result.duration:.2f}s")
    else:
        print(f"\n❌ Recognition failed: {result.error if result else 'Unknown error'}")
