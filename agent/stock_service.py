from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf


DEFAULT_INDIAN_TICKERS = ["RELIANCE.NS", "TCS.NS"]


@dataclass
class StockSnapshot:
    ticker: str
    company_name: str
    currency: str
    last_price: float
    previous_close: float
    day_change: float
    day_change_pct: float
    volume: int
    data_source: str = "live"


DEMO_SNAPSHOT_DATA = {
    "RELIANCE.NS": {
        "company_name": "Reliance Industries Ltd",
        "currency": "INR",
        "last_price": 2968.50,
        "previous_close": 2951.20,
        "volume": 5123400,
    },
    "TCS.NS": {
        "company_name": "Tata Consultancy Services Ltd",
        "currency": "INR",
        "last_price": 4188.40,
        "previous_close": 4210.95,
        "volume": 2389100,
    },
}


def _demo_snapshot(ticker: str) -> Optional[StockSnapshot]:
    payload = DEMO_SNAPSHOT_DATA.get(ticker)
    if payload is None:
        return None

    last_price = float(payload["last_price"])
    previous_close = float(payload["previous_close"])
    day_change = last_price - previous_close
    day_change_pct = (day_change / previous_close * 100.0) if previous_close else 0.0

    return StockSnapshot(
        ticker=ticker,
        company_name=str(payload["company_name"]),
        currency=str(payload["currency"]),
        last_price=last_price,
        previous_close=previous_close,
        day_change=day_change,
        day_change_pct=day_change_pct,
        volume=int(payload["volume"]),
        data_source="demo",
    )


def _demo_history(ticker: str) -> pd.DataFrame:
    snapshot = _demo_snapshot(ticker)
    if snapshot is None:
        return pd.DataFrame()

    base = snapshot.previous_close
    dates = pd.date_range(end=datetime.now(), periods=30, freq="D")
    rows = []
    for index, current_date in enumerate(dates):
        drift = (index - 15) * 0.002
        open_price = base * (1 + drift)
        close_price = open_price * (1 + (0.001 if index % 2 == 0 else -0.0008))
        high_price = max(open_price, close_price) * 1.004
        low_price = min(open_price, close_price) * 0.996
        volume = int(snapshot.volume * (0.85 + (index % 5) * 0.05))
        rows.append(
            {
                "Datetime": current_date,
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(close_price, 2),
                "Volume": volume,
            }
        )

    return pd.DataFrame(rows)


def normalize_ticker(raw_ticker: str) -> str:
    ticker = (raw_ticker or "").strip().upper()
    if not ticker:
        return ""
    return ticker


def fetch_stock_snapshot(ticker: str) -> Optional[StockSnapshot]:
    clean_ticker = normalize_ticker(ticker)
    if not clean_ticker:
        return None

    stock = yf.Ticker(clean_ticker)

    try:
        history = stock.history(period="5d", interval="1d")
    except Exception:
        return _demo_snapshot(clean_ticker)

    if history.empty:
        return _demo_snapshot(clean_ticker)

    close_series = history["Close"].dropna()
    if close_series.empty:
        return _demo_snapshot(clean_ticker)

    last_price = float(close_series.iloc[-1])
    previous_close = float(close_series.iloc[-2]) if len(close_series) > 1 else last_price
    volume = int(history["Volume"].iloc[-1]) if "Volume" in history.columns else 0

    company_name = clean_ticker
    currency = "INR" if clean_ticker.endswith(".NS") else "USD"

    try:
        fast_info = stock.fast_info
        if fast_info:
            last_price = float(fast_info.get("lastPrice") or last_price)
            previous_close = float(fast_info.get("previousClose") or previous_close)
            volume = int(fast_info.get("lastVolume") or volume)
            currency = fast_info.get("currency") or currency
    except Exception:
        pass

    previous_close = float(previous_close) if previous_close is not None else float(last_price)
    volume = int(volume) if volume is not None else 0
    day_change = float(last_price) - previous_close
    day_change_pct = (day_change / previous_close * 100.0) if previous_close else 0.0

    return StockSnapshot(
        ticker=clean_ticker,
        company_name=company_name,
        currency=currency,
        last_price=float(last_price),
        previous_close=previous_close,
        day_change=day_change,
        day_change_pct=day_change_pct,
        volume=volume,
        data_source="live",
    )


def fetch_price_history(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    clean_ticker = normalize_ticker(ticker)
    if not clean_ticker:
        return pd.DataFrame()

    stock = yf.Ticker(clean_ticker)
    try:
        history = stock.history(period=period, interval=interval)
    except Exception:
        return _demo_history(clean_ticker)

    if history.empty:
        return _demo_history(clean_ticker)

    history = history.reset_index()
    if "Date" in history.columns:
        history.rename(columns={"Date": "Datetime"}, inplace=True)

    return history
