import streamlit as st
import pandas as pd
from strategy.baseline_v1 import run_baseline_v1

st.set_page_config(page_title="Backtest", page_icon="📊")

st.title("📊 Backtest")
st.write("Upload your 1-minute Excel file and run Baseline V1.0.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    col1, col2 = st.columns(2)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))

    if st.button("▶️ Run Baseline V1.0"):
        summary, trade_log = run_baseline_v1(df)

        st.subheader("📌 Baseline V1.0 Results")

        col1, col2 = st.columns(2)
        col1.metric("Trades", summary["trades"])
        col2.metric("Win Rate", f'{summary["win_rate"]}%')

        col3, col4 = st.columns(2)
        col3.metric("Net Points", summary["net_points"])
        col4.metric("Profit Factor", summary["profit_factor"])

        col5, col6 = st.columns(2)
        col5.metric("Max Drawdown", summary["max_drawdown"])
        col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

        st.subheader("📋 Trade Log")
        st.dataframe(trade_log)