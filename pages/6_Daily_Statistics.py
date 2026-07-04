import streamlit as st

st.set_page_config(page_title="Daily Statistics", page_icon="📅")

st.title("📅 Daily Statistics")

if "trade_log" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

trade_log = st.session_state["trade_log"].copy()

trade_log["equity"] = trade_log["points"].cumsum()
trade_log["drawdown"] = trade_log["equity"] - trade_log["equity"].cummax()

daily_display = trade_log[
    ["date", "type", "entry_time", "exit_time", "result", "points", "equity", "drawdown"]
].copy()

daily_display.columns = [
    "Date", "Trade", "Entry Time", "Exit Time", "Result",
    "Points", "Running Equity", "Drawdown"
]

st.subheader("📊 Daily Performance")

col1, col2 = st.columns(2)
col1.metric("Trading Days", len(daily_display))
col2.metric("Net Points", round(daily_display["Points"].sum(), 2))

st.dataframe(daily_display, use_container_width=True, hide_index=True)

st.subheader("📈 Daily Equity Curve")
st.line_chart(daily_display["Running Equity"])