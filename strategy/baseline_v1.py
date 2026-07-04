import pandas as pd

SL_POINTS = 50
TARGET_POINTS = 100
ENTRY_TIME = "09:40:00"


def run_baseline_v1(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    df["datetime"] = pd.to_datetime(df["date"])
    df["trade_date"] = df["datetime"].dt.date
    df["trade_time"] = df["datetime"].dt.time

    trades = []

    for trade_date, day in df.groupby("trade_date"):
        day = day.sort_values("datetime").reset_index(drop=True)

        signal_rows = day[day["datetime"].dt.strftime("%H:%M:%S") >= ENTRY_TIME]

        if signal_rows.empty:
            continue

        trade = None

        for idx, row in signal_rows.iterrows():
            if (
                row["ATR_Slope"] > 0
                and row["Gamma_Momentum"] > 0
                and row["EMA_Slope"] > 0
                and row["close"] > row["EMA20"]
            ):
                trade = {
                    "date": trade_date,
                    "type": "CE",
                    "entry_time": row["datetime"],
                    "entry_price": row["close"],
                    "entry_index": idx,
                }
                break

            if (
                row["ATR_Slope"] > 0
                and row["Gamma_Momentum"] < 0
                and row["EMA_Slope"] < 0
                and row["close"] < row["EMA20"]
            ):
                trade = {
                    "date": trade_date,
                    "type": "PE",
                    "entry_time": row["datetime"],
                    "entry_price": row["close"],
                    "entry_index": idx,
                }
                break

        if trade is None:
            continue

        entry = trade["entry_price"]

        if trade["type"] == "CE":
            sl = entry - SL_POINTS
            target = entry + TARGET_POINTS
        else:
            sl = entry + SL_POINTS
            target = entry - TARGET_POINTS

        exit_price = day.iloc[-1]["close"]
        exit_time = day.iloc[-1]["datetime"]
        result = "EOD"

        future = day.iloc[trade["entry_index"] + 1 :]

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

        if trade["type"] == "CE":
            points = exit_price - entry
        else:
            points = entry - exit_price

        trade.update(
            {
                "exit_time": exit_time,
                "exit_price": exit_price,
                "result": result,
                "points": points,
            }
        )

        trades.append(trade)

    trade_log = pd.DataFrame(trades)

    if trade_log.empty:
        return {}, trade_log

    wins = (trade_log["points"] > 0).sum()
    losses = (trade_log["points"] < 0).sum()
    gross_profit = trade_log.loc[trade_log["points"] > 0, "points"].sum()
    gross_loss = abs(trade_log.loc[trade_log["points"] < 0, "points"].sum())

    equity = trade_log["points"].cumsum()
    drawdown = equity - equity.cummax()

    summary = {
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

    return summary, trade_log