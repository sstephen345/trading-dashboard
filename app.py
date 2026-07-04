import streamlit as st
import pandas as pd
from strategy.baseline_v1 import run_baseline_v1
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Stephen Trading Dashboard",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Stephen Trading Dashboard")
st.caption("Mobile-first intraday trading research platform")

st.divider()

now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
st.success("🟢 System Online")
st.write(f"Current IST Time: **{now_ist.strftime('%d %b %Y, %I:%M:%S %p')}**")

st.divider()

st.subheader("📂 Upload Dataset Once")

uploaded_file = st.file_uploader(
    "Upload your 1-minute Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    summary, trade_log = run_baseline_v1(df)

    st.session_state["data_loaded"] = True
    st.session_state["df"] = df
    st.session_state["summary"] = summary
    st.session_state["trade_log"] = trade_log

    st.success("✅ Data loaded and Baseline V1.0 completed")

    st.divider()

    st.subheader("📌 Baseline V1.0 Summary")

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

    st.divider()

    st.subheader("📈 Equity Curve")
    trade_log["equity"] = trade_log["points"].cumsum()
    st.line_chart(trade_log["equity"])

else:
    st.warning("Upload Excel file to activate the dashboard.")

st.divider()

st.subheader("🚀 Project Status")
st.write("✅ GitHub setup complete")
st.write("✅ Streamlit cloud app live")
st.write("✅ Baseline V1.0 verified")
st.write("✅ Equity curve added")
st.write("✅ Daily and monthly statistics added")
st.write("🔜 Shared data across all pages")
st.write("🔜 Replay mode")
st.write("🔜 Forward test")