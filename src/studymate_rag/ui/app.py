import os
from html import escape
from pathlib import Path

import streamlit as st

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

from studymate_rag.core.config import get_settings
from studymate_rag.core.logging import configure_logging
from studymate_rag.services.document_service import DocumentService
from studymate_rag.services.export_service import ExportService
from studymate_rag.services.rag_service import RagService
from studymate_rag.services.study_service import StudyService

from studymate_rag.summarization.summary_service import SummaryService
from studymate_rag.voice.voice_service import VoiceService
from studymate_rag.learning.learning_service import LearningService

from studymate_rag.ui.summarizer_page import render_summarizer
from studymate_rag.ui.voice_page import render_voice_assistant
from studymate_rag.ui.learning_page import render_learning_dashboard


st.set_page_config(page_title="StudyMate RAG", layout="wide")
configure_logging()


def apply_design_system() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --surface: #f7f9fb;
            --surface-lowest: #ffffff;
            --surface-low: #f2f4f6;
            --surface-container: #eceef0;
            --outline: #c7c4d8;
            --outline-soft: #e2e8f0;
            --text: #191c1e;
            --muted: #464555;
            --primary: #3525cd;
            --primary-soft: #e2dfff;
            --secondary: #505f76;
            --error-soft: #ffdad6;
            --error: #93000a;
        }

        html, body, [class*="css"] {
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
            background: var(--surface);
            color: var(--text);
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .main,
        .block-container,
        iframe,
        iframe:focus,
        div:focus {
            border-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }

        .block-container {
            max-width: 1280px;
            padding: 0 32px 32px;
        }

        h1 {
            font-size: 36px !important;
            line-height: 44px !important;
            letter-spacing: 0 !important;
            font-weight: 700 !important;
            color: var(--text);
        }

        h2, h3 {
            letter-spacing: 0 !important;
            color: var(--text);
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: 1.4rem;
            border-bottom: 1px solid var(--outline-soft);
            background: var(--surface);
            position: sticky;
            top: 0;
            z-index: 9;
            padding-top: .25rem;
        }

        [data-testid="stTabs"] [role="tab"] {
            border-radius: 0;
            padding: .75rem .1rem .65rem;
            color: var(--secondary);
            font-size: 13px;
            font-weight: 600;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
        }

        .sm-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            height: 64px;
            border-bottom: 1px solid var(--outline-soft);
            margin-bottom: 0;
            background: var(--surface);
        }

        .sm-brand {
            font-size: 36px;
            line-height: 44px;
            font-weight: 800;
            color: var(--primary);
        }

        .sm-status-row {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .sm-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid var(--outline-soft);
            background: var(--surface-low);
            color: var(--muted);
            border-radius: 4px;
            padding: 5px 9px;
            font-size: 12px;
            line-height: 16px;
            font-weight: 600;
        }

        .sm-chip-primary {
            background: var(--primary-soft);
            color: var(--primary);
            border-color: #c3c0ff;
        }

        .sm-hero {
            max-width: 720px;
            margin: 28px 0 24px;
        }

        .sm-hero p {
            font-size: 16px;
            line-height: 26px;
            color: var(--muted);
            margin-top: 6px;
        }

        .sm-panel {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid var(--outline-soft);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }

        .sm-toolbar {
            min-height: 48px;
            border: 1px solid var(--outline-soft);
            background: var(--surface-low);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }

        .sm-two-pane {
            border: 1px solid var(--outline-soft);
            background: #fff;
            border-radius: 8px;
            padding: 16px;
        }

        .sm-panel-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 14px;
            font-weight: 700;
        }

        .sm-muted {
            color: var(--muted);
            font-size: 13px;
            line-height: 20px;
        }

        .sm-doc-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 12px 0;
            border-top: 1px solid var(--outline-soft);
        }

        .sm-doc-icon {
            width: 38px;
            height: 38px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--error-soft);
            color: var(--error);
            font-weight: 800;
            font-size: 12px;
        }

        .sm-ai-block {
            border-left: 4px solid var(--primary);
            background: rgba(226, 223, 255, .45);
            border-radius: 0 8px 8px 0;
            padding: 14px 16px;
            margin: 12px 0 16px;
        }

        div[data-testid="stMetric"] {
            background: var(--surface-lowest);
            border: 1px solid var(--outline-soft);
            border-radius: 6px;
            padding: 12px;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            border-radius: 4px !important;
            font-weight: 700 !important;
            border: 1px solid var(--primary) !important;
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: var(--primary) !important;
            color: #fff !important;
        }

        [data-testid="stFileUploader"] {
            background: var(--surface-low);
            border: 2px dashed var(--outline);
            border-radius: 8px;
            padding: 14px;
        }

        [data-testid="stChatMessage"] {
            border: 1px solid var(--outline-soft);
            border-radius: 8px;
            background: var(--surface-lowest);
        }

        hr {
            border-color: var(--outline-soft);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def services():
    settings = get_settings()
    rag = RagService(settings)
    documents = DocumentService(settings)
    return {
        "settings": settings,
        "documents": documents,
        "rag": rag,
        "study": StudyService(),
        "export": ExportService(settings),
        "summarization": SummaryService(settings, rag, documents),
        "voice": VoiceService(settings, rag),
        "learning": LearningService(settings),
    }


def init_state() -> None:
    st.session_state.setdefault("chat", [])
    st.session_state.setdefault("study_text", "")


def provider_label(svc: dict) -> tuple[str, str]:
    settings = svc["settings"]
    provider = settings.llm_provider.lower()
    return provider, settings.groq_model


def safe_html(value: object) -> str:
    return escape(str(value), quote=True)


def render_topbar(svc: dict) -> None:
    provider, model = provider_label(svc)
    embedding = Path(svc["settings"].embed_model).name
    chunk_count = svc["rag"].index.count()
    st.markdown(
        f"""
        <div class="sm-topbar">
            <div class="sm-brand">StudyMate RAG</div>
            <div class="sm-status-row">
                <span class="sm-chip sm-chip-primary">LLM: {safe_html(provider)} / {safe_html(model)}</span>
                <span class="sm-chip">Embedding: {safe_html(embedding)}</span>
                <span class="sm-chip">Chunks: {chunk_count}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_ingestion(svc: dict) -> None:
    st.markdown(
        """
        <div class="sm-panel-title">
            <span>Document Ingestion</span>
            <span>
                <span class="sm-chip">PDF</span>
                <span class="sm-chip">TXT</span>
                <span class="sm-chip">Markdown</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploads = st.file_uploader(
        "Upload PDFs or text files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploads and st.button("Save and index", type="primary"):
        with st.status("Indexing documents", expanded=True) as status:
            total = 0
            for upload in uploads:
                path = svc["documents"].save_upload(upload.name, upload.getvalue())
                count = svc["rag"].index_document(path)
                total += count
                st.write(f"{upload.name}: {count} chunks")
            status.update(label=f"Indexed {total} chunks", state="complete")


def render_document_list(svc: dict) -> None:
    docs = svc["documents"].list_documents()
    if not docs:
        st.info("Upload source documents to start building the study knowledge base.")
        return

    st.markdown(
        f"""
        <div class="sm-panel-title">
            <span>Local Knowledge Graph</span>
            <span class="sm-chip sm-chip-primary">{len(docs)} Documents Ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for path in docs:
        suffix = safe_html((path.suffix.replace(".", "").upper() or "DOC")[:3])
        file_name = safe_html(path.name)
        file_size = path.stat().st_size / 1024
        st.markdown(
            f"""
            <div class="sm-doc-row">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span class="sm-doc-icon">{suffix}</span>
                    <div>
                        <div style="font-weight:700;">{file_name}</div>
                        <div class="sm-muted">{file_size:.1f} KB saved locally</div>
                    </div>
                </div>
                <span class="sm-chip">Ready</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_home(svc: dict) -> None:
    docs = svc["documents"].list_documents()
    provider, model = provider_label(svc)
    embedding = Path(svc["settings"].embed_model).name
    st.markdown(
        """
        <div class="sm-hero">
            <h1>StudyMate RAG: Your Document-Grounded AI Assistant</h1>
            <p>Upload study documents, index them into a local knowledge base, then chat, summarize, quiz, revise, and export grounded study material.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1], gap="large")
    with left:
        st.markdown('<div class="sm-panel">', unsafe_allow_html=True)
        render_document_ingestion(svc)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sm-panel">', unsafe_allow_html=True)
        render_document_list(svc)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            f"""
            <div class="sm-panel">
                <div class="sm-panel-title"><span>System Parameters</span></div>
                <div class="sm-doc-row"><span>Active LLM</span><span class="sm-chip sm-chip-primary">{safe_html(provider)} / {safe_html(model)}</span></div>
                <div class="sm-doc-row"><span>Embedding</span><span class="sm-chip">{safe_html(embedding)}</span></div>
                <div class="sm-doc-row"><span>Status</span><span class="sm-chip sm-chip-primary">Idle</span></div>
            </div>
            <div class="sm-panel">
                <div class="sm-panel-title"><span>Total Corpus Stats</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        metric_a, metric_b = st.columns(2)
        metric_a.metric("Vector Chunks", svc["rag"].index.count())
        metric_b.metric("Sources", len(docs))
        st.markdown(
            """
            <div class="sm-ai-block">
                <strong>RAG Context Optimization</strong>
                <div class="sm-muted">Documents are segmented into semantic chunks for cited retrieval and study workflows.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_chat(svc: dict) -> None:
    st.markdown('<div class="sm-hero"><h1>Chat</h1><p>Ask document-grounded questions and review page-level citations.</p></div>', unsafe_allow_html=True)
    chat_text = chat_as_text()
    st.markdown('<div class="sm-toolbar"><strong>Current Session: Document Research</strong><span class="sm-chip sm-chip-primary">RAG enabled</span></div>', unsafe_allow_html=True)
    chat_left, chat_right = st.columns([3, 1], gap="large")

    with chat_right:
        st.markdown('<div class="sm-panel-title"><span>Retrieval Settings</span></div>', unsafe_allow_html=True)
        top_k = st.slider("Retrieved chunks", 2, 10, svc["settings"].top_k)
        docs = svc["documents"].list_documents()
        st.metric("Documents", len(docs))
        st.metric("Indexed Chunks", svc["rag"].index.count())
        if chat_text:
            st.download_button(
                "Download Chat PDF",
                data=svc["export"].pdf_bytes("StudyMate Chat", chat_text),
                file_name="studymate-chat.pdf",
                mime="application/pdf",
            )

    with chat_left:
        if not st.session_state.chat:
            st.info("Ask your first question about your documents.")
        for message in st.session_state.chat:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message.get("citations"):
                    st.caption("Sources: " + ", ".join(message["citations"]))

    question = st.chat_input("Ask a question about your documents")
    if not question:
        return

    st.session_state.chat.append({"role": "user", "content": question})
    with st.spinner("Retrieving and answering"):
        answer = svc["rag"].ask(question, top_k=top_k)
    citation_labels = [f"{c.source} p.{c.page}" for c in answer.citations]
    st.session_state.chat.append(
        {"role": "assistant", "content": answer.answer, "citations": citation_labels}
    )
    st.rerun()


def chat_as_text() -> str:
    lines: list[str] = []
    for item in st.session_state.chat:
        lines.append(f"{item['role'].title()}: {item['content']}")
        if item.get("citations"):
            lines.append("Sources: " + ", ".join(item["citations"]))
    return "\n\n".join(lines)


def document_text(svc: dict, path: Path) -> str:
    pages = svc["documents"].loader.load(path)
    return "\n\n".join(f"{page.source_name} page {page.page_number}\n{page.text}" for page in pages)


def pdf_download(svc: dict, title: str, body: str, key: str) -> None:
    st.download_button(
        f"Download {title} PDF",
        data=svc["export"].pdf_bytes(title, body),
        file_name=f"{title.lower().replace(' ', '-')}.pdf",
        mime="application/pdf",
        key=key,
    )


def render_study_tools(svc: dict) -> None:
    st.markdown('<div class="sm-hero"><h1>Study Tools</h1><p>Turn uploaded documents, chat history, or custom notes into revision material.</p></div>', unsafe_allow_html=True)
    docs = svc["documents"].list_documents()
    source = st.radio("Source", ["Uploaded Document", "Chat History", "Custom Text"], horizontal=True)

    text = ""
    if source == "Uploaded Document":
        if not docs:
            st.info("Upload a document first, then return here to generate study material.")
            return
        selected = st.selectbox("Document", docs, format_func=lambda path: path.name, key="study_tools_doc_select")
        if selected:
            text = document_text(svc, selected)
    elif source == "Chat History":
        text = chat_as_text()
        if not text.strip():
            st.info("Ask at least one chat question before using chat history as study material.")
            return
    else:
        st.session_state.study_text = st.text_area(
            "Paste text or notes",
            value=st.session_state.study_text,
            height=180,
        )
        text = st.session_state.study_text

    tool = st.radio(
        "Tool",
        ["Summary", "Flashcards", "Quiz", "Revision Notes", "Key Concepts", "Interview Mode", "Suggestions"],
        index=0,
        horizontal=True,
    )
    if not text.strip():
        st.info("Add text to generate study material.")
        return

    study = svc["study"]
    if tool == "Summary":
        result = study.summarize(text)
        st.write(result)
        pdf_download(svc, "Summary", result, "download-summary")
    elif tool == "Flashcards":
        cards = study.flashcards(text)
        result = "\n\n".join(f"Q: {card.front}\nA: {card.back}" for card in cards)
        for card in cards:
            with st.expander(card.front):
                st.write(card.back)
        pdf_download(svc, "Flashcards", result, "download-flashcards")
    elif tool == "Quiz":
        quiz = study.quiz(text)
        result = "\n\n".join(f"Q: {item.question}\nA: {item.answer}" for item in quiz)
        for item in quiz:
            st.write(f"**Q:** {item.question}")
            st.caption(f"Answer: {item.answer}")
            if item.source:
                st.caption(f"Source fact: {item.source}")
        pdf_download(svc, "Quiz", result, "download-quiz")
    elif tool == "Revision Notes":
        result = "\n".join(study.revision_notes(text))
        st.markdown(result)
        pdf_download(svc, "Revision Notes", result, "download-revision-notes")
    elif tool == "Key Concepts":
        result = "\n".join(f"- {concept}" for concept in study.key_concepts(text))
        st.markdown(result)
        pdf_download(svc, "Key Concepts", result, "download-key-concepts")
    elif tool == "Interview Mode":
        prompts = study.interview_prompts(text)
        result = "\n".join(f"- {prompt}" for prompt in prompts)
        for prompt in prompts:
            st.write(prompt)
        pdf_download(svc, "Interview Mode", result, "download-interview-mode")
    else:
        suggestions = study.suggestions(text)
        result = "\n".join(f"- {suggestion}" for suggestion in suggestions)
        for suggestion in suggestions:
            st.write(f"- {suggestion}")
        pdf_download(svc, "Suggestions", result, "download-suggestions")


def render_exports(svc: dict) -> None:
    st.markdown('<div class="sm-hero"><h1>Export</h1><p>Download chat notes and generated study material for revision.</p></div>', unsafe_allow_html=True)
    chat_text = chat_as_text()
    notes = st.text_area("Notes to export", value=chat_text, height=220)
    col_md, col_pdf = st.columns(2)
    if col_md.button("Export Markdown"):
        path = svc["export"].export_markdown("StudyMate Notes", notes)
        st.success(f"Exported to {path}")
    with col_pdf:
        if notes.strip():
            pdf_download(svc, "StudyMate Notes", notes, "download-notes-pdf")


def main() -> None:
    init_state()
    svc = services()
    apply_design_system()
    render_topbar(svc)

    tab_home, tab_chat, tab_study, tab_sum, tab_voice, tab_learn, tab_export = st.tabs([
        "Home", "Chat", "Tools", "Summarizer", "Voice", "Dashboard", "Export"
    ])
    with tab_home:
        render_home(svc)
    with tab_chat:
        render_chat(svc)
    with tab_study:
        render_study_tools(svc)
    with tab_sum:
        render_summarizer(svc)
    with tab_voice:
        render_voice_assistant(svc)
    with tab_learn:
        render_learning_dashboard(svc)
    with tab_export:
        render_exports(svc)


if __name__ == "__main__":
    main()
