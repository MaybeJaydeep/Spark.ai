"""
GUI Controller Layer

Runs STT / wake-word detection in background threads and exposes a simple
event/callback interface for the UI.
"""

from __future__ import annotations

import threading
import logging
import time
from dataclasses import dataclass
from typing import Callable, Optional, List, Dict
from nlp.intent_parser import Intent, IntentParser
from speech.stt_sounddevice import SoundDeviceSTT
from speech.tts import get_tts
from toc.dispatcher import CommandDispatcher
from wake_word.detector_sounddevice import SoundDeviceWakeWord, WakeWordEvent
from llm.local_client import LocalLLMClient
from nlp.intent_parser import IntentType


@dataclass(frozen=True)
class AssistantSettings:
    enable_tts: bool = True
    enable_wake_word: bool = False
    enable_llm: bool = True
    wake_words: tuple[str, ...] = ("hey assistant", "computer")
    wake_word_confidence_threshold: float = 0.6
    stt_duration_seconds: float = 5.0
    stt_retry_on_failure: int = 1  # retry once on STT failure
    log_file: str = "assistant.log"


class AssistantController:
    """
    Thin orchestration layer for UI usage.

    The UI supplies callbacks; the controller handles threading + sequencing:
    wake word -> STT -> intent parse -> dispatch -> (optional) TTS.
    """

    def __init__(
        self,
        *,
        settings: Optional[AssistantSettings] = None,
        on_log: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
        on_intent: Optional[Callable[[Intent], None]] = None,
        on_result: Optional[Callable[[dict], None]] = None,
    ):
        self.settings = settings or AssistantSettings()

        self._on_log = on_log or (lambda _msg: None)
        self._on_status = on_status or (lambda _msg: None)
        self._on_intent = on_intent or (lambda _intent: None)
        self._on_result = on_result or (lambda _res: None)

        self._lock = threading.Lock()
        self._running = False

        self._stt: Optional[SoundDeviceSTT] = None
        self._parser: Optional[IntentParser] = None
        self._dispatcher: Optional[CommandDispatcher] = None
        self._wake: Optional[SoundDeviceWakeWord] = None
        self._wake_started = False
        self._wake_enabled = False
        self._history: List[Dict[str, str]] = []

        self._tts = get_tts()
        self._llm = LocalLLMClient() if self.settings.enable_llm else None

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def start(self) -> bool:
        with self._lock:
            if self._running:
                return True
            self._running = True

        try:
            self._on_status("Initializing...")
            self._configure_logging()
            self._dispatcher = CommandDispatcher()
            self._parser = IntentParser()
            self._stt = SoundDeviceSTT()
            self._stt.adjust_for_ambient_noise(1.0)

            if self.settings.enable_wake_word:
                self._start_wake_word()

            self._on_status("Ready")
            self._on_log("Assistant started.")
            return True
        except Exception as e:
            self._on_log(f"Failed to start assistant: {e}")
            self._on_status("Error")
            with self._lock:
                self._running = False
            return False

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False

        try:
            if self._wake:
                self._wake.stop()
            self._on_status("Stopped")
            self._on_log("Assistant stopped.")
        except Exception as e:
            self._on_log(f"Error stopping assistant: {e}")

    def run_text_command(self, text: str) -> None:
        if not text or not text.strip():
            return
        threading.Thread(target=self._process_text, args=(text,), daemon=True).start()

    def run_voice_command(self, duration: Optional[float] = None) -> None:
        threading.Thread(target=self._process_voice, args=(duration,), daemon=True).start()

    def _on_wake_word(self, event: WakeWordEvent) -> None:
        if not self.is_running:
            return
        self._on_log(f"Wake word: '{event.wake_word}'")
        if self.settings.enable_tts:
            self._tts.speak("Yes?")
        self.run_voice_command(self.settings.stt_duration_seconds)

    def _process_text(self, text: str) -> None:
        if not self.is_running:
            return
        self._on_status("Processing...")
        self._on_log(f"You: {text}")
        # Track conversation history for LLM
        self._history.append({"role": "user", "content": text})
        try:
            intent = self._parser.parse(text) if self._parser else None
            handled = False
            if intent:
                self._on_intent(intent)
                # If we have a confident non-UNKNOWN intent, use the command pipeline
                if intent.type != IntentType.UNKNOWN and intent.confidence >= 0.5:
                    res = self._dispatcher.dispatch(intent) if self._dispatcher else {
                        "success": False,
                        "message": "Dispatcher not initialized",
                    }
                    self._on_result(res)
                    msg = res.get("message", "")
                    if msg:
                        self._history.append({"role": "assistant", "content": msg})
                        self._on_log(f"Spark: {msg}")
                        if self.settings.enable_tts:
                            self._tts.speak(msg)
                    handled = True

            # If not handled by command pipeline, fall back to local LLM chat
            if not handled and self._llm:
                try:
                    reply = self._chat_with_llm()
                except Exception as e:
                    text = str(e)
                    # Common case: local LLM server (e.g. Ollama) not running
                    if "failed to establish a new connection" in text.lower() or "actively refused" in text.lower():
                        self._on_log("Local LLM is not reachable (e.g. Ollama not running on localhost:11434). I'll continue without chat mode.")
                        # Disable LLM for the rest of this session to avoid repeated errors
                        self._llm = None
                    else:
                        self._on_log(f"LLM error: {e}")
                else:
                    if reply:
                        self._history.append({"role": "assistant", "content": reply})
                        self._on_log(f"Spark: {reply}")
                        if self.settings.enable_tts:
                            self._tts.speak(reply)
        except Exception as e:
            error_str = str(e).lower()
            if 'network' in error_str or 'connection' in error_str:
                self._on_log("Network error. Check your internet connection.")
            elif 'weather' in error_str and 'api' in error_str:
                self._on_log("Weather API error. Set OPENWEATHER_API_KEY environment variable for weather, or use web search.")
            else:
                self._on_log(f"Error: {e}")
        finally:
            self._on_status("Ready")

    def _chat_with_llm(self) -> str:
        """
        Use local LLM as a conversational fallback / chat brain.

        Keeps a short rolling history for personalization and context.
        """
        if not self._llm:
            raise RuntimeError("LLM is disabled or not configured")

        # Keep last few exchanges to stay light-weight
        history = self._history[-8:]
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are a personal AI assistant running entirely on the user's local machine. "
                    "Be concise, friendly, and helpful. When the user asks for things like opening apps, "
                    "changing volume, or system actions, respond naturally but do not describe internal code. "
                    "If something is better done by the existing command system, simply answer as if it already happened."
                ),
            }
        ] + history

        return self._llm.chat(messages)

    def _process_voice(self, duration: Optional[float]) -> None:
        if not self.is_running:
            return
        if not self._stt:
            self._on_log("STT not initialized.")
            return

        dur = duration if duration is not None else self.settings.stt_duration_seconds

        self._on_status("Listening...")
        self._on_log("Listening for voice command...")
        try:
            attempts = 0
            stt_res = None
            while attempts <= self.settings.stt_retry_on_failure:
                stt_res = self._stt.listen_once(duration=dur)
                if stt_res and stt_res.success:
                    break
                attempts += 1
                if attempts <= self.settings.stt_retry_on_failure:
                    self._on_log("Didn't catch that, trying again...")

            if not stt_res or not stt_res.success:
                error_msg = getattr(stt_res, 'error', 'Unknown error')
                if 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                    self._on_log("Could not connect to speech recognition service. Check your internet connection.")
                elif 'timeout' in error_msg.lower():
                    self._on_log("Speech recognition timed out. Please try again.")
                elif 'microphone' in error_msg.lower() or 'device' in error_msg.lower():
                    self._on_log("Microphone not detected. Check your audio device settings.")
                else:
                    self._on_log(f"Could not understand audio. Please speak clearly or try typing instead.")
                return
            self._process_text(stt_res.text)
        except Exception as e:
            self._on_log(f"Voice error: {e}")
        finally:
            # small delay to avoid UI flicker in fast paths
            time.sleep(0.05)
            if self.is_running:
                self._on_status("Ready")

    # Wake-word control that can be toggled at runtime
    def set_wake_word_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._wake_enabled = enabled
        if enabled:
            self._start_wake_word()
        else:
            self._stop_wake_word()

    def _start_wake_word(self) -> None:
        if self._wake_started:
            return
        self._wake = SoundDeviceWakeWord(
            wake_words=list(self.settings.wake_words),
            chunk_duration=2.0,
            confidence_threshold=self.settings.wake_word_confidence_threshold,
        )
        self._wake.add_listener(self._on_wake_word)
        self._wake_started = self._wake.start()
        self._wake_enabled = True
        if not self._wake_started:
            self._on_log("Wake word failed to start; continuing without it.")
            self._on_status("Wake word: OFF")
            self._wake_enabled = False
        else:
            self._on_log("Wake word listening started.")
            self._on_status("Wake word: ON")

    def _stop_wake_word(self) -> None:
        if self._wake and self._wake_started:
            self._wake.stop()
            self._wake_started = False
            self._wake_enabled = False
            self._on_log("Wake word stopped.")
            self._on_status("Wake word: OFF")

    def _configure_logging(self) -> None:
        try:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s - %(message)s",
                filename=self.settings.log_file,
                filemode="a",
            )
        except Exception:
            # If file logging fails, continue without raising
            pass

