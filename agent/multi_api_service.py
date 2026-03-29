from __future__ import annotations

import os
from dataclasses import dataclass
from time import sleep
from typing import Any

import requests


@dataclass
class ApiResult:
    provider: str
    success: bool
    payload: dict[str, Any]
    error: str = ""


def _safe_get(url: str, params: dict[str, Any] | None = None, timeout: int = 8, retries: int = 2) -> dict[str, Any]:
    params = params or {}
    last_error = ""

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = str(exc)
            if attempt < retries:
                sleep(0.4 * (attempt + 1))

    raise RuntimeError(last_error)


def _alpha_vantage_quote(symbol: str) -> ApiResult:
    key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    if not key:
        return ApiResult(provider="alpha_vantage", success=False, payload={}, error="missing api key")

    try:
        payload = _safe_get(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": key},
        )
        return ApiResult(provider="alpha_vantage", success=True, payload=payload)
    except Exception as exc:
        return ApiResult(provider="alpha_vantage", success=False, payload={}, error=str(exc))


def _finnhub_quote(symbol: str) -> ApiResult:
    key = os.getenv("FINNHUB_API_KEY", "")
    if not key:
        return ApiResult(provider="finnhub", success=False, payload={}, error="missing api key")

    try:
        payload = _safe_get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": key},
        )
        return ApiResult(provider="finnhub", success=True, payload=payload)
    except Exception as exc:
        return ApiResult(provider="finnhub", success=False, payload={}, error=str(exc))


def _fmp_quote(symbol: str) -> ApiResult:
    key = os.getenv("FMP_API_KEY", "")
    if not key:
        return ApiResult(provider="financial_modeling_prep", success=False, payload={}, error="missing api key")

    try:
        payload = _safe_get(
            f"https://financialmodelingprep.com/api/v3/quote/{symbol}",
            params={"apikey": key},
        )
        return ApiResult(provider="financial_modeling_prep", success=True, payload={"data": payload})
    except Exception as exc:
        return ApiResult(provider="financial_modeling_prep", success=False, payload={}, error=str(exc))


def _twelve_data_quote(symbol: str) -> ApiResult:
    key = os.getenv("TWELVE_DATA_API_KEY", "")
    if not key:
        return ApiResult(provider="twelve_data", success=False, payload={}, error="missing api key")

    try:
        payload = _safe_get(
            "https://api.twelvedata.com/quote",
            params={"symbol": symbol, "apikey": key},
        )
        return ApiResult(provider="twelve_data", success=True, payload=payload)
    except Exception as exc:
        return ApiResult(provider="twelve_data", success=False, payload={}, error=str(exc))


def _fred_indicator(series_id: str = "DGS10") -> ApiResult:
    key = os.getenv("FRED_API_KEY", "")
    if not key:
        return ApiResult(provider="fred", success=False, payload={}, error="missing api key")

    try:
        payload = _safe_get(
            "https://api.stlouisfed.org/fred/series/observations",
            params={"series_id": series_id, "api_key": key, "file_type": "json", "sort_order": "desc", "limit": 1},
        )
        return ApiResult(provider="fred", success=True, payload=payload)
    except Exception as exc:
        return ApiResult(provider="fred", success=False, payload={}, error=str(exc))


def _exchangerate_inr() -> ApiResult:
    try:
        payload = _safe_get("https://api.exchangerate.host/latest", params={"base": "USD", "symbols": "INR"})
        return ApiResult(provider="exchangerate_host", success=True, payload=payload)
    except Exception as exc:
        return ApiResult(provider="exchangerate_host", success=False, payload={}, error=str(exc))


def fetch_multi_api_snapshot(symbol: str) -> list[ApiResult]:
    return [
        _alpha_vantage_quote(symbol),
        _finnhub_quote(symbol),
        _fmp_quote(symbol),
        _twelve_data_quote(symbol),
        _fred_indicator(),
        _exchangerate_inr(),
    ]
