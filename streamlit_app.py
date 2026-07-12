import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Data Explorer", layout="wide", page_icon="📊")

if "df" not in st.session_state:
    dates = [datetime.now() - timedelta(days=i) for i in range(99, -1, -1)]
    st.session_state.df = pd.DataFrame({
        "date": dates,
        "sales": np.random.randint(100, 500, 100).cumsum(),
        "users": np.random.randint(50, 200, 100).cumsum(),
        "category": np.random.choice(["A", "B", "C"], 100),
        "region": np.random.choice(["North", "South", "East", "West"], 100),
        "score": np.random.uniform(0, 100, 100).round(1),
    })

page = st.sidebar.radio("Navigation", ["Data Explorer", "Visualizations", "About"])

if page == "Data Explorer":
    st.title("Data Explorer")
    col1, col2, col3, col4 = st.columns(4)
    df = st.session_state.df
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Numeric Cols", len(df.select_dtypes(include=np.number).columns))
    col4.metric("Missing", df.isna().sum().sum())

    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        try:
            st.session_state.df = pd.read_csv(uploaded)
            st.success("File loaded!")
        except Exception as e:
            st.error(f"Error: {e}")

    df = st.session_state.df
    with st.expander("Preview", expanded=True):
        st.dataframe(df, use_container_width=True, height=300)
    with st.expander("Summary Stats"):
        st.dataframe(
            df.describe(include="all").round(2)
            if len(df.select_dtypes(include=np.number).columns) > 0
            else df.describe(include="object"),
            use_container_width=True,
        )

elif page == "Visualizations":
    st.title("Visualizations")
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64", "object"]).columns.tolist()

    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter"])
    x_col = st.selectbox("X axis", date_cols + numeric_cols, index=0)

    if chart_type == "Scatter":
        c1, c2 = st.columns(2)
        y_col = c1.selectbox("Y axis", numeric_cols, index=1)
        color_col = c2.selectbox("Color by", [None] + df.columns.tolist())
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} vs {x_col}")
    elif chart_type == "Bar":
        y_col = st.selectbox("Y axis", numeric_cols, index=0)
        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}", barmode="group")
    else:
        y_cols = st.multiselect("Y columns", numeric_cols, default=numeric_cols[:2])
        fig = px.line(df, x=x_col, y=y_cols, title="Trend")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(df, use_container_width=True, height=200)

else:
    st.title("About")
    st.markdown("""
    **Data Explorer** — a single-page Streamlit app demonstrating:
    - CSV upload / sample data
    - Interactive Plotly charts
    - Data preview & summary stats
    - Session state persistence
    """)
    st.info("Built with Streamlit + Pandas + Plotly")
    st.caption(f"App version 1.0 · {datetime.now().year}")
