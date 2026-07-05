import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="AI Strategy Discovery", page_icon="🤖")

st.title("🤖 AI Strategy Discovery")
st.write("Search many strategy combinations and rank them using an overall score.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Direction")
direction = st.selectbox(
    "Direction",
    ["Both CE and PE", "CE Only", "PE Only"]
)

allow_ce = direction in ["Both CE and PE", "CE Only"]
allow_pe = direction in ["Both CE and PE", "PE Only"]

st.subheader("⚙️ Search Space")

sl_values = st.multiselect(
    "Stop Loss Values",
    [10, 15, 20, 25, 30, 40, 50],
    default=[20, 30, 40]
)

target_values = st.multiselect(
    "Target Values",
    [20, 30, 40, 50, 60, 80, 100],
    default=[40, 50, 80, 100]
)

ema_values = st.multiselect(
    "EMA Threshold Values",
    [0.0, 0.5, 1.0, 1.5],
    default=[0.0, 0.5, 1.0]
)

atr_values = st.multiselect(
    "ATR Threshold Values",
    [0.0, 0.1, 0.2, 0.5],
    default=[0.0]
)

gamma_values = st.multiselect(
    "Gamma Threshold Values",
    [0.0, 0.5, 1.0],
    default=[0.0]
)

rsi_ranges = st.multiselect(
    "RSI Ranges",
    ["0-100", "40-70", "45-70", "50-70", "40-65"],
    default=["0-100", "40-70"]
)

ranking_method = st.selectbox(
    "Rank By",
    ["AI Score", "Profit Factor", "Net Points", "Win Rate %", "Lowest Drawdown"]
)

min_trades = st.number_input(
    "Minimum Trades Required",
    min_value=1,
    max_value=500,
    value=20,
    step=5
)

def parse_rsi_range(label):
    a, b = label.split("-")
    return float(a), float(b)

def normalize(series):
    if series.max() == series.min():
        return series * 0 + 50
    return 100 * (series - series.min()) / (series.max() - series.min())

def rank_results(df_results, method):
    if method == "Profit Factor":
        return df_results.sort_values(["Profit Factor", "Net Points"], ascending=[False, False])
    if method == "Net Points":
        return df_results.sort_values(["Net Points", "Profit Factor"], ascending=[False, False])
    if method == "Win Rate %":
        return df_results.sort_values(["Win Rate %", "Profit Factor"], ascending=[False, False])
    if method == "Lowest Drawdown":
        temp = df_results.copy()
        temp["Drawdown Abs"] = temp["Max DD"].abs()
        temp = temp.sort_values(["Drawdown Abs", "Profit Factor"], ascending=[True, False])
        return temp.drop(columns=["Drawdown Abs"])

    return df_results.sort_values(["AI Score", "Profit Factor"], ascending=[False, False])

if not sl_values or not target_values or not ema_values or not atr_values or not gamma_values or not rsi_ranges:
    st.warning("Please select at least one value in every search field.")
    st.stop()

total_combinations = (
    len(sl_values)
    * len(target_values)
    * len(ema_values)
    * len(atr_values)
    * len(gamma_values)
    * len(rsi_ranges)
)

st.info(f"Total strategies to test: {total_combinations}")

