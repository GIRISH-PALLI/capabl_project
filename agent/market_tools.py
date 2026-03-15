from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from time import sleep, time
from typing import Any

import yfinance as yf

from agent.sentiment_service import (
    SentimentReport,
    analyze_sentiment_simple,
    analyze_sentiment_transformer,
    fetch_news_items,
)
from agent.stock_service import fetch_price_history, fetch_stock_snapshot, normalize_ticker
from agent.technical_analysis import TechnicalSnapshot, latest_technical_snapshot


_RATE_LIMIT_SECONDS = 0.4
_last_call_at = 0.0
_cache: dict[str, tuple[float, Any]] = {}
_CACHE_TTL_SECONDS = 300


@dataclass
class StockResearch:
    ticker: str
    snapshot: Any
    technicals: TechnicalSnapshot
    sentiment: SentimentReport


@dataclass
class OptionContractSummary:
    expiration: str
    call_open_interest: int
    put_open_interest: int
    put_call_ratio: float


@dataclass
class MacroInstrumentSnapshot:
    symbol: str
    name: str
    price: float
    day_change_pct: float


def _throttle() -> None:
    global _last_call_at
    now = time()
    elapsed = now - _last_call_at
    if elapsed < _RATE_LIMIT_SECONDS:
        sleep(_RATE_LIMIT_SECONDS - elapsed)
    _last_call_at = time()


def _cache_get(key: str) -> Any | None:
    payload = _cache.get(key)
    if payload is None:
        return None
    expires_at, value = payload
    if time() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def _cache_put(key: str, value: Any, ttl: int = _CACHE_TTL_SECONDS) -> Any:
    _cache[key] = (time() + ttl, value)
    return value


def _safe_fast_info(symbol: str) -> tuple[float, float]:
    _throttle()
    stock = yf.Ticker(symbol)
    info = stock.fast_info or {}
    last_price = float(info.get("lastPrice") or 0.0)
    prev_close = float(info.get("previousClose") or last_price)
    change_pct = ((last_price - prev_close) / prev_close * 100.0) if prev_close else 0.0
    return last_price, change_pct


def get_stock_research(ticker: str, use_transformer: bool = False) -> StockResearch | None:
    clean_ticker = normalize_ticker(ticker)
    if not clean_ticker:
        return None

    cache_key = f"stock-research:{clean_ticker}:{use_transformer}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    snapshot = fetch_stock_snapshot(clean_ticker)
    if snapshot is None:
        return None

    history = fetch_price_history(clean_ticker, period="6mo", interval="1d")
    technicals = latest_technical_snapshot(history)

    news = fetch_news_items(clean_ticker, max_items=10)
    if use_transformer:
        sentiment = analyze_sentiment_transformer(news)
    else:
        sentiment = analyze_sentiment_simple(news)

    result = StockResearch(
        ticker=clean_ticker,
        snapshot=snapshot,
        technicals=technicals,
        sentiment=sentiment,
    )
    return _cache_put(cache_key, result)


def compare_stocks(tickers: list[str], use_transformer: bool = False) -> list[StockResearch]:
    unique_tickers = []
    seen: set[str] = set()
    for ticker in tickers:
        clean = normalize_ticker(ticker)
        if clean and clean not in seen:
            seen.add(clean)
            unique_tickers.append(clean)

    result: list[StockResearch] = []
    for ticker in unique_tickers:
        research = get_stock_research(ticker, use_transformer=use_transformer)
        if research is not None:
            result.append(research)
    return result


def get_options_tool(ticker: str) -> list[OptionContractSummary]:
    clean_ticker = normalize_ticker(ticker)
    if not clean_ticker:
        return []

    cache_key = f"options:{clean_ticker}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    stock = yf.Ticker(clean_ticker)
    try:
        _throttle()
        expirations = stock.options or []
    except Exception:
        return _cache_put(cache_key, [], ttl=90)

    rows: list[OptionContractSummary] = []
    for exp in expirations[:3]:
        try:
            _throttle()
            chain = stock.option_chain(exp)
            call_oi = int(chain.calls.get("openInterest", []).sum()) if not chain.calls.empty else 0
            put_oi = int(chain.puts.get("openInterest", []).sum()) if not chain.puts.empty else 0
            ratio = (put_oi / call_oi) if call_oi else 0.0
            rows.append(
                OptionContractSummary(
                    expiration=exp,
                    call_open_interest=call_oi,
                    put_open_interest=put_oi,
                    put_call_ratio=ratio,
                )
            )
        except Exception:
            continue

    return _cache_put(cache_key, rows, ttl=180)


def get_futures_tool() -> list[MacroInstrumentSnapshot]:
    cache_key = "futures"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    instruments = {
        "GC=F": "Gold Futures",
        "CL=F": "Crude Oil Futures",
        "SI=F": "Silver Futures",
    }
    rows: list[MacroInstrumentSnapshot] = []
    for symbol, name in instruments.items():
        try:
            price, change_pct = _safe_fast_info(symbol)
        except Exception:
            price, change_pct = 0.0, 0.0
        rows.append(MacroInstrumentSnapshot(symbol=symbol, name=name, price=price, day_change_pct=change_pct))

    return _cache_put(cache_key, rows)


def get_bonds_tool() -> list[MacroInstrumentSnapshot]:
    cache_key = "bonds"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    instruments = {
        "^TNX": "US 10Y Treasury Yield",
        "^TYX": "US 30Y Treasury Yield",
        "^FVX": "US 5Y Treasury Yield",
    }
    rows: list[MacroInstrumentSnapshot] = []
    for symbol, name in instruments.items():
        try:
            price, change_pct = _safe_fast_info(symbol)
        except Exception:
            price, change_pct = 0.0, 0.0
        rows.append(MacroInstrumentSnapshot(symbol=symbol, name=name, price=price, day_change_pct=change_pct))

    return _cache_put(cache_key, rows)


def get_economic_indicators_tool() -> list[MacroInstrumentSnapshot]:
    cache_key = "economic-indicators"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    instruments = {
        "^VIX": "CBOE Volatility Index",
        "DX-Y.NYB": "US Dollar Index",
        "^GSPC": "S&P 500 Index",
    }
    rows: list[MacroInstrumentSnapshot] = []
    for symbol, name in instruments.items():
        try:
            price, change_pct = _safe_fast_info(symbol)
        except Exception:
            price, change_pct = 0.0, 0.0
        rows.append(MacroInstrumentSnapshot(symbol=symbol, name=name, price=price, day_change_pct=change_pct))

    return _cache_put(cache_key, rows)


def etl_market_snapshot(tickers: list[str]) -> dict[str, Any]:
    result = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "stocks": compare_stocks(tickers),
        "futures": get_futures_tool(),
        "bonds": get_bonds_tool(),
        "economic_indicators": get_economic_indicators_tool(),
    }
    return result
