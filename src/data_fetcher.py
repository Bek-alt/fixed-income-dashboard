# src/data_fetcher.py
import pandas as pd
from fredapi import Fred
from config import FRED_API_KEY, TREASURY_SERIES, START_DATE
import os

def get_fred_client():
    return Fred(api_key=FRED_API_KEY)

def fetch_yield_data():
    """Fetch all treasury yields from FRED and combine into one DataFrame."""
    fred = get_fred_client()
    frames = {}

    for label, series_id in TREASURY_SERIES.items():
        print(f"Fetching {label} yield...")
        s = fred.get_series(series_id, observation_start=START_DATE)
        frames[label] = s

    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = df.dropna(how="all")      # drop rows where ALL yields missing
    df = df.ffill()                # forward fill minor gaps
    return df

def compute_spreads(df):
    """Compute key yield spreads used in Fixed Income analysis."""
    spreads = pd.DataFrame(index=df.index)
    spreads["10Y-2Y"]  = df["10Y"] - df["2Y"]    # most watched recession signal
    spreads["10Y-3M"]  = df["10Y"] - df["3M"]    # Fed preferred spread
    spreads["30Y-10Y"] = df["30Y"] - df["10Y"]   # long-end steepness
    spreads["5Y-2Y"]   = df["5Y"]  - df["2Y"]    # short-end steepness
    return spreads

def get_curve_snapshot(df):
    """Get the latest yield curve as a single row."""
    latest = df.dropna().iloc[-1]
    return latest

def save_data(df, spreads):
    """Save to CSV for caching so we don't hit API every run."""
    os.makedirs("data", exist_ok=True)  # Ensure the 'data' directory exists
    df.to_csv("data/yields.csv")
    spreads.to_csv("data/spreads.csv")
    print("Data saved to /data folder.")

def load_or_fetch():
    """Load from cache if available, otherwise fetch fresh."""
    try:
        df = pd.read_csv("data/yields.csv", index_col="date", parse_dates=True)
        spreads = pd.read_csv("data/spreads.csv", index_col="date", parse_dates=True)
        print("Loaded from cache.")
    except FileNotFoundError:
        df = fetch_yield_data()
        spreads = compute_spreads(df)
        save_data(df, spreads)
    return df, spreads