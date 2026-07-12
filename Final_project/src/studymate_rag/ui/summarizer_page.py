import streamlit as st
import json

from studymate_rag.summarization.models import SummaryScope, SummaryLevel, SummaryRequest
from studymate_rag.summarization.cache import generate_cache_key
def render_summarizer(svc: dict) -> None:
    from studymate_rag.ui.app import chat_as_text, pdf_download
    st.subheader("Intelligent Summarizer")
    
    docs = svc["documents"].list_documents()
    summary_svc = svc["summarization"]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 1. What to summarize?")
        source = st.radio("Source", ["Entire Document", "Page Range", "Topic Search", "Chat History", "Custom Text"], horizontal=False)
        
        req = SummaryRequest(scope=SummaryScope.ENTIRE_DOCUMENT)
        
        if source == "Entire Document" or source == "Page Range":
            if not docs:
                st.info("Upload a document first.")
                return
            selected = st.selectbox("Document", docs, format_func=lambda path: path.name, key="summarizer_doc_select")
            if selected:
                req.document_name = selected.name
                
            if source == "Entire Document":
                req.scope = SummaryScope.SPECIFIC_DOCUMENT
            else:
                req.scope = SummaryScope.PAGE_RANGE
                col_p1, col_p2 = st.columns(2)
                start = col_p1.number_input("Start Page", min_value=1, value=1)
                end = col_p2.number_input("End Page", min_value=start, value=start+5)
                req.page_range = (start, end)
                
        elif source == "Topic Search":
            req.scope = SummaryScope.TOPIC
            req.topic = st.text_input("Enter topic to search across all documents:")
            if not req.topic:
                st.warning("Please enter a topic.")
                
        elif source == "Chat History":
            req.scope = SummaryScope.ENTIRE_DOCUMENT
            req.text = chat_as_text()
            if not req.text.strip():
                st.info("Ask questions in the Chat tab first.")
                return
                
        else: # Custom Text
            req.scope = SummaryScope.SELECTED_TEXT
            req.text = st.text_area("Paste text to summarize", height=150)
            if not req.text.strip():
                return

    with col2:
        st.markdown("### 2. How to summarize?")
        level_map = {
            "Quick Summary": SummaryLevel.QUICK,
            "1-Minute Revision": SummaryLevel.ONE_MINUTE,
            "5-Minute Revision": SummaryLevel.FIVE_MINUTE,
            "Detailed Analysis": SummaryLevel.DETAILED,
            "Academic Paper": SummaryLevel.ACADEMIC,
            "Executive Summary": SummaryLevel.EXECUTIVE,
            "Bullet Points": SummaryLevel.BULLET,
            "Explain Like I'm 10": SummaryLevel.ELI10,
            "Technical Focus": SummaryLevel.TECHNICAL,
            "Exam Revision": SummaryLevel.EXAM_REVISION
        }
        selected_level = st.selectbox("Summary Style", list(level_map.keys()), index=3)
        req.level = level_map[selected_level]
        
        # Check cache status
        if source == "Custom Text" or source == "Chat History":
            preview_text = req.text
        elif req.document_name:
            preview_text = req.document_name + str(req.page_range) + str(req.topic)
        else:
            preview_text = req.topic or ""
            
        cache_key = generate_cache_key(preview_text, req.level.value, req.scope.value)
        is_cached = summary_svc.cache.has(cache_key)
        
        if is_cached:
            st.success("⚡ Ready instantly (Cached)")
        
        generate = st.button("Generate Summary", type="primary", use_container_width=True)

    if generate:
        if (source == "Topic Search" and not req.topic) or (source == "Custom Text" and not req.text):
            return
            
        with st.status(f"Generating {selected_level}...", expanded=True) as status:
            try:
                result = summary_svc.summarize(req)
                status.update(label="Summary complete!", state="complete")
                
                st.divider()
                st.markdown(f"## {result.title}")
                
                # Metadata tags
                cols = st.columns(4)
                cols[0].metric("Reading Time", f"{result.reading_time_minutes} min")
                cols[1].metric("Word Count", result.word_count)
                cols[2].metric("Difficulty", result.difficulty_level)
                cols[3].metric("Confidence", f"{result.confidence_score*100:.0f}%")
                
                st.markdown("### Summary")
                st.write(result.summary)
                
                if result.key_topics:
                    st.markdown("### Key Topics")
                    st.write(", ".join(f"`{t}`" for t in result.key_topics))
                    
                col_a, col_b = st.columns(2)
                with col_a:
                    if result.definitions:
                        with st.expander("📚 Definitions", expanded=True):
                            for term, dfn in result.definitions.items():
                                st.markdown(f"**{term}**: {dfn}")
                    
                    if result.examples:
                        with st.expander("💡 Examples"):
                            for ex in result.examples:
                                st.markdown(f"- {ex}")
                                
                    if result.formulas:
                        with st.expander("∑ Formulas"):
                            for form in result.formulas:
                                st.markdown(f"`{form}`")
                                
                with col_b:
                    if result.exam_tips:
                        with st.expander("🎯 Exam Tips", expanded=True):
                            for tip in result.exam_tips:
                                st.markdown(f"- {tip}")
                                
                    if result.common_mistakes:
                        with st.expander("⚠️ Common Mistakes"):
                            for mk in result.common_mistakes:
                                st.markdown(f"- {mk}")
                                
                    if result.revision_checklist:
                        with st.expander("✅ Revision Checklist"):
                            for item in result.revision_checklist:
                                st.markdown(f"- [ ] {item}")
                                
                if result.follow_up_questions:
                    st.markdown("### Suggested Follow-up Questions")
                    for q in result.follow_up_questions:
                        st.markdown(f"- {q}")
                
                # Export options
                st.divider()
                md_text = f"# {result.title}\n\n{result.summary}"
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    pdf_download(svc, result.title or "Summary", md_text, "dl-summary")
                with col_dl2:
                    st.download_button("Download Markdown", md_text, file_name="summary.md")
                    
            except Exception as e:
                status.update(label="Error generating summary", state="error")
                st.error(str(e))
