"""
Analytics Service Microservice
Advanced financial analytics including sentiment analysis, portfolio optimization, sector comparison
"""

from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.market_tools import compare_stocks, compare_sector
from agent.advanced_models import optimize_portfolio_mpt, black_scholes_price
from agent.sentiment_service import get_sentiment_score
from agent.stock_service import fetch_stock_snapshot, DEFAULT_INDIAN_TICKERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Analytics Service",
    description="Advanced financial analytics and optimization",
    version="1.0.0"
)


class StockComparison(BaseModel):
    tickers: List[str]


class PortfolioOptimization(BaseModel):
    tickers: List[str]


class OptionsPrice(BaseModel):
    spot: float
    strike: float
    maturity_days: float
    rate: float
    volatility: float


# ===================== Comparison Endpoints =====================

@app.get("/comparison")
async def get_comparison(
    tickers: str,
    x_user_id: Optional[str] = Header(None)
):
    """Compare multiple stocks with technical and sentiment data"""
    
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    
    if len(ticker_list) < 2 or len(ticker_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 2-10 tickers for comparison"
        )
    
    # Normalize tickers
    normalized_tickers = []
    for ticker in ticker_list:
        if not ticker.endswith((".NS", ".BO")):
            ticker = f"{ticker}.NS"
        normalized_tickers.append(ticker)
    
    try:
        research_rows = compare_stocks(normalized_tickers, use_transformer=False)
        
        if not research_rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No comparison data available"
            )
        
        comparison = []
        for row in research_rows:
            comparison.append({
                "ticker": row.snapshot.ticker,
                "price": row.snapshot.last_price,
                "day_change": row.snapshot.day_change,
                "day_change_pct": row.snapshot.day_change_pct,
                "volume": row.snapshot.volume,
                "rsi": row.technicals.rsi_14,
                "sma_20": row.technicals.sma_20,
                "sma_50": row.technicals.sma_50,
                "macd": row.technicals.macd,
                "sentiment": row.sentiment.label,
                "sentiment_score": row.sentiment.score
            })
        
        return {
            "comparison": comparison,
            "count": len(comparison),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch comparison data"
        )


# ===================== Sentiment Analysis =====================

@app.get("/sentiment/{ticker}")
async def get_sentiment(
    ticker: str,
    x_user_id: Optional[str] = Header(None)
):
    """Get sentiment analysis for a ticker"""
    
    normalized_ticker = ticker.upper()
    if not normalized_ticker.endswith((".NS", ".BO")):
        normalized_ticker = f"{normalized_ticker}.NS"
    
    try:
        research = compare_stocks([normalized_ticker], use_transformer=False)
        
        if not research:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data for {ticker}"
            )
        
        sentiment = research[0].sentiment
        
        return {
            "ticker": normalized_ticker,
            "sentiment": {
                "label": sentiment.label,
                "score": sentiment.score,
                "source": sentiment.source,
                "sample_size": sentiment.sample_size
            },
            "interpretation": interpret_sentiment(sentiment.score, sentiment.label),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch sentiment data"
        )


def interpret_sentiment(score: float, label: str) -> str:
    """Interpret sentiment score and label"""
    if label == "positive":
        return f"Strong positive sentiment ({score:.3f}). Market perception is bullish."
    elif label == "negative":
        return f"Strong negative sentiment ({score:.3f}). Market perception is bearish."
    else:
        return f"Neutral sentiment ({score:.3f}). Mixed market perception."


# ===================== Portfolio Optimization =====================

@app.post("/portfolio-optimization")
async def optimize_portfolio(
    payload: PortfolioOptimization,
    x_user_id: Optional[str] = Header(None)
):
    """Get MPT-based portfolio optimization"""
    
    if len(payload.tickers) < 2 or len(payload.tickers) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 2-10 tickers for optimization"
        )
    
    # Normalize tickers
    normalized_tickers = []
    for ticker in payload.tickers:
        ticker = ticker.upper()
        if not ticker.endswith((".NS", ".BO")):
            ticker = f"{ticker}.NS"
        normalized_tickers.append(ticker)
    
    try:
        result = optimize_portfolio_mpt(normalized_tickers)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to optimize - insufficient data"
            )
        
        weights_formatted = [
            {"ticker": k, "weight": round(v, 4), "weight_pct": round(v * 100, 2)}
            for k, v in result.weights.items()
        ]
        
        return {
            "optimization": {
                "expected_return": round(result.expected_return * 100, 2),
                "volatility": round(result.volatility * 100, 2),
                "sharpe_ratio": round(result.sharpe_ratio, 2),
                "weights": weights_formatted
            },
            "recommendation": generate_optimization_recommendation(result),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in optimization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to perform optimization"
        )


def generate_optimization_recommendation(result) -> str:
    """Generate optimization recommendation"""
    sharpe = result.sharpe_ratio
    if sharpe > 1.5:
        return "Excellent risk-adjusted returns. This allocation optimizes return per unit of risk."
    elif sharpe > 1.0:
        return "Good risk-adjusted returns. This is a solid allocation."
    else:
        return "Consider adjusting allocation for better risk-adjusted returns."


# ===================== Sector Comparison =====================

@app.get("/sector-comparison")
async def get_sector_comparison(
    tickers: str,
    x_user_id: Optional[str] = Header(None)
):
    """Compare stocks within same sector"""
    
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    
    if len(ticker_list) < 1 or len(ticker_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 1-10 tickers"
        )
    
    # Normalize tickers
    normalized_tickers = []
    for ticker in ticker_list:
        if not ticker.endswith((".NS", ".BO")):
            ticker = f"{ticker}.NS"
        normalized_tickers.append(ticker)
    
    try:
        rows = compare_sector(normalized_tickers)
        
        comparison = []
        for row in rows:
            comparison.append({
                "ticker": row.ticker,
                "sector": row.sector,
                "industry": row.industry,
                "pe_ratio": row.pe_ratio,
                "debt_to_equity": row.debt_to_equity,
                "revenue_growth": row.revenue_growth,
                "return_on_equity": row.return_on_equity
            })
        
        return {
            "sector_comparison": comparison,
            "count": len(comparison),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in sector comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch sector comparison"
        )


# ===================== Options Pricing =====================

@app.post("/options-pricing")
async def get_options_pricing(
    payload: OptionsPrice,
    x_user_id: Optional[str] = Header(None)
):
    """Calculate Black-Scholes option prices"""
    
    if payload.spot <= 0 or payload.strike <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spot and strike prices must be positive"
        )
    
    if payload.maturity_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maturity days must be positive"
        )
    
    if payload.volatility <= 0 or payload.volatility > 2.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volatility must be between 0 and 2.0"
        )
    
    try:
        pricing = black_scholes_price(
            spot_price=payload.spot,
            strike_price=payload.strike,
            time_to_maturity=payload.maturity_days / 365.0,
            risk_free_rate=payload.rate,
            volatility=payload.volatility
        )
        
        return {
            "inputs": {
                "spot": payload.spot,
                "strike": payload.strike,
                "maturity_days": payload.maturity_days,
                "rate": payload.rate,
                "volatility": payload.volatility
            },
            "pricing": {
                "call_price": round(pricing.call_price, 4),
                "put_price": round(pricing.put_price, 4),
                "intrinsic_value_call": round(max(payload.spot - payload.strike, 0), 4),
                "intrinsic_value_put": round(max(payload.strike - payload.spot, 0), 4)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in options pricing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to calculate option prices"
        )


# ===================== Health Check =====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        workers=2,
        reload=False
    )
