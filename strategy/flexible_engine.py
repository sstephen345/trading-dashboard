import strategy.baseline_v1 as baseline
from strategy.baseline_v1 import run_baseline_v1


def run_flexible_strategy(
    df,
    sl_points=50,
    target_points=100,
    allow_ce=True,
    allow_pe=True,
    ema_filter_enabled=False,
    ema_threshold=0.0,
):
    old_sl = baseline.SL_POINTS
    old_target = baseline.TARGET_POINTS

    baseline.SL_POINTS = sl_points
    baseline.TARGET_POINTS = target_points

    summary, trade_log = run_baseline_v1(df)

    baseline.SL_POINTS = old_sl
    baseline.TARGET_POINTS = old_target

    if trade_log.empty:
        return summary, trade_log

    if not allow_ce:
        trade_log = trade_log[trade_log["type"] != "CE"]

    if not allow_pe:
        trade_log = trade_log[trade_log["type"] != "PE"]

    if ema_filter_enabled:
        if "entry_ema_slope" in trade_log.columns:
            trade_log = trade_log[
                ((trade_log["type"] == "CE") & (trade_log["entry_ema_slope"] >= ema_threshold))
                | ((trade_log["type"] == "PE") & (trade_log["entry_ema_slope"] <= -ema_threshold))
            ]

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