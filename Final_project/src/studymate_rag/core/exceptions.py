class StudyMateError(Exception):
    """Base application exception."""


class DocumentIngestionError(StudyMateError):
    """Raised when a document cannot be parsed or indexed."""


class RetrievalError(StudyMateError):
    """Raised when retrieval or answer generation fails."""


class SummarizationError(StudyMateError):
    """Raised when summarization fails."""


class VoiceError(StudyMateError):
    """Raised when voice transcription or synthesis fails."""


class LearningEngineError(StudyMateError):
    """Raised when the personalized learning engine encounters an error."""

