from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yfinance as yf

from agent.india_market import ensure_indian_ticker


@dataclass
class FundamentalSnapshot:
    ticker: str
    sector: str
    industry: str
    pe_ratio: float
    debt_to_equity: float
    revenue_growth: float
    earnings_growth: float
    return_on_equity: float
    market_cap: float


@dataclass
class SectorComparisonRow:
    ticker: str
    sector: str
    pe_ratio: float
    debt_to_equity: float
    revenue_growth: float
    earnings_growth: float
    roe: float


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_fundamental_snapshot(ticker: str) -> FundamentalSnapshot:
    clean = ensure_indian_ticker(ticker)
    info = {}
    try:
        info = yf.Ticker(clean).info or {}
    except Exception:
        info = {}

    return FundamentalSnapshot(
        ticker=clean,
        sector=str(info.get("sector") or "Unknown"),
        industry=str(info.get("industry") or "Unknown"),
        pe_ratio=_to_float(info.get("trailingPE") or info.get("forwardPE")),
        debt_to_equity=_to_float(info.get("debtToEquity")),
        revenue_growth=_to_float(info.get("revenueGrowth")),
        earnings_growth=_to_float(info.get("earningsGrowth")),
        return_on_equity=_to_float(info.get("returnOnEquity")),
        market_cap=_to_float(info.get("marketCap")),
    )


def compare_sector(tickers: list[str]) -> list[SectorComparisonRow]:
    rows: list[SectorComparisonRow] = []
    for ticker in tickers:
        snap = get_fundamental_snapshot(ticker)
        rows.append(
            SectorComparisonRow(
                ticker=snap.ticker,
                sector=snap.sector,
                pe_ratio=snap.pe_ratio,
                debt_to_equity=snap.debt_to_equity,
                revenue_growth=snap.revenue_growth,
                earnings_growth=snap.earnings_growth,
                roe=snap.return_on_equity,
            )
        )
    return rows
