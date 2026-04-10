"""
Market Data Microservice
Handles stock quotes, price history, technical indicators, and market data aggregation
"""

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import JSONResponse
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio
from functools import lru_cache
import time

# Setup path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.stock_service import fetch_stock_snapshot, fetch_price_history, DEFAULT_INDIAN_TICKERS
from agent.technical_analysis import add_indicators
from agent.sentiment_service import get_sentiment_score
from agent.market_tools import get_stock_research

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Market Data Service",
    description="Real-time stock quotes and technical analysis",
    version="1.0.0"
)

# Response caching with TTL
CACHE_TTL = {
    "quotes": 60,  # 1 minute
    "history": 300,  # 5 minutes
    "technicals": 300,  # 5 minutes
}

cache_store: Dict[str, tuple[Any, float]] = {}


def get_cached(key: str, ttl: int) -> Optional[Any]:
    """Get value from cache if not expired"""
    if key in cache_store:
        value, timestamp = cache_store[key]
        if time.time() - timestamp < ttl:
            logger.info(f"Cache hit: {key}")
            return value
    return None


def set_cache(key: str, value: Any):
    """Set value in cache with timestamp"""
    cache_store[key] = (value, time.time())
    logger.info(f"Cache set: {key}")


# ===================== Quote Endpoints =====================

@app.get("/quotes/{ticker}")
async def get_quotes(
    ticker: str,
    x_user_id: Optional[str] = Header(None)
):
    """Get real-time stock quotes with technical indicators"""
    
    # Validate ticker
    normalized_ticker = ticker.upper()
    if not normalized_ticker.endswith((".NS", ".BO")):
        normalized_ticker = f"{normalized_ticker}.NS"
    
    cache_key = f"quotes:{normalized_ticker}"
    cached = get_cached(cache_key, CACHE_TTL["quotes"])
    if cached:
        return cached
    
    try:
        snapshot = fetch_stock_snapshot(normalized_ticker)
        if snapshot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker {ticker} not found"
            )
        
        response = {
            "ticker": snapshot.ticker,
            "last_price": snapshot.last_price,
            "day_change": snapshot.day_change,
            "day_change_pct": snapshot.day_change_pct,
            "volume": snapshot.volume,
            "currency": snapshot.currency,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": snapshot.data_source
        }
        
        set_cache(cache_key, response)
        return response
    
    except Exception as e:
        logger.error(f"Error fetching quotes for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch quotes for {ticker}"
        )


# ===================== History Endpoints =====================

@app.get("/history/{ticker}")
async def get_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    x_user_id: Optional[str] = Header(None)
):
    """Get historical price data"""
    
    # Validate inputs
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
    valid_intervals = ["1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"]
    
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period. Must be one of {valid_periods}"
        )
    
    if interval not in valid_intervals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interval. Must be one of {valid_intervals}"
        )
    
    normalized_ticker = ticker.upper()
    if not normalized_ticker.endswith((".NS", ".BO")):
        normalized_ticker = f"{normalized_ticker}.NS"
    
    cache_key = f"history:{normalized_ticker}:{period}:{interval}"
    cached = get_cached(cache_key, CACHE_TTL["history"])
    if cached:
        return cached
    
    try:
        history = fetch_price_history(
            ticker=normalized_ticker,
            period=period,
            interval=interval
        )
        
        if history is None or history.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price history available for {ticker}"
            )
        
        # Format response
        records = []
        for idx, row in history.iterrows():
            records.append({
                "date": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                "open": float(row["Open"]) if "Open" in row else None,
                "high": float(row["High"]) if "High" in row else None,
                "low": float(row["Low"]) if "Low" in row else None,
                "close": float(row["Close"]) if "Close" in row else None,
                "volume": int(row["Volume"]) if "Volume" in row else 0,
            })
        
        response = {
            "ticker": normalized_ticker,
            "period": period,
            "interval": interval,
            "data_points": len(records),
            "prices": records,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        set_cache(cache_key, response)
        return response
    
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch price history for {ticker}"
        )


