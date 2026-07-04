import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monthly Statistics", page_icon="📆")

st.title("📆 Monthly Statistics")

if "trade_log" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

trade_log = st.session_state["trade_log"].copy()

trade_log["date"] = pd.to_datetime(trade_log["date"])
trade_log["Month"] = trade_log["date"].dt.to_period("M").astype(str)

monthly = trade_log.groupby("Month").agg(
    Trades=("points", "count"),
    Wins=("points", lambda x: (x > 0).sum()),
    Losses=("points", lambda x: (x < 0).sum()),
    Net_Points=("points", "sum"),
).reset_index()

monthly["Win_Rate_%"] = (monthly["Wins"] / monthly["Trades"] * 100).round(2)

st.subheader("📊 Month-wise Performance")
st.dataframe(monthly, use_container_width=True, hide_index=True)

st.subheader("📈 Monthly Net Points")
st.bar_chart(monthly.set_index("Month")["Net_Points"])