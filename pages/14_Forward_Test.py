import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Forward Test", page_icon="📡")

st.title("📡 Forward Test Dashboard")
st.write("Prepare a selected strategy for paper trading and live monitoring.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Strategy for Forward Test")

direction = st.selectbox("Direction", ["Both CE and PE", "CE Only", "PE Only"])
allow_ce = direction in ["Both CE and PE", "CE Only"]
allow_pe = direction in ["Both CE and PE", "PE Only"]

sl_points = st.number_input("Stop Loss Points", min_value=5, max_value=200, value=20, step=5)
target_points = st.number_input("Target Points", min_value=5, max_value=300, value=100, step=5)

ema_filter_enabled = st.checkbox("Enable EMA Filter", value=True)
ema_threshold = st.number_input("EMA Threshold", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

rsi_filter_enabled = st.checkbox("Enable RSI Filter", value=False)
rsi_min = st.number_input("RSI Minimum", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
rsi_max = st.number_input("RSI Maximum", min_value=0.0, max_value=100.0, value=100.0, step=1.0)

st.subheader("🧪 Historical Check Before Forward Test")

if st.button("▶️ Validate Strategy"):
    summary, trade_log = run_flexible_strategy(
        df,
        sl_points=sl_points,
        target_points=target_points,
        allow_ce=allow_ce,
        allow_pe=allow_pe,
        ema_filter_enabled=ema_filter_enabled,
        ema_threshold=ema_threshold,
        rsi_filter_enabled=rsi_filter_enabled,
        rsi_min=rsi_min,
        rsi_max=rsi_max,
    )

    if not summary:
        st.error("No trades found for this setup.")
        st.stop()

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

    st.subheader("📈 Equity Curve")
    trade_log["equity"] = trade_log["points"].cumsum()
    st.line_chart(trade_log["equity"])

st.divider()

st.subheader("📡 Forward Test Status")

st.info("Live data is not connected yet. This page currently prepares the strategy for paper testing.")

st.write("Next implementation stages:")
st.write("1. Connect Yahoo Finance demo data")
st.write("2. Generate daily signal at 9:40 AM IST")
st.write("3. Log paper trades")
st.write("4. Add Telegram alerts")
st.write("5. Move to VPS/Angel One live feed")

st.subheader("📋 Paper Test Rules")

st.write(f"Direction: **{direction}**")
st.write(f"Stop Loss: **{sl_points} points**")
st.write(f"Target: **{target_points} points**")
st.write(f"EMA Filter: **{'ON' if ema_filter_enabled else 'OFF'}**")
st.write(f"EMA Threshold: **{ema_threshold}**")
st.write(f"RSI Filter: **{'ON' if rsi_filter_enabled else 'OFF'}**")