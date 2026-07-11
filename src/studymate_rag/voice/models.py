from typing import Optional
from pydantic import BaseModel, Field

class TranscriptionResult(BaseModel):
    text: str = Field(description="The transcribed text")
    language: str = Field(default="en", description="The detected language")
    confidence: float = Field(default=0.0, description="Confidence score of the transcription (if available)")
    duration_seconds: float = Field(default=0.0, description="Duration of the audio in seconds")

class VoiceResponse(BaseModel):
    answer_text: str = Field(description="The text answer from the LLM")
    audio_bytes: Optional[bytes] = Field(default=None, description="The synthesized audio answer as bytes")
    citations: list[str] = Field(default_factory=list, description="Citations used in the answer")
    transcript: str = Field(default="", description="Final transcript used as the question")
    transcription_confidence: float = Field(default=0.0, description="Estimated transcription confidence")
