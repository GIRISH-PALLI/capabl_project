"""
Demo Scenarios for Track B - Live Trading Showcase
Demonstrates real-time financial analysis platform capabilities
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


class DemoScenarios:
    """Live demo scenarios showcasing platform capabilities"""
    
    @staticmethod
    def scenario_1_live_portfolio_tracking() -> Dict[str, Any]:
        """
        Scenario 1: Live Portfolio Tracking (2 minutes)
        - Show real-time portfolio positions
        - Display live P&L updates
        - Compare against market benchmarks
        """
        return {
            "name": "Live Portfolio Tracking",
            "duration_minutes": 2,
            "steps": [
                {
                    "step": 1,
                    "action": "Login and navigate to Dashboard",
                    "description": "User logs in and lands on portfolio dashboard",
                    "expected_result": "Portfolio shows 15 positions with live prices"
                },
                {
                    "step": 2,
                    "action": "View Real-time P&L",
                    "description": "Display portfolio metrics updating every 2 seconds",
                    "portfolio_data": {
                        "total_invested": 5500000,
                        "total_market_value": 5872500,
                        "total_unrealized_pnl": 372500,
                        "total_return_pct": 6.77,
                        "daily_pnl": 8500,
                        "positions": [
                            {
                                "ticker": "RELIANCE.NS",
                                "quantity": 100,
                                "average_cost": 2750,
                                "current_price": 2850.50,
                                "change_pct": 3.65
                            },
                            {
                                "ticker": "TCS.NS",
                                "quantity": 50,
                                "average_cost": 3500,
                                "current_price": 3520.75,
                                "change_pct": 0.59
                            },
                            {
                                "ticker": "WIPRO.NS",
                                "quantity": 200,
                                "average_cost": 420,
                                "current_price": 456.25,
                                "change_pct": 8.63
                            }
                        ]
                    }
                },
                {
                    "step": 3,
                    "action": "Compare vs Benchmark",
                    "description": "Show portfolio performance vs NIFTY-50",
                    "benchmark_comparison": {
                        "portfolio_return_ytd": 12.34,
                        "nifty_50_return_ytd": 5.23,
                        "outperformance": 7.11,
                        "chart_data": "Display over 6-month period"
                    }
                },
                {
                    "step": 4,
                    "action": "Identify Top Gainer",
                    "description": "Highlight WIPRO.NS as top performer",
                    "action_items": "Option to add more/reduce position"
                }
            ],
            "success_criteria": "All real-time data updates smooth without lag"
        }
    
    @staticmethod
    def scenario_2_stock_comparison() -> Dict[str, Any]:
        """
        Scenario 2: Stock Comparison Analysis (2 minutes)
        - Compare 3-4 stocks side-by-side
        - Show technical indicators
        - Display sentiment analysis
        """
        return {
            "name": "Stock Comparison Analysis",
            "duration_minutes": 2,
            "steps": [
                {
                    "step": 1,
                    "action": "Select Tickers for Comparison",
                    "description": "User selects RELIANCE.NS, TCS.NS, WIPRO.NS, INFY.NS",
                    "tickers": ["RELIANCE.NS", "TCS.NS", "WIPRO.NS", "INFY.NS"]
                },
                {
                    "step": 2,
                    "action": "Display Candlestick Charts",
                    "description": "Show 1-month price data with technical indicators",
                    "chart_features": {
                        "period": "1mo",
                        "interval": "1d",
                        "indicators": ["SMA20", "SMA50", "Bollinger Bands"],
                        "zoom_capability": "User can zoom into specific date ranges"
                    }
                },
                {
                    "step": 3,
                    "action": "Show Technical Metrics Table",
                    "description": "Compare RSI, MACD, ATR, Bollinger Bands",
                    "comparison_table": {
                        "columns": ["Ticker", "Price", "RSI", "MACD", "BB_Status", "Signal"],
                        "data": [
                            {"ticker": "RELIANCE.NS", "price": 2850.50, "rsi": 68.45, "macd": "Positive", "bb": "Above Upper", "signal": "Overbought"},
                            {"ticker": "TCS.NS", "price": 3520.75, "rsi": 52.10, "macd": "Positive", "bb": "Middle", "signal": "Neutral"},
                            {"ticker": "WIPRO.NS", "price": 456.25, "rsi": 45.30, "macd": "Positive", "bb": "Below Upper", "signal": "Strong Buy"}
                        ]
                    }
                },
                {
                    "step": 4,
                    "action": "Display Sentiment Analysis",
                    "description": "Show news sentiment for each stock",
                    "sentiment_data": {
                        "RELIANCE.NS": {"sentiment": "Positive", "score": 0.78, "sources": 245},
                        "TCS.NS": {"sentiment": "Positive", "score": 0.65, "sources": 189},
                        "WIPRO.NS": {"sentiment": "Very Positive", "score": 0.82, "sources": 156},
                        "INFY.NS": {"sentiment": "Positive", "score": 0.71, "sources": 203}
                    }
                },
                {
                    "step": 5,
                    "action": "Sector Performance Context",
                    "description": "Show each stock's sector & industry outperformance",
                    "sector_data": "IT sector up 1.23%, Pharma up 0.45%, Energy up 0.78%"
                }
            ],
            "success_criteria": "Smooth animation transitions between datasets, no data lag"
        }
    
    @staticmethod
    def scenario_3_portfolio_optimization() -> Dict[str, Any]:
        """
        Scenario 3: Portfolio Optimization (2 minutes)
        - Run MPT optimization
        - Show efficient frontier
        - Display optimal weights
        """
        return {
            "name": "Portfolio Optimization",
            "duration_minutes": 2,
            "steps": [
                {
                    "step": 1,
                    "action": "Select Portfolio Stocks",
                    "description": "User selects 5 stocks from portfolio for optimization",
                    "selected_stocks": ["RELIANCE.NS", "TCS.NS", "WIPRO.NS", "INFY.NS", "BAJAJFINSV.NS"]
                },
                {
                    "step": 2,
                    "action": "Run MPT Optimization",
                    "description": "Calculate efficient frontier and optimal weight allocation",
                    "optimization_result": {
                        "expected_return": 14.23,
                        "volatility": 16.45,
                        "sharpe_ratio": 0.865,
                        "weights": {
                            "RELIANCE.NS": 0.35,
                            "TCS.NS": 0.30,
                            "WIPRO.NS": 0.20,
                            "INFY.NS": 0.10,
                            "BAJAJFINSV.NS": 0.05
                        }
                    }
                },
                {
                    "step": 3,
                    "action": "Visualize Efficient Frontier",
                    "description": "D3.js scatter plot showing risk-return tradeoff",
                    "visualization": {
                        "type": "D3 scatter plot",
                        "x_axis": "Volatility (%)",
                        "y_axis": "Expected Return (%)",
                        "points": "100+ portfolio combinations",
                        "highlighted": ["Optimal Portfolio", "Current Portfolio", "NIFTY-50"]
                    }
                },
                {
                    "step": 4,
                    "action": "Compare Current vs Optimal",
                    "description": "Show how current portfolio compares to optimal",
                    "comparison": {
                        "current": {
                            "expected_return": 11.56,
                            "volatility": 18.23,
                            "sharpe_ratio": 0.634
                        },
                        "optimal": {
                            "expected_return": 14.23,
                            "volatility": 16.45,
                            "sharpe_ratio": 0.865
                        },
                        "improvement": "23% better risk-adjusted return"
                    }
                },
                {
                    "step": 5,
                    "action": "Rebalancing Recommendation",
                    "description": "Show how to rebalance to optimal allocation",
                    "recommendation": {
                        "action_type": "Sell INFY.NS, Increase RELIANCE.NS and TCS.NS",
                        "estimated_transaction_cost": 2500,
                        "tax_impact": 1500,
                        "net_expected_benefit": "2.67% annual return improvement"
                    }
                }
            ],
            "success_criteria": "Efficient frontier renders smoothly with 100+ datapoints"
        }
    
    @staticmethod
    def scenario_4_market_overview() -> Dict[str, Any]:
        """
        Scenario 4: Market Overview Dashboard (1.5 minutes)
        - Show market indices
        - Display sector performance
        - Identify top gainers/losers
        """
        return {
            "name": "Market Overview Dashboard",
            "duration_minutes": 1.5,
            "steps": [
                {
                    "step": 1,
                    "action": "Load Market Dashboard",
                    "description": "Display real-time market indices",
                    "indices": {
                        "NIFTY50": {
                            "index": 21456.85,
                            "change": 123.45,
                            "change_pct": 0.58,
                            "trades": 1250000
                        },
                        "SENSEX": {
                            "index": 70234.12,
                            "change": 325.10,
                            "change_pct": 0.47,
                            "trades": 980000
                        },
                        "NIFTY_BANK": {
                            "index": 45231.50,
                            "change": 287.65,
                            "change_pct": 0.64,
                            "trades": 650000
                        }
                    }
                },
                {
                    "step": 2,
                    "action": "Sector Performance",
                    "description": "Show sector-wise performance with color coding",
                    "sectors": [
                        {"name": "IT", "change_pct": 1.23, "leader": "TCS.NS"},
                        {"name": "Pharma", "change_pct": 0.45, "leader": "SUNPHARMA.NS"},
                        {"name": "Banking", "change_pct": 0.78, "leader": "HDFCBANK.NS"},
                        {"name": "Energy", "change_pct": -0.23, "leader": "RELIANCE.NS"},
                        {"name": "Auto", "change_pct": 0.12, "leader": "MARUTI.NS"}
                    ],
                    "visualization": "Color-coded gauges or heatmap"
                },
                {
                    "step": 3,
                    "action": "Top Gainers & Losers",
                    "description": "Scrollable list of top performers and underperformers",
                    "gainers": [
                        {"ticker": "WIPRO.NS", "price": 456.25, "change_pct": 3.45},
                        {"ticker": "INFY.NS", "price": 1823.50, "change_pct": 2.87},
                        {"ticker": "BAJAJFINSV.NS", "price": 1234.10, "change_pct": 2.34}
                    ],
                    "losers": [
                        {"ticker": "GAIL.NS", "price": 134.20, "change_pct": -2.34},
                        {"ticker": "COALINDIA.NS", "price": 456.75, "change_pct": -1.87},
                        {"ticker": "ONGC.NS", "price": 289.45, "change_pct": -1.23}
                    ]
                },
                {
                    "step": 4,
                    "action": "Market Breadth",
                    "description": "Display advancing vs declining stocks",
                    "breadth": {
                        "advances": 1834,
                        "declines": 1123,
                        "unchanged": 89,
                        "visualization": "Progress bar or ratio display"
                    }
                }
            ],
            "success_criteria": "Live data updates every 2 seconds with smooth transitions"
        }
    
    @staticmethod
    def scenario_5_trading_alert_workflow() -> Dict[str, Any]:
        """
        Scenario 5: Live Trading Alert & Execution (2 minutes)
        - Set price alert
        - Alert triggers
        - Real-time notification
        """
        return {
            "name": "Trading Alert Workflow",
            "duration_minutes": 2,
            "steps": [
                {
                    "step": 1,
                    "action": "Create Price Alert",
                    "description": "User sets alert for RELIANCE.NS above 2900",
                    "alert_config": {
                        "ticker": "RELIANCE.NS",
                        "type": "price",
                        "direction": "above",
                        "threshold": 2900,
                        "notification": "Email, SMS, In-app"
                    }
                },
                {
                    "step": 2,
                    "action": "Market Moves",
                    "description": "Simulate market movement - RELIANCE.NS reaches 2900.50",
                    "market_event": {
                        "time": datetime.utcnow().isoformat(),
                        "ticker": "RELIANCE.NS",
                        "price": 2900.50,
                        "trigger_status": "Alert threshold breached"
                    }
                },
                {
                    "step": 3,
                    "action": "Real-time Notification",
                    "description": "Instant notification displayed",
                    "notification": {
                        "title": "Price Alert - RELIANCE.NS",
                        "message": "RELIANCE.NS touched 2900.50 (threshold: 2900)",
                        "actions": ["View Chart", "Execute Trade", "Adjust Alert"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                },
                {
                    "step": 4,
                    "action": "Execute Quick Trade",
                    "description": "One-click order placement from notification",
                    "trade_execution": {
                        "order_type": "LIMIT",
                        "ticker": "RELIANCE.NS",
                        "quantity": 50,
                        "price": 2900,
                        "status": "Order placed successfully",
                        "order_id": f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                    }
                },
                {
                    "step": 5,
                    "action": "Trade Confirmation",
                    "description": "Show order confirmation and portfolio update",
                    "confirmation": {
                        "status": "Filled",
                        "filled_quantity": 50,
                        "filled_price": 2900,
                        "commission": 50,
                        "net_cost": 145050,
                        "portfolio_update": "Automatic position update"
                    }
                }
            ],
            "success_criteria": "Alert triggers within 2 seconds, order executes immediately"
        }
    
    @staticmethod
    def get_all_scenarios() -> List[Dict[str, Any]]:
        """Return all demo scenarios"""
        return [
            DemoScenarios.scenario_1_live_portfolio_tracking(),
            DemoScenarios.scenario_2_stock_comparison(),
            DemoScenarios.scenario_3_portfolio_optimization(),
            DemoScenarios.scenario_4_market_overview(),
            DemoScenarios.scenario_5_trading_alert_workflow()
        ]
    
    @staticmethod
    def get_demo_script() -> str:
        """Generate complete demo script"""
        script = """
