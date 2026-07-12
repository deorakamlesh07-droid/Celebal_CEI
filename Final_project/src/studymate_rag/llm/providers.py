from studymate_rag.core.config import Settings


def build_llm(settings: Settings):
    provider = settings.llm_provider.lower().strip()

    if provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("Groq api key is required in .env file.")
        from llama_index.llms.groq import Groq

        return Groq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=settings.llm_temperature,
            timeout=120.0,
        )

    raise ValueError("Unsupported LLM provider. Set LLM_PROVIDER=groq.")
