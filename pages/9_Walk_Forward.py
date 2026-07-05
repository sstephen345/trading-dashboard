import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Walk Forward", page_icon="🚶")

st.title("🚶 Walk-Forward Optimization")
st.write("Optimize on training data, then validate on unseen testing data.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"].copy()
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

st.subheader("⚙️ Split Settings")
train_percent = st.slider("Training Data %", 50, 90, 70, 5)

split_index = int(len(df) * train_percent / 100)
train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()

st.write(f"Training rows: **{len(train_df):,}**")
st.write(f"Testing rows: **{len(test_df):,}**")

st.subheader("📌 Direction")
direction = st.selectbox("Direction", ["Both CE and PE", "CE Only", "PE Only"])

allow_ce = direction in ["Both CE and PE", "CE Only"]
allow_pe = direction in ["Both CE and PE", "PE Only"]

st.subheader("⚙️ Optimization Ranges")

sl_values = st.multiselect(
    "Stop Loss Values",
    [10, 15, 20, 25, 30, 40, 50],
    default=[20, 30, 40, 50],
)

target_values = st.multiselect(
    "Target Values",
    [20, 30, 40, 50, 60, 80, 100],
    default=[40, 50, 60, 80, 100],
)

ema_values = st.multiselect(
    "EMA Threshold Values",
    [0.0, 0.5, 1.0, 1.5],
    default=[0.0, 0.5, 1.0],
)

rsi_ranges = st.multiselect(
    "RSI Ranges",
    ["0-100", "40-70", "45-70", "50-70", "40-65"],
    default=["0-100", "40-70"],
)

ranking_method = st.selectbox(
    "Select Best Strategy By",
    ["Profit Factor", "Net Points", "Win Rate %", "Lowest Drawdown"],
)

def parse_rsi_range(r):
    a, b = r.split("-")
    return float(a), float(b)

def rank_results(results_df, method):
    if method == "Profit Factor":
        return results_df.sort_values(["Profit Factor", "Net Points"], ascending=[False, False])
    if method == "Net Points":
        return results_df.sort_values(["Net Points", "Profit Factor"], ascending=[False, False])
    if method == "Win Rate %":
        return results_df.sort_values(["Win Rate %", "Profit Factor"], ascending=[False, False])

    results_df = results_df.copy()
    results_df["Drawdown Abs"] = results_df["Max DD"].abs()
    results_df = results_df.sort_values(["Drawdown Abs", "Profit Factor"], ascending=[True, False])
    return results_df.drop(columns=["Drawdown Abs"])

if st.button("🚀 Run Walk-Forward Test"):

    results = []
    total_tests = len(sl_values) * len(target_values) * len(ema_values) * len(rsi_ranges)

    st.write(f"Training optimization combinations: **{total_tests}**")
    progress = st.progress(0)
    count = 0

    for sl in sl_values:
        for target in target_values:
            for ema in ema_values:
                for rsi_label in rsi_ranges:
                    rsi_min, rsi_max = parse_rsi_range(rsi_label)

                    summary, _ = run_flexible_strategy(
                        train_df,
                        sl_points=sl,
                        target_points=target,
                        allow_ce=allow_ce,
                        allow_pe=allow_pe,
                        ema_filter_enabled=(ema > 0),
                        ema_threshold=ema,
                        rsi_filter_enabled=(rsi_label != "0-100"),
                        rsi_min=rsi_min,
                        rsi_max=rsi_max,
                    )

                    if summary:
                        results.append({
                            "SL": sl,
                            "Target": target,
                            "EMA": ema,
                            "RSI": rsi_label,
                            "Trades": summary["trades"],
                            "Win Rate %": summary["win_rate"],
                            "Net Points": summary["net_points"],
                            "Profit Factor": summary["profit_factor"],
                            "Max DD": summary["max_drawdown"],
                        })

                    count += 1
                    progress.progress(count / total_tests)

    train_results = pd.DataFrame(results)

    if train_results.empty:
        st.error("No valid training results found.")
        st.stop()

    train_results = rank_results(train_results, ranking_method).reset_index(drop=True)
    train_results.insert(0, "Rank", train_results.index + 1)

    best = train_results.iloc[0]

    st.subheader("🏆 Best Training Setup")

    col1, col2 = st.columns(2)
    col1.metric("SL", int(best["SL"]))
    col2.metric("Target", int(best["Target"]))

    col3, col4 = st.columns(2)
    col3.metric("EMA", best["EMA"])
    col4.metric("RSI", best["RSI"])

    st.subheader("📊 Training Result")
    col1, col2 = st.columns(2)
    col1.metric("Win Rate", f'{best["Win Rate %"]}%')
    col2.metric("Profit Factor", best["Profit Factor"])

    col3, col4 = st.columns(2)
    col3.metric("Net Points", best["Net Points"])
    col4.metric("Max DD", best["Max DD"])

    rsi_min, rsi_max = parse_rsi_range(best["RSI"])

    test_summary, test_trade_log = run_flexible_strategy(
        test_df,
        sl_points=int(best["SL"]),
        target_points=int(best["Target"]),
        allow_ce=allow_ce,
        allow_pe=allow_pe,
        ema_filter_enabled=(best["EMA"] > 0),
        ema_threshold=float(best["EMA"]),
        rsi_filter_enabled=(best["RSI"] != "0-100"),
        rsi_min=rsi_min,
        rsi_max=rsi_max,
    )

    st.subheader("🧪 Testing Result - Unseen Data")

    if not test_summary:
        st.error("No trades generated on testing data.")
        st.stop()

    col1, col2 = st.columns(2)
    col1.metric("Trades", test_summary["trades"])
    col2.metric("Win Rate", f'{test_summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", test_summary["net_points"])
    col4.metric("Profit Factor", test_summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", test_summary["max_drawdown"])
    col6.metric("CE / PE", f'{test_summary["ce_trades"]} / {test_summary["pe_trades"]}')

    st.subheader("🧭 Strategy Quality")

    train_pf = float(best["Profit Factor"])
    test_pf = float(test_summary["profit_factor"])
    train_wr = float(best["Win Rate %"])
    test_wr = float(test_summary["win_rate"])
    win_rate_drop = train_wr - test_wr

    if test_pf >= 1.8 and win_rate_drop <= 5:
        st.success("🟢 Excellent: Testing performance is close to training.")
    elif test_pf >= 1.5:
        st.warning("🟡 Good: Testing result is acceptable, but monitor carefully.")
    else:
        st.error("🔴 Possible overfit: Testing result is weak.")

    st.write(f"Training PF: **{train_pf}**")
    st.write(f"Testing PF: **{test_pf}**")
    st.write(f"Win Rate Drop: **{round(win_rate_drop, 2)}%**")

    st.subheader("📈 Testing Equity Curve")
    test_trade_log["equity"] = test_trade_log["points"].cumsum()
    st.line_chart(test_trade_log["equity"])

    st.subheader("🏆 Top Training Results")
    st.dataframe(train_results.head(50), use_container_width=True, hide_index=True)

    csv = train_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Training Optimization Results",
        data=csv,
        file_name="walk_forward_training_results.csv",
        mime="text/csv",
    )