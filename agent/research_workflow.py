from __future__ import annotations

from typing import Any, TypedDict

from agent.advanced_models import optimize_portfolio_mpt
from agent.market_tools import (
    compare_stocks,
    get_bonds_tool,
    get_economic_indicators_tool,
    get_fundamental_tool,
    get_futures_tool,
    get_multi_api_health_tool,
    get_options_tool,
    get_sector_comparison_tool,
    get_stock_research,
)
from agent.portfolio import Holding, analyze_portfolio


class ResearchState(TypedDict, total=False):
    ticker: str
    peers: list[str]
    use_transformer: bool
    holdings: list[dict[str, float | str]]
    stock_research: Any
    peer_comparison: Any
    options: Any
    fundamentals: Any
    sector_comparison: Any
    futures: Any
    bonds: Any
    economic_indicators: Any
    multi_api: Any
    portfolio: Any
    mpt: Any
    summary: str


def _gather_primary(state: ResearchState) -> ResearchState:
    state["stock_research"] = get_stock_research(
        state["ticker"],
        use_transformer=bool(state.get("use_transformer", False)),
    )
    state["options"] = get_options_tool(state["ticker"])
    state["fundamentals"] = get_fundamental_tool(state["ticker"])
    state["multi_api"] = get_multi_api_health_tool(state["ticker"])
    return state


def _gather_macro(state: ResearchState) -> ResearchState:
    state["futures"] = get_futures_tool()
    state["bonds"] = get_bonds_tool()
    state["economic_indicators"] = get_economic_indicators_tool()
    return state


def _peer_analysis(state: ResearchState) -> ResearchState:
    peers = state.get("peers") or []
    if peers:
        tickers = [state["ticker"], *peers]
        state["peer_comparison"] = compare_stocks(tickers, use_transformer=bool(state.get("use_transformer", False)))
        state["sector_comparison"] = get_sector_comparison_tool(tickers)
        state["mpt"] = optimize_portfolio_mpt(tickers)
    else:
        state["peer_comparison"] = []
        state["sector_comparison"] = []
        state["mpt"] = None
    return state


def _portfolio_analysis(state: ResearchState) -> ResearchState:
    holdings_payload = state.get("holdings") or []
    holdings: list[Holding] = []
    for payload in holdings_payload:
        holdings.append(
            Holding(
                ticker=str(payload.get("ticker") or ""),
                quantity=float(payload.get("quantity") or 0.0),
                average_cost=float(payload.get("average_cost") or 0.0),
            )
        )

    state["portfolio"] = analyze_portfolio(holdings) if holdings else None
    return state


def _summarize(state: ResearchState) -> ResearchState:
    stock = state.get("stock_research")
    if stock is None:
        state["summary"] = "No stock research data available for the selected ticker."
        return state

    summary = (
        f"{stock.snapshot.ticker}: price {stock.snapshot.last_price:.2f} {stock.snapshot.currency}, "
        f"daily move {stock.snapshot.day_change_pct:.2f}%, RSI {stock.technicals.rsi_14:.2f}, "
        f"sentiment {stock.sentiment.label} ({stock.sentiment.score:.3f})."
    )

    peer_count = len(state.get("peer_comparison") or [])
    if peer_count > 1:
        summary += f" Compared against {peer_count - 1} peer stocks."

    if state.get("mpt") is not None:
        summary += f" MPT portfolio Sharpe: {state['mpt'].sharpe_ratio:.2f}."

    if state.get("portfolio") is not None:
        summary += " Portfolio analytics included."

    state["summary"] = summary
    return state


def _run_fallback_workflow(initial_state: ResearchState) -> ResearchState:
    state = dict(initial_state)
    for step in (_gather_primary, _gather_macro, _peer_analysis, _portfolio_analysis, _summarize):
        state = step(state)
    return state


def run_financial_research(
    ticker: str,
    peers: list[str] | None = None,
    holdings: list[dict[str, float | str]] | None = None,
    use_transformer: bool = False,
) -> ResearchState:
    initial_state: ResearchState = {
        "ticker": ticker,
        "peers": peers or [],
        "holdings": holdings or [],
        "use_transformer": use_transformer,
    }

    try:
        from langgraph.graph import END, START, StateGraph
    except Exception:
        return _run_fallback_workflow(initial_state)

    graph = StateGraph(ResearchState)
    graph.add_node("gather_primary", _gather_primary)
    graph.add_node("gather_macro", _gather_macro)
    graph.add_node("peer_analysis", _peer_analysis)
    graph.add_node("portfolio_analysis", _portfolio_analysis)
    graph.add_node("summarize", _summarize)

    graph.add_edge(START, "gather_primary")
    graph.add_edge("gather_primary", "gather_macro")
    graph.add_edge("gather_macro", "peer_analysis")
    graph.add_edge("peer_analysis", "portfolio_analysis")
    graph.add_edge("portfolio_analysis", "summarize")
    graph.add_edge("summarize", END)

    app = graph.compile()
    return app.invoke(initial_state)
