import streamlit as st

from frontend.pages.dashboard import show_dashboard
from frontend.pages.upload_resume import show_upload_resume
from frontend.pages.ats_checker import show_ats_checker
from frontend.pages.jd_match import show_jd_match
from frontend.pages.ai_feedback import show_ai_feedback
from frontend.pages.analytics import show_analytics

# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Dashboard",
        "Upload Resume",
        "ATS Checker",
        "JD Match",
        "AI Feedback",
        "Analytics"
    ]
)

# --------------------------------
# PAGE ROUTING
# --------------------------------

if page == "Dashboard":
    show_dashboard()

elif page == "Upload Resume":
    show_upload_resume()

elif page == "ATS Checker":
    show_ats_checker()

elif page == "JD Match":
    show_jd_match()

elif page == "Analytics":
    show_analytics()

try:
    result = analyze_resume(file_path)

except Exception as e:
    st.error(str(e))

