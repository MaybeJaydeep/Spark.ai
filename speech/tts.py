"""
Text-to-Speech Module

Converts text to speech using system TTS engines.
"""

import logging
import platform
import subprocess
from typing import Optional
import threading


class TextToSpeech:
    """
    Text-to-Speech Engine
    
    Provides cross-platform text-to-speech functionality.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.is_speaking = False
    
    def speak(self, text: str, async_mode: bool = True) -> bool:
        """
        Speak the given text
        
        Args:
            text: Text to speak
            async_mode: If True, speak in background thread
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        if async_mode:
            # Speak in background thread
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()
            return True
        else:
            # Speak synchronously
            return self._speak_sync(text)
    
    def _speak_sync(self, text: str) -> bool:
        """Internal synchronous speak method"""
        self.is_speaking = True
        
        try:
            if self.system == "windows":
                success = self._speak_windows(text)
            elif self.system == "linux":
                success = self._speak_linux(text)
            elif self.system == "darwin":
                success = self._speak_macos(text)
            else:
                self.logger.error(f"Unsupported platform: {self.system}")
                success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
            return False
        
        finally:
            self.is_speaking = False
    
    def _speak_windows(self, text: str) -> bool:
        """Speak on Windows using PowerShell"""
        try:
            # Escape single quotes in text
            text = text.replace("'", "''")
            
            # Use PowerShell with SAPI
            script = f"""
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Speak('{text}')
            $synth.Dispose()
            """
            
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=30
            )
            
            self.logger.info(f"Spoke: '{text}'")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("Speech timeout")
            return False
        except Exception as e:
            self.logger.error(f"Windows TTS error: {e}")
            return False
    
    def _speak_linux(self, text: str) -> bool:
        """Speak on Linux using espeak or festival"""
        try:
            # Try espeak first
            try:
                subprocess.run(
                    ["espeak", text],
                    capture_output=True,
                    timeout=30
                )
                self.logger.info(f"Spoke: '{text}'")
                return True
            except FileNotFoundError:
                pass
            
            # Try festival as fallback
            try:
                subprocess.run(
                    ["festival", "--tts"],
                    input=text.encode(),
                    capture_output=True,
                    timeout=30
                )
                self.logger.info(f"Spoke: '{text}'")
                return True
            except FileNotFoundError:
                pass
            
            # Try spd-say as another fallback
            try:
                subprocess.run(
                    ["spd-say", text],
                    capture_output=True,
                    timeout=30
                )
                self.logger.info(f"Spoke: '{text}'")
                return True
            except FileNotFoundError:
                pass
            
            self.logger.error("No TTS engine found on Linux (tried espeak, festival, spd-say)")
            return False
            
        except subprocess.TimeoutExpired:
            self.logger.error("Speech timeout")
            return False
        except Exception as e:
            self.logger.error(f"Linux TTS error: {e}")
            return False
    
    def _speak_macos(self, text: str) -> bool:
        """Speak on macOS using 'say' command"""
        try:
            subprocess.run(
                ["say", text],
                capture_output=True,
                timeout=30
            )
            
            self.logger.info(f"Spoke: '{text}'")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("Speech timeout")
            return False
        except Exception as e:
            self.logger.error(f"macOS TTS error: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop current speech (platform-dependent)"""
        try:
            if self.system == "windows":
                # Kill PowerShell processes (not ideal but works)
                subprocess.run(["taskkill", "/F", "/IM", "powershell.exe"], 
                             capture_output=True)
            elif self.system == "linux":
                subprocess.run(["pkill", "-f", "espeak|festival|spd-say"],
                             capture_output=True)
            elif self.system == "darwin":
                subprocess.run(["killall", "say"],
                             capture_output=True)
            
            self.is_speaking = False
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
            return False


# Global TTS instance
_tts_instance: Optional[TextToSpeech] = None


def get_tts() -> TextToSpeech:
    """Get the global TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    tts = TextToSpeech()
    
    print("Testing Text-to-Speech...")
    
    # Test speaking
    print("\nSpeaking: 'Hello, I am your voice assistant'")
    tts.speak("Hello, I am your voice assistant", async_mode=False)
    
    print("\nSpeaking: 'How can I help you today?'")
    tts.speak("How can I help you today?", async_mode=False)
    
    print("\nTTS test complete!")
