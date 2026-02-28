from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.chatbot import answer_query
from agent.stock_service import DEFAULT_INDIAN_TICKERS, fetch_price_history, fetch_stock_snapshot


st.set_page_config(page_title="Financial Research AI - CAPABL", layout="wide")

CACHE_VERSION = "v2"


@st.cache_data(ttl=300, show_spinner=False)
def _get_snapshot_cached(ticker: str, cache_version: str):
    return fetch_stock_snapshot(ticker)


@st.cache_data(ttl=300, show_spinner=False)
def _get_history_cached(ticker: str, period: str, interval: str, cache_version: str) -> pd.DataFrame:
    return fetch_price_history(ticker=ticker, period=period, interval=interval)


def _render_chart(history: pd.DataFrame, ticker: str) -> None:
    if history.empty:
        st.warning("No chart data available for this ticker.")
        return

    x_col = "Datetime" if "Datetime" in history.columns else history.columns[0]

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=history[x_col],
                open=history["Open"],
                high=history["High"],
                low=history["Low"],
                close=history["Close"],
                name=ticker,
            )
        ]
    )
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_snapshot(ticker: str) -> None:
    snapshot = _get_snapshot_cached(ticker, CACHE_VERSION)
    if snapshot is None:
        st.warning("Unable to fetch live market snapshot right now (possibly temporary rate limit). Please retry in a minute.")
        return

    if snapshot.data_source == "demo":
        st.info("Showing demo market data because live Yahoo Finance is temporarily rate-limited.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ticker", snapshot.ticker)
    c2.metric("Last Price", f"{snapshot.last_price:.2f} {snapshot.currency}")
    c3.metric("Daily Change", f"{snapshot.day_change:.2f}", f"{snapshot.day_change_pct:.2f}%")
    c4.metric("Volume", f"{snapshot.volume:,}")


def main() -> None:
    st.title("Financial Research AI Agent - Week 1 & 2 MVP")
    st.caption("CAPABL Internship Project | Track A (Essential)")

    with st.sidebar:
        st.subheader("Quick Tickers")
        ticker = st.selectbox("Select ticker", DEFAULT_INDIAN_TICKERS, index=0)
        period = st.selectbox("Chart period", ["1mo", "3mo", "6mo", "1y"], index=1)
        interval = st.selectbox("Interval", ["1d", "1h"], index=0)
        if st.button("Refresh data cache"):
            st.cache_data.clear()
            st.rerun()

    _render_snapshot(ticker)
    history = _get_history_cached(ticker=ticker, period=period, interval=interval, cache_version=CACHE_VERSION)
    _render_chart(history, ticker)

    st.divider()
    st.subheader("Stock Price Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for role, message in st.session_state.messages:
        with st.chat_message(role):
            st.write(message)

    prompt = st.chat_input("Ask: What is RELIANCE.NS price?")
    if prompt:
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        response = answer_query(prompt)
        st.session_state.messages.append(("assistant", response.text))
        with st.chat_message("assistant"):
            st.write(response.text)

        if response.ticker:
            chat_history = _get_history_cached(response.ticker, period="1mo", interval="1d", cache_version=CACHE_VERSION)
            st.markdown("### Chart from chat ticker")
            _render_chart(chat_history, response.ticker)


if __name__ == "__main__":
    main()
