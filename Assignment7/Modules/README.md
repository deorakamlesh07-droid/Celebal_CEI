## 📦 Modules Overview

The project follows a modular architecture where each Python module is responsible for a specific stage of the RAG pipeline.

| Module | Description |
|---------|-------------|
| **loader.py** | Loads and extracts text from PDF and TXT documents for processing. |
| **preprocessing.py** | Cleans, normalizes, and prepares extracted text before chunking. |
| **splitter.py** | Splits documents into configurable text chunks with overlap for efficient retrieval. |
| **embeddings.py** | Generates semantic vector embeddings using Sentence Transformers. |
| **vector_store.py** | Creates, saves, and loads the FAISS vector database for similarity search. |
| **retriever.py** | Retrieves the most relevant document chunks based on user queries. |
| **generator.py** | Sends retrieved context to the LLM and generates grounded responses using the Groq API. |
| **metrics.py** | Tracks system performance, retrieval metrics, latency, and validation results. |
| **utils.py** | Provides helper utilities such as logging, PDF report generation, and common helper functions. |

> **Note:** The modular design improves readability, maintainability, scalability, and allows each component of the RAG pipeline to be developed, tested, and extended independently.
