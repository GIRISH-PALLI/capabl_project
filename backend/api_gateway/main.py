"""
API Gateway - Central entry point for Track B microservices
Handles authentication, rate limiting, request routing, and response aggregation
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import httpx
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import logging
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CAPABL Financial AI - API Gateway",
    description="Production microservices gateway for financial analysis",
    version="1.0.0"
)

# Security configuration
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Service URLs - configure based on deployment
SERVICE_URLS = {
    "market_data": os.getenv("MARKET_DATA_SERVICE_URL", "http://localhost:8001"),
    "portfolio": os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8002"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003"),
}

# Rate limiting store (in-memory; use Redis for production)
rate_limit_store: Dict[str, list[float]] = {}
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
)


def verify_jwt_token(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and return decoded payload"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def check_rate_limit(user_id: str) -> bool:
    """Check if user is within rate limit"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []
    
    # Clean old requests outside window
    rate_limit_store[user_id] = [
        req_time for req_time in rate_limit_store[user_id]
        if req_time > window_start
    ]
    
    if len(rate_limit_store[user_id]) >= RATE_LIMIT_REQUESTS:
        return False
    
    rate_limit_store[user_id].append(now)
    return True


def create_access_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def forward_request(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Forward request to microservice with error handling"""
    
    base_url = SERVICE_URLS.get(service_name)
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service {service_name} not configured"
        )
    
    url = f"{base_url}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if user_id:
        headers["X-User-ID"] = user_id
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=payload, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=payload, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail=f"Method {method} not allowed"
                )
            
            if response.status_code >= 400:
                logger.error(f"Service error from {service_name}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
    
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to {service_name}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Service {service_name} timeout"
        )
    except Exception as e:
        logger.error(f"Error forwarding to {service_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Service {service_name} unavailable"
        )


# ===================== Authentication Endpoints =====================

@app.post("/auth/token")
async def get_token(username: str, password: str):
    """Authenticate and return JWT token"""
    # In production, validate against secure credential store
    # This is simplified for demo
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


# ===================== Market Data Endpoints =====================

@app.get("/api/v1/market/quotes/{ticker}")
async def get_stock_quotes(
    ticker: str,
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get real-time stock quotes"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "market_data",
        f"quotes/{ticker}",
        method="GET",
        user_id=user_id
    )


@app.get("/api/v1/market/history/{ticker}")
async def get_price_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get historical price data"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "market_data",
        f"history/{ticker}?period={period}&interval={interval}",
        method="GET",
        user_id=user_id
    )


@app.get("/api/v1/market/technicals/{ticker}")
async def get_technical_indicators(
    ticker: str,
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get technical analysis indicators"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "market_data",
        f"technicals/{ticker}",
        method="GET",
        user_id=user_id
    )


# ===================== Portfolio Endpoints =====================

@app.get("/api/v1/portfolio/positions")
async def get_portfolio_positions(payload: HTTPAuthCredentials = Depends(security)):
    """Get user's portfolio positions"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "portfolio",
        "positions",
        method="GET",
        user_id=user_id
    )


@app.post("/api/v1/portfolio/positions")
async def add_portfolio_position(
    position: Dict[str, Any],
    payload: HTTPAuthCredentials = Depends(security)
):
    """Add position to portfolio"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "portfolio",
        "positions",
        method="POST",
        payload=position,
        user_id=user_id
    )


@app.get("/api/v1/portfolio/performance")
async def get_portfolio_performance(
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get portfolio performance metrics"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "portfolio",
        "performance",
        method="GET",
        user_id=user_id
    )


# ===================== Analytics Endpoints =====================

@app.get("/api/v1/analytics/comparison")
async def compare_stocks(
    tickers: str,
    payload: HTTPAuthCredentials = Depends(security)
):
    """Compare multiple stocks"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "analytics",
        f"comparison?tickers={tickers}",
        method="GET",
        user_id=user_id
    )


@app.get("/api/v1/analytics/sentiment/{ticker}")
async def get_sentiment_analysis(
    ticker: str,
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get sentiment analysis for ticker"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "analytics",
        f"sentiment/{ticker}",
        method="GET",
        user_id=user_id
    )


@app.post("/api/v1/analytics/portfolio-optimization")
async def optimize_portfolio(
    tickers: list[str],
    payload: HTTPAuthCredentials = Depends(security)
):
    """Get portfolio optimization recommendations"""
    token_data = verify_jwt_token(payload)
    user_id = token_data.get("sub")
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await forward_request(
        "analytics",
        "portfolio-optimization",
        method="POST",
        payload={"tickers": tickers},
        user_id=user_id
    )


# ===================== Health Check =====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check each service
    for service_name, url in SERVICE_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                health_status["services"][service_name] = {
                    "status": "up" if response.status_code == 200 else "down",
                    "latency_ms": response.elapsed.total_seconds() * 1000
                }
        except Exception as e:
            health_status["services"][service_name] = {
                "status": "down",
                "error": str(e)
            }
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=False
    )
