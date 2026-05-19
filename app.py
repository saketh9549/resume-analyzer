"""
Resume Analyzer Main Application
"""
import streamlit as st

def main():
    st.set_page_config(
        page_title="Resume Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("Resume Analyzer")
    st.write("Welcome to the Resume Analyzer application")

if __name__ == "__main__":
    main()
