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
from agent.market_tools import (
    compare_stocks,
    get_bonds_tool,
    get_economic_indicators_tool,
    get_futures_tool,
    get_stock_research,
)
from agent.portfolio import Holding, analyze_portfolio
from agent.research_workflow import run_financial_research
from agent.stock_service import DEFAULT_INDIAN_TICKERS, fetch_price_history
from agent.technical_analysis import add_indicators


st.set_page_config(page_title="Financial Research AI - CAPABL", layout="wide")

CACHE_VERSION = "v3"


@st.cache_data(ttl=300, show_spinner=False)
def _get_stock_research_cached(ticker: str, use_transformer: bool, cache_version: str):
    return get_stock_research(ticker, use_transformer=use_transformer)


@st.cache_data(ttl=300, show_spinner=False)
def _get_history_cached(ticker: str, period: str, interval: str, cache_version: str) -> pd.DataFrame:
    return fetch_price_history(ticker=ticker, period=period, interval=interval)


@st.cache_data(ttl=300, show_spinner=False)
def _get_comparison_cached(tickers: tuple[str, ...], use_transformer: bool, cache_version: str):
    return compare_stocks(list(tickers), use_transformer=use_transformer)


@st.cache_data(ttl=300, show_spinner=False)
def _get_macro_cached(cache_version: str):
    return {
        "futures": get_futures_tool(),
        "bonds": get_bonds_tool(),
        "economic": get_economic_indicators_tool(),
    }


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


