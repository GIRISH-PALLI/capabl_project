# Financial Research AI Agent (CAPABL Internship)

Track: **A + B (Week 3-4 Architecture Build)**  
Duration: **8 Weeks**  
Current Scope: **Multi-source Financial Analysis Agent**

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
    chatbot.py
    market_tools.py
    portfolio.py
    research_workflow.py
    sentiment_service.py
    stock_service.py
    technical_analysis.py
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
