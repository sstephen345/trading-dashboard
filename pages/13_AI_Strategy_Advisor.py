import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="AI Strategy Advisor", page_icon="🧠")

st.title("🧠 AI Strategy Advisor")
st.write("Get an automatic strategy health report and paper-trading recommendation.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Strategy Settings")

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

def score_strategy(summary):
    score = 0

    pf = summary["profit_factor"]
    wr = summary["win_rate"]
    net = summary["net_points"]
    dd = abs(summary["max_drawdown"])
    trades = summary["trades"]

    if pf >= 2.0:
        score += 30
    elif pf >= 1.5:
        score += 22
    elif pf >= 1.2:
        score += 12

    if net > 0:
        score += 20

    if wr >= 50:
        score += 20
    elif wr >= 35:
        score += 12
    elif wr >= 25:
        score += 7

    if dd <= 200:
        score += 20
    elif dd <= 500:
        score += 12
    elif dd <= 1000:
        score += 5

    if trades >= 100:
        score += 10
    elif trades >= 50:
        score += 6
    elif trades >= 20:
        score += 3

    return min(score, 100)

if st.button("🧠 Analyze Strategy"):

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
        st.error("No trades found for selected strategy.")
        st.stop()

    score = score_strategy(summary)

    st.subheader("🧠 AI Verdict")

    if score >= 80:
        st.success(f"🟢 Strong strategy candidate. Score: {score}/100")
        verdict = "Ready for paper trading"
    elif score >= 60:
        st.warning(f"🟡 Moderate strategy. Score: {score}/100")
        verdict = "Paper trade carefully"
    else:
        st.error(f"🔴 Weak strategy. Score: {score}/100")
        verdict = "Do not paper trade yet"

    st.metric("Recommendation", verdict)

    st.subheader("📊 Strategy Metrics")

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

    st.subheader("✅ Strengths")

    if summary["profit_factor"] >= 1.5:
        st.write("✅ Profit Factor is acceptable or strong.")
    if summary["net_points"] > 0:
        st.write("✅ Strategy is net profitable.")
    if abs(summary["max_drawdown"]) <= 500:
        st.write("✅ Drawdown is controlled.")
    if summary["trades"] >= 50:
        st.write("✅ Trade sample size is reasonable.")

    st.subheader("⚠️ Weaknesses")

    if summary["win_rate"] < 35:
        st.write("⚠️ Win rate is low. This strategy depends on large winners.")
    if abs(summary["max_drawdown"]) > 500:
        st.write("⚠️ Drawdown is high. Reduce lot size or improve filters.")
    if summary["trades"] < 50:
        st.write("⚠️ Trade count is low. Result may not be statistically reliable.")
    if summary["profit_factor"] < 1.5:
        st.write("⚠️ Profit Factor is not strong enough yet.")

    st.subheader("📌 Suggested Action")

    if score >= 80:
        st.write("✅ Move this setup to Forward Test / Paper Trading.")
        st.write("✅ Start with small quantity only.")
        st.write("✅ Track live performance for at least 20–30 trades.")
    elif score >= 60:
        st.write("⚠️ Run Walk-Forward and Monte Carlo again before using.")
        st.write("⚠️ Consider reducing target or adding filters.")
    else:
        st.write("❌ Do not use this setup live.")
        st.write("❌ Continue optimization and validation.")

    st.subheader("📈 Equity Curve")
    trade_log["equity"] = trade_log["points"].cumsum()
    st.line_chart(trade_log["equity"])

    st.subheader("📋 Trade Log")
    st.dataframe(trade_log, use_container_width=True, hide_index=True)