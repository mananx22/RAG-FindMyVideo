"""Sample Streamlit App — Single Page Dashboard

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Sample Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Controls")
    st.markdown("---")

    chart_type = st.selectbox(
        "Chart type",
        ["Line", "Bar", "Area"],
    )

    n_points = st.slider("Data points", 10, 200, 50, step=10)

    show_raw = st.checkbox("Show raw data", value=False)

    st.markdown("---")
    st.caption(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ── Main area ────────────────────────────────────────────────
st.title("📊 Sample Streamlit Dashboard")
st.markdown("A quick demo of common Streamlit widgets and charts.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📋 Data", "ℹ️ About"])

# ── Tab 1: Chart ─────────────────────────────────────────────
with tab1:
    st.subheader(f"{chart_type} Chart")

    # Generate random time-series data
    dates = [datetime.now() - timedelta(days=i) for i in range(n_points)]
    dates.reverse()
    values = np.cumsum(np.random.randn(n_points)) + 50

    df = pd.DataFrame({"Date": dates, "Value": values})

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest", f"{values[-1]:.1f}", f"{values[-1] - values[-2]:+.1f}")
    col2.metric("Mean", f"{np.mean(values):.1f}")
    col3.metric("Std Dev", f"{np.std(values):.1f}")

    if chart_type == "Line":
        st.line_chart(df, x="Date", y="Value")
    elif chart_type == "Bar":
        st.bar_chart(df, x="Date", y="Value")
    else:
        st.area_chart(df, x="Date", y="Value")

# ── Tab 2: Data ──────────────────────────────────────────────
with tab2:
    st.subheader("Raw Data")

    if show_raw:
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "data.csv",
            "text/csv",
        )
    else:
        st.info("👈 Enable **Show raw data** in the sidebar to see the table.")

    # Interactive filter demo
    st.subheader("Filter Demo")
    filter_val = st.slider("Minimum value", float(df["Value"].min()), float(df["Value"].max()), float(df["Value"].min()))
    filtered = df[df["Value"] >= filter_val]
    st.write(f"Rows above {filter_val:.1f}: **{len(filtered)}** of {len(df)}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ── Tab 3: About ─────────────────────────────────────────────
with tab3:
    st.subheader("About This App")
    st.markdown("""
    This is a minimal **Streamlit** demo showcasing:

    - 📊 **Charts** — line, bar, and area charts via `st.line_chart`, `st.bar_chart`, `st.area_chart`
    - 📋 **DataFrames** — interactive tables with `st.dataframe`
    - 🎛️ **Widgets** — select boxes, sliders, checkboxes, metrics
    - 📑 **Tabs** — organizing content with `st.tabs`
    - ⬇️ **Download** — CSV export button
    - 📐 **Layout** — sidebar, columns, wide mode

    Run it with:
    ```
    streamlit run streamlit_app.py
    ```
    """)

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.caption("Built with ❤️ using Streamlit")
