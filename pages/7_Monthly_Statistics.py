import streamlit as st
import pandas as pd
from strategy.baseline_v1 import run_baseline_v1

st.set_page_config(page_title="Monthly Statistics", page_icon="📆")

st.title("📆 Monthly Statistics")
st.write("Upload Excel and view month-wise Baseline V1.0 performance.")

uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    summary, trade_log = run_baseline_v1(df)

    st.success("✅ Baseline V1.0 completed")

    trade_log["date"] = pd.to_datetime(trade_log["date"])
    trade_log["Month"] = trade_log["date"].dt.to_period("M").astype(str)

    monthly = trade_log.groupby("Month").agg(
        Trades=("points", "count"),
        Wins=("points", lambda x: (x > 0).sum()),
        Losses=("points", lambda x: (x < 0).sum()),
        Net_Points=("points", "sum"),
    ).reset_index()

    monthly["Win_Rate_%"] = (monthly["Wins"] / monthly["Trades"] * 100).round(2)

    monthly["Profit_Factor"] = monthly["Month"].apply(
        lambda m: round(
            trade_log[(trade_log["Month"] == m) & (trade_log["points"] > 0)]["points"].sum()
            / abs(trade_log[(trade_log["Month"] == m) & (trade_log["points"] < 0)]["points"].sum()),
            3
        )
        if abs(trade_log[(trade_log["Month"] == m) & (trade_log["points"] < 0)]["points"].sum()) > 0
        else 0
    )

    st.subheader("📊 Month-wise Performance")

    st.dataframe(
        monthly,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("📈 Monthly Net Points")

    chart_data = monthly.set_index("Month")["Net_Points"]
    st.bar_chart(chart_data)