CAPABL Financial AI - Track B Production Demo Script
Duration: 8-10 minutes
Platform: Professional React/Next.js Interface with Microservices Backend

===== INTRODUCTION (1 minute) =====
"Welcome to CAPABL, a production-ready financial analysis platform built on modern microservices architecture.
This demo showcases real-time portfolio tracking, advanced technical analysis, AI-driven optimization, and live
trading capabilities for the Indian financial market."

===== SCENARIO 1: PORTFOLIO TRACKING (2 minutes) =====
1. Show login screen → Dashboard load
2. Display portfolio: 15 positions, ₹5.87M total value, +6.77% YTD returns
3. Highlight live P&L updates (updating every 2 seconds)
4. Compare portfolio performance vs NIFTY-50 (+12.34% vs +5.23%)
5. Identify top gainer: WIPRO.NS +8.63%

===== SCENARIO 2: TECHNICAL ANALYSIS (2 minutes) =====
1. Navigate to Stock Comparison
2. Select 4 stocks: RELIANCE.NS, TCS.NS, WIPRO.NS, INFY.NS
3. Display interactive candlestick charts (1-month data)
4. Show technical indicators: SMA20, SMA50, Bollinger Bands, RSI
5. Display sentiment analysis (Positive: 0.78 for RELIANCE)
6. Highlight: WIPRO showing strong bullish setup

