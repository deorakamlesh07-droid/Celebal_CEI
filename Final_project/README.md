# Celebal CEI - StudyMate RAG Final Project

This repository contains my Celebal Excellence Internship work, including weekly assignments and the final project: **StudyMate RAG**, a local-first study assistant for asking questions across uploaded documents and generating learning material such as summaries, flashcards, quizzes, revision notes, and interview prompts.

## Repository Contents

- `Assignment1` to `Assignment8`: Internship assignments and submissions
- `Final_project/src/studymate_rag`: Final project source code
- `Final_project/config`: Runtime YAML configuration
- `Final_project/docs`: Architecture, deployment, and presentation notes
- `Final_project/tests`: Focused unit tests

## StudyMate RAG Highlights

- Multi-document chat with page-aware citations
- PDF and text ingestion with metadata extraction
- Semantic chunking and local vector storage with ChromaDB
- Groq-powered LLM runtime for fast cloud generation
- Local embedding model support through Hugging Face embeddings
- Study tools for flashcards, quizzes, key concepts, revision notes, and interview prompts
- Intelligent summarization with multiple modes and recursive chunk merging for long documents
- Voice interaction using Whisper for speech-to-text and pyttsx3 for offline text-to-speech
- Personalized learning with student profiles, quiz scores, spaced repetition, and adaptive study goals
- Streamlit interface with document management, retrieval settings, chat export, and light/dark support

## Tech Stack

| Area | Choice |
| --- | --- |
| Language | Python |
| App UI | Streamlit |
| RAG Framework | LlamaIndex |
| Vector Store | ChromaDB |
| LLM Provider | Groq |
| Default Model | llama-3.1-8b-instant |
| Embeddings | BAAI/bge-small-en-v1.5 |
| PDF Parsing | PyMuPDF |
| Configuration | `.env` and YAML |
| Testing | pytest |
| Deployment | Docker |
| Voice Recognition | OpenAI Whisper |
| Voice Synthesis | pyttsx3 |

## Project Structure

```text
config/                 Runtime YAML configuration
data/                   Local uploads, vector store, and exports
docs/                   Architecture, deployment, and presentation notes
src/studymate_rag/
  core/                 Settings, logging, shared exceptions
  ingestion/            Document loading and chunking
  embeddings/           Embedding provider factory
  retrieval/            Chroma vector store integration
  llm/                  LLM provider factory
  services/             RAG orchestration, documents, study tools, exports
  summarization/        Intelligent hierarchical summarizer
  voice/                Whisper transcription and TTS
  learning/             Adaptive learning tracking and recommendation
  ui/                   Streamlit application
tests/                  Focused unit tests
```

## How to Run the Project

Follow these steps from the final project folder:

```powershell
cd D:\Dekstop\celebl\Final_Project\Final_project
```

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install project dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

Copy the example environment file:

```powershell
copy .env.example .env
```

Open `.env` and set the values you want to use.

For Groq:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Do not commit `.env`. It is already ignored by git.

### 5. Start the Streamlit app

```powershell
streamlit run run_app.py
```

After the server starts, open the local URL shown in the terminal. Usually it is:

```text
http://localhost:8501
```

## Usage

1. Open the Streamlit app.
2. Upload PDF or text documents from the Documents tab.
3. Index the uploaded documents.
4. Ask questions in Chat and review citations.
5. Generate summaries, flashcards, quizzes, revision notes, key concepts, interview prompts, and suggestions.
6. Export generated content from the available download options.

## Optional Voice Setup

Voice features use Whisper for speech-to-text and `pyttsx3` for text-to-speech.

For better audio file support, install FFmpeg and make sure it is available in your system `PATH`.

```powershell
ffmpeg -version
```

## Testing

```bash
pytest
```

## Docker

```bash
docker build -t studymate-rag .
docker run --rm -p 8501:8501 --env-file .env studymate-rag
```
