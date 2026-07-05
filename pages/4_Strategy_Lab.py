import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Strategy Lab", page_icon="🧪")

st.title("🧪 Strategy Lab")
st.write("Research and optimize strategy variations against Baseline V1.0.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

with st.expander("📌 Entry Settings", expanded=True):
    allow_ce = st.checkbox("Allow CE Trades", value=True)
    allow_pe = st.checkbox("Allow PE Trades", value=True)

with st.expander("📈 Entry Filters", expanded=True):
    ema_filter_enabled = st.checkbox("Enable EMA Slope Filter", value=False)
    ema_threshold = st.number_input(
        "Minimum EMA Slope",
        min_value=0.0,
        max_value=10.0,
        value=0.5,
        step=0.1,
    )

    st.caption("EMA filter will work after entry EMA values are stored in the trade log.")

with st.expander("⚙️ Risk Management", expanded=True):
    sl_points = st.number_input(
        "Stop Loss Points",
        min_value=5,
        max_value=200,
        value=50,
        step=5,
    )

    target_points = st.number_input(
        "Target Points",
        min_value=5,
        max_value=300,
        value=100,
        step=5,
    )

st.divider()

if st.button("▶️ Run Single Test"):
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

    st.subheader("📊 Single Test Result")

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

with st.expander("🧠 SL / Target Optimizer", expanded=False):
    ranking_method = st.selectbox(
        "Rank optimizer results by",
        ["Profit Factor", "Net Points", "Win Rate %", "Lowest Drawdown"],
    )

    sl_from = st.number_input("SL From", min_value=5, max_value=200, value=10, step=5)
    sl_to = st.number_input("SL To", min_value=5, max_value=200, value=50, step=5)
    sl_step = st.number_input("SL Step", min_value=5, max_value=50, value=5, step=5)

    target_from = st.number_input("Target From", min_value=5, max_value=300, value=20, step=5)
    target_to = st.number_input("Target To", min_value=5, max_value=300, value=100, step=5)
    target_step = st.number_input("Target Step", min_value=5, max_value=50, value=10, step=5)

    if st.button("🔍 Optimize Strategy"):
        results = []

        sl_values = range(int(sl_from), int(sl_to) + 1, int(sl_step))
        target_values = range(int(target_from), int(target_to) + 1, int(target_step))

        total_tests = len(list(sl_values)) * len(list(target_values))
        progress = st.progress(0)
        test_count = 0

        for sl in range(int(sl_from), int(sl_to) + 1, int(sl_step)):
            for target in range(int(target_from), int(target_to) + 1, int(target_step)):
                summary, trade_log = run_flexible_strategy(
                    df,
                    sl_points=sl,
                    target_points=target,
                    allow_ce=allow_ce,
                    allow_pe=allow_pe,
                    ema_filter_enabled=ema_filter_enabled,
                    ema_threshold=ema_threshold,
                )

                if summary:
                    results.append(
                        {
                            "SL": sl,
                            "Target": target,
                            "Trades": summary["trades"],
                            "Win Rate %": summary["win_rate"],
                            "Net Points": summary["net_points"],
                            "Profit Factor": summary["profit_factor"],
                            "Max DD": summary["max_drawdown"],
                            "CE Trades": summary["ce_trades"],
                            "PE Trades": summary["pe_trades"],
                        }
                    )

                test_count += 1
                progress.progress(test_count / total_tests)

        results_df = pd.DataFrame(results)

        if results_df.empty:
            st.error("No results found.")
            st.stop()

        if ranking_method == "Profit Factor":
            results_df = results_df.sort_values(["Profit Factor", "Net Points"], ascending=[False, False])
        elif ranking_method == "Net Points":
            results_df = results_df.sort_values(["Net Points", "Profit Factor"], ascending=[False, False])
        elif ranking_method == "Win Rate %":
            results_df = results_df.sort_values(["Win Rate %", "Profit Factor"], ascending=[False, False])
        else:
            results_df["Drawdown Abs"] = results_df["Max DD"].abs()
            results_df = results_df.sort_values(["Drawdown Abs", "Profit Factor"], ascending=[True, False])
            results_df = results_df.drop(columns=["Drawdown Abs"])

        results_df = results_df.reset_index(drop=True)
        results_df.insert(0, "Rank", results_df.index + 1)

        st.subheader(f"🏆 Optimizer Results - Ranked by {ranking_method}")
        st.dataframe(results_df, use_container_width=True, hide_index=True)

        st.subheader("🥇 Best Setup")
        best = results_df.iloc[0]

        col1, col2 = st.columns(2)
        col1.metric("Best SL", int(best["SL"]))
        col2.metric("Best Target", int(best["Target"]))

        col3, col4 = st.columns(2)
        col3.metric("Win Rate", f'{best["Win Rate %"]}%')
        col4.metric("Profit Factor", best["Profit Factor"])

        col5, col6 = st.columns(2)
        col5.metric("Net Points", best["Net Points"])
        col6.metric("Max DD", best["Max DD"])