if st.button("🚀 Discover Strategies"):

    results = []
    progress = st.progress(0)
    count = 0

    for sl in sl_values:
        for target in target_values:
            for ema in ema_values:
                for atr in atr_values:
                    for gamma in gamma_values:
                        for rsi_label in rsi_ranges:
                            rsi_min, rsi_max = parse_rsi_range(rsi_label)

                            summary, trade_log = run_flexible_strategy(
                                df,
                                sl_points=int(sl),
                                target_points=int(target),
                                allow_ce=allow_ce,
                                allow_pe=allow_pe,
                                ema_filter_enabled=(float(ema) > 0),
                                ema_threshold=float(ema),
                                atr_filter_enabled=(float(atr) > 0),
                                atr_threshold=float(atr),
                                gamma_filter_enabled=(float(gamma) > 0),
                                gamma_threshold=float(gamma),
                                rsi_filter_enabled=(rsi_label != "0-100"),
                                rsi_min=rsi_min,
                                rsi_max=rsi_max,
                            )

                            if summary and summary["trades"] >= min_trades:
                                results.append({
                                    "SL": int(sl),
                                    "Target": int(target),
                                    "EMA": float(ema),
                                    "ATR": float(atr),
                                    "Gamma": float(gamma),
                                    "RSI": rsi_label,
                                    "Trades": summary["trades"],
                                    "Win Rate %": summary["win_rate"],
                                    "Net Points": summary["net_points"],
                                    "Profit Factor": summary["profit_factor"],
                                    "Max DD": summary["max_drawdown"],
                                    "CE Trades": summary["ce_trades"],
                                    "PE Trades": summary["pe_trades"],
                                })

                            count += 1
                            progress.progress(count / total_combinations)

    results_df = pd.DataFrame(results)

    if results_df.empty:
        st.error("No strategies passed the minimum trade requirement.")
        st.stop()

    results_df["PF Score"] = normalize(results_df["Profit Factor"])
    results_df["Net Score"] = normalize(results_df["Net Points"])
    results_df["Win Score"] = normalize(results_df["Win Rate %"])
    results_df["DD Score"] = 100 - normalize(results_df["Max DD"].abs())

    results_df["AI Score"] = (
        results_df["PF Score"] * 0.40
        + results_df["Net Score"] * 0.25
        + results_df["Win Score"] * 0.15
        + results_df["DD Score"] * 0.20
    ).round(2)

    results_df = rank_results(results_df, ranking_method).reset_index(drop=True)
    results_df.insert(0, "Rank", results_df.index + 1)

    st.subheader("🏆 Top Strategies")
    display_cols = [
        "Rank", "AI Score", "SL", "Target", "EMA", "ATR", "Gamma", "RSI",
        "Trades", "Win Rate %", "Net Points", "Profit Factor", "Max DD",
        "CE Trades", "PE Trades"
    ]
    st.dataframe(results_df[display_cols].head(50), use_container_width=True, hide_index=True)

    st.subheader("🥇 Best Strategy")
    best = results_df.iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("AI Score", best["AI Score"])
    col2.metric("Profit Factor", best["Profit Factor"])

    col3, col4 = st.columns(2)
    col3.metric("SL", int(best["SL"]))
    col4.metric("Target", int(best["Target"]))

    col5, col6 = st.columns(2)
    col5.metric("EMA", best["EMA"])
    col6.metric("RSI", best["RSI"])

    col7, col8 = st.columns(2)
    col7.metric("Net Points", best["Net Points"])
    col8.metric("Max DD", best["Max DD"])

    st.subheader("📈 Best Strategy Equity Curve")

    rsi_min, rsi_max = parse_rsi_range(best["RSI"])

    best_summary, best_trade_log = run_flexible_strategy(
        df,
        sl_points=int(best["SL"]),
        target_points=int(best["Target"]),
        allow_ce=allow_ce,
        allow_pe=allow_pe,
        ema_filter_enabled=(float(best["EMA"]) > 0),
        ema_threshold=float(best["EMA"]),
        atr_filter_enabled=(float(best["ATR"]) > 0),
        atr_threshold=float(best["ATR"]),
        gamma_filter_enabled=(float(best["Gamma"]) > 0),
        gamma_threshold=float(best["Gamma"]),
        rsi_filter_enabled=(best["RSI"] != "0-100"),
        rsi_min=rsi_min,
        rsi_max=rsi_max,
    )

    best_trade_log["equity"] = best_trade_log["points"].cumsum()
    st.line_chart(best_trade_log["equity"])

    csv = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Discovery Results CSV",
        data=csv,
        file_name="ai_strategy_discovery_results.csv",
        mime="text/csv"
    )