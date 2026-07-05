import pandas as pd
import numpy as np


def calculate_rsi(close, period=14):
    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def calculate_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr.fillna(0)


def build_live_indicator_table(raw_df):
    df = raw_df.copy()

    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "Datetime": "datetime",
        "Date": "datetime",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }

    df = df.rename(columns=rename_map)

    df["datetime"] = pd.to_datetime(df["datetime"])

    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if "volume" not in df.columns:
        df["volume"] = 0

    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)

    df = df.dropna(subset=["datetime", "open", "high", "low", "close"])
    df = df.sort_values("datetime").reset_index(drop=True)

    # EMAs
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()

    df["EMA_Slope"] = df["EMA20"] - df["EMA20"].shift(1)

    # RSI
    df["RSI14"] = calculate_rsi(df["close"], 14)

    # ATR
    atr_df = df.rename(columns={"high": "High", "low": "Low", "close": "Close"})
    df["ATR14"] = calculate_atr(atr_df, 14)
    df["ATR_Slope"] = df["ATR14"] - df["ATR14"].shift(1)

    # VWAP
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_pv = (typical_price * df["volume"]).cumsum()
    cumulative_volume = df["volume"].replace(0, np.nan).cumsum()
    df["VWAP"] = cumulative_pv / cumulative_volume
    df["VWAP"] = df["VWAP"].fillna(df["close"])

    # Candle structure
    df["Range"] = df["high"] - df["low"]
    df["Candle_Body"] = (df["close"] - df["open"]).abs()
    df["Upper_Wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["Lower_Wick"] = df[["open", "close"]].min(axis=1) - df["low"]

    # Relative position
    df["Distance_from_EMA20"] = df["close"] - df["EMA20"]
    df["Distance_from_VWAP"] = df["close"] - df["VWAP"]

    # Previous candle breakout
    df["Previous_High"] = df["high"].shift(1)
    df["Previous_Low"] = df["low"].shift(1)

    # Gamma Momentum approximation
    df["Price_Change"] = df["close"] - df["close"].shift(1)
    df["Momentum_3"] = df["close"] - df["close"].shift(3)
    df["Gamma_Momentum"] = df["Momentum_3"] / df["ATR14"].replace(0, np.nan)
    df["Gamma_Momentum"] = df["Gamma_Momentum"].fillna(0)

    # Volume filters
    df["Volume_MA20"] = df["volume"].rolling(20).mean().fillna(0)
    df["Volume_Ratio"] = df["volume"] / df["Volume_MA20"].replace(0, np.nan)
    df["Volume_Ratio"] = df["Volume_Ratio"].fillna(0)

    # Trend label
    df["Trend"] = np.where(
        (df["close"] > df["EMA20"]) & (df["EMA_Slope"] > 0),
        "Bullish",
        np.where(
            (df["close"] < df["EMA20"]) & (df["EMA_Slope"] < 0),
            "Bearish",
            "Neutral",
        ),
    )

    # Basic signal label
    df["Signal"] = "WAIT"

    ce_condition = (
        (df["ATR_Slope"] > 0)
        & (df["Gamma_Momentum"] > 0)
        & (df["EMA_Slope"] > 0)
        & (df["close"] > df["EMA20"])
    )

    pe_condition = (
        (df["ATR_Slope"] > 0)
        & (df["Gamma_Momentum"] < 0)
        & (df["EMA_Slope"] < 0)
        & (df["close"] < df["EMA20"])
    )

    df.loc[ce_condition, "Signal"] = "BUY CE"
    df.loc[pe_condition, "Signal"] = "BUY PE"

    return df