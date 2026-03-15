from __future__ import annotations

from dataclasses import dataclass

from agent.stock_service import fetch_price_history, fetch_stock_snapshot, normalize_ticker


@dataclass
class Holding:
    ticker: str
    quantity: float
    average_cost: float


@dataclass
class PortfolioReport:
    invested_value: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    daily_pnl: float


def _holding_daily_change(ticker: str) -> float:
    history = fetch_price_history(ticker, period="5d", interval="1d")
    if history.empty or "Close" not in history.columns:
        return 0.0

    closes = history["Close"].dropna()
    if len(closes) < 2:
        return 0.0

    return float(closes.iloc[-1] - closes.iloc[-2])


def analyze_portfolio(holdings: list[Holding]) -> PortfolioReport:
    invested = 0.0
    market = 0.0
    daily_pnl = 0.0

    for holding in holdings:
        ticker = normalize_ticker(holding.ticker)
        if not ticker or holding.quantity <= 0:
            continue

        snapshot = fetch_stock_snapshot(ticker)
        if snapshot is None:
            continue

        invested += holding.quantity * holding.average_cost
        market += holding.quantity * snapshot.last_price
        daily_pnl += holding.quantity * _holding_daily_change(ticker)

    pnl = market - invested
    pnl_pct = (pnl / invested * 100.0) if invested else 0.0

    return PortfolioReport(
        invested_value=invested,
        market_value=market,
        unrealized_pnl=pnl,
        unrealized_pnl_pct=pnl_pct,
        daily_pnl=daily_pnl,
    )
