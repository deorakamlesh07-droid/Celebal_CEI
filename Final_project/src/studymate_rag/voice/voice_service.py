import logging
from pathlib import Path

from studymate_rag.core.config import Settings
from studymate_rag.core.exceptions import VoiceError
from studymate_rag.services.rag_service import RagService
from studymate_rag.voice.models import VoiceResponse, TranscriptionResult
from studymate_rag.voice.transcriber import WhisperTranscriber
from studymate_rag.voice.synthesizer import TTSSynthesizer

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self, settings: Settings, rag_service: RagService):
        self.settings = settings
        self.rag = rag_service
        self.transcriber = WhisperTranscriber(
            model_name=settings.whisper_model,
            max_size_mb=settings.max_audio_size_mb
        )
        self.synthesizer = TTSSynthesizer(rate=settings.tts_rate)

    def process_voice_query(self, audio_bytes: bytes, format: str = "wav") -> VoiceResponse:
        """End-to-end: Transcribe -> RAG Ask -> Synthesize -> Return Text + Audio"""
        logger.info("Starting voice query pipeline")
        
        # 1. Transcribe
        transcription = self.transcriber.transcribe_bytes(audio_bytes, format)
        logger.info(f"Transcribed (Confidence: {transcription.confidence:.2f}): {transcription.text}")
        return self.answer_text_query(transcription.text, transcription.confidence)

    def answer_text_query(self, question: str, transcription_confidence: float = 1.0) -> VoiceResponse:
        cleaned_question = " ".join(question.split())
        if len(cleaned_question.split()) < 3:
            raise VoiceError("The question is too short or unclear. Please record again or edit the transcript.")

        try:
            rag_answer = self.rag.ask(cleaned_question)
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise VoiceError(f"Failed to generate answer for voice query: {e}")

        logger.info("Synthesizing answer to audio")
        try:
            audio_response_bytes = self.synthesizer.synthesize_to_bytes(rag_answer.answer)
        except Exception as e:
            logger.warning(f"Audio synthesis failed, returning text only: {e}")
            audio_response_bytes = None
        citations = [f"{c.source} p.{c.page}" for c in rag_answer.citations]
        
        return VoiceResponse(
            answer_text=rag_answer.answer,
            audio_bytes=audio_response_bytes,
            citations=citations,
            transcript=cleaned_question,
            transcription_confidence=transcription_confidence,
        )

    def process_uploaded_audio(self, path: Path) -> VoiceResponse:
        """End-to-end pipeline from a saved file"""
        logger.info(f"Starting voice query from file: {path}")
        
        transcription = self.transcriber.transcribe(path)
        logger.info(f"Transcribed: {transcription.text}")
        
        return self.answer_text_query(transcription.text, transcription.confidence)

    def transcribe_only(self, audio_bytes: bytes, format: str = "wav") -> TranscriptionResult:
        """Just transcribe the audio without RAG or TTS"""
        return self.transcriber.transcribe_bytes(audio_bytes, format)

    def speak_only(self, text: str) -> bytes:
        """Just synthesize the text to audio bytes"""
        return self.synthesizer.synthesize_to_bytes(text)
        
    def set_voice(self, index: int) -> None:
        """Change the TTS voice"""
        self.synthesizer.set_voice(index)
        
    def get_available_voices(self) -> list[dict]:
        """Get list of available TTS voices"""
        return self.synthesizer.list_voices()
