import streamlit as st
import pandas as pd

def render_learning_dashboard(svc: dict) -> None:
    st.subheader("Personalized Learning Dashboard")
    
    learning_svc = svc["learning"]
    student_id = st.session_state.get("student_id", "default_student")
    
    # 1. Fetch data
    try:
        dash = learning_svc.get_dashboard_data(student_id)
        profile = dash["profile"]
        analytics = dash["analytics"]
        recs = dash["recommendations"]
        goal = dash["daily_goal"]
    except Exception as e:
        st.error(f"Failed to load learning data: {e}")
        return

    # 2. Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 Study Streak", f"{analytics.study_streak} days")
    col2.metric("🎯 Progress Score", f"{analytics.progress_score:.1f}/100")
    col3.metric("🧠 Mastered Topics", len(profile.mastered_concepts))
    col4.metric("⏱️ Today's Mins", f"{goal.completed_minutes:.0f} / {goal.target_minutes}")

    st.divider()

    col_main, col_side = st.columns([2, 1])

    with col_main:
        # Recommendations
        st.markdown("### 💡 Recommended for You")
        if not recs:
            st.info("No recommendations right now. Keep studying!")
        else:
            for rec in recs:
                icon = "📚" if rec.type == "study" else "🔄" if rec.type == "revise" else "📝"
                with st.container():
                    col_r1, col_r2, col_r3 = st.columns([1, 4, 1])
                    col_r1.markdown(f"## {icon}")
                    col_r2.markdown(f"**{rec.topic}** ({rec.type.title()})")
                    col_r2.caption(f"{rec.reason} • Difficulty: {rec.difficulty.title()}")
                    col_r3.button("Start", key=f"btn_{rec.topic}_{rec.type}")
                    st.divider()

        # Analytics Charts
        st.markdown("### 📊 Learning Trend")
        if analytics.daily_minutes:
            df_trend = pd.DataFrame([
                {"Date": k, "Minutes": v} for k, v in analytics.daily_minutes.items()
            ]).sort_values("Date")
            st.line_chart(df_trend, x="Date", y="Minutes", height=200)
        else:
            st.info("Not enough data for trend chart.")

    with col_side:
        # Weak Topics
        st.markdown("### ⚠️ Needs Attention")
        if profile.weak_concepts:
            for topic in profile.weak_concepts:
                st.error(topic)
        else:
            st.success("No weak topics identified yet!")

        st.markdown("### 🏆 Mastered")
        if profile.mastered_concepts:
            for topic in profile.mastered_concepts:
                st.success(topic)
        else:
            st.info("Complete quizzes to master topics.")
            
        st.markdown("### 📝 Log Activity (Manual)")
        with st.form("log_activity"):
            topic = st.text_input("Topic")
            duration = st.number_input("Duration (minutes)", min_value=1, value=15)
            score_col, submit_col = st.columns(2)
            score = score_col.number_input("Quiz Score % (optional)", min_value=0, max_value=100, value=0)
            
            if submit_col.form_submit_button("Log Activity", use_container_width=True):
                if topic:
                    learning_svc.record_study_activity(student_id, topic, duration, "study")
                    if score > 0:
                        learning_svc.record_quiz_result(student_id, topic, score, 100)
                    st.success("Logged!")
                    st.rerun()
                else:
                    st.error("Topic is required.")
