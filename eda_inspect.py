"""Quick EDA — inspect all 3 CSVs in the data/ folder."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

for csv_path in sorted(DATA_DIR.glob("*.csv")):
    print(f"\n{'='*60}")
    print(f"FILE: {csv_path.name}")
    print(f"{'='*60}")

    df = pd.read_csv(csv_path)

    print(f"\nShape: {df.shape[0]:,} rows × {df.shape[1]} cols")

    print("\nColumns & dtypes:")
    print(df.dtypes.to_string())

    print("\nFirst 5 rows:")
    print(df.head(5).to_string())

    print("\nNull counts:")
    nulls = df.isnull().sum()
    if nulls.sum() == 0:
        print("  (no nulls)")
    else:
        print(nulls[nulls > 0].to_string())

    print("\nBasic stats (numeric cols):")
    print(df.describe().to_string())
