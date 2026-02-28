# Financial Research AI Agent (CAPABL Internship)

Track: **A - Essential**  
Duration: **8 Weeks**  
Current Scope: **Week 1-2 Foundation & Quick Win**

## Week 1-2 Outcome

- Working stock chatbot for Indian symbols (`RELIANCE.NS`, `TCS.NS`)
- Live price snapshot + candlestick chart visualization
- Streamlit app ready for deployment (Streamlit Cloud)

## Project Structure

```text
capabl_project/
  app/
    main.py
  agent/
    __init__.py
    chatbot.py
    stock_service.py
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

## Suggested 2-Minute Demo Script

1. Open app and show sidebar ticker selector.
2. Select `RELIANCE.NS`; explain KPI cards and candlestick chart.
3. Ask chatbot: `What is RELIANCE.NS price?`
4. Ask chatbot: `Show TCS.NS stock price`
5. Conclude with deployment URL and Week 1-2 milestone achieved.

## Week 1-2 Checklist Status

- [x] Create GitHub repo with financial project structure
- [x] Set up development environment (Python, pandas, yfinance, LangChain)
- [x] Build basic stock price chatbot with Indian stock support
- [x] Add simple chart visualization using Plotly/Streamlit
- [x] Prepare deployment flow on Streamlit Cloud
- [ ] Record 2-minute demo showing stock price queries
- [x] Milestone: Working deployable demo with Indian stock data

## Next (Week 3)

- Add News API integration
- Add basic sentiment score (positive/neutral/negative)
- Show sentiment next to price summary
