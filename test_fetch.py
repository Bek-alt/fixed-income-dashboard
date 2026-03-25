# test_fetch.py
from src.data_fetcher import load_or_fetch, get_curve_snapshot

df, spreads = load_or_fetch()

print("\n--- Last 5 rows of yield data ---")
print(df.tail())

print("\n--- Last 5 rows of spreads ---")
print(spreads.tail())

print("\n--- Latest Yield Curve Snapshot ---")
print(get_curve_snapshot(df))