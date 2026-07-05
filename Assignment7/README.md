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
- **Modular architecture** – Separate loader, pre‑processor, splitter, embeddings, vector store, retriever, generator, and utils for easy extension and unit testing.
- **Performance‑focused** – Real‑time latency metrics, vector‑store size reporting, and configurable chunk parameters.
- **Groundedness validation** – Automated checks help ensure answers are based on retrieved context, reducing hallucinations.
- **Educational showcase** – Ideal for learning RAG pipelines, prompt engineering, and hybrid search techniques.

---

## 🛠️ Installation & Setup

1. **Clone the repository** (or navigate to the workspace root):
  
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

-

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




# Output 📸 Application Screenshots

The following screenshots demonstrate the key features of the RAG-based Document Question Answering System.
 📂 Documents Hub
<p align="center">
  <img src="https://raw.githubusercontent.com/deorakamlesh07-droid/Celabal_CEI/main/Assignment7/Output/upload%20document.png" alt="Documents Hub" width="900"/>
</p>

 💬 AI Chat Hub
<p align="center">
  <img src="https://raw.githubusercontent.com/deorakamlesh07-droid/Celabal_CEI/main/Assignment7/Output/Ai%20chat%20bot.png" alt="AI Chat Hub" width="900"/>
</p>
📊 Performance Analytics
<p align="center">
  <img src="https://raw.githubusercontent.com/deorakamlesh07-droid/Celabal_CEI/main/Assignment7/Output/Performance%20Analytics.png" alt="Performance Analytics" width="900"/>
</p>
 🧪 Tuning Experiments
<p align="center">
  <img src="https://raw.githubusercontent.com/deorakamlesh07-droid/Celabal_CEI/main/Assignment7/Output/tuning.png" alt="Tuning Experiments" width="900"/>
</p>
 ✅ Validation Center
<p align="center">
  <img src="https://raw.githubusercontent.com/deorakamlesh07-droid/Celabal_CEI/main/Assignment7/Output/validation.png" alt="Validation Center" width="900"/>
</p>

## 🎓 Learning Outcomes
By completing this project, the following concepts and skills were demonstrated:

- Developed a complete **Retrieval-Augmented Generation (RAG)** pipeline from document ingestion to answer generation.
- Implemented document processing for **PDF and TXT** files with automated text extraction and preprocessing.
- Applied **text chunking strategies** using configurable chunk size and overlap to improve retrieval quality.
- Generated semantic embeddings using **Sentence Transformers** and stored them efficiently in a **FAISS** vector database.
- Performed **similarity-based retrieval** to provide relevant context for Large Language Models (LLMs).
- Integrated the **Groq API** with a modern LLM to generate context-aware, grounded responses.
- Designed a modular and scalable architecture with reusable components for loading, preprocessing, embedding, retrieval, and generation.
- Built an interactive **Streamlit** web application with an intuitive user interface for document upload, question answering, analytics, and validation.
- Evaluated system performance using latency measurements, retrieval statistics, and configurable RAG parameters.
- Implemented validation techniques to reduce hallucinations and verify that generated answers are supported by retrieved document context.
- Gained practical experience with **LangChain**, **FAISS**, **Sentence Transformers**, **Prompt Engineering**, and modern **Generative AI** application development.
- Strengthened understanding of end-to-end AI application deployment, modular software engineering, and production-ready RAG system design.

## 👨‍💻 Author

**Kamlesh Deora**
B.Tech CSE (AI & ML)
Celebal Technologies – Data Science Internship (Week 7)
