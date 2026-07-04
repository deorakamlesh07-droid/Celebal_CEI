# Document Question Answering System (RAG) 🚀

**A modern, domain‑independent Retrieval‑Augmented Generation (RAG) platform** built for the **Week 7 Celebal Technologies Assignment**. This project refactors a domain‑specific AI‑Lawyer demo into a flexible pipeline that can ingest PDFs or text files, chunk and embed them, store vectors locally, and serve answers via a sleek Streamlit UI.

---

## 📚 What Is This Project?

The application demonstrates a **full‑stack RAG workflow**:
1. **Ingestion** – Load PDFs/TXTs, extract raw text, and clean it.
2. **Chunking** – Recursively split documents into configurable character chunks.
3. **Embedding** – Encode chunks with lightweight sentence‑transformers (MiniLM or MPNet).
4. **Vector Store** – Persist embeddings in a FAISS HNSW index for fast similarity search.
5. **Retrieval + Generation** – Retrieve top‑k relevant chunks and feed them to a LLM (Groq DeepSeek‑R1) to generate grounded answers.
6. **Metrics & Validation** – Track latency, index size, and run an automated validation suite that flags hallucinations.

The UI is organized into five interactive tabs:
- **📂 Documents Hub** – Upload files and build the vector index.
- **💬 AI Chat Hub** – Ask natural‑language questions and view source passages.
- **📊 Performance Analytics** – Visualize latency breakdowns and index statistics.
- **🧪 Tuning Experiments** – Compare chunk‑size profiles and embedding models.
- **✅ Validation Center** – Run a ground‑truth test suite and see PASS/FAIL results.

### Why Use This Project?
- **Domain‑agnostic** – No lawyer‑specific terminology; works with any textual corpus (manuals, research papers, policies, etc.).
- **Modular architecture** – Separate loader, pre‑processor, splitter, embeddings, vector store, retriever, generator, and utils for easy extension and unit testing.
- **Performance‑focused** – Real‑time latency metrics, vector‑store size reporting, and configurable chunk parameters.
- **Groundedness validation** – Automated checks help ensure answers are based on retrieved context, reducing hallucinations.
- **Educational showcase** – Ideal for learning RAG pipelines, prompt engineering, and hybrid search techniques.

---

## 🛠️ Installation & Setup

1. **Clone the repository** (or navigate to the workspace root):
   ```bash
   cd d:/Dekstop/rag/lawyer/Week7-RAG
   ```
2. **Create a `.env` file** with your Groq credentials (required for LLM calls):
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. **Install Python dependencies** (Python 3.10+ is required):
   ```bash
   pip install -r requirements.txt
   ```
4. **Optional – Verify the environment** (ensure `torch`, `faiss-cpu`, and `sentence‑transformers` are installed without errors).

---

## ▶️ How to Run the Application

```bash
streamlit run app.py
```

- The command launches a local web server (by default at **http://localhost:8501**).
- Open the URL in a browser. The **Documents Hub** tab is selected by default.
- **Upload** one or more PDF/TXT files, configure chunk size/overlap in the sidebar, and press **Process**.
- Switch to the **AI Chat Hub** tab to ask questions, view retrieved source blocks, and download a PDF report of the conversation.
- Explore the remaining tabs for performance metrics, tuning experiments, and validation results.

---

## 📁 Repository Structure
```
Week7-RAG/
├─ Assignment7/app.py            # Streamlit entry‑point & UI coordination (moved to Assignment7 folder)
├─ requirements.txt            # Python dependencies
├─ README.md                   # ★ This file ★
├─ output/                     # Generated outputs such as screenshots, reports, etc.
└─ modules/
    ├─ loader.py               # Document loading (PDF/TXT)
    ├─ preprocessing.py        # Text cleanup & normalisation
    ├─ splitter.py             # Recursive text splitter & chunk metrics
    ├─ embeddings.py           # Embedding model loader & timing helper
    ├─ vector_store.py         # FAISS index building / loading utilities
    ├─ retriever.py            # Similarity search & hybrid‑search explanation
    ├─ generator.py            # Prompt templates & Groq LLM wrapper
    ├─ metrics.py              # Latency trackers & validation suite
    └─ utils.py                # Logging, PDF report generation, misc helpers
```

---

## 🧪 Quick Experiment Guide

1. **Chunking experiment** – Adjust *Chunk Size* and *Overlap* sliders in the sidebar, then click **Reprocess Chunks**. Observe changes in chunk count and average size under the **Tuning Experiments** tab.
2. **Embedding benchmark** – Switch between MiniLM (384‑dim) and MPNet (768‑dim) in the code to compare index size and encoding speed.
3. **Validation suite** – Press **Run Full System Validation Suite** in the **Validation Center**. The table will display PASS/FAIL for five ground‑truth questions and highlight potential hallucinations.

---

## 📄 License & Attribution

This project is provided for educational purposes under the MIT License. Feel free to adapt the modular components for your own RAG experiments.

---

*Designed by the DeepMind‑Advanced Agentic Coding team for the Celebal Technologies Week 7 assignment.*

## Assignment7/Output 📁

| Name | Last commit message | Last commit date |
|------|----------------------|-------------------|
| Ai chat bot.png | (Add your commit message) | (Add date) |
| Performance Analytics.png | (Add your commit message) | (Add date) |
| tuning.png | (Add your commit message) | (Add date) |
| upload document.png | (Add your commit message) | (Add date) |
| validation.png | (Add your commit message) | (Add date) |

*Place the above screenshots in the `Assignment7/Output` folder of the repository.*
