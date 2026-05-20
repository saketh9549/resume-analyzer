import streamlit as st

def show_dashboard():

    st.title("Dashboard")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Resumes",
            "25"
        )

    with col2:
        st.metric(
            "Average ATS Score",
            "78%"
        )

    with col3:
        st.metric(
            "Jobs Matched",
            "14"
        )

    st.markdown("---")

    st.subheader("Project Overview")

    st.write("""
    This AI Resume Analyzer helps users:
    - Analyze resumes
    - Generate ATS scores
    - Match job descriptions
    - Get AI feedback
    - Improve resumes
    """)