import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Portfolio Builder", page_icon="💼")

st.title("💼 Portfolio Builder")
st.write("Combine multiple strategy configurations and analyze the combined equity curve.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")


def parse_rsi(label):
    a, b = label.split("-")
    return float(a), float(b)


def portfolio_summary(trade_log):
    if trade_log.empty:
        return {}

    wins = (trade_log["points"] > 0).sum()
    losses = (trade_log["points"] < 0).sum()

    gross_profit = trade_log.loc[trade_log["points"] > 0, "points"].sum()
    gross_loss = abs(trade_log.loc[trade_log["points"] < 0, "points"].sum())

    equity = trade_log["points"].cumsum()
    drawdown = equity - equity.cummax()

    return {
        "trades": len(trade_log),
        "wins": int(wins),
        "losses": int(losses),
        "win_rate": round(wins / len(trade_log) * 100, 2),
        "net_points": round(trade_log["points"].sum(), 2),
        "profit_factor": round(gross_profit / gross_loss, 3) if gross_loss else 0,
        "max_drawdown": round(drawdown.min(), 2),
    }


st.subheader("⚙️ Strategy Configurations")

num_strategies = st.selectbox("Number of strategies to combine", [2, 3], index=0)

strategy_configs = []

for i in range(1, num_strategies + 1):
    with st.expander(f"Strategy {i}", expanded=(i == 1)):
        name = st.text_input(f"Strategy {i} Name", value=f"Strategy {i}", key=f"name_{i}")

        direction = st.selectbox(
            f"Direction {i}",
            ["Both CE and PE", "CE Only", "PE Only"],
            key=f"direction_{i}",
        )

        allow_ce = direction in ["Both CE and PE", "CE Only"]
        allow_pe = direction in ["Both CE and PE", "PE Only"]

        sl = st.number_input(f"SL {i}", min_value=5, max_value=200, value=20, step=5, key=f"sl_{i}")
        target = st.number_input(f"Target {i}", min_value=5, max_value=300, value=100, step=5, key=f"target_{i}")

        ema_enabled = st.checkbox(f"EMA Filter {i}", value=True, key=f"ema_enabled_{i}")
        ema = st.number_input(f"EMA Threshold {i}", min_value=0.0, max_value=10.0, value=0.5, step=0.1, key=f"ema_{i}")

        rsi_enabled = st.checkbox(f"RSI Filter {i}", value=False, key=f"rsi_enabled_{i}")
        rsi_label = st.selectbox(
            f"RSI Range {i}",
            ["0-100", "40-70", "45-70", "50-70", "40-65"],
            key=f"rsi_{i}",
        )

        lots = st.number_input(f"Lots / Weight {i}", min_value=1, max_value=10, value=1, step=1, key=f"lots_{i}")

        strategy_configs.append({
            "name": name,
            "allow_ce": allow_ce,
            "allow_pe": allow_pe,
            "sl": sl,
            "target": target,
            "ema_enabled": ema_enabled,
            "ema": ema,
            "rsi_enabled": rsi_enabled,
            "rsi_label": rsi_label,
            "lots": lots,
        })


if st.button("🚀 Build Portfolio"):

    all_logs = []
    individual_results = []

    for cfg in strategy_configs:
        rsi_min, rsi_max = parse_rsi(cfg["rsi_label"])

        summary, trade_log = run_flexible_strategy(
            df,
            sl_points=cfg["sl"],
            target_points=cfg["target"],
            allow_ce=cfg["allow_ce"],
            allow_pe=cfg["allow_pe"],
            ema_filter_enabled=cfg["ema_enabled"],
            ema_threshold=cfg["ema"],
            rsi_filter_enabled=cfg["rsi_enabled"],
            rsi_min=rsi_min,
            rsi_max=rsi_max,
        )

        if trade_log.empty:
            continue

        trade_log = trade_log.copy()
        trade_log["strategy"] = cfg["name"]
        trade_log["lots"] = cfg["lots"]
        trade_log["raw_points"] = trade_log["points"]
        trade_log["points"] = trade_log["points"] * cfg["lots"]

        all_logs.append(trade_log)

        individual_results.append({
            "Strategy": cfg["name"],
            "SL": cfg["sl"],
            "Target": cfg["target"],
            "EMA": cfg["ema"] if cfg["ema_enabled"] else "OFF",
            "RSI": cfg["rsi_label"] if cfg["rsi_enabled"] else "OFF",
            "Lots": cfg["lots"],
            "Trades": summary["trades"],
            "Win Rate %": summary["win_rate"],
            "Net Points": summary["net_points"] * cfg["lots"],
            "Profit Factor": summary["profit_factor"],
            "Max DD": summary["max_drawdown"] * cfg["lots"],
        })

    if not all_logs:
        st.error("No trades found for selected strategy portfolio.")
        st.stop()

    portfolio_log = pd.concat(all_logs, ignore_index=True)
    portfolio_log["exit_time"] = pd.to_datetime(portfolio_log["exit_time"])
    portfolio_log = portfolio_log.sort_values("exit_time").reset_index(drop=True)

    summary = portfolio_summary(portfolio_log)

    st.subheader("📊 Portfolio Result")

    col1, col2 = st.columns(2)
    col1.metric("Total Trades", summary["trades"])
    col2.metric("Win Rate", f'{summary["win_rate"]}%')

    col3, col4 = st.columns(2)
    col3.metric("Net Points", summary["net_points"])
    col4.metric("Profit Factor", summary["profit_factor"])

    col5, col6 = st.columns(2)
    col5.metric("Max DD", summary["max_drawdown"])
    col6.metric("Strategies", len(all_logs))

    st.subheader("📈 Combined Equity Curve")
    portfolio_log["equity"] = portfolio_log["points"].cumsum()
    st.line_chart(portfolio_log["equity"])

    st.subheader("📋 Individual Strategy Results")
    result_df = pd.DataFrame(individual_results)
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    st.subheader("📅 Daily Portfolio P&L")
    portfolio_log["date"] = pd.to_datetime(portfolio_log["exit_time"]).dt.date
    daily_pnl = portfolio_log.groupby("date")["points"].sum().reset_index()
    daily_pnl["cumulative"] = daily_pnl["points"].cumsum()
    st.line_chart(daily_pnl.set_index("date")["cumulative"])

    st.subheader("🔗 Strategy Correlation")
    pivot = portfolio_log.pivot_table(
        index="date",
        columns="strategy",
        values="points",
        aggfunc="sum",
        fill_value=0,
    )

    if pivot.shape[1] > 1:
        corr = pivot.corr()
        st.dataframe(corr, use_container_width=True)
    else:
        st.info("Need at least 2 active strategies to calculate correlation.")

    st.subheader("📋 Combined Trade Log")
    st.dataframe(portfolio_log, use_container_width=True, hide_index=True)

    csv = portfolio_log.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Portfolio Trade Log",
        data=csv,
        file_name="portfolio_trade_log.csv",
        mime="text/csv",
    )