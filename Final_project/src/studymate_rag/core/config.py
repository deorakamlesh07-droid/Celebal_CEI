from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("StudyMate RAG", alias="APP_NAME")
    app_env: str = Field("local", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    llm_provider: str = Field("groq", alias="LLM_PROVIDER")
    groq_api_key: str = Field("", alias="GROQ_API_KEY")
    groq_model: str = Field("llama-3.1-8b-instant", alias="GROQ_MODEL")
    llm_temperature: float = Field(0.2, alias="LLM_TEMPERATURE")

    embed_model: str = Field("BAAI/bge-small-en-v1.5", alias="EMBED_MODEL")
    vector_db_path: Path = Field(Path("data/vector_store"), alias="VECTOR_DB_PATH")
    upload_dir: Path = Field(Path("data/uploads"), alias="UPLOAD_DIR")
    export_dir: Path = Field(Path("data/exports"), alias="EXPORT_DIR")

    chunk_size: int = Field(900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(140, alias="CHUNK_OVERLAP")
    top_k: int = Field(5, alias="TOP_K")
    similarity_cutoff: float = Field(0.35, alias="SIMILARITY_CUTOFF")

    summary_cache_dir: Path = Field(Path("data/summary_cache"), alias="SUMMARY_CACHE_DIR")
    learning_data_dir: Path = Field(Path("data/learning"), alias="LEARNING_DATA_DIR")
    audio_dir: Path = Field(Path("data/audio"), alias="AUDIO_DIR")
    whisper_model: str = Field("base", alias="WHISPER_MODEL")
    tts_rate: int = Field(175, alias="TTS_RATE")
    max_recording_seconds: int = Field(120, alias="MAX_RECORDING_SECONDS")
    max_audio_size_mb: int = Field(25, alias="MAX_AUDIO_SIZE_MB")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def ensure_dirs(self) -> None:
        for path in (self.vector_db_path, self.upload_dir, self.export_dir, self.summary_cache_dir, self.learning_data_dir, self.audio_dir):
            path.mkdir(parents=True, exist_ok=True)


def _load_yaml_defaults(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return {
        "APP_NAME": raw.get("app", {}).get("name"),
        "APP_ENV": raw.get("app", {}).get("environment"),
        "LOG_LEVEL": raw.get("app", {}).get("log_level"),
        "UPLOAD_DIR": raw.get("paths", {}).get("upload_dir"),
        "VECTOR_DB_PATH": raw.get("paths", {}).get("vector_db_path"),
        "EXPORT_DIR": raw.get("paths", {}).get("export_dir"),
        "CHUNK_SIZE": raw.get("rag", {}).get("chunk_size"),
        "CHUNK_OVERLAP": raw.get("rag", {}).get("chunk_overlap"),
        "TOP_K": raw.get("rag", {}).get("top_k"),
        "SIMILARITY_CUTOFF": raw.get("rag", {}).get("similarity_cutoff"),
        "LLM_PROVIDER": raw.get("llm", {}).get("provider"),
        "GROQ_MODEL": raw.get("llm", {}).get("groq_model"),
        "LLM_TEMPERATURE": raw.get("llm", {}).get("temperature"),
        "EMBED_MODEL": raw.get("embeddings", {}).get("model_name"),
        "SUMMARY_CACHE_DIR": raw.get("paths", {}).get("summary_cache_dir"),
        "LEARNING_DATA_DIR": raw.get("paths", {}).get("learning_data_dir"),
        "AUDIO_DIR": raw.get("paths", {}).get("audio_dir"),
        "WHISPER_MODEL": raw.get("voice", {}).get("whisper_model"),
        "TTS_RATE": raw.get("voice", {}).get("tts_rate"),
        "MAX_RECORDING_SECONDS": raw.get("voice", {}).get("max_recording_seconds"),
        "MAX_AUDIO_SIZE_MB": raw.get("voice", {}).get("max_audio_size_mb"),
    }


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    defaults = {
        k: v
        for k, v in _load_yaml_defaults(Path("config/settings.yaml")).items()
        if v is not None and k not in os.environ
    }
    settings = Settings(**defaults)
    settings.ensure_dirs()
    return settings
