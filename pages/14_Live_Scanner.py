import streamlit as st
import pandas as pd
from datetime import datetime
from strategy.flexible_engine import run_flexible_strategy
from strategy.live_indicators import build_live_indicator_table

try:
    import yfinance as yf
except ImportError:
    yf = None

st.set_page_config(page_title="Live Scanner", page_icon="📡")

st.title("📡 Live Signal Engine")
st.write("Live scanner with signal history. No real orders are placed.")

if "signal_history" not in st.session_state:
    st.session_state["signal_history"] = []

if "last_signal_candle" not in st.session_state:
    st.session_state["last_signal_candle"] = None

st.subheader("📌 Active Strategy")

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

st.subheader("🌐 Demo Live Feed")

symbol = st.selectbox(
    "Yahoo Symbol",
    ["^NSEI", "^NSEBANK", "RELIANCE.NS", "SBIN.NS", "TCS.NS"]
)

interval = st.selectbox("Interval", ["1m", "5m", "15m"], index=0)
period = st.selectbox("Period", ["1d", "5d"], index=0)


def calculate_confidence(latest, signal):
    score = 50

    if abs(float(latest["EMA_Slope"])) >= ema_threshold:
        score += 15

    if float(latest["ATR_Slope"]) > 0:
        score += 15

    if signal == "BUY CE" and float(latest["Gamma_Momentum"]) > 0:
        score += 10

    if signal == "BUY PE" and float(latest["Gamma_Momentum"]) < 0:
        score += 10

    rsi = float(latest["RSI14"])
    if 40 <= rsi <= 70:
        score += 10

    return min(score, 100)


def get_live_signal(latest):
    ce_ok = (
        allow_ce
        and latest["ATR_Slope"] > 0
        and latest["Gamma_Momentum"] > 0
        and latest["EMA_Slope"] > 0
        and latest["close"] > latest["EMA20"]
    )

    pe_ok = (
        allow_pe
        and latest["ATR_Slope"] > 0
        and latest["Gamma_Momentum"] < 0
        and latest["EMA_Slope"] < 0
        and latest["close"] < latest["EMA20"]
    )

    if ema_filter_enabled:
        ce_ok = ce_ok and latest["EMA_Slope"] >= ema_threshold
        pe_ok = pe_ok and latest["EMA_Slope"] <= -ema_threshold

    if rsi_filter_enabled:
        ce_ok = ce_ok and rsi_min <= latest["RSI14"] <= rsi_max
        pe_ok = pe_ok and rsi_min <= latest["RSI14"] <= rsi_max

    if ce_ok:
        return "BUY CE"

    if pe_ok:
        return "BUY PE"

    return "NO TRADE"


if st.button("🔄 Scan Latest Candle"):

    if yf is None:
        st.error("yfinance is not installed. Add yfinance to requirements.txt and reboot app.")
        st.stop()

    try:
        live_df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
        )

        if live_df.empty:
            st.error("No data received from Yahoo Finance.")
            st.stop()

        live_df = live_df.reset_index()

        if isinstance(live_df.columns, pd.MultiIndex):
            live_df.columns = [
                col[0] if col[0] else col[1]
                for col in live_df.columns
            ]

        indicator_df = build_live_indicator_table(live_df)

        latest = indicator_df.iloc[-1]
        candle_time = str(latest["datetime"])
        close_price = float(latest["close"])

        signal = get_live_signal(latest)

        st.subheader("📡 Current Market Snapshot")

        col1, col2 = st.columns(2)
        col1.metric("Latest Close", round(close_price, 2))
        col2.metric("Signal", signal)

        col3, col4 = st.columns(2)
        col3.metric("EMA Slope", round(float(latest["EMA_Slope"]), 3))
        col4.metric("RSI14", round(float(latest["RSI14"]), 2))

        col5, col6 = st.columns(2)
        col5.metric("ATR Slope", round(float(latest["ATR_Slope"]), 3))
        col6.metric("Gamma", round(float(latest["Gamma_Momentum"]), 3))

        st.subheader("🚨 Signal Box")

        if signal == "NO TRADE":
            st.warning("⚪ No trade. Conditions not satisfied.")
        else:
            entry = close_price

            if signal == "BUY CE":
                sl = entry - sl_points
                target = entry + target_points
                st.success("🟢 BUY CE Signal")
            else:
                sl = entry + sl_points
                target = entry - target_points
                st.error("🔴 BUY PE Signal")

            confidence = calculate_confidence(latest, signal)

            col1, col2, col3 = st.columns(3)
            col1.metric("Entry", round(entry, 2))
            col2.metric("SL", round(sl, 2))
            col3.metric("Target", round(target, 2))

            st.metric("Confidence", f"{confidence}%")

            if st.session_state["last_signal_candle"] != candle_time:
                st.session_state["signal_history"].append(
                    {
                        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symbol": symbol,
                        "candle_time": candle_time,
                        "signal": signal,
                        "entry": round(entry, 2),
                        "sl": round(sl, 2),
                        "target": round(target, 2),
                        "confidence": confidence,
                        "status": "OPEN PAPER",
                        "ema_slope": round(float(latest["EMA_Slope"]), 4),
                        "rsi": round(float(latest["RSI14"]), 2),
                        "atr_slope": round(float(latest["ATR_Slope"]), 4),
                        "gamma": round(float(latest["Gamma_Momentum"]), 4),
                    }
                )
                st.session_state["last_signal_candle"] = candle_time
                st.success("✅ New paper signal added to history.")
            else:
                st.info("Duplicate candle ignored. Signal already recorded for this candle.")

        st.subheader("📊 Latest Indicator Table")

        display_cols = [
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "EMA20",
            "EMA_Slope",
            "RSI14",
            "ATR14",
            "ATR_Slope",
            "VWAP",
            "Gamma_Momentum",
            "Trend",
            "Signal",
        ]

        st.dataframe(
            indicator_df[display_cols].tail(30),
            use_container_width=True,
            hide_index=True,
        )

    except Exception as e:
        st.error(f"Live signal engine error: {e}")

