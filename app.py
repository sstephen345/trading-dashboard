import streamlit as st

st.set_page_config(
    page_title="Stephen Trading Dashboard",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Stephen Trading Dashboard")
st.caption("Intraday Forward Test System")

st.divider()

st.subheader("Strategy")
st.info("V1.1 Candidate – ATR Breakout + EMA 0.5 Filter")

st.subheader("Market")
st.write("Instrument: **BANKNIFTY / NIFTY**")
st.write("Mode: **Paper Test**")
st.write("Status: **Prototype – No live data connected yet**")

st.divider()

st.subheader("Today's Signal")
st.warning("⚪ Waiting for market data")

col1, col2, col3 = st.columns(3)
col1.metric("Entry", "-")
col2.metric("SL", "-")
col3.metric("Target", "-")

st.divider()

st.subheader("Backtest Reference")

col1, col2 = st.columns(2)
col1.metric("Win Rate", "44.13%")
col2.metric("Profit Factor", "1.595")

col3, col4 = st.columns(2)
col3.metric("Net Points", "+4,637.75")
col4.metric("Max Drawdown", "-550 pts")

st.divider()

st.subheader("Next Features")
st.write("✅ GitHub setup complete")
st.write("✅ Streamlit app deployed")
st.write("🔜 Historical replay")
st.write("🔜 Trade history")
st.write("🔜 Live market data")
st.write("🔜 Telegram alerts")