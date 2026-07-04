import streamlit as st
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Strategy Lab", page_icon="🧪")

st.title("🧪 Strategy Lab")
st.write("Test strategy variations against Baseline V1.0.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.subheader("⚙️ Parameters")

sl_points = st.number_input("Stop Loss Points", min_value=5, max_value=200, value=50, step=5)
target_points = st.number_input("Target Points", min_value=5, max_value=300, value=100, step=5)

st.subheader("📌 Trade Direction")
allow_ce = st.checkbox("Allow CE Trades", value=True)
allow_pe = st.checkbox("Allow PE Trades", value=True)

st.subheader("📈 EMA Filter")
ema_filter_enabled = st.checkbox("Enable EMA Slope Filter", value=False)
ema_threshold = st.number_input("Minimum EMA Slope", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

if st.button("▶️ Run Strategy Test"):
    summary, trade_log = run_flexible_strategy(
        df,
        sl_points=sl_points,
        target_points=target_points,
        allow_ce=allow_ce,
        allow_pe=allow_pe,
        ema_filter_enabled=ema_filter_enabled,
        ema_threshold=ema_threshold,
    )

    if not summary:
        st.error("No trades found for selected settings.")
        st.stop()

    st.subheader("📌 Result")

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

    st.subheader("📋 Trade Log")
    st.dataframe(trade_log, use_container_width=True, hide_index=True)