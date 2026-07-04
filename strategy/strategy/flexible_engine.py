from strategy.baseline_v1 import run_baseline_v1
import strategy.baseline_v1 as baseline


def run_flexible_strategy(df, sl_points=50, target_points=100):
    old_sl = baseline.SL_POINTS
    old_target = baseline.TARGET_POINTS

    baseline.SL_POINTS = sl_points
    baseline.TARGET_POINTS = target_points

    summary, trade_log = run_baseline_v1(df)

    baseline.SL_POINTS = old_sl
    baseline.TARGET_POINTS = old_target

    return summary, trade_log