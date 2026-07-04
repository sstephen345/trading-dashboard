import streamlit as st
import pandas as pd
from strategy.baseline_v1 import run_baseline_v1

st.set_page_config(page_title="Daily Statistics", page_icon="📅")

st.title("📅 Daily Statistics")
st.write("Upload Excel and view one-row-per-day performance.")

uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    summary, trade_log = run_baseline_v1(df)

    st.success("✅ Baseline V1.0 completed")

    daily = trade_log.copy()
    daily["equity"] = daily["points"].cumsum()
    daily["drawdown"] = daily["equity"] - daily["equity"].cummax()

    daily_display = daily[
        [
            "date",
            "type",
            "entry_time",
            "exit_time",
            "result",
            "points",
            "equity",
            "drawdown",
        ]
    ].copy()

    daily_display.columns = [
        "Date",
        "Trade",
        "Entry Time",
        "Exit Time",
        "Result",
        "Points",
        "Running Equity",
        "Drawdown",
    ]

    st.subheader("📊 Daily Performance")

    col1, col2 = st.columns(2)
    col1.metric("Trading Days", len(daily_display))
    col2.metric("Net Points", round(daily_display["Points"].sum(), 2))

    col3, col4 = st.columns(2)
    col3.metric("Best Day", round(daily_display["Points"].max(), 2))
    col4.metric("Worst Day", round(daily_display["Points"].min(), 2))

    st.dataframe(
        daily_display,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("📈 Daily Equity Curve")
    st.line_chart(daily_display["Running Equity"])