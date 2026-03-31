"""
JARVIS Voice Module (OPTIONAL)
Speech-to-Text and Text-to-Speech.
This module is completely optional and gracefully disabled if dependencies missing.
"""

import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class VoiceModule:
    """
    Optional voice I/O. Wraps speech_recognition and pyttsx3.
    Gracefully degrades if packages not installed.
    """

    def __init__(self, config, on_speech_callback: Optional[Callable] = None):
        self.config = config
        self.on_speech = on_speech_callback
        self.available = False
        self.tts_available = False
        self._listening = False
        self._tts_engine = None
        self._recognizer = None
        self._microphone = None
        self._listen_thread = None

        self._init_stt()
        self._init_tts()

    def _init_stt(self):
        """Initialize Speech-to-Text."""
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            self.available = True
            logger.info("STT initialized successfully.")
        except ImportError:
            logger.warning("speech_recognition not installed. Voice input unavailable.")
        except Exception as e:
            logger.warning(f"STT init failed: {e}")

    def _init_tts(self):
        """Initialize Text-to-Speech."""
        try:
            import pyttsx3
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", 180)
            self.tts_available = True
            logger.info("TTS initialized successfully.")
        except ImportError:
            logger.warning("pyttsx3 not installed. TTS unavailable.")
        except Exception as e:
            logger.warning(f"TTS init failed: {e}")

    def speak(self, text: str):
        """Speak text aloud (non-blocking)."""
        if not self.tts_available or not self.config.tts_enabled:
            return
        try:
            # Run TTS in separate thread to avoid blocking
            def _speak():
                self._tts_engine.say(text)
                self._tts_engine.runAndWait()
            threading.Thread(target=_speak, daemon=True).start()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def start_listening(self):
        """Start background listening for voice commands."""
        if not self.available or not self.config.voice_enabled:
            return
        if self._listening:
            return
        self._listening = True
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        logger.info("Voice listening started.")

    def stop_listening(self):
        """Stop background voice listening."""
        self._listening = False
        logger.info("Voice listening stopped.")

    def _listen_loop(self):
        """Background loop: waits for wake word then captures command."""
        import speech_recognition as sr

        wake_word = self.config.wake_word.lower()

        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)

        while self._listening:
            try:
                with self._microphone as source:
                    audio = self._recognizer.listen(source, timeout=3, phrase_time_limit=8)

                text = self._recognizer.recognize_google(
                    audio, language=self.config.voice_language
                ).lower()

                logger.info(f"Heard: {text}")

                # Check for wake word
                if wake_word in text:
                    # Extract command after wake word
                    command = text.split(wake_word, 1)[-1].strip()
                    if command and self.on_speech:
                        self.on_speech(command)
                    elif self.on_speech:
                        # Just wake word, prompt for command
                        self.speak("Yes? I'm listening.")

            except sr.WaitTimeoutError:
                pass  # Normal — no speech detected
            except sr.UnknownValueError:
                pass  # Could not understand audio
            except sr.RequestError as e:
                logger.error(f"STT service error: {e}")
            except Exception as e:
                logger.error(f"Voice loop error: {e}")

    def listen_once(self) -> Optional[str]:
        """Listen for a single voice command (blocking)."""
        if not self.available:
            return None
        import speech_recognition as sr
        try:
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return self._recognizer.recognize_google(audio)
        except Exception:
            return None

    @property
    def status(self) -> str:
        parts = []
        parts.append("🎙️ STT: " + ("✅ Ready" if self.available else "❌ Unavailable"))
        parts.append("🔊 TTS: " + ("✅ Ready" if self.tts_available else "❌ Unavailable"))
        parts.append("👂 Listening: " + ("Active" if self._listening else "Off"))
        return " | ".join(parts)
