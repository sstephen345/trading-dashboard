import streamlit as st
import pandas as pd
from datetime import datetime
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Live Scanner", page_icon="📡")

st.title("📡 Live Scanner / Paper Trading")
st.write("Prepare live signal monitoring and paper trade logging. No real orders are placed.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"].copy()
df["date"] = pd.to_datetime(df["date"])

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Active Strategy")

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

st.subheader("🧪 Paper Test Simulation")

if st.button("▶️ Run Paper Test on Uploaded Data"):

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
        st.error("No trades found for selected setup.")
        st.stop()

    st.subheader("📊 Paper Test Result")

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

    trade_log["equity"] = trade_log["points"].cumsum()

    st.subheader("📈 Paper Equity Curve")
    st.line_chart(trade_log["equity"])

    st.subheader("📋 Paper Trade Log")
    st.dataframe(trade_log, use_container_width=True, hide_index=True)

    csv = trade_log.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Paper Trade Log",
        data=csv,
        file_name="paper_trade_log.csv",
        mime="text/csv",
    )

st.divider()

st.subheader("📡 Live Status")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.info("Live market feed is not connected yet.")
st.write(f"Last dashboard refresh: **{now}**")

st.write("Current stage:")
st.write("✅ Strategy selected")
st.write("✅ Paper trade structure ready")
st.write("⬜ Live data feed")
st.write("⬜ Telegram alert")
st.write("⬜ Angel One connection")
st.write("⬜ Real order execution")

st.subheader("🚨 Signal Box")

st.warning("No live signal yet. Live feed connection is the next development step.")

st.subheader("📋 Forward Test Rules")

rules = {
    "Direction": direction,
    "Stop Loss": sl_points,
    "Target": target_points,
    "EMA Filter": "ON" if ema_filter_enabled else "OFF",
    "EMA Threshold": ema_threshold,
    "RSI Filter": "ON" if rsi_filter_enabled else "OFF",
    "RSI Min": rsi_min,
    "RSI Max": rsi_max,
    "Mode": "Paper Trading Only",
}

st.json(rules)