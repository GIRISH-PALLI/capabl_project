from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = dt_time(hour=9, minute=15)
MARKET_CLOSE = dt_time(hour=15, minute=30)


@dataclass
class MarketHoursStatus:
    is_open: bool
    session: str
    now_ist: datetime
    opens_at_ist: datetime
    closes_at_ist: datetime


def ensure_indian_ticker(raw_ticker: str) -> str:
    ticker = (raw_ticker or "").strip().upper()
    if not ticker:
        return ""

    if "." in ticker:
        return ticker

    return f"{ticker}.NS"


def format_inr(value: float) -> str:
    return f"INR {value:,.2f}"


def get_market_hours_status(now: datetime | None = None) -> MarketHoursStatus:
    current = (now or datetime.now(tz=IST)).astimezone(IST)

    opens_at = current.replace(hour=MARKET_OPEN.hour, minute=MARKET_OPEN.minute, second=0, microsecond=0)
    closes_at = current.replace(hour=MARKET_CLOSE.hour, minute=MARKET_CLOSE.minute, second=0, microsecond=0)

    is_weekday = current.weekday() < 5
    in_session = MARKET_OPEN <= current.time().replace(tzinfo=None) <= MARKET_CLOSE

    if is_weekday and in_session:
        session = "Regular Trading"
    elif is_weekday and current.time().replace(tzinfo=None) < MARKET_OPEN:
        session = "Pre-open/Before market"
    elif is_weekday:
        session = "After market"
    else:
        session = "Weekend"

    return MarketHoursStatus(
        is_open=bool(is_weekday and in_session),
        session=session,
        now_ist=current,
        opens_at_ist=opens_at,
        closes_at_ist=closes_at,
    )
