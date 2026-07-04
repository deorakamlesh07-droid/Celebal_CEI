"""
Rebranded Native Streamlit Application for RAG Pipeline.
Coordinates loaders, retrievers, generators, metrics, and dashboard tabs.
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Disable TensorFlow to avoid Protobuf version mismatch errors
os.environ["USE_TF"] = "0"

# Load environment variables
load_dotenv()

# Import modular layers
from modules.loader import load_documents
from modules.preprocessing import preprocess_documents
from modules.splitter import split_documents, calculate_chunk_metrics, run_chunking_experiments
from modules.embeddings import (
    get_embeddings_model, 
    get_embedding_dimension, 
    get_embedding_model_name, 
    generate_embeddings_with_timing
)
from modules.vector_store import (
    build_vector_store, 
    load_vector_store, 
    get_vector_store_stats, 
    DEFAULT_STORE_DIR
)
from modules.retriever import retrieve_documents, get_hybrid_search_explanation
from modules.generator import generate_answer, DEFAULT_MODEL
from modules.metrics import run_system_validation
from modules.utils import sys_logger, generate_pdf_report

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Intelligence Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set CSS styling for clean margins
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# Create folders if they don't exist
TEMP_DIR = os.path.join("data", "temp_docs")
os.makedirs(TEMP_DIR, exist_ok=True)

# ── Session State Initialisation ──────────────────────────────────────────────
if "user_queries" not in st.session_state:
    st.session_state.user_queries = []
if "ai_responses" not in st.session_state:
    st.session_state.ai_responses = []
if "similarity_scores" not in st.session_state:
    st.session_state.similarity_scores = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "file_stats" not in st.session_state:
    st.session_state.file_stats = []
if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "embedding_model": "MiniLM",
        "embedding_dimension": 384,
        "chunk_size": 512,
        "chunk_overlap": 50,
        "chunks_created": 0,
        "retrieval_time": 0.0,
        "generation_time": 0.0,
        "inference_time": 0.0,
        "llm": DEFAULT_MODEL,
        "top_k": 3
    }
if "pipeline_logs" not in st.session_state:
    st.session_state.pipeline_logs = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []
if "raw_docs" not in st.session_state:
    st.session_state.raw_docs = []
if "validation_results" not in st.session_state:
    st.session_state.validation_results = []

# Synchronize Logger
def add_ui_log(msg: str):
    sys_logger.info(msg)
    st.session_state.pipeline_logs = sys_logger.get_logs().copy()

# Ensure at least one log is shown
if not st.session_state.pipeline_logs:
    add_ui_log("Workspace initialized successfully.")

# ── Sidebar Configurations ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Config Parameters")
    
    st.markdown("### Chunking Parameters")
    st.session_state.metrics["chunk_size"] = st.slider(
        "Chunk Size (chars)",
        min_value=128,
        max_value=2048,
        value=st.session_state.metrics["chunk_size"],
        step=128
    )
    st.session_state.metrics["chunk_overlap"] = st.slider(
        "Overlap Size (chars)",
        min_value=0,
        max_value=250,
        value=st.session_state.metrics["chunk_overlap"],
        step=10
    )
    
    st.markdown("### Retrieval Options")
    st.session_state.metrics["top_k"] = st.slider(
        "Top K Documents",
        min_value=1,
        max_value=10,
        value=st.session_state.metrics["top_k"],
        step=1
    )
    
    st.markdown("---")
    if st.button("⚡ Reprocess Chunks", use_container_width=True):
        if st.session_state.raw_docs:
            with st.spinner("Processing..."):
                add_ui_log("Reprocessing document chunks...")
                cleaned_docs = preprocess_documents(st.session_state.raw_docs)
                chunks = split_documents(
                    cleaned_docs, 
                    chunk_size=st.session_state.metrics["chunk_size"], 
                    chunk_overlap=st.session_state.metrics["chunk_overlap"]
                )
                st.session_state.chunks = chunks
                
                embed_model = get_embeddings_model("MiniLM")
                v_db = build_vector_store(chunks, embed_model, DEFAULT_STORE_DIR)
                st.session_state.vector_store = v_db
                
                st.session_state.metrics["chunks_created"] = len(chunks)
                add_ui_log(f"Database rebuilt successfully. Total chunks: {len(chunks)}.")
                st.success("Database re-indexed!")
                st.rerun()
        else:
            st.warning("No documents loaded to process.")
            
    if st.button("🗑️ Reset Chat History", use_container_width=True):
        st.session_state.user_queries = []
        st.session_state.ai_responses = []
        st.session_state.similarity_scores = []
        add_ui_log("Dialogue history reset.")
        st.success("History cleared!")
        st.rerun()

# ── Title Header ─────────────────────────────────────────────────────────────
st.title("⚡ RAG Intelligence Workspace")
st.caption("Legal Compliance Knowledge Base ingestion, benchmarking, and semantic verification engine.")

# ── Tabs Navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 Documents Hub", 
    "💬 AI Chat Hub", 
    "📊 Performance Analytics", 
    "🧪 Tuning Experiments", 
    "✅ Validation Center"
])

# ── Tab 1: Documents Hub ──────────────────────────────────────────────────────
with tab1:
    st.header("📂 Document Intelligence")
    st.write("Upload raw TXT or PDF documents to build vector database representations.")
    
    uploaded_files = st.file_uploader(
        "Upload compliance files:",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        new_filenames = [f.name for f in uploaded_files]
        if new_filenames != st.session_state.processed_files:
            sys_logger.clear()
            add_ui_log("Loading document...")
            
            file_paths = []
            for f in os.listdir(TEMP_DIR):
                os.remove(os.path.join(TEMP_DIR, f))
            for file in uploaded_files:
                path = os.path.join(TEMP_DIR, file.name)
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                file_paths.append(path)
                
            raw_docs, stats = load_documents(file_paths)
            st.session_state.file_stats = stats
            st.session_state.raw_docs = raw_docs
            st.session_state.processed_files = new_filenames
            add_ui_log(f"Ingested {len(raw_docs)} files.")
            
            add_ui_log("Extracting and cleaning text...")
            cleaned_docs = preprocess_documents(raw_docs)
            add_ui_log("Preprocessing completed successfully.")
            
            add_ui_log("Creating chunks...")
            chunks = split_documents(
                cleaned_docs, 
                chunk_size=st.session_state.metrics["chunk_size"], 
                chunk_overlap=st.session_state.metrics["chunk_overlap"]
            )
            st.session_state.chunks = chunks
            
            add_ui_log("Generating embeddings using sentence-transformers/all-MiniLM-L6-v2...")
            embed_model, embed_time = generate_embeddings_with_timing([c.page_content for c in chunks], "MiniLM")
            
            add_ui_log("Building vector database...")
            v_db = build_vector_store(chunks, embed_model, DEFAULT_STORE_DIR)
            st.session_state.vector_store = v_db
            
            st.session_state.metrics["chunks_created"] = len(chunks)
            st.session_state.metrics["retrieval_time"] = 0.0
            st.session_state.metrics["generation_time"] = 0.0
            st.session_state.metrics["inference_time"] = 0.0
            add_ui_log("Completed successfully.")
            
            st.success("Successfully ingested new documents!")
            st.rerun()

    st.markdown("---")
    st.subheader("📚 Active Documents list")
    
    if st.session_state.file_stats:
        for idx, file in enumerate(st.session_state.file_stats):
            col_name, col_pages, col_tokens, col_status, col_del = st.columns([4, 2, 2, 2, 1])
            with col_name:
                st.markdown(f"📄 **{file['filename']}**")
            with col_pages:
                st.markdown(f"📄 `{file['pages']}` pages")
            with col_tokens:
                tokens = int(file["char_count"] / 4)
                st.markdown(f"🔤 `{tokens:,}` tokens")
            with col_status:
                status_label = "Ready" if "Success" in file["status"] else file["status"]
                if "Success" in file["status"]:
                    st.success(status_label)
                else:
                    st.error(status_label)
            with col_del:
                if st.button("🗑️", key=f"del_doc_{idx}"):
                    filename_to_delete = file["filename"]
                    st.session_state.file_stats = [f for f in st.session_state.file_stats if f["filename"] != filename_to_delete]
                    st.session_state.processed_files = [f for f in st.session_state.processed_files if f != filename_to_delete]
                    st.session_state.raw_docs = [doc for doc in st.session_state.raw_docs if doc.metadata.get("source") != filename_to_delete]
                    
                    if not st.session_state.file_stats:
                        st.session_state.vector_store = None
                        st.session_state.raw_docs = []
                        st.session_state.chunks = []
                        st.session_state.metrics["chunks_created"] = 0
                        add_ui_log(f"Deleted document: {filename_to_delete}. Vector database empty.")
                    else:
                        add_ui_log(f"Deleted document: {filename_to_delete}. Re-indexing remaining docs...")
                        cleaned_docs = preprocess_documents(st.session_state.raw_docs)
                        chunks = split_documents(
                            cleaned_docs, 
                            chunk_size=st.session_state.metrics["chunk_size"], 
                            chunk_overlap=st.session_state.metrics["chunk_overlap"]
                        )
                        st.session_state.chunks = chunks
                        embed_model = get_embeddings_model("MiniLM")
                        v_db = build_vector_store(chunks, embed_model, DEFAULT_STORE_DIR)
                        st.session_state.vector_store = v_db
                        st.session_state.metrics["chunks_created"] = len(chunks)
                        
                    st.rerun()
    else:
        st.info("No active documents loaded. Please upload compliance files above.")

# ── Tab 2: AI Chat Hub ────────────────────────────────────────────────────────
with tab2:
    st.header("💬 AI Chat Workspace")
    st.write("Query the indexed documents and view retrieved similarity source chunks.")
    
    chat_col, source_col = st.columns([3, 2])
    
    with chat_col:
        st.subheader("Dialogue History")
        
        if st.session_state.user_queries:
            for q, a in zip(st.session_state.user_queries, st.session_state.ai_responses):
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a)
        else:
            st.info("Type a query in the chat input block below.")
            
        user_query = st.chat_input("Ask a follow-up question...")
        
        if user_query:
            if not st.session_state.vector_store:
                st.error("Please load and build a document index first!")
            else:
                with st.spinner("Analyzing context & generating response..."):
                    sys_logger.clear()
                    add_ui_log(f"User Query: {user_query}")
                    
                    # Retrieval
                    add_ui_log("Searching vector index...")
                    start_ret = time.time()
                    ret_docs = retrieve_documents(
                        st.session_state.vector_store, 
                        user_query, 
                        k=st.session_state.metrics["top_k"]
                    )
                    ret_time = time.time() - start_ret
                    add_ui_log(f"Context blocks isolation completed in {ret_time:.4f}s.")
                    
                    # Generation
                    add_ui_log(f"Invoking generation engine ({st.session_state.metrics['llm']})...")
                    context = "\n\n".join([doc["content"] for doc in ret_docs])
                    answer, gen_time = generate_answer(user_query, context, prompt_type="Simple")
                    add_ui_log(f"Response compiled in {gen_time:.4f}s.")
                    
                    # Save states
                    st.session_state.user_queries.append(user_query)
                    st.session_state.ai_responses.append(answer)
                    st.session_state.similarity_scores.append(ret_docs[0]["similarity_score"] if ret_docs else 0.0)
                    
                    st.session_state.metrics["retrieval_time"] = ret_time
                    st.session_state.metrics["generation_time"] = gen_time
                    st.session_state.metrics["inference_time"] = ret_time + gen_time
                    add_ui_log("Completed successfully.")
                    
                    st.rerun()
                    
        if st.session_state.user_queries:
            st.markdown("---")
            pdf_bytes = generate_pdf_report(
                user_queries=st.session_state.user_queries,
                ai_responses=st.session_state.ai_responses,
                similarity_scores=st.session_state.similarity_scores,
                metrics=st.session_state.metrics
            )
            st.download_button(
                label="📥 Download Generated PDF Report",
                data=pdf_bytes,
                file_name="Document_QA_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    with source_col:
        st.subheader("🔍 Retrieved Context Blocks")
        if st.session_state.user_queries:
            last_q = st.session_state.user_queries[-1]
            if st.session_state.vector_store:
                last_docs = retrieve_documents(
                    st.session_state.vector_store, 
                    last_q, 
                    k=st.session_state.metrics["top_k"]
                )
                for rank, doc in enumerate(last_docs, 1):
                    score = doc["similarity_score"]
                    with st.expander(f"[Source {rank}] {doc['source']} — Score: {score:.4f}", expanded=(rank == 1)):
                        st.markdown(f"*{doc['content']}*")
                        st.progress(float(score))
                        st.caption(f"Page: {doc['page']} | Groundedness: {score:.1%}")
        else:
            st.info("Ask queries to view context block cards.")

# ── Tab 3: Performance Analytics ──────────────────────────────────────────────
with tab3:
    st.header("📊 Performance Analytics")
    st.write("Real-time telemetry diagnostic metrics detailing latencies, parameters, and database sizes.")
    
    col_inf, col_ret, col_gen = st.columns(3)
    with col_inf:
        st.metric(
            label="Total End-to-End Latency", 
            value=f"{st.session_state.metrics['inference_time']:.4f}s"
        )
    with col_ret:
        st.metric(
            label="Retrieval Latency", 
            value=f"{st.session_state.metrics['retrieval_time']:.4f}s"
        )
    with col_gen:
        st.metric(
            label="LLM Generation Latency", 
            value=f"{st.session_state.metrics['generation_time']:.4f}s"
        )
        
    st.markdown("---")
    st.subheader("Latency Processing Splits")
    if st.session_state.metrics["inference_time"] > 0:
        pct_gen = (st.session_state.metrics["generation_time"] / st.session_state.metrics["inference_time"])
        pct_ret = (st.session_state.metrics["retrieval_time"] / st.session_state.metrics["inference_time"])
        
        st.write(f"**Generation Latency share:** `{pct_gen:.1%}`")
        st.progress(pct_gen)
        
        st.write(f"**Retrieval Latency share:** `{pct_ret:.1%}`")
        st.progress(pct_ret)
    else:
        st.info("Execute user queries in the Chat tab to start logging latency statistics.")
        
    st.markdown("---")
    st.subheader("Vector Infrastructure Details")
    db_stats = get_vector_store_stats(DEFAULT_STORE_DIR)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"**Database:** `FAISS (HNSW Index)`")
        st.markdown(f"**Index File Size:** `{db_stats['formatted_size']}`")
    with col_s2:
        st.markdown(f"**Total Chunks Count:** `{st.session_state.metrics['chunks_created']}`")
        st.markdown(f"**Embedding Model:** `{st.session_state.metrics['embedding_model']}`")
    with col_s3:
        st.markdown(f"**Embedding Dimensions:** `{st.session_state.metrics['embedding_dimension']}`")
        st.markdown(f"**LLM Configuration:** `{st.session_state.metrics['llm']}`")

# ── Tab 4: Tuning Experiments ─────────────────────────────────────────────────
with tab4:
    st.header("🧪 Pipeline Tuning Experiments")
    st.write("Compare parameters and configurations to optimize token density and response accuracy.")
    
    st.subheader("1. Chunking Profiles Comparison")
    if st.session_state.raw_docs:
        with st.spinner("Analyzing alternatives..."):
            exp_results = run_chunking_experiments(st.session_state.raw_docs)
            table_data = []
            for size, data in exp_results.items():
                m = data["metrics"]
                table_data.append({
                    "Target Chunk Size (chars)": size,
                    "Total Chunks": m["chunk_count"],
                    "Avg Chunk Size (chars)": f"{m['avg_chunk_size']:.1f}",
                    "Largest Chunk": m["largest_chunk"],
                    "Smallest Chunk": m["smallest_chunk"]
                })
            st.table(table_data)
    else:
        st.info("Please load active documents to generate parameter simulation data.")
        
    st.markdown("---")
    st.subheader("2. Pre-trained Embedding Benchmarks")
    emb_bench = [
        {"Embedding Model": "sentence-transformers/all-MiniLM-L6-v2", "Dimensions": 384, "Size / 1k Chunks": "1.5 MB", "Precision Score": "High (MTEB: 56.1)"},
        {"Embedding Model": "OpenAI text-embedding-3-small", "Dimensions": 1536, "Size / 1k Chunks": "6.1 MB", "Precision Score": "Premium (MTEB: 62.3)"}
    ]
    st.dataframe(emb_bench, use_container_width=True)

# ── Tab 5: Validation Center ──────────────────────────────────────────────────
with tab5:
    st.header("✅ Validation Center")
    st.write("Run grounding evaluation tests to check context relevance and detect hallucinations.")
    
    if st.button("🚀 Run Full System Validation Suite", use_container_width=True):
        if not st.session_state.vector_store:
            st.error("Vector database is empty. Load documents first.")
        else:
            with st.spinner("Invoking validation suite..."):
                results = run_system_validation(
                    vector_store=st.session_state.vector_store,
                    prompt_type="Simple"
                )
                st.session_state.validation_results = results
                add_ui_log(f"Validation complete. PASS rate: {sum(1 for r in results if r['status'] == 'PASS') / len(results):.1%}")
                st.success("Validation complete!")
                st.rerun()
                
    if st.session_state.validation_results:
        pass_count = sum(1 for r in st.session_state.validation_results if r["status"] == "PASS")
        total_count = len(st.session_state.validation_results)
        pass_rate = pass_count / total_count if total_count > 0 else 0.0
        
        st.subheader(f"Verification Pass Rate: {pass_rate:.1%}")
        
        test_case_records = []
        for idx, res in enumerate(st.session_state.validation_results, 1):
            similarity = res["retrieved_chunks"][0]["similarity_score"] if res["retrieved_chunks"] else 0.0
            test_case_records.append({
                "Test ID": idx,
                "Status": "✅ PASS" if res["status"] == "PASS" else "❌ FAIL",
                "Question": res["question"],
                "Groundedness": f"{similarity:.4f}",
                "Latency": f"{res['latency_sec']*1000:.0f}ms",
                "Answer": res["answer"]
            })
        st.dataframe(test_case_records, use_container_width=True)
    else:
        st.info("Execute verification test suite queries to display PASS/FAIL grounding results.")
        
    st.markdown("---")
    st.subheader("💻 System Trace Console")
    logs_str = "\n".join(st.session_state.pipeline_logs)
    st.code(logs_str, language="bash")
