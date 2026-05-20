import streamlit as st

from backend.services.resume_service import analyze_resume

def show_upload_resume():

    st.title("Upload Resume")

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file:

        file_path = f"uploads/resumes/{uploaded_file.name}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        result = analyze_resume(file_path)

        st.success("Resume Uploaded Successfully")

        st.markdown("---")

        st.subheader("Extracted Skills")

        st.write(result["skills"])

        st.subheader("Experience")

        st.write(f"{result['experience']} Years")

        st.subheader("Education")

        st.write(result["education"])

        st.subheader("ATS Score")

        st.metric(
            "Score",
            f"{result['ats_score']}%"
        )