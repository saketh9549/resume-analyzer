import streamlit as st

def show_ats_checker():

    st.title("ATS Score Checker")

    st.info("""
    ATS score measures how well your resume
    matches recruiter systems.
    """)

    st.metric(
        "Current ATS Benchmark",
        "75%"
    )

    st.progress(75)