import streamlit as st
from data import query_data
import plotly.express as px
import argparse

def display(db_file: str):
    df = query_data(db_file)
    fig = px.line(
        df,
        x="time_week",
        y="num_items",
        color="project_name",
    )
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Tasks Completed",
        legend_title="Project"
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-file")
    args = parser.parse_args()
    st.set_page_config(layout="wide")
    st.title("Todoist Tasks")
    display(args.db_file)

if __name__ == "__main__":
    main()
