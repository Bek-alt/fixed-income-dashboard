from src.data_fetcher import load_or_fetch, get_curve_snapshot
from src.analyzer import (
    classify_yield_curve,
    recession_signal,
    rolling_volatility,
    spread_zscore,
    summary_stats
)

# Load data
df, spreads = load_or_fetch()
snapshot = get_curve_snapshot(df)

# 1. Yield curve classification
shape, description = classify_yield_curve(snapshot)
print("\n--- Yield Curve Shape ---")
print(f"Shape      : {shape}")
print(f"Description: {description}")

# 2. Recession signals
print("\n--- Recession Signal (last 10 days) ---")
signals = recession_signal(spreads)
print(signals.tail(10))

# 3. Rolling volatility
print("\n--- 30-Day Rolling Volatility (last 5 rows) ---")
vol = rolling_volatility(df)
print(vol.tail())

# 4. Spread z-scores
print("\n--- Spread Z-Scores (last 5 rows) ---")
zscores = spread_zscore(spreads)
print(zscores.tail())

# 5. Summary stats
print("\n--- Summary Statistics ---")
stats = summary_stats(df, spreads)
print(stats)