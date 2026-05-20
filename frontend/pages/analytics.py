import streamlit as st
import plotly.express as px

from backend.services.analytics_service import (
    get_skill_data
)

def show_analytics():

    st.title("Resume Analytics")

    df = get_skill_data()

    fig = px.bar(
        df,
        x="skill_name",
        y="count",
        title="Top Skills"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )