# CAPABL Financial AI - API Documentation

## Authentication

### Get Access Token

**Endpoint:** `POST /auth/token`

**Request:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "trader@example.com",
    "password": "secure_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Usage:** Include token in all subsequent requests:
```bash
Authorization: Bearer <access_token>
```

---

## Market Data Endpoints

### Get Stock Quotes

**Endpoint:** `GET /api/v1/market/quotes/{ticker}`

**Parameters:**
- `ticker` (string, required): Stock symbol (e.g., RELIANCE.NS, TCS.BO)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "last_price": 2850.50,
  "day_change": 45.25,
  "day_change_pct": 1.61,
  "volume": 15234500,
  "currency": "INR",
  "timestamp": "2026-04-10T14:30:00Z",
  "data_source": "yahoo_finance"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/market/quotes/RELIANCE.NS \
  -H "Authorization: Bearer <token>"
```

---

### Get Price History

**Endpoint:** `GET /api/v1/market/history/{ticker}`

**Parameters:**
- `ticker` (string, required): Stock symbol
- `period` (string, optional): Data period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y (default: 1mo)
- `interval` (string, optional): Data interval - 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo (default: 1d)

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "period": "1mo",
  "interval": "1d",
  "data_points": 20,
  "prices": [
    {
      "date": "2026-03-11",
      "open": 2750.00,
      "high": 2875.25,
      "low": 2745.50,
      "close": 2850.50,
      "volume": 12345678
    }
  ],
  "timestamp": "2026-04-10T14:30:00Z"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/market/history/RELIANCE.NS?period=3mo&interval=1d" \
  -H "Authorization: Bearer <token>"
```

---

### Get Technical Indicators

**Endpoint:** `GET /api/v1/market/technicals/{ticker}`

**Parameters:**
- `ticker` (string, required): Stock symbol
- `period` (string, optional): Analysis period (default: 1mo)

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "as_of_date": "2026-04-10T14:30:00Z",
  "indicators": {
    "sma_20": 2812.34,
    "sma_50": 2756.78,
    "sma_200": 2701.23,
    "rsi_14": 68.45,
    "macd": 120.34,
    "macd_signal": 98.76,
    "macd_histogram": 21.58,
    "bb_upper": 2890.12,
    "bb_middle": 2820.34,
    "bb_lower": 2750.56,
    "atr": 45.67
  },
  "signal": "OVERBOUGHT + BULLISH_CROSS",
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Compare Multiple Stocks

**Endpoint:** `GET /api/v1/market/comparison?tickers=TICKER1,TICKER2,TICKER3`

**Parameters:**
- `tickers` (string, required): Comma-separated stock symbols