# ===================== Technical Indicators =====================

@app.get("/technicals/{ticker}")
async def get_technicals(
    ticker: str,
    period: str = "1mo",
    x_user_id: Optional[str] = Header(None)
):
    """Get technical analysis indicators"""
    
    normalized_ticker = ticker.upper()
    if not normalized_ticker.endswith((".NS", ".BO")):
        normalized_ticker = f"{normalized_ticker}.NS"
    
    cache_key = f"technicals:{normalized_ticker}:{period}"
    cached = get_cached(cache_key, CACHE_TTL["technicals"])
    if cached:
        return cached
    
    try:
        history = fetch_price_history(
            ticker=normalized_ticker,
            period=period,
            interval="1d"
        )
        
        if history is None or history.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data for technical analysis: {ticker}"
            )
        
        # Add technical indicators
        enriched = add_indicators(history)
        
        # Get latest values
        latest = enriched.iloc[-1]
        
        response = {
            "ticker": normalized_ticker,
            "as_of_date": datetime.utcnow().isoformat(),
            "indicators": {
                "sma_20": float(latest.get("SMA_20", 0)),
                "sma_50": float(latest.get("SMA_50", 0)),
                "sma_200": float(latest.get("SMA_200", 0)),
                "rsi_14": float(latest.get("RSI_14", 0)),
                "macd": float(latest.get("MACD", 0)),
                "macd_signal": float(latest.get("MACD_Signal", 0)),
                "macd_histogram": float(latest.get("MACD_Histogram", 0)),
                "bb_upper": float(latest.get("BB_UPPER", 0)),
                "bb_middle": float(latest.get("BB_MIDDLE", 0)),
                "bb_lower": float(latest.get("BB_LOWER", 0)),
                "atr": float(latest.get("ATR", 0)),
            },
            "signal": generate_technical_signal(latest),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        set_cache(cache_key, response)
        return response
    
    except Exception as e:
        logger.error(f"Error calculating technicals for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to calculate technical indicators for {ticker}"
        )


def generate_technical_signal(indicators_row) -> str:
    """Generate buy/sell signal based on technical indicators"""
    rsi = indicators_row.get("RSI_14", 50)
    macd = indicators_row.get("MACD", 0)
    macd_signal = indicators_row.get("MACD_Signal", 0)
    close = indicators_row.get("Close", 0)
    bb_upper = indicators_row.get("BB_UPPER", 0)
    bb_lower = indicators_row.get("BB_LOWER", 0)
    
    signals = []
    
    if rsi < 30:
        signals.append("OVERSOLD")
    elif rsi > 70:
        signals.append("OVERBOUGHT")
    
    if macd > macd_signal:
        signals.append("BULLISH_CROSS")
    elif macd < macd_signal:
        signals.append("BEARISH_CROSS")
    
    if close > bb_upper:
        signals.append("ABOVE_BB_UPPER")
    elif close < bb_lower:
        signals.append("BELOW_BB_LOWER")
    
    return " + ".join(signals) if signals else "NEUTRAL"


# ===================== Comparison Endpoint =====================

@app.get("/comparison")
async def compare_tickers(
    tickers: str,
    x_user_id: Optional[str] = Header(None)
):
    """Compare multiple tickers"""
    
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    if len(ticker_list) < 1 or len(ticker_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 1-10 tickers for comparison"
        )
    
    results = []
    for ticker in ticker_list:
        normalized = ticker if ticker.endswith((".NS", ".BO")) else f"{ticker}.NS"
        try:
            snapshot = fetch_stock_snapshot(normalized)
            if snapshot:
                results.append({
                    "ticker": snapshot.ticker,
                    "price": snapshot.last_price,
                    "change": snapshot.day_change,
                    "change_pct": snapshot.day_change_pct,
                    "volume": snapshot.volume
                })
        except Exception as e:
            logger.warning(f"Could not fetch {ticker}: {str(e)}")
    
    return {
        "comparison": results,
        "count": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }


# ===================== Health Check =====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "market_data",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        workers=2,
        reload=False
    )