def _render_indicator_chart(history: pd.DataFrame, ticker: str) -> None:
    if history.empty or "Close" not in history.columns:
        return

    enriched = add_indicators(history)
    x_col = "Datetime" if "Datetime" in enriched.columns else enriched.columns[0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=enriched[x_col], y=enriched["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=enriched[x_col], y=enriched["SMA_20"], mode="lines", name="SMA 20"))
    fig.add_trace(go.Scatter(x=enriched[x_col], y=enriched["SMA_50"], mode="lines", name="SMA 50"))
    fig.add_trace(go.Scatter(x=enriched[x_col], y=enriched["BB_UPPER"], mode="lines", name="BB Upper", opacity=0.5))
    fig.add_trace(go.Scatter(x=enriched[x_col], y=enriched["BB_LOWER"], mode="lines", name="BB Lower", opacity=0.5))

    fig.update_layout(
        title=f"{ticker} Technical Indicator Overlay",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_snapshot(ticker: str, use_transformer: bool) -> None:
    research = _get_stock_research_cached(ticker, use_transformer, CACHE_VERSION)
    if research is None:
        st.warning("Unable to fetch live market snapshot right now (possibly temporary rate limit). Please retry in a minute.")
        return

    snapshot = research.snapshot
    technicals = research.technicals
    sentiment = research.sentiment

    if snapshot.data_source == "demo":
        st.info("Showing demo market data because live Yahoo Finance is temporarily rate-limited.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ticker", snapshot.ticker)
    c2.metric("Last Price", f"{snapshot.last_price:.2f} {snapshot.currency}")
    c3.metric("Daily Change", f"{snapshot.day_change:.2f}", f"{snapshot.day_change_pct:.2f}%")
    c4.metric("Volume", f"{snapshot.volume:,}")
    c5.metric("RSI (14)", f"{technicals.rsi_14:.2f}")

    tc1, tc2, tc3, tc4 = st.columns(4)
    tc1.metric("SMA 20", f"{technicals.sma_20:.2f}")
    tc2.metric("SMA 50", f"{technicals.sma_50:.2f}")
    tc3.metric("MACD", f"{technicals.macd:.3f}")
    tc4.metric("Sentiment", f"{sentiment.label} ({sentiment.score:.3f})")
    st.caption(f"Sentiment source: {sentiment.source} from {sentiment.sample_size} recent headlines")


def _render_comparison_table(tickers: list[str], use_transformer: bool) -> None:
    research_rows = _get_comparison_cached(tuple(tickers), use_transformer, CACHE_VERSION)
    if not research_rows:
        st.warning("No comparison data is available for the selected tickers.")
        return

    rows = []
    for row in research_rows:
        rows.append(
            {
                "Ticker": row.snapshot.ticker,
                "Price": round(row.snapshot.last_price, 2),
                "DayChangePct": round(row.snapshot.day_change_pct, 2),
                "RSI14": round(row.technicals.rsi_14, 2),
                "SMA20": round(row.technicals.sma_20, 2),
                "SMA50": round(row.technicals.sma_50, 2),
                "Sentiment": row.sentiment.label,
                "SentimentScore": round(row.sentiment.score, 3),
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _render_portfolio_section(default_ticker: str) -> None:
    st.write("Add holdings to evaluate invested value, market value, unrealized P&L, and daily P&L.")

    if "portfolio_df" not in st.session_state:
        st.session_state.portfolio_df = pd.DataFrame(
            [
                {"ticker": default_ticker, "quantity": 10.0, "average_cost": 2800.0},
                {"ticker": "TCS.NS", "quantity": 5.0, "average_cost": 4100.0},
            ]
        )

    edited = st.data_editor(st.session_state.portfolio_df, num_rows="dynamic", use_container_width=True)
    st.session_state.portfolio_df = edited

    holdings: list[Holding] = []
    for row in edited.to_dict(orient="records"):
        holdings.append(
            Holding(
                ticker=str(row.get("ticker") or ""),
                quantity=float(row.get("quantity") or 0.0),
                average_cost=float(row.get("average_cost") or 0.0),
            )
        )

    report = analyze_portfolio(holdings)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Invested Value", f"{report.invested_value:.2f}")
    c2.metric("Market Value", f"{report.market_value:.2f}")
    c3.metric("Unrealized P&L", f"{report.unrealized_pnl:.2f}", f"{report.unrealized_pnl_pct:.2f}%")
    c4.metric("Daily P&L", f"{report.daily_pnl:.2f}")


def _render_macro_dashboard() -> None:
    macro = _get_macro_cached(CACHE_VERSION)
    st.markdown("#### Futures")
    st.dataframe(
        pd.DataFrame([x.__dict__ for x in macro["futures"]]),
        use_container_width=True,
    )

    st.markdown("#### Bonds")
    st.dataframe(
        pd.DataFrame([x.__dict__ for x in macro["bonds"]]),
        use_container_width=True,
    )

    st.markdown("#### Economic Indicators")
    st.dataframe(
        pd.DataFrame([x.__dict__ for x in macro["economic"]]),
        use_container_width=True,
    )


def _render_workflow_section(ticker: str, peers: list[str], use_transformer: bool) -> None:
    holdings_payload = []
    if "portfolio_df" in st.session_state:
        holdings_payload = st.session_state.portfolio_df.to_dict(orient="records")

    try:
        state = run_financial_research(
            ticker=ticker,
            peers=peers,
            holdings=holdings_payload,
            use_transformer=use_transformer,
        )
    except Exception:
        st.warning("Research workflow is temporarily unavailable due to market API rate limiting. Please retry in a minute.")
        return

    st.success(state.get("summary", "Research workflow completed."))

    options_payload = state.get("options") or []
    if options_payload:
        st.markdown("#### Options Overview")
        st.dataframe(pd.DataFrame([x.__dict__ for x in options_payload]), use_container_width=True)

    peer_payload = state.get("peer_comparison") or []
    if peer_payload:
        st.markdown("#### Peer Research")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "ticker": x.snapshot.ticker,
                        "price": x.snapshot.last_price,
                        "rsi": x.technicals.rsi_14,
                        "sentiment": x.sentiment.label,
                    }
                    for x in peer_payload
                ]
            ),
            use_container_width=True,
        )


def main() -> None:
    st.title("Financial Research AI Agent - Week 3 & 4")
    st.caption("CAPABL Internship Project | Multi-Source Financial Analysis")

    with st.sidebar:
        st.subheader("Research Controls")
        ticker = st.selectbox("Select ticker", DEFAULT_INDIAN_TICKERS, index=0)
        peers = st.multiselect("Comparison tickers", DEFAULT_INDIAN_TICKERS, default=[x for x in DEFAULT_INDIAN_TICKERS if x != ticker])
        period = st.selectbox("Chart period", ["1mo", "3mo", "6mo", "1y"], index=1)
        interval = st.selectbox("Interval", ["1d", "1h"], index=0)
        use_transformer = st.toggle("Use transformer sentiment (Track B)", value=False)
        if st.button("Refresh data cache"):
            st.cache_data.clear()
            st.rerun()

    tabs = st.tabs(
        [
            "Stock Deep Dive",
            "Stock Comparison",
            "Portfolio Analytics",
            "Research Workflow",
            "Macro Dashboard",
            "Chatbot",
        ]
    )

    with tabs[0]:
        _render_snapshot(ticker, use_transformer)
        history = _get_history_cached(ticker=ticker, period=period, interval=interval, cache_version=CACHE_VERSION)
        _render_chart(history, ticker)
        _render_indicator_chart(history, ticker)

    with tabs[1]:
        compare_targets = [ticker, *peers]
        _render_comparison_table(compare_targets, use_transformer)

    with tabs[2]:
        _render_portfolio_section(default_ticker=ticker)

    with tabs[3]:
        _render_workflow_section(ticker=ticker, peers=peers, use_transformer=use_transformer)

    with tabs[4]:
        _render_macro_dashboard()

    with tabs[5]:
        st.subheader("Financial Research Chatbot")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for role, message in st.session_state.messages:
            with st.chat_message(role):
                st.write(message)

        prompt = st.chat_input("Ask: Compare RELIANCE.NS and TCS.NS sentiment")
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