===== SCENARIO 3: PORTFOLIO OPTIMIZATION (2 minutes) =====
1. Navigate to Portfolio Optimizer
2. Select portfolio stocks for MPT analysis
3. Run optimization calculation
4. Display efficient frontier (D3 visualization)
5. Show optimal weights: RELIANCE 35%, TCS 30%, WIPRO 20%, INFY 10%, BAJAJFINSV 5%
6. Compare: Expected return +14.23% vs current +11.56% (23% improvement)
7. Show rebalancing recommendation

===== SCENARIO 4: MARKET OVERVIEW (1 minute) =====
1. Show market indices: NIFTY-50 +0.58%, SENSEX +0.47%
2. Display sector performance heatmap
3. Show top gainers: WIPRO +3.45%, INFY +2.87%
4. Show top losers: GAIL -2.34%, COALINDIA -1.87%
5. Market breadth: 1834 advances vs 1123 declines

===== SCENARIO 5: TRADING ALERT (1-2 minutes) =====
1. Create price alert: RELIANCE.NS above ₹2900
2. Simulate market movement to ₹2900.50
3. Show real-time notification popup
4. One-click order execution
5. Confirm trade: 50 shares @ ₹2900, Order ID displayed
6. Portfolio updates automatically

===== ARCHITECTURE HIGHLIGHT (1 minute) =====
"This platform runs on 5 microservices:
- API Gateway (8000): Authentication, rate limiting, routing
- Market Data Service (8001): Real-time quotes, technical analysis
- Portfolio Service (8002): Position tracking, P&L calculation
- Analytics Service (8003): Sentiment, optimization, comparisons
- Monitoring (8004): Real-time metrics and system health

All services are containerized, auto-scaled, and production-ready."

===== KEY FEATURES DEMONSTRATED =====
✓ Real-time portfolio tracking with live P&L
✓ Advanced technical analysis with Chart.js
✓ AI-driven portfolio optimization (MPT)
✓ News sentiment analysis integration
✓ One-click trading with real-time execution
✓ Mobile-responsive design
✓ Microservices architecture at scale
✓ Enterprise-grade security (JWT, encryption, rate limiting)

===== PERFORMANCE METRICS (displayed in monitoring dashboard) =====
- API Gateway: 150 req/sec, P99 latency 280ms
- Cache hit rate: 75%
- Error rate: <0.5%
- All services: 99.9% uptime
        """
        return script


# Initialize demo scenarios
demo = DemoScenarios()

if __name__ == "__main__":
    # Print demo script
    print(demo.get_demo_script())
    
    # Print all scenarios
    scenarios = demo.get_all_scenarios()
    print(f"\n\nTotal Scenarios: {len(scenarios)}")
    for s in scenarios:
        print(f"- {s['name']} ({s['duration_minutes']} min)")
