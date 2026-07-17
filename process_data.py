"""
Data processing script for Quantium Task 2.

Soul Foods asked: "Were sales higher before or after the Pink Morsel price
increase on the 15th of January, 2021?"

The raw data lives in three CSV files (data/daily_sales_data_{0,1,2}.csv),
each row being the quantity of a given morsel sold in a given region at a
given price on a given day. Soul Foods only cares about Pink Morsels.

This script converts those three raw files into a single formatted output
file containing exactly three fields, as specified by the task brief:

    Sales      -> quantity * price  (Pink Morsels only)
    Date       -> the sale date, untouched
    Region     -> the region, untouched

After processing it also prints a before/after comparison around the
2021-01-15 price change so the Soul Foods question can be answered at
a glance.

Run from the project root with the venv active:
    .venv\\Scripts\\python.exe process_data.py
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path


# ── Paths ────────────────────────────────────────────────────────────────────
RAW_DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR   = RAW_DATA_DIR / "processed"
OUTPUT_FILE  = OUTPUT_DIR / "sales_data.csv"

PRICE_CHANGE_DATE = pd.Timestamp("2021-01-15")
TARGET_PRODUCT    = "pink morsel"


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading raw CSVs ...")
raw_dfs = []
for csv_path in sorted(RAW_DATA_DIR.glob("daily_sales_data_*.csv")):
    df = pd.read_csv(csv_path)
    print(f"  {csv_path.name}: {len(df):,} rows")
    raw_dfs.append(df)

raw = pd.concat(raw_dfs, ignore_index=True)
print(f"\nCombined raw: {len(raw):,} rows  ({raw.shape[1]} cols)")


# ── Normalise text columns ─────────────────────────────────────────────────────
# Lower-case and strip whitespace so the product filter is robust.
for col in ("product", "region"):
    raw[col] = raw[col].str.lower().str.strip()


# ── Filter to Pink Morsels only ────────────────────────────────────────────────
before = len(raw)
pink = raw[raw["product"] == TARGET_PRODUCT].copy()
print(f"\nFiltering to '{TARGET_PRODUCT}': {before:,} -> {len(pink):,} rows")


# ── Clean price ───────────────────────────────────────────────────────────────
# Strip the leading $ and cast to float.
pink["price"] = (
    pink["price"]
    .str.replace("$", "", regex=False)
    .str.strip()
    .astype(float)
)


# ── Parse date ────────────────────────────────────────────────────────────────
pink["date"] = pd.to_datetime(pink["date"])


# ── Derive Sales = quantity * price ───────────────────────────────────────────
pink["Sales"] = pink["quantity"] * pink["price"]


# ── Select & rename to the three required fields ──────────────────────────────
# Per the Task 2 spec the output file should contain exactly:
#     Sales, Date, Region
output = pink.rename(columns={"date": "Date", "region": "Region"})[
    ["Sales", "Date", "Region"]
].copy()

# Sort for stable, reproducible output.
output.sort_values(["Date", "Region"], inplace=True)
output.reset_index(drop=True, inplace=True)


# ── Sanity checks ─────────────────────────────────────────────────────────────
assert output["Sales"].notna().all(),          "NaN in Sales"
assert output["Date"].notna().all(),             "NaN in Date"
assert output["Region"].notna().all(),            "NaN in Region"
assert (output["Sales"] >= 0).all(),            "Negative Sales found"
assert len(output) == len(pink),                "Row count mismatch after selection"

date_min, date_max = output["Date"].min(), output["Date"].max()
assert date_min == pd.Timestamp("2018-02-06"),  f"Unexpected min date: {date_min}"
assert date_max == pd.Timestamp("2022-02-14"),  f"Unexpected max date: {date_max}"

# Region values should be the four Soul Foods regions only.
assert set(output["Region"].unique()) == {"east", "north", "south", "west"}, \
    f"Unexpected regions: {sorted(output['Region'].unique())}"

# Pink Morsel price should be $3.00 before 2021-01-15 and $5.00 on/after.
pre_prices  = pink.loc[pink["date"] <  PRICE_CHANGE_DATE, "price"].unique()
post_prices = pink.loc[pink["date"] >= PRICE_CHANGE_DATE, "price"].unique()
assert set(pre_prices)  == {3.00}, f"Unexpected pre-change prices: {pre_prices}"
assert set(post_prices) == {5.00}, f"Unexpected post-change prices: {post_prices}"

print("\nSanity checks passed.")


# ── Final output summary ─────────────────────────────────────────────────────
print(f"\nOutput rows: {len(output):,}")
print(f"Output cols: {list(output.columns)}")
print(f"Date range : {date_min.date()} to {date_max.date()}")
print(f"Regions    : {sorted(output['Region'].unique())}")

print("\nSample (first 8 rows):")
print(output.head(8).to_string(index=False))

print("\nSample (last 4 rows):")
print(output.tail(4).to_string(index=False))


# ── Answer the Soul Foods question ────────────────────────────────────────────
pre  = output.loc[output["Date"] <  PRICE_CHANGE_DATE, "Sales"].sum()
post = output.loc[output["Date"] >= PRICE_CHANGE_DATE, "Sales"].sum()
n_pre  = (output["Date"] <  PRICE_CHANGE_DATE).sum()
n_post = (output["Date"] >= PRICE_CHANGE_DATE).sum()

print("\n" + "=" * 60)
print("PINK MORSel SALES — BEFORE vs AFTER 2021-01-15 price rise")
print("=" * 60)
print(f"  Before: {n_pre:>5,} rows  | total sales = ${pre:>14,.2f}")
print(f"  After : {n_post:>5,} rows  | total sales = ${post:>14,.2f}")
print(f"  Ratio  : post/pre = {post/pre:.2f}x")
print("=" * 60)


# ── Save ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR.mkdir(exist_ok=True)
output.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved: {OUTPUT_FILE}  ({len(output):,} rows, "
      f"{len(output.columns)} cols: {list(output.columns)})")
