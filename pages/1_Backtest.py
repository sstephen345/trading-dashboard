import streamlit as st
from strategy.baseline_v1 import run_baseline_v1

st.set_page_config(page_title="Backtest", page_icon="📊")

st.title("📊 Backtest")

if "data_loaded" not in st.session_state:
    st.warning("Please upload Excel first from the Dashboard page.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

if st.button("▶️ Run Baseline V1.0"):
    summary, trade_log = run_baseline_v1(df)

    st.session_state["summary"] = summary
    st.session_state["trade_log"] = trade_log

    st.subheader("📌 Baseline V1.0 Results")

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')