st.divider()

st.subheader("📋 Live Signal History")

history_df = pd.DataFrame(st.session_state["signal_history"])

if history_df.empty:
    st.info("No live paper signals recorded yet.")
else:
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    csv = history_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Signal History",
        data=csv,
        file_name="live_signal_history.csv",
        mime="text/csv",
    )

    if st.button("🧹 Clear Signal History"):
        st.session_state["signal_history"] = []
        st.session_state["last_signal_candle"] = None
        st.success("Signal history cleared. Refresh page to update.")

st.divider()

st.subheader("🧪 Paper Test on Uploaded Dataset")

if "df" not in st.session_state:
    st.info("Upload Excel from Dashboard to enable historical paper test.")
else:
    df = st.session_state["df"].copy()
    df["date"] = pd.to_datetime(df["date"])

    if st.button("▶️ Run Paper Test on Uploaded Data"):

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
            st.error("No trades found for selected setup.")
            st.stop()

        st.subheader("📊 Paper Test Result")

        col1, col2 = st.columns(2)
        col1.metric("Trades", summary["trades"])
        col2.metric("Win Rate", f'{summary["win_rate"]}%')

        col3, col4 = st.columns(2)
        col3.metric("Net Points", summary["net_points"])
        col4.metric("Profit Factor", summary["profit_factor"])

        col5, col6 = st.columns(2)
        col5.metric("Max DD", summary["max_drawdown"])
        col6.metric("CE / PE", f'{summary["ce_trades"]} / {summary["pe_trades"]}')

        trade_log["equity"] = trade_log["points"].cumsum()

        st.subheader("📈 Paper Equity Curve")
        st.line_chart(trade_log["equity"])

        st.subheader("📋 Paper Trade Log")
        st.dataframe(trade_log, use_container_width=True, hide_index=True)

st.divider()

st.subheader("📡 Live Status")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.write(f"Last dashboard refresh: **{now}**")

st.write("Current stage:")
st.write("✅ Strategy selected")
st.write("✅ Paper trade structure ready")
st.write("✅ Yahoo demo live feed")
st.write("✅ Live indicator table")
st.write("✅ Live signal calculation")
st.write("✅ Signal history")
st.write("⬜ Telegram alert")
st.write("⬜ Angel One connection")
st.write("⬜ Real order execution")

st.subheader("📋 Forward Test Rules")

rules = {
    "Direction": direction,
    "Stop Loss": sl_points,
    "Target": target_points,
    "EMA Filter": "ON" if ema_filter_enabled else "OFF",
    "EMA Threshold": ema_threshold,
    "RSI Filter": "ON" if rsi_filter_enabled else "OFF",
    "RSI Min": rsi_min,
    "RSI Max": rsi_max,
    "Mode": "Paper Trading Only",
    "Data Feed": "Yahoo Finance Demo",
}

st.json(rules)