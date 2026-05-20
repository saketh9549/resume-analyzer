import streamlit as st

from backend.matching.jd_matcher import match_job_description

def show_jd_match():

    st.title("Job Description Matching")

    resume_text = st.text_area(
        "Paste Resume Text"
    )

    job_description = st.text_area(
        "Paste Job Description"
    )

    if st.button("Match Resume"):

        score = match_job_description(
            resume_text,
            job_description
        )

        st.success("Matching Complete")

        st.metric(
            "Match Percentage",
            f"{score}%"
        )