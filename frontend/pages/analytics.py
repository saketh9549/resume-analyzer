import streamlit as st
import pandas as pd

def show_analytics():

    st.title("Resume Analytics")

    data = pd.DataFrame({
        "Category": [
            "Python",
            "SQL",
            "AWS",
            "Docker"
        ],
        "Count": [20, 15, 10, 12]
    })

    st.bar_chart(
        data.set_index("Category")
    )