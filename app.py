import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Stephen Trading Dashboard",
    page_icon="📈",
    layout="centered"
)

now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
current_time = now_ist.strftime("%d %b %Y, %I:%M:%S %p IST")

st.title("📈 Stephen Trading Dashboard")
st.caption("Mobile-first intraday forward test system")

st.divider()

st.subheader("🟢 System Status")
st.success("App online")
st.write(f"Current Time: **{current_time}**")
st.write("Mode: **Paper Test**")

st.divider()

st.subheader("📊 Strategy")
st.info("V1.1 Candidate – ATR Breakout + EMA 0.5 Filter")

st.write("Market: **BANKNIFTY / NIFTY**")
st.write("Signal Time: **After 9:40 AM IST**")
st.write("Trade Limit: **One trade per day**")

st.divider()

st.subheader("🎯 Today's Signal")
st.warning("⚪ Waiting for market data")

col1, col2, col3 = st.columns(3)
col1.metric("Entry", "-")
col2.metric("SL", "-")
col3.metric("Target", "-")

st.write("Reason: **Live data not connected yet**")

st.divider()

st.subheader("📌 Backtest Reference")

col1, col2 = st.columns(2)
col1.metric("Win Rate", "44.13%")
col2.metric("Profit Factor", "1.595")

col3, col4 = st.columns(2)
col3.metric("Net Points", "+4,637.75")
col4.metric("Max Drawdown", "-550 pts")

st.divider()

st.subheader("📒 Paper Test Log")
col1, col2, col3 = st.columns(3)
col1.metric("Trades", "0")
col2.metric("Wins", "0")
col3.metric("Losses", "0")

st.caption("Trade logging will be added in the next versions.")

st.divider()

st.subheader("🚧 Roadmap")
st.write("✅ GitHub setup complete")
st.write("✅ Streamlit app deployed")
st.write("✅ Dashboard layout added")
st.write("🔜 Historical replay")
st.write("🔜 Excel data upload")
st.write("🔜 Live market data")
st.write("🔜 Telegram alerts")