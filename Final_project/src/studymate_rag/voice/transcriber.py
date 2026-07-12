import io
import os
import tempfile
import logging
import soundfile as sf
import numpy as np
from pathlib import Path
from functools import lru_cache

from studymate_rag.core.exceptions import VoiceError
from studymate_rag.voice.models import TranscriptionResult

logger = logging.getLogger(__name__)

# Try importing optional dependencies, fallback gracefully
try:
    import whisper
except ImportError:
    whisper = None

try:
    import noisereduce as nr
except ImportError:
    nr = None
    
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


@lru_cache(maxsize=1)
def load_whisper_model(model_name: str = "base"):
    if not whisper:
        raise VoiceError("openai-whisper is not installed. Please install it to use voice features.")
    
    logger.info(f"Loading Whisper model '{model_name}'...")
    try:
        # Load the model; device is automatically selected by whisper (CUDA if available)
        return whisper.load_model(model_name)
    except Exception as e:
        raise VoiceError(f"Failed to load Whisper model '{model_name}': {e}")


class WhisperTranscriber:
    def __init__(self, model_name: str = "base", max_size_mb: int = 25):
        self.model_name = model_name
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        if not audio_path.exists():
            raise VoiceError(f"Audio file not found: {audio_path}")
            
        self._validate_file_size(audio_path)
        
        try:
            # Process and clean the audio
            processed_audio, sr = self._preprocess_audio(audio_path)
            
            # Load model and transcribe
            model = load_whisper_model(self.model_name)
            
            logger.info("Starting transcription...")
            # Whisper expects float32 array in range [-1.0, 1.0] and 16000 Hz
            result = model.transcribe(
                processed_audio,
                fp16=False,
                language="en",
                task="transcribe",
                condition_on_previous_text=False,
                temperature=0,
            )
            
            text = result.get("text", "").strip()
            if not text:
                raise VoiceError("Transcription resulted in empty text.")
                
            return TranscriptionResult(
                text=text,
                language=result.get("language", "en"),
                confidence=self._confidence(result),
                duration_seconds=len(processed_audio) / sr
            )
            
        except VoiceError:
            raise
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise VoiceError(f"Transcription failed: {str(e)}") from e

    def transcribe_bytes(self, audio_bytes: bytes, format: str = "wav") -> TranscriptionResult:
        if len(audio_bytes) > self.max_size_bytes:
            raise VoiceError(f"Audio size exceeds maximum allowed ({self.max_size_bytes / 1024 / 1024} MB)")
            
        # Write bytes to a temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = Path(tmp_file.name)
            
        try:
            return self.transcribe(tmp_path)
        finally:
            # Clean up temp file
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def _validate_file_size(self, path: Path):
        size = path.stat().st_size
        if size > self.max_size_bytes:
            raise VoiceError(f"Audio file too large: {size} bytes. Max allowed is {self.max_size_bytes} bytes.")
            
    def _preprocess_audio(self, path: Path) -> tuple[np.ndarray, int]:
        target_sr = 16000
        
        # Load audio using pydub to handle various formats
        if not AudioSegment:
            raise VoiceError("pydub is not installed. Required for audio format processing.")
            
        try:
            audio_segment = AudioSegment.from_file(str(path))
        except Exception as e:
            raise VoiceError(f"Unsupported audio format or corrupted file: {e}")
            
        # Convert to mono and target sample rate
        audio_segment = audio_segment.set_channels(1).set_frame_rate(target_sr)
        
        # Get raw data as numpy array
        samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        
        # Normalize
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val
            
        # Optional light noise reduction for noisy clips without damaging speech.
        if nr and len(samples) > target_sr:
            logger.info("Applying noise reduction...")
            samples = nr.reduce_noise(y=samples, sr=target_sr, prop_decrease=0.45)
            
        return samples, target_sr

    def _confidence(self, result: dict) -> float:
        segments = result.get("segments") or []
        if not segments:
            return 0.0
        scores: list[float] = []
        for segment in segments:
            avg_logprob = float(segment.get("avg_logprob", -1.0))
            no_speech_prob = float(segment.get("no_speech_prob", 0.0))
            logprob_score = max(0.0, min(1.0, (avg_logprob + 1.0)))
            speech_score = max(0.0, min(1.0, 1.0 - no_speech_prob))
            scores.append((logprob_score + speech_score) / 2)
        return sum(scores) / len(scores)
