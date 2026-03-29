from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finance.sqlite3"


@dataclass
class WatchlistItem:
    id: int
    list_name: str
    ticker: str
    notes: str


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_sqlite() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(list_name, ticker)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                direction TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_to_watchlist(list_name: str, ticker: str, notes: str = "") -> bool:
    initialize_sqlite()
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO watchlists(list_name, ticker, notes) VALUES(?, ?, ?)",
                (list_name.strip() or "default", ticker.strip().upper(), notes.strip()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_from_watchlist(list_name: str, ticker: str) -> bool:
    initialize_sqlite()
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM watchlists WHERE list_name = ? AND ticker = ?",
            (list_name.strip() or "default", ticker.strip().upper()),
        )
    return cur.rowcount > 0


def get_watchlist(list_name: str = "default") -> list[WatchlistItem]:
    initialize_sqlite()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, list_name, ticker, notes FROM watchlists WHERE list_name = ? ORDER BY ticker",
            (list_name.strip() or "default",),
        ).fetchall()

    return [
        WatchlistItem(id=int(row["id"]), list_name=str(row["list_name"]), ticker=str(row["ticker"]), notes=str(row["notes"]))
        for row in rows
    ]


def add_alert(ticker: str, rule_type: str, threshold: float, direction: str = "above") -> None:
    initialize_sqlite()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO alerts(ticker, rule_type, threshold, direction) VALUES(?, ?, ?, ?)",
            (ticker.strip().upper(), rule_type.strip().lower(), float(threshold), direction.strip().lower()),
        )


def list_alerts(active_only: bool = True) -> list[sqlite3.Row]:
    initialize_sqlite()
    query = "SELECT * FROM alerts"
    params: tuple[int, ...] | tuple[()] = tuple()
    if active_only:
        query += " WHERE is_active = ?"
        params = (1,)
    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        return conn.execute(query, params).fetchall()


def deactivate_alert(alert_id: int) -> None:
    initialize_sqlite()
    with _connect() as conn:
        conn.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (int(alert_id),))
