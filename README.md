# Fixed Income Analytics Dashboard 📈

A web-based analytics dashboard for US Treasury yield curve analysis,
built with Python, Streamlit, and the FRED API.

## Features
- Live US Treasury yield data (3M, 2Y, 5Y, 10Y, 30Y)
- Yield curve shape classification (Normal / Flat / Inverted / Fully Inverted)
- Recession signal indicator based on 10Y-2Y spread inversion
- Rolling 30-day volatility monitoring
- Spread z-score analysis
- Executive-style KPI summary table
- Interactive Plotly charts with date range filtering

## Tech Stack
- **Data:** FRED API (Federal Reserve Economic Data)
- **Analysis:** Python, pandas, NumPy
- **Dashboard:** Streamlit, Plotly
- **Deployment:** Local / Streamlit Cloud

## Setup

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/fixed-income-dashboard.git
cd fixed-income-dashboard

### 2. Install dependencies
pip install -r requirements.txt

### 3. Configure API key
cp config_template.py config.py
# Edit config.py and add your FRED API key
# Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html

### 4. Run the dashboard
streamlit run app.py

## Project Structure
```
fixed-income-dashboard/
├── src/
│   ├── data_fetcher.py   # FRED API connection and data pipeline
│   └── analyzer.py       # Yield curve analysis engine
├── app.py                # Streamlit dashboard
├── config_template.py    # API key template
└── requirements.txt      # Dependencies
```

## Key Concepts
- **Yield Spread:** Difference between long and short term treasury yields
- **Curve Inversion:** When short-term yields exceed long-term yields
- **Recession Signal:** 10Y-2Y inversion has preceded every US recession since 1955
- **Z-Score:** Measures how unusual current spreads are vs 1-year history

## Author
Built as a Fixed Income analytics project inspired by
Business Analytics Strategist roles in financial services.