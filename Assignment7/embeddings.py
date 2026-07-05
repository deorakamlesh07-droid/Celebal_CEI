"""
Embeddings Module.
Manages HuggingFaceEmbeddings models, calculates model dimensions, and measures timing.
"""

import os
os.environ["USE_TF"] = "0"

import time
from typing import Dict, Any, Tuple, List

from langchain_huggingface import HuggingFaceEmbeddings

# Predefined configurations for supported embedding models
MODEL_CONFIGS = {
    "MiniLM": {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384
    },
    "MPNet": {
        "model_name": "sentence-transformers/all-mpnet-base-v2",
        "dimension": 768
    }
}

def get_embeddings_model(model_key: str = "MiniLM") -> HuggingFaceEmbeddings:
    """
    Returns the instantiated HuggingFaceEmbeddings object for a given key.
    """
    config = MODEL_CONFIGS.get(model_key, MODEL_CONFIGS["MiniLM"])
    return HuggingFaceEmbeddings(
        model_name=config["model_name"],
        model_kwargs={'device': 'cpu'}
    )

def get_embedding_dimension(model_key: str = "MiniLM") -> int:
    """
    Returns the numeric vector dimension size for the selected model.
    """
    config = MODEL_CONFIGS.get(model_key, MODEL_CONFIGS["MiniLM"])
    return config["dimension"]

def get_embedding_model_name(model_key: str = "MiniLM") -> str:
    """
    Returns the model path or repository name for display.
    """
    config = MODEL_CONFIGS.get(model_key, MODEL_CONFIGS["MiniLM"])
    return config["model_name"]

def generate_embeddings_with_timing(
    texts: List[str], 
    model_key: str = "MiniLM"
) -> Tuple[HuggingFaceEmbeddings, float]:
    """
    Measures the execution time to load the embedding model and vectorise texts.
    Returns the model object and execution time in seconds.
    """
    start_time = time.time()
    embeddings = get_embeddings_model(model_key)
    # Perform a single vectorisation sample to trigger execution trace
    if texts:
        embeddings.embed_documents(texts[:1])
    generation_time = time.time() - start_time
    return embeddings, generation_time
