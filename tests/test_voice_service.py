from unittest.mock import Mock, patch
from pathlib import Path

from studymate_rag.core.exceptions import VoiceError
from studymate_rag.voice.transcriber import WhisperTranscriber
from studymate_rag.voice.voice_service import VoiceService

def test_transcriber_validates_size(tmp_path: Path):
    transcriber = WhisperTranscriber(max_size_mb=1) # 1 MB limit
    
    # Create a dummy file larger than 1MB
    large_file = tmp_path / "large.wav"
    large_file.write_bytes(b"0" * (2 * 1024 * 1024))
    
    try:
        transcriber.transcribe(large_file)
    except VoiceError as e:
        assert "too large" in str(e).lower()
    else:
        raise AssertionError("Expected VoiceError for large file")

def test_transcribe_bytes_size_limit():
    transcriber = WhisperTranscriber(max_size_mb=1)
    
    large_bytes = b"0" * (2 * 1024 * 1024)
    try:
        transcriber.transcribe_bytes(large_bytes)
    except VoiceError as e:
        assert "exceeds maximum allowed" in str(e).lower()
    else:
        raise AssertionError("Expected VoiceError for large bytes")


def test_voice_service_rejects_unclear_question():
    service = VoiceService.__new__(VoiceService)
    try:
        service.answer_text_query("hi")
    except VoiceError as exc:
        assert "too short" in str(exc).lower()
    else:
        raise AssertionError("Expected VoiceError for unclear voice query")


def test_voice_service_uses_reviewed_transcript():
    service = VoiceService.__new__(VoiceService)
    service.rag = Mock()
    service.rag.ask.return_value = Mock(
        answer="Grounded answer",
        citations=[Mock(source="doc.pdf", page=2)],
    )
    service.synthesizer = Mock()
    service.synthesizer.synthesize_to_bytes.return_value = b"audio"

    response = service.answer_text_query("  What does article one say?  ", transcription_confidence=0.8)

    service.rag.ask.assert_called_once_with("What does article one say?")
    assert response.transcript == "What does article one say?"
    assert response.transcription_confidence == 0.8
    assert response.citations == ["doc.pdf p.2"]
