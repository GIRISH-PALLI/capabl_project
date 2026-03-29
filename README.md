# Financial Research AI Agent (CAPABL Internship)

Track: **A1 + B (Week 5-6 Domain Specialization + Advanced Build)**  
Duration: **8 Weeks**  
Current Scope: **Indian Market Specialization + Multi-API Financial Analysis Agent**

## Week 5-6 Outcome

- Indian market support for NSE/BSE tickers with `.NS/.BO` normalization
- INR-aware pricing display and Indian market hours context (IST)
- SQLite-based stock watchlists and alert rules
- Fundamental analysis snapshot (P/E, debt/equity, growth, ROE) and sector comparison
- Multi-API resilience layer integrating 5+ financial/economic APIs with retry/error handling
- Advanced analytics with MPT portfolio optimization and Black-Scholes options pricing
- PostgreSQL production schema for financial data lake and alert/audit workflows

## Week 3-4 Outcome

- Multi-source agent with stock + news sentiment + macro tools
- Technical analysis engine with moving averages, RSI, MACD, Bollinger Bands, ATR
- Stock comparison dashboard (price, momentum, sentiment)
- Portfolio analytics (invested value, market value, P&L)
- Financial research workflow orchestration with LangGraph (with fallback)
- API throttling and caching for resilient data calls

## Project Structure

```text
capabl_project/
  app/
    main.py
  agent/
    advanced_models.py
    alerts.py
    chatbot.py
    fundamental_analysis.py
    india_market.py
    market_tools.py
    multi_api_service.py
    portfolio.py
    research_workflow.py
    sentiment_service.py
    stock_service.py
    technical_analysis.py
    watchlist_db.py
  database/
    postgres_schema.sql
  requirements.txt
  README.md
  .gitignore
```

## Setup (Local)

1. Create and activate virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run app:

   ```bash
   streamlit run app/main.py
   ```

## Deploy on Streamlit Cloud

1. Push this project to GitHub.
2. Open Streamlit Cloud and create a new app from your repo.
3. Set main file path to: `app/main.py`
4. Deploy.

## Track A Checklist Status

- [x] Integrate 2 financial tools (stock data + news sentiment)
- [x] Implement basic financial calculations (moving averages, RSI)
- [x] Add simple news sentiment analysis using TextBlob/VADER
- [x] Create stock comparison functionality
- [x] Handle API rate limiting and caching
- [x] Milestone: Agent provides multi-dimensional stock analysis

## Track A1 (Indian Stock Analysis Assistant) Status

- [x] Integrate NSE/BSE data via Yahoo Finance (`.NS/.BO` suffix handling)
- [x] Add SQLite database for saving stock watchlists
- [x] Create basic fundamental analysis (P/E, debt ratios, growth metrics)
- [x] Implement sector comparison for Indian markets
- [x] Add INR currency handling and Indian market hours

## Track B (Week 5-6) Status

- [x] Integrate 5+ financial APIs with error handling and retries
- [x] Design complex PostgreSQL schema for financial data
- [x] Implement portfolio optimization using Modern Portfolio Theory (Monte Carlo Sharpe max)
- [x] Add real-time style alerts and notification checks in app refresh cycle
- [x] Create multi-asset class analysis (equities, fixed income, commodities)
- [x] Advanced: Implement options pricing model (Black-Scholes)

## Optional API Keys (for full multi-API mode)

Set any of these as environment variables to activate provider calls:

- `ALPHA_VANTAGE_API_KEY`
- `FINNHUB_API_KEY`
- `FMP_API_KEY`
- `TWELVE_DATA_API_KEY`
- `FRED_API_KEY`

## Track B Checklist Status

- [x] All Track A requirements
- [x] Implement complex agent workflow with LangGraph for financial research
- [x] Add 4+ financial tools (stocks, options, futures, bonds, economic indicators)
- [x] Implement sophisticated sentiment analysis using transformer models (optional toggle)
- [x] Add portfolio tracking and performance analytics
- [x] Create comprehensive financial data pipeline with ETL snapshot output
- [x] Implement advanced technical analysis indicators

## Notes

- Transformer sentiment is optional and controlled by a UI toggle. If transformer dependencies are unavailable at runtime, the app automatically falls back to VADER/TextBlob/lexicon sentiment.
- LangGraph is also optional at runtime. If unavailable, the same workflow steps run sequentially.
