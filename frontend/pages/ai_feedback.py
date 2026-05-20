import streamlit as st

from backend.ai.openai_service import (
    get_resume_feedback
)

def show_ai_feedback():

    st.title("AI Resume Feedback")

    resume_text = st.text_area(
        "Paste Resume Text"
    )

    if st.button("Generate AI Feedback"):

        with st.spinner("Analyzing Resume..."):

            feedback = get_resume_feedback(
                resume_text
            )

        st.success("Feedback Generated")

        st.write(feedback)