from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, sqrt

import numpy as np
import pandas as pd

from agent.stock_service import fetch_price_history, normalize_ticker


@dataclass
class MPTResult:
    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: dict[str, float]


@dataclass
class OptionPrice:
    call_price: float
    put_price: float


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def black_scholes_price(spot: float, strike: float, time_to_expiry: float, risk_free_rate: float, volatility: float) -> OptionPrice:
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        return OptionPrice(call_price=0.0, put_price=0.0)

    d1 = (log(spot / strike) + (risk_free_rate + 0.5 * volatility * volatility) * time_to_expiry) / (volatility * sqrt(time_to_expiry))
    d2 = d1 - volatility * sqrt(time_to_expiry)

    call = spot * _norm_cdf(d1) - strike * exp(-risk_free_rate * time_to_expiry) * _norm_cdf(d2)
    put = strike * exp(-risk_free_rate * time_to_expiry) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)
    return OptionPrice(call_price=float(call), put_price=float(put))


def optimize_portfolio_mpt(tickers: list[str], risk_free_rate: float = 0.06, simulations: int = 3000) -> MPTResult | None:
    clean = [normalize_ticker(t) for t in tickers if normalize_ticker(t)]
    if len(clean) < 2:
        return None

    close_map: dict[str, pd.Series] = {}
    for ticker in clean:
        history = fetch_price_history(ticker, period="1y", interval="1d")
        if history.empty or "Close" not in history.columns:
            continue
        close_map[ticker] = history["Close"].reset_index(drop=True)

    if len(close_map) < 2:
        return None

    frame = pd.DataFrame(close_map).dropna(how="any")
    if frame.empty:
        return None

    returns = frame.pct_change().dropna(how="any")
    if returns.empty:
        return None

    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    assets = list(mean_returns.index)
    num_assets = len(assets)

    best = {"sharpe": -1e9, "ret": 0.0, "vol": 0.0, "weights": np.ones(num_assets) / num_assets}

    for _ in range(max(500, simulations)):
        weights = np.random.random(num_assets)
        weights = weights / np.sum(weights)

        portfolio_return = float(np.dot(weights, mean_returns.values))
        portfolio_vol = float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights))))
        if portfolio_vol <= 0:
            continue

        sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
        if sharpe > best["sharpe"]:
            best = {"sharpe": sharpe, "ret": portfolio_return, "vol": portfolio_vol, "weights": weights}

    return MPTResult(
        expected_return=float(best["ret"]),
        volatility=float(best["vol"]),
        sharpe_ratio=float(best["sharpe"]),
        weights={asset: float(weight) for asset, weight in zip(assets, best["weights"])},
    )
