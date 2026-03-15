from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class TechnicalSnapshot:
    sma_20: float
    sma_50: float
    ema_20: float
    rsi_14: float
    macd: float
    macd_signal: float
    bb_upper: float
    bb_lower: float
    atr_14: float


def _safe_last(series: pd.Series) -> float:
    clean = series.dropna()
    return float(clean.iloc[-1]) if not clean.empty else 0.0


def moving_average(series: pd.Series, window: int = 20) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def exponential_moving_average(series: pd.Series, span: int = 20) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series.fillna(50.0)


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series]:
    ema_fast = exponential_moving_average(series, span=fast)
    ema_slow = exponential_moving_average(series, span=slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series]:
    mean = moving_average(series, window=window)
    std = series.rolling(window=window, min_periods=window).std()
    upper = mean + num_std * std
    lower = mean - num_std * std
    return upper, lower


def average_true_range(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Close" not in df.columns:
        return df

    result = df.copy()
    result["SMA_20"] = moving_average(result["Close"], window=20)
    result["SMA_50"] = moving_average(result["Close"], window=50)
    result["EMA_20"] = exponential_moving_average(result["Close"], span=20)
    result["RSI_14"] = rsi(result["Close"], period=14)

    macd_line, signal_line = macd(result["Close"])
    result["MACD"] = macd_line
    result["MACD_SIGNAL"] = signal_line

    bb_upper, bb_lower = bollinger_bands(result["Close"], window=20)
    result["BB_UPPER"] = bb_upper
    result["BB_LOWER"] = bb_lower

    if {"High", "Low", "Close"}.issubset(result.columns):
        result["ATR_14"] = average_true_range(result, period=14)
    else:
        result["ATR_14"] = pd.NA

    return result


def latest_technical_snapshot(df: pd.DataFrame) -> TechnicalSnapshot:
    enriched = add_indicators(df)
    return TechnicalSnapshot(
        sma_20=_safe_last(enriched.get("SMA_20", pd.Series(dtype=float))),
        sma_50=_safe_last(enriched.get("SMA_50", pd.Series(dtype=float))),
        ema_20=_safe_last(enriched.get("EMA_20", pd.Series(dtype=float))),
        rsi_14=_safe_last(enriched.get("RSI_14", pd.Series(dtype=float))),
        macd=_safe_last(enriched.get("MACD", pd.Series(dtype=float))),
        macd_signal=_safe_last(enriched.get("MACD_SIGNAL", pd.Series(dtype=float))),
        bb_upper=_safe_last(enriched.get("BB_UPPER", pd.Series(dtype=float))),
        bb_lower=_safe_last(enriched.get("BB_LOWER", pd.Series(dtype=float))),
        atr_14=_safe_last(enriched.get("ATR_14", pd.Series(dtype=float))),
    )
