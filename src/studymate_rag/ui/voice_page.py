import streamlit as st


def render_voice_assistant(svc: dict) -> None:
    st.subheader("Voice Assistant")
    voice_svc = svc["voice"]

    st.session_state.setdefault("voice_transcript", "")
    st.session_state.setdefault("voice_confidence", 0.0)

    col_input, col_settings = st.columns([2, 1])

    with col_input:
        mode = st.radio("Input", ["Upload Audio", "Type Question"], horizontal=True)

        if mode == "Upload Audio":
            audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "ogg", "flac", "webm"])
            if st.button("Transcribe Audio", type="primary", disabled=not audio_file):
                try:
                    ext = audio_file.name.split(".")[-1].lower() if "." in audio_file.name else "wav"
                    with st.spinner("Transcribing with Whisper"):
                        result = voice_svc.transcribe_only(audio_file.getvalue(), format=ext)
                    st.session_state.voice_transcript = result.text
                    st.session_state.voice_confidence = result.confidence
                except Exception as exc:
                    st.error(str(exc))
        else:
            typed = st.text_area("Question", value=st.session_state.voice_transcript, height=120)
            st.session_state.voice_transcript = typed
            st.session_state.voice_confidence = 1.0 if typed.strip() else 0.0

        transcript = st.text_area(
            "Review transcript before asking",
            value=st.session_state.voice_transcript,
            height=120,
            key="voice_transcript_editor",
        )
        st.session_state.voice_transcript = transcript

        confidence = st.session_state.voice_confidence
        if transcript.strip():
            st.caption(f"Transcription confidence: {confidence:.2f}")
            if confidence and confidence < 0.45:
                st.warning("Transcript confidence is low. Edit the transcript before asking for the best answer.")

        ask_btn = st.button("Ask With Reviewed Transcript", disabled=not transcript.strip())

    with col_settings:
        voices = voice_svc.get_available_voices()
        if voices:
            voice_names = [voice["name"] for voice in voices]
            selected_voice = st.selectbox("Voice", voice_names)
            voice_svc.set_voice(voice_names.index(selected_voice))
        else:
            st.info("No TTS voices found on this system.")

        speed = st.slider("Speech Speed", min_value=100, max_value=250, value=175, step=5)
        voice_svc.synthesizer.set_rate(speed)

    if ask_btn:
        with st.status("Answering from indexed documents", expanded=True) as status:
            try:
                response = voice_svc.answer_text_query(
                    st.session_state.voice_transcript,
                    st.session_state.voice_confidence,
                )
                status.update(label="Complete", state="complete")
            except Exception as exc:
                status.update(label="Voice query failed", state="error")
                st.error(str(exc))
                return

        st.markdown("### Answer")
        st.write(response.answer_text)
        if response.citations:
            st.caption("Sources: " + ", ".join(response.citations))

        if response.audio_bytes:
            st.audio(response.audio_bytes, format="audio/wav")
            st.download_button(
                "Download Audio",
                data=response.audio_bytes,
                file_name="answer.wav",
                mime="audio/wav",
            )
        else:
            st.warning("Audio synthesis failed. The text answer is still available.")
