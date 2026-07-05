import streamlit as st
import pandas as pd
import numpy as np
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Monte Carlo", page_icon="🎲")

st.title("🎲 Monte Carlo Risk Analyzer")
st.write("Simulate many possible equity paths by reshuffling historical trades.")

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

st.subheader("🎲 Simulation Settings")

num_simulations = st.number_input(
    "Number of Simulations",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100,
)

if st.button("🚀 Run Monte Carlo"):

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

    if trade_log.empty:
        st.error("No trades found for selected strategy.")
        st.stop()

    points = trade_log["points"].values
    original_equity = np.cumsum(points)

    simulation_final_pnl = []
    simulation_max_dd = []
    sample_curves = []

    progress = st.progress(0)

    for i in range(int(num_simulations)):
        shuffled = np.random.permutation(points)
        equity = np.cumsum(shuffled)

        running_max = np.maximum.accumulate(equity)
        drawdown = equity - running_max

        simulation_final_pnl.append(equity[-1])
        simulation_max_dd.append(drawdown.min())

        if i < 20:
            sample_curves.append(equity)

        progress.progress((i + 1) / int(num_simulations))

    final_pnl = np.array(simulation_final_pnl)
    max_dd = np.array(simulation_max_dd)

    st.subheader("📊 Base Strategy Result")

    col1, col2 = st.columns(2)
    col1.metric("Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

    st.subheader("🎲 Monte Carlo Risk Result")

    probability_loss = (final_pnl < 0).mean() * 100
    dd_95 = np.percentile(max_dd, 5)
    pnl_5 = np.percentile(final_pnl, 5)
    pnl_50 = np.percentile(final_pnl, 50)
    pnl_95 = np.percentile(final_pnl, 95)

    col1, col2 = st.columns(2)
    col1.metric("Probability of Loss", f"{probability_loss:.2f}%")
    col2.metric("Worst DD 95%", round(dd_95, 2))

    col3, col4 = st.columns(2)
    col3.metric("5% Worst PnL", round(pnl_5, 2))
    col4.metric("Median PnL", round(pnl_50, 2))

    col5, col6 = st.columns(2)
    col5.metric("95% Best PnL", round(pnl_95, 2))
    col6.metric("Simulations", int(num_simulations))

    st.subheader("📈 Original Equity Curve")
    st.line_chart(pd.DataFrame({"Original Equity": original_equity}))

    st.subheader("🌪️ Sample Monte Carlo Equity Curves")
    curves_df = pd.DataFrame(sample_curves).T
    st.line_chart(curves_df)

    st.subheader("📉 Drawdown Distribution")
    dd_df = pd.DataFrame({"Max Drawdown": max_dd})
    st.bar_chart(dd_df["Max Drawdown"].value_counts().sort_index())

    st.subheader("📋 Simulation Summary")
    result_df = pd.DataFrame({
        "Simulation": range(1, int(num_simulations) + 1),
        "Final PnL": final_pnl,
        "Max Drawdown": max_dd,
    })

    st.dataframe(result_df.head(100), use_container_width=True, hide_index=True)

    csv = result_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Monte Carlo Results CSV",
        data=csv,
        file_name="monte_carlo_results.csv",
        mime="text/csv",
    )