**Response:**
```json
{
  "comparison": [
    {
      "ticker": "RELIANCE.NS",
      "price": 2850.50,
      "change": 45.25,
      "change_pct": 1.61,
      "volume": 15234500
    },
    {
      "ticker": "TCS.NS",
      "price": 3520.75,
      "change": 28.50,
      "change_pct": 0.82,
      "volume": 8923400
    }
  ],
  "count": 2,
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

## Portfolio Endpoints

### Get Portfolio Positions

**Endpoint:** `GET /api/v1/portfolio/positions`

**Response:**
```json
{
  "user_id": "trader@example.com",
  "positions": [
    {
      "ticker": "RELIANCE.NS",
      "quantity": 100,
      "average_cost": 2750,
      "current_price": 2850.50,
      "market_value": 285050,
      "invested_value": 275000,
      "unrealized_pnl": 10050,
      "unrealized_pnl_pct": 3.65,
      "daily_pnl": 4525
    }
  ],
  "total_invested": 275000,
  "total_market_value": 285050,
  "total_unrealized_pnl": 10050,
  "total_unrealized_pnl_pct": 3.65,
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Add Portfolio Position

**Endpoint:** `POST /api/v1/portfolio/positions`

**Request:**
```json
{
  "ticker": "RELIANCE.NS",
  "quantity": 50,
  "average_cost": 2820,
  "notes": "Entry at strong support"
}
```

**Response:**
```json
{
  "status": "success",
  "action": "added",
  "message": "Position added successfully",
  "ticker": "RELIANCE.NS",
  "quantity": 50,
  "average_cost": 2820
}
```

---

### Remove Portfolio Position

**Endpoint:** `DELETE /api/v1/portfolio/positions/{ticker}`

**Response:**
```json
{
  "status": "success",
  "message": "Position removed: RELIANCE.NS"
}
```

---

### Get Portfolio Performance

**Endpoint:** `GET /api/v1/portfolio/performance`

**Response:**
```json
{
  "user_id": "trader@example.com",
  "total_invested": 550000,
  "total_market_value": 587000,
  "total_return": 37000,
  "total_return_pct": 6.73,
  "daily_pnl": 8500,
  "position_count": 5,
  "top_gainer": {
    "ticker": "WIPRO.NS",
    "unrealized_pnl_pct": 12.45
  },
  "top_loser": {
    "ticker": "COAL_INDIA.NS",
    "unrealized_pnl_pct": -2.34
  },
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

## Analytics Endpoints

### Compare Stocks with Sentiment

**Endpoint:** `GET /api/v1/analytics/comparison?tickers=RELIANCE.NS,TCS.NS`

**Response:**
```json
{
  "comparison": [
    {
      "ticker": "RELIANCE.NS",
      "price": 2850.50,
      "day_change": 45.25,
      "day_change_pct": 1.61,
      "volume": 15234500,
      "rsi": 68.45,
      "sma_20": 2812.34,
      "sma_50": 2756.78,
      "macd": 120.34,
      "sentiment": "positive",
      "sentiment_score": 0.78
    }
  ],
  "count": 2,
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Get Sentiment Analysis

**Endpoint:** `GET /api/v1/analytics/sentiment/{ticker}`

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "sentiment": {
    "label": "positive",
    "score": 0.78,
    "source": "news_headlines",
    "sample_size": 245
  },
  "interpretation": "Strong positive sentiment (0.780). Market perception is bullish.",
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Portfolio Optimization (MPT)

**Endpoint:** `POST /api/v1/analytics/portfolio-optimization`

**Request:**
```json
{
  "tickers": ["RELIANCE.NS", "TCS.NS", "WIPRO.NS", "INFY.NS"]
}
```

**Response:**
```json
{
  "optimization": {
    "expected_return": 14.23,
    "volatility": 16.45,
    "sharpe_ratio": 0.865,
    "weights": [
      {
        "ticker": "RELIANCE.NS",
        "weight": 0.35,
        "weight_pct": 35.0
      },
      {
        "ticker": "TCS.NS",
        "weight": 0.30,
        "weight_pct": 30.0
      },
      {
        "ticker": "WIPRO.NS",
        "weight": 0.20,
        "weight_pct": 20.0
      },
      {
        "ticker": "INFY.NS",
        "weight": 0.15,
        "weight_pct": 15.0
      }
    ]
  },
  "recommendation": "Good risk-adjusted returns. This is a solid allocation.",
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Sector Comparison

**Endpoint:** `GET /api/v1/analytics/sector-comparison?tickers=RELIANCE.NS,TCS.NS`

**Response:**
```json
{
  "sector_comparison": [
    {
      "ticker": "RELIANCE.NS",
      "sector": "Energy",
      "industry": "Oil & Gas",
      "pe_ratio": 18.45,
      "debt_to_equity": 0.42,
      "revenue_growth": 0.08,
      "return_on_equity": 0.18
    }
  ],
  "count": 2,
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Options Pricing (Black-Scholes)

**Endpoint:** `POST /api/v1/analytics/options-pricing`

**Request:**
```json
{
  "spot": 100,
  "strike": 105,
  "maturity_days": 30,
  "rate": 0.06,
  "volatility": 0.25
}
```

**Response:**
```json
{
  "inputs": {
    "spot": 100,
    "strike": 105,
    "maturity_days": 30,
    "rate": 0.06,
    "volatility": 0.25
  },
  "pricing": {
    "call_price": 2.7854,
    "put_price": 7.4675,
    "intrinsic_value_call": 0,
    "intrinsic_value_put": 5
  },
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

## Monitoring Endpoints

### Get Service Metrics

**Endpoint:** `GET /api/v1/monitoring/metrics/services`

**Response:**
```json
{
  "services": [
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
    }
  ],
  "overall_health": "healthy",
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

### Get Financial Metrics Dashboard

**Endpoint:** `GET /api/v1/monitoring/dashboard/financial-metrics`

**Response:**
```json
{
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
    }
  },
  "sector_performance": [
    {
      "sector": "IT",
      "change_pct": 1.23,
      "top_performer": "TCS.NS"
    }
  ],
  "top_gainers": [...],
  "top_losers": [...],
  "market_breadth": {
    "advances": 1834,
    "declines": 1123,
    "unchanged": 89
  },
  "timestamp": "2026-04-10T14:30:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status_code": 400,
  "detail": "Invalid ticker format"
}
```

### 401 Unauthorized
```json
{
  "status_code": 401,
  "detail": "Invalid token"
}
```

### 429 Rate Limited
```json
{
  "status_code": 429,
  "detail": "Rate limit exceeded"
}
```

### 503 Service Unavailable
```json
{
  "status_code": 503,
  "detail": "Service temporarily unavailable"
}
```

---

## Rate Limiting

- **Limit**: 100 requests per minute per user
- **Header**: `X-RateLimit-Remaining: 99`
- **Retry-After**: 60 seconds

---

## Caching

- **Quotes**: 60 seconds
- **Price History**: 300 seconds
- **Technical Indicators**: 300 seconds
- **Fundamentals**: 3600 seconds

---

## Pagination

Endpoints returning large datasets support pagination:

```
GET /api/v1/endpoint?page=1&per_page=50
```

---

## Webhook Support (Coming Soon)

Subscribe to real-time events:

```json
POST /api/v1/webhooks/subscribe
{
  "event": "price_alert",
  "ticker": "RELIANCE.NS",
  "threshold": 2850,
  "url": "https://your-app.com/webhook"
}
```

---

## API Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-10T14:30:00Z",
  "services": {
    "api_gateway": {
      "status": "up",
      "latency_ms": 1.2
    },
    "market_data": {
      "status": "up",
      "latency_ms": 45.3
    }
  }
}
```

---

## SDKs & Libraries

### Python
```python
from capabl_sdk import CapablClient

client = CapablClient(api_key="your_token")
quotes = client.market.get_quotes("RELIANCE.NS")
```

### JavaScript/TypeScript
```javascript
import { CapablAPI } from '@capabl/sdk';

const api = new CapablAPI({ token: 'your_token' });
const quotes = await api.market.getQuotes('RELIANCE.NS');
```

---

**Last Updated**: 2026-04-10  
**API Version**: 1.0.0  
**Status**: Production Ready
