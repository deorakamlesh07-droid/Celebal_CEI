import os
import tempfile
import logging
from pathlib import Path
from typing import Optional

from studymate_rag.core.exceptions import VoiceError

logger = logging.getLogger(__name__)

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

class TTSSynthesizer:
    def __init__(self, rate: int = 175, voice_index: Optional[int] = None):
        if not pyttsx3:
            raise VoiceError("pyttsx3 is not installed. Please install it for TTS support.")
            
        try:
            self.engine = pyttsx3.init()
            self.set_rate(rate)
            if voice_index is not None:
                self.set_voice(voice_index)
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise VoiceError(f"TTS initialization failed: {e}")

    def speak(self, text: str) -> None:
        """Speak the text aloud (blocking)."""
        if not text.strip():
            return
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS playback failed: {e}")
            raise VoiceError(f"TTS playback failed: {e}")

    def synthesize_to_file(self, text: str, output_path: Path) -> Path:
        """Synthesize text and save to a WAV/MP3 file."""
        if not text.strip():
            raise VoiceError("Cannot synthesize empty text")
            
        try:
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceError("TTS engine failed to generate audio file")
                
            return output_path
        except Exception as e:
            logger.error(f"TTS file synthesis failed: {e}")
            raise VoiceError(f"TTS file synthesis failed: {e}")

    def synthesize_to_bytes(self, text: str) -> bytes:
        """Synthesize text and return audio bytes."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
        try:
            self.synthesize_to_file(text, tmp_path)
            return tmp_path.read_bytes()
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def list_voices(self) -> list[dict]:
        """List available system voices."""
        try:
            voices = self.engine.getProperty('voices')
            return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
        except Exception as e:
            logger.warning(f"Failed to list TTS voices: {e}")
            return []

    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)."""
        try:
            self.engine.setProperty('rate', rate)
        except Exception as e:
            logger.warning(f"Failed to set TTS rate: {e}")

    def set_voice(self, index: int) -> None:
        """Set voice by index in the available voices list."""
        try:
            voices = self.engine.getProperty('voices')
            if 0 <= index < len(voices):
                self.engine.setProperty('voice', voices[index].id)
            else:
                logger.warning(f"Voice index {index} out of range")
        except Exception as e:
            logger.warning(f"Failed to set TTS voice: {e}")
