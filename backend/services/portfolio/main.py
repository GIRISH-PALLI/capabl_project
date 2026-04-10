"""
Portfolio Service Microservice
Manages portfolio positions, performance tracking, and P&L calculations
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

from agent.portfolio import Holding, analyze_portfolio
from agent.stock_service import fetch_stock_snapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portfolio Service",
    description="Portfolio position and performance management",
    version="1.0.0"
)

# In-memory portfolio store (use database in production)
portfolio_store: Dict[str, List[Dict[str, Any]]] = {}


class PortfolioPosition(BaseModel):
    ticker: str
    quantity: float
    average_cost: float
    notes: Optional[str] = None


class PortfolioResponse(BaseModel):
    ticker: str
    quantity: float
    average_cost: float
    current_price: float
    market_value: float
    invested_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    daily_pnl: float


# ===================== Portfolio Management =====================

@app.get("/positions")
async def get_positions(
    x_user_id: Optional[str] = Header(None)
):
    """Get user's portfolio positions"""
    
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    if x_user_id not in portfolio_store:
        return {
            "user_id": x_user_id,
            "positions": [],
            "total_invested": 0.0,
            "total_market_value": 0.0,
            "total_pnl": 0.0
        }
    
    positions = []
    total_invested = 0.0
    total_market_value = 0.0
    total_pnl = 0.0
    
    for pos in portfolio_store[x_user_id]:
        ticker = pos["ticker"]
        quantity = pos["quantity"]
        avg_cost = pos["average_cost"]
        
        try:
            snapshot = fetch_stock_snapshot(ticker)
            if snapshot:
                invested = quantity * avg_cost
                market_val = quantity * snapshot.last_price
                unrealized = market_val - invested
                unrealized_pct = (unrealized / invested * 100) if invested > 0 else 0
                
                positions.append({
                    "ticker": ticker,
                    "quantity": quantity,
                    "average_cost": avg_cost,
                    "current_price": snapshot.last_price,
                    "market_value": market_val,
                    "invested_value": invested,
                    "unrealized_pnl": unrealized,
                    "unrealized_pnl_pct": unrealized_pct,
                    "daily_pnl": quantity * snapshot.day_change
                })
                
                total_invested += invested
                total_market_value += market_val
                total_pnl += unrealized
        except Exception as e:
            logger.warning(f"Could not fetch {ticker}: {str(e)}")
    
    return {
        "user_id": x_user_id,
        "positions": positions,
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "total_unrealized_pnl": total_pnl,
        "total_unrealized_pnl_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/positions")
async def add_position(
    position: PortfolioPosition,
    x_user_id: Optional[str] = Header(None)
):
    """Add position to portfolio"""
    
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    # Validate ticker format
    ticker = position.ticker.upper()
    if not ticker.endswith((".NS", ".BO")):
        ticker = f"{ticker}.NS"
    
    if position.quantity <= 0 or position.average_cost <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity and average cost must be positive"
        )
    
    if x_user_id not in portfolio_store:
        portfolio_store[x_user_id] = []
    
    # Check if position exists
    existing = next((p for p in portfolio_store[x_user_id] if p["ticker"] == ticker), None)
    
    if existing:
        # Update existing position (simple average)
        total_qty = existing["quantity"] + position.quantity
        total_cost = existing["quantity"] * existing["average_cost"] + position.quantity * position.average_cost
        existing["average_cost"] = total_cost / total_qty
        existing["quantity"] = total_qty
        action = "updated"
    else:
        # Add new position
        portfolio_store[x_user_id].append({
            "ticker": ticker,
            "quantity": position.quantity,
            "average_cost": position.average_cost,
            "notes": position.notes or "",
            "added_at": datetime.utcnow().isoformat()
        })
        action = "added"
    
    logger.info(f"Position {action} for {x_user_id}: {ticker}")
    
    return {
        "status": "success",
        "action": action,
        "message": f"Position {action} successfully",
        "ticker": ticker,
        "quantity": position.quantity,
        "average_cost": position.average_cost
    }


@app.delete("/positions/{ticker}")
async def remove_position(
    ticker: str,
    x_user_id: Optional[str] = Header(None)
):
    """Remove position from portfolio"""
    
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    normalized_ticker = ticker.upper()
    if not normalized_ticker.endswith((".NS", ".BO")):
        normalized_ticker = f"{normalized_ticker}.NS"
    
    if x_user_id not in portfolio_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No positions found"
        )
    
    initial_len = len(portfolio_store[x_user_id])
    portfolio_store[x_user_id] = [
        p for p in portfolio_store[x_user_id] if p["ticker"] != normalized_ticker
    ]
    
    if len(portfolio_store[x_user_id]) == initial_len:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position not found: {ticker}"
        )
    
    logger.info(f"Position removed for {x_user_id}: {normalized_ticker}")
    
    return {
        "status": "success",
        "message": f"Position removed: {normalized_ticker}"
    }


# ===================== Performance Analytics =====================

@app.get("/performance")
async def get_performance(
    x_user_id: Optional[str] = Header(None)
):
    """Get portfolio performance metrics"""
    
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    if x_user_id not in portfolio_store or not portfolio_store[x_user_id]:
        return {
            "user_id": x_user_id,
            "total_return": 0.0,
            "total_return_pct": 0.0,
            "daily_pnl": 0.0,
            "position_count": 0,
            "top_gainer": None,
            "top_loser": None
        }
    
    positions = []
    total_invested = 0.0
    total_market_value = 0.0
    total_daily_pnl = 0.0
    
    for pos in portfolio_store[x_user_id]:
        ticker = pos["ticker"]
        quantity = pos["quantity"]
        avg_cost = pos["average_cost"]
        
        try:
            snapshot = fetch_stock_snapshot(ticker)
            if snapshot:
                invested = quantity * avg_cost
                market_val = quantity * snapshot.last_price
                unrealized = market_val - invested
                daily_pnl = quantity * snapshot.day_change
                unrealized_pct = (unrealized / invested * 100) if invested > 0 else 0
                
                positions.append({
                    "ticker": ticker,
                    "unrealized_pnl_pct": unrealized_pct,
                    "unrealized_pnl": unrealized,
                    "daily_pnl": daily_pnl
                })
                
                total_invested += invested
                total_market_value += market_val
                total_daily_pnl += daily_pnl
        except Exception as e:
            logger.warning(f"Could not fetch {ticker}: {str(e)}")
    
    # Sort to find gainers and losers
    positions.sort(key=lambda x: x["unrealized_pnl_pct"], reverse=True)
    
    total_pnl = total_market_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "user_id": x_user_id,
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "total_return": total_pnl,
        "total_return_pct": total_pnl_pct,
        "daily_pnl": total_daily_pnl,
        "position_count": len([x_user_id]),
        "top_gainer": positions[0] if positions else None,
        "top_loser": positions[-1] if positions else None,
        "timestamp": datetime.utcnow().isoformat()
    }


# ===================== Health Check =====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "portfolio",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        workers=2,
        reload=False
    )
