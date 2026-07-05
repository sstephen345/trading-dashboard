import pandas as pd


def calculate_summary(trade_log):
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
        "ce_trades": int((trade_log["type"] == "CE").sum()),
        "pe_trades": int((trade_log["type"] == "PE").sum()),
    }


def run_flexible_strategy(
    df,
    sl_points=50,
    target_points=100,
    allow_ce=True,
    allow_pe=True,
    ema_filter_enabled=False,
    ema_threshold=0.0,
    atr_filter_enabled=False,
    atr_threshold=0.0,
    gamma_filter_enabled=False,
    gamma_threshold=0.0,
):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    df["datetime"] = pd.to_datetime(df["date"])
    df["trade_date"] = df["datetime"].dt.date
    df["trade_time_str"] = df["datetime"].dt.strftime("%H:%M:%S")

    ENTRY_TIME = "09:40:00"
    EOD_EXIT_TIME = "15:15:00"

    trades = []

    for trade_date, day in df.groupby("trade_date"):
        day = day.sort_values("datetime").reset_index(drop=True)
        signal_rows = day[day["trade_time_str"] >= ENTRY_TIME]

        trade = None

        for idx, row in signal_rows.iterrows():

            ce_condition = (
                allow_ce
                and row["ATR_Slope"] > 0
                and row["Gamma_Momentum"] > 0
                and row["EMA_Slope"] > 0
                and row["close"] > row["EMA20"]
            )

            pe_condition = (
                allow_pe
                and row["ATR_Slope"] > 0
                and row["Gamma_Momentum"] < 0
                and row["EMA_Slope"] < 0
                and row["close"] < row["EMA20"]
            )

            if ema_filter_enabled:
                ce_condition = ce_condition and row["EMA_Slope"] >= ema_threshold
                pe_condition = pe_condition and row["EMA_Slope"] <= -ema_threshold

            if atr_filter_enabled:
                ce_condition = ce_condition and row["ATR_Slope"] >= atr_threshold
                pe_condition = pe_condition and row["ATR_Slope"] >= atr_threshold

            if gamma_filter_enabled:
                ce_condition = ce_condition and row["Gamma_Momentum"] >= gamma_threshold
                pe_condition = pe_condition and row["Gamma_Momentum"] <= -gamma_threshold

            if ce_condition:
                trade = {
                    "date": trade_date,
                    "type": "CE",
                    "entry_time": row["datetime"],
                    "entry_price": row["close"],
                    "entry_index": idx,
                    "entry_ema_slope": row["EMA_Slope"],
                    "entry_atr_slope": row["ATR_Slope"],
                    "entry_gamma": row["Gamma_Momentum"],
                }
                break

            if pe_condition:
                trade = {
                    "date": trade_date,
                    "type": "PE",
                    "entry_time": row["datetime"],
                    "entry_price": row["close"],
                    "entry_index": idx,
                    "entry_ema_slope": row["EMA_Slope"],
                    "entry_atr_slope": row["ATR_Slope"],
                    "entry_gamma": row["Gamma_Momentum"],
                }
                break

        if trade is None:
            continue

        entry = trade["entry_price"]

        if trade["type"] == "CE":
            sl = entry - sl_points
            target = entry + target_points
        else:
            sl = entry + sl_points
            target = entry - target_points

        eod_rows = day[day["trade_time_str"] <= EOD_EXIT_TIME]
        eod_row = eod_rows.iloc[-1]

        exit_price = eod_row["close"]
        exit_time = eod_row["datetime"]
        result = "EOD"

        future = day[
            (day.index > trade["entry_index"])
            & (day["trade_time_str"] <= EOD_EXIT_TIME)
        ]

        for _, r in future.iterrows():
            if trade["type"] == "CE":
                sl_hit = r["low"] <= sl
                target_hit = r["high"] >= target

                if sl_hit:
                    exit_price = sl
                    exit_time = r["datetime"]
                    result = "SL"
                    break

                if target_hit:
                    exit_price = target
                    exit_time = r["datetime"]
                    result = "TARGET"
                    break

            else:
                sl_hit = r["high"] >= sl
                target_hit = r["low"] <= target

                if sl_hit:
                    exit_price = sl
                    exit_time = r["datetime"]
                    result = "SL"
                    break

                if target_hit:
                    exit_price = target
                    exit_time = r["datetime"]
                    result = "TARGET"
                    break

        points = exit_price - entry if trade["type"] == "CE" else entry - exit_price

        trade.update(
            {
                "sl": sl,
                "target": target,
                "exit_time": exit_time,
                "exit_price": exit_price,
                "result": result,
                "points": points,
            }
        )

        trades.append(trade)

    trade_log = pd.DataFrame(trades)
    summary = calculate_summary(trade_log)

    return summary, trade_log