"""Deep EDA — unique values, date ranges, price values."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

for csv_path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(csv_path)
    print(f"\n{'='*60}")
    print(f"FILE: {csv_path.name}")
    print(f"  Products  : {sorted(df['product'].unique())}")
    print(f"  Regions   : {sorted(df['region'].unique())}")
    print(f"  Prices    : {sorted(df['price'].unique())}")
    dates = pd.to_datetime(df['date'])
    print(f"  Date range: {dates.min().date()} to {dates.max().date()}")
    print(f"  Unique dates: {dates.nunique()}")
    # Check if all days in the range are present
    full_range = pd.date_range(dates.min(), dates.max(), freq='D')
    missing = set(full_range) - set(dates)
    print(f"  Missing days in range: {len(missing)}")

# Combined
print("\n" + "="*60)
print("COMBINED (all 3 files)")
print("="*60)
dfs = [pd.read_csv(p) for p in sorted(DATA_DIR.glob("*.csv"))]
combined = pd.concat(dfs, ignore_index=True)
print(f"  Total rows: {len(combined):,}")
print(f"  Products  : {sorted(combined['product'].unique())}")
print(f"  Regions   : {sorted(combined['region'].unique())}")
print(f"  Prices    : {sorted(combined['price'].unique())}")
all_dates = pd.to_datetime(combined['date'])
print(f"  Date range: {all_dates.min().date()} to {all_dates.max().date()}")
print(f"  Unique dates: {all_dates.nunique()}")
# Check for duplicate (date, product, region) combos
dupes = combined.duplicated(subset=['date', 'product', 'region'])
print(f"  Duplicate rows (date+product+region): {dupes.sum()}")
