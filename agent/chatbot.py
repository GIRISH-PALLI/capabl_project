from __future__ import annotations

import re
from dataclasses import dataclass

from agent.stock_service import DEFAULT_INDIAN_TICKERS, fetch_stock_snapshot


@dataclass
class ChatResponse:
    text: str
    ticker: str | None = None


EXCHANGE_TICKER_PATTERN = re.compile(r"\b[A-Z]{2,10}\.(?:NS|BO|NSE|BSE)\b")


def _extract_ticker(user_message: str) -> str | None:
    message = (user_message or "").upper()

    explicit_exchange = EXCHANGE_TICKER_PATTERN.findall(message)
    if explicit_exchange:
        return explicit_exchange[0]

    known_tickers = set(DEFAULT_INDIAN_TICKERS)
    tokens = re.findall(r"\b[A-Z0-9.]{2,15}\b", message)
    for token in tokens:
        if token in known_tickers:
            return token

    aliases = {
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
    }
    for alias, ticker in aliases.items():
        if alias in message:
            return ticker

    return None


def _is_price_intent(user_message: str) -> bool:
    message = (user_message or "").lower()
    keywords = ["price", "stock", "quote", "latest", "trading", "market", "value"]
    return any(keyword in message for keyword in keywords)


def answer_query(user_message: str) -> ChatResponse:
    ticker = _extract_ticker(user_message)

    if not ticker and _is_price_intent(user_message):
        return ChatResponse(
            text=(
                "Please share a ticker symbol. Try RELIANCE.NS or TCS.NS. "
                f"Default supported Indian symbols: {', '.join(DEFAULT_INDIAN_TICKERS)}"
            )
        )

    if not ticker:
        return ChatResponse(
            text=(
                "I can help with stock price queries. Example: 'What is RELIANCE.NS price?' "
                "or 'Show TCS.NS stock'."
            )
        )

    snapshot = fetch_stock_snapshot(ticker)
    if snapshot is None:
        return ChatResponse(
            text=f"I could not fetch live data for {ticker}. Please verify the ticker and try again.",
            ticker=ticker,
        )

    direction = "up" if snapshot.day_change >= 0 else "down"
    source_note = " [demo data]" if snapshot.data_source == "demo" else ""
    text = (
        f"{snapshot.company_name} ({snapshot.ticker}) is trading at {snapshot.last_price:.2f} {snapshot.currency}. "
        f"It is {direction} {abs(snapshot.day_change):.2f} ({abs(snapshot.day_change_pct):.2f}%) vs previous close. "
        f"Volume: {snapshot.volume:,}.{source_note}"
    )
    return ChatResponse(text=text, ticker=snapshot.ticker)
