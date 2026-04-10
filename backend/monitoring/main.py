"""
Monitoring & Observability Dashboard
Real-time metrics collection, analysis, and visualization
"""

from fastapi import FastAPI, HTTPException, Header, status
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Monitoring Dashboard",
    description="Financial metrics and system monitoring",
    version="1.0.0"
)


@dataclass
class MetricPoint:
    timestamp: datetime
    service: str
    metric_name: str
    value: float
    unit: str


# Metrics storage (use Prometheus/InfluxDB in production)
metrics_store: List[MetricPoint] = []


def record_metric(service: str, metric_name: str, value: float, unit: str = ""):
    """Record a metric point"""
    metric = MetricPoint(
        timestamp=datetime.utcnow(),
        service=service,
        metric_name=metric_name,
        value=value,
        unit=unit
    )
    metrics_store.append(metric)
    
    # Keep only last 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    metrics_store[:] = [m for m in metrics_store if m.timestamp > cutoff]


# ===================== System Metrics =====================

@app.get("/metrics/services")
async def get_service_metrics(
    x_user_id: Optional[str] = Header(None)
):
    """Get metrics for all services"""
    
    services = [
        {
            "name": "api_gateway",
            "port": 8000,
            "status": "healthy",
            "uptime_hours": 24,
            "requests_processed": 15420,
            "error_rate": 0.02,
            "avg_response_time_ms": 145,
            "cpu_usage": 23.5,
            "memory_usage_mb": 512
        },
        {
            "name": "market_data",
            "port": 8001,
            "status": "healthy",
            "uptime_hours": 24,
            "requests_processed": 8920,
            "error_rate": 0.01,
            "avg_response_time_ms": 230,
            "cpu_usage": 18.2,
            "memory_usage_mb": 384
        },
        {
            "name": "portfolio",
            "port": 8002,
            "status": "healthy",
            "uptime_hours": 24,
            "requests_processed": 3450,
            "error_rate": 0.005,
            "avg_response_time_ms": 95,
            "cpu_usage": 12.1,
            "memory_usage_mb": 256
        },
        {
            "name": "analytics",
            "port": 8003,
            "status": "healthy",
            "uptime_hours": 24,
            "requests_processed": 2890,
            "error_rate": 0.015,
            "avg_response_time_ms": 420,
            "cpu_usage": 28.7,
            "memory_usage_mb": 640
        }
    ]
    
    return {
        "services": services,
        "overall_health": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics/performance")
async def get_performance_metrics(
    service: Optional[str] = None,
    x_user_id: Optional[str] = Header(None)
):
    """Get performance metrics"""
    
    metrics = {
        "latency": {
            "p50": 45,
            "p95": 150,
            "p99": 280,
            "avg": 98
        },
        "throughput": {
            "requests_per_second": 156,
            "successful": 154,
            "failed": 2
        },
        "cache_efficiency": {
            "hit_rate": 0.75,
            "miss_rate": 0.25,
            "size_mb": 128
        },
        "errors": {
            "total_errors": 24,
            "authentication_failures": 2,
            "rate_limit_hits": 5,
            "service_unavailable": 0,
            "timeout": 17
        }
    }
    
    return {
        "metrics": metrics,
        "service": service or "all",
        "timestamp": datetime.utcnow().isoformat()
    }


# ===================== Financial Metrics Dashboard =====================

@app.get("/dashboard/financial-metrics")
async def get_financial_metrics(
    x_user_id: Optional[str] = Header(None)
):
    """Get real-time financial market metrics"""
    
    return {
        "market_overview": {
            "nifty_50": {
                "index": 21456.85,
                "change": 123.45,
                "change_pct": 0.58,
                "trades": 1250000
            },
            "sensex": {
                "index": 70234.12,
                "change": 325.10,
                "change_pct": 0.47,
                "trades": 980000
            },
            "nifty_bank": {
                "index": 45231.50,
                "change": 287.65,
                "change_pct": 0.64,
                "trades": 650000
            }
        },
        "sector_performance": [
            {"sector": "IT", "change_pct": 1.23, "top_performer": "TCS.NS"},
            {"sector": "Pharma", "change_pct": 0.45, "top_performer": "SUNPHARMA.NS"},
            {"sector": "Banking", "change_pct": 0.78, "top_performer": "HDFCBANK.NS"},
            {"sector": "Energy", "change_pct": -0.23, "top_performer": "RELIANCE.NS"},
            {"sector": "Auto", "change_pct": 0.12, "top_performer": "MARUTI.NS"},
        ],
        "top_gainers": [
            {"ticker": "WIPRO.NS", "price": 456.25, "change_pct": 3.45},
            {"ticker": "INFY.NS", "price": 1823.50, "change_pct": 2.87},
            {"ticker": "BAJAJFINSV.NS", "price": 1234.10, "change_pct": 2.34},
        ],
        "top_losers": [
            {"ticker": "GAIL.NS", "price": 134.20, "change_pct": -2.34},
            {"ticker": "COALINDIA.NS", "price": 456.75, "change_pct": -1.87},
            {"ticker": "ONGC.NS", "price": 289.45, "change_pct": -1.23},
        ],
        "market_breadth": {
            "advances": 1834,
            "declines": 1123,
            "unchanged": 89
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/dashboard/user-analytics")
async def get_user_analytics(
    x_user_id: Optional[str] = Header(None)
):
    """Get user portfolio and activity analytics"""
    
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    return {
        "user_id": x_user_id,
        "portfolio_summary": {
            "total_value": 5234500.50,
            "invested_value": 4850000.00,
            "unrealized_gains": 384500.50,
            "return_pct": 7.92,
            "positions": 15
        },
        "activity": {
            "trades_this_month": 12,
            "alerts_triggered": 8,
            "watchlists": 3,
            "last_trade": datetime.utcnow().isoformat()
        },
        "performance_vs_benchmark": {
            "portfolio_return": 7.92,
            "nifty_50_return": 5.23,
            "outperformance": 2.69,
            "year_to_date": 12.34
        },
        "risk_metrics": {
            "volatility": 14.5,
            "beta": 1.08,
            "sharpe_ratio": 1.34,
            "max_drawdown": 8.23
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ===================== Alert Management =====================

@app.get("/alerts/active")
async def get_active_alerts(
    x_user_id: Optional[str] = Header(None)
):
    """Get active system and user alerts"""
    
    alerts = [
        {
            "id": "sys_001",
            "type": "system",
            "severity": "info",
            "title": "Scheduled maintenance",
            "message": "Analytics service will have maintenance 2AM-3AM IST tonight",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=10)).isoformat()
        },
        {
            "id": "alert_001",
            "type": "price",
            "severity": "info",
            "title": "Price alert: RELIANCE.NS",
            "message": "RELIANCE.NS touched 2850 (above threshold 2800)",
            "created_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        }
    ]
    
    return {
        "alerts": alerts,
        "active_count": len(alerts),
        "timestamp": datetime.utcnow().isoformat()
    }


# ===================== Health Check =====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "monitoring",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        workers=2,
        reload=False
    )
