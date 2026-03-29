from __future__ import annotations

from dataclasses import dataclass

from agent.stock_service import fetch_stock_snapshot
from agent.watchlist_db import deactivate_alert, list_alerts


@dataclass
class TriggeredAlert:
    id: int
    ticker: str
    message: str
    observed_value: float


def evaluate_price_alerts() -> list[TriggeredAlert]:
    triggered: list[TriggeredAlert] = []
    for row in list_alerts(active_only=True):
        alert_id = int(row["id"])
        ticker = str(row["ticker"])
        rule_type = str(row["rule_type"])
        threshold = float(row["threshold"])
        direction = str(row["direction"])

        if rule_type != "price":
            continue

        snapshot = fetch_stock_snapshot(ticker)
        if snapshot is None:
            continue

        current = float(snapshot.last_price)
        hit = (direction == "above" and current >= threshold) or (direction == "below" and current <= threshold)
        if not hit:
            continue

        message = f"{ticker} price {current:.2f} crossed {direction} {threshold:.2f}"
        triggered.append(TriggeredAlert(id=alert_id, ticker=ticker, message=message, observed_value=current))
        deactivate_alert(alert_id)

    return triggered
