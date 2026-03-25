# src/analyzer.py
import pandas as pd
import numpy as np

def classify_yield_curve(snapshot):
    """
    Classify the current shape of the yield curve.
    snapshot: latest row from yield DataFrame
    """
    spread_10y_2y = snapshot["10Y"] - snapshot["2Y"]
    spread_2y_3m  = snapshot["2Y"]  - snapshot["3M"]

    if spread_10y_2y < 0 and spread_2y_3m < 0:
        return "⛔ Fully Inverted", "Strong recession warning signal"
    elif spread_10y_2y < 0:
        return "🔴 Inverted (10Y-2Y)", "Recession warning signal"
    elif spread_10y_2y < 0.15:
        return "🟡 Flat", "Slowdown signal, watch closely"
    else:
        return "🟢 Normal", "Healthy growth expected"

def recession_signal(spreads):
    """
    Flag dates where 10Y-2Y spread was negative (inverted).
    Historically predicts recession 12-18 months ahead.
    """
    signals = pd.DataFrame(index=spreads.index)
    signals["10Y-2Y"]         = spreads["10Y-2Y"]
    signals["inverted"]       = spreads["10Y-2Y"] < 0
    signals["inversion_days"] = (
        signals["inverted"]
        .groupby((~signals["inverted"]).cumsum())
        .cumcount()
    )
    return signals

def rolling_volatility(df, window=30):
    """
    Compute 30-day rolling volatility for each yield.
    Useful for risk monitoring.
    """
    vol = df.rolling(window=window).std()
    vol.columns = [f"{c}_vol" for c in vol.columns]
    return vol

def spread_zscore(spreads, window=252):
    """
    Compute z-score of spreads vs 1-year rolling mean.
    Helps identify when spreads are unusually wide or tight.
    """
    rolling_mean = spreads.rolling(window=window).mean()
    rolling_std  = spreads.rolling(window=window).std()
    zscore = (spreads - rolling_mean) / rolling_std
    zscore.columns = [f"{c}_zscore" for c in zscore.columns]
    return zscore

def summary_stats(df, spreads):
    """
    Generate a summary statistics table for the dashboard.
    """
    latest_yields  = df.dropna().iloc[-1]
    latest_spreads = spreads.dropna().iloc[-1]
    prev_yields    = df.dropna().iloc[-2]
    prev_spreads   = spreads.dropna().iloc[-2]

    stats = {}

    for col in df.columns:
        
        stats[f"{col} Yield"] = {
            "current": round(latest_yields[col], 2),
            "change":  round(latest_yields[col] - prev_yields[col], 3),
            "1Y_high": round(df[col].last("365D").max(), 2),
            "1Y_low":  round(df[col].last("365D").min(), 2),
        }

    for col in spreads.columns:
        stats[f"{col} Spread"] = {
            "current": round(latest_spreads[col], 2),
            "change":  round(latest_spreads[col] - prev_spreads[col], 3),
            "1Y_high": round(spreads[col].last("365D").max(), 2),
            "1Y_low":  round(spreads[col].last("365D").min(), 2),
        }

    return pd.DataFrame(stats).T