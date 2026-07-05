import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Auto Optimizer", page_icon="🧠")

st.title("🧠 Auto Optimizer")
st.write("Automatically test multiple strategy combinations.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Trade Direction")

direction = st.selectbox(
    "Select Direction",
    ["Both CE and PE", "CE Only", "PE Only"]
)

allow_ce = direction in ["Both CE and PE", "CE Only"]
allow_pe = direction in ["Both CE and PE", "PE Only"]

st.subheader("⚙️ SL / Target Range")

sl_from = st.number_input("SL From", value=10, step=5)
sl_to = st.number_input("SL To", value=50, step=5)
sl_step = st.number_input("SL Step", value=5, step=5)

target_from = st.number_input("Target From", value=20, step=10)
target_to = st.number_input("Target To", value=100, step=10)
target_step = st.number_input("Target Step", value=10, step=10)
st.subheader("📈 Filter Ranges")

use_ema = st.checkbox("Optimize EMA Filter", value=True)
ema_values = [0.0, 0.5, 1.0, 1.5] if use_ema else [0.0]

use_atr = st.checkbox("Optimize ATR Filter", value=False)
atr_values = [0.0, 0.1, 0.2, 0.5] if use_atr else [0.0]

use_gamma = st.checkbox("Optimize Gamma Filter", value=False)
gamma_values = [0.0, 0.5, 1.0] if use_gamma else [0.0]

use_rsi = st.checkbox("Optimize RSI Filter", value=False)
rsi_ranges = [(40, 70), (45, 70), (50, 70), (40, 65)] if use_rsi else [(0, 100)]

ranking_method = st.selectbox(
    "Rank Results By",
    ["Profit Factor", "Net Points", "Win Rate %", "Lowest Drawdown"]
)

if st.button("🚀 Run Auto Optimization"):

    results = []

    sl_values = list(range(int(sl_from), int(sl_to) + 1, int(sl_step)))
    target_values = list(range(int(target_from), int(target_to) + 1, int(target_step)))

    total_tests = (
        len(sl_values)
        * len(target_values)
        * len(ema_values)
        * len(atr_values)
        * len(gamma_values)
        * len(rsi_ranges)
    )

    st.write(f"Total combinations: **{total_tests}**")

    progress = st.progress(0)
    count = 0

    for sl in sl_values:
        for target in target_values:
            for ema in ema_values:
                for atr in atr_values:
                    for gamma in gamma_values:
                        for rsi_min, rsi_max in rsi_ranges:

                            summary, trade_log = run_flexible_strategy(
                                df,
                                sl_points=sl,
                                target_points=target,
                                allow_ce=allow_ce,
                                allow_pe=allow_pe,
                                ema_filter_enabled=use_ema,
                                ema_threshold=ema,
                                atr_filter_enabled=use_atr,
                                atr_threshold=atr,
                                gamma_filter_enabled=use_gamma,
                                gamma_threshold=gamma,
                                rsi_filter_enabled=use_rsi,
                                rsi_min=rsi_min,
                                rsi_max=rsi_max,
                            )

                            if summary:
                                results.append({
                                    "SL": sl,
                                    "Target": target,
                                    "EMA": ema,
                                    "ATR": atr,
                                    "Gamma": gamma,
                                    "RSI Min": rsi_min,
                                    "RSI Max": rsi_max,
                                    "Trades": summary["trades"],
                                    "Win Rate %": summary["win_rate"],
                                    "Net Points": summary["net_points"],
                                    "Profit Factor": summary["profit_factor"],
                                    "Max DD": summary["max_drawdown"],
                                    "CE Trades": summary["ce_trades"],
                                    "PE Trades": summary["pe_trades"],
                                })

                            count += 1
                            progress.progress(count / total_tests)

    results_df = pd.DataFrame(results)

    if results_df.empty:
        st.error("No valid results found.")
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

    st.subheader("🏆 Top 50 Results")
    st.dataframe(results_df.head(50), use_container_width=True, hide_index=True)

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

    csv = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Full Results CSV",
        data=csv,
        file_name="auto_optimizer_results.csv",
        mime="text/csv"
    )