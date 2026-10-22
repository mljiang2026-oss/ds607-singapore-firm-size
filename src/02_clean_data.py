from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# File locations
# --------------------------------------------------

INPUT_FILE = Path(
    "data/interim/orbis_singapore_fy2023_merged.parquet"
)

OUTPUT_FILE = Path(
    "data/processed/orbis_singapore_fy2023_clean.parquet"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Read merged Orbis data
# --------------------------------------------------

df = pd.read_parquet(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")
print(f"Columns before renaming: {len(df.columns)}")


# --------------------------------------------------
# Rename variables
# --------------------------------------------------

rename_map = {
    "BvD ID number": "bvd_id",
    "Listing status": "listing_status",
    "NACE Rev. 2, core code (4 digits)": "nace4",
    "Consolidation code": "consolidation_code",
    "Date of incorporation": "incorporation_date",
    "Total assets th USD 2023": "assets_th_usd",
    "Operating revenue (Turnover) th USD 2023": "revenue_th_usd",
    "Number of employees 2023": "employees",
    "Country ISO code": "country_code",
    "Branch": "branch",
    "Status": "status",
    "ISH - BvD ID number": "ish_bvd_id",
    "GUO - BvD ID number": "guo_bvd_id",
    "Closing date 2023": "closing_date_2023",
}

df = df.rename(columns=rename_map)

print("\nRenamed columns:")

for old_name, new_name in rename_map.items():
    print(f"  {old_name} -> {new_name}")


# --------------------------------------------------
# Clean text variables
# --------------------------------------------------

text_columns = [
    "bvd_id",
    "listing_status",
    "nace4",
    "consolidation_code",
    "country_code",
    "branch",
    "status",
    "ish_bvd_id",
    "guo_bvd_id",
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# --------------------------------------------------
# Convert numeric variables
# --------------------------------------------------

numeric_columns = [
    "assets_th_usd",
    "revenue_th_usd",
    "employees",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# --------------------------------------------------
# Convert date variables
# --------------------------------------------------

date_columns = [
    "incorporation_date",
    "closing_date_2023",
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
    )


# --------------------------------------------------
# Construct listed indicator
# --------------------------------------------------

df["listed"] = (
    df["listing_status"]
    .map({
        "Listed": 1,
        "Unlisted": 0,
    })
    .astype("Int64")
)


# --------------------------------------------------
# Convert total assets from thousand USD to USD
# --------------------------------------------------

df["assets_usd"] = df["assets_th_usd"] * 1000


# --------------------------------------------------
# Construct log total assets
# --------------------------------------------------

# where() replaces non-positive assets with NaN before taking logs.
df["log_assets"] = np.log(
    df["assets_usd"].where(df["assets_usd"] > 0)
)


# --------------------------------------------------
# Construct two-digit industry code
# --------------------------------------------------

df["nace4"] = (
    df["nace4"]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(4)
)

df["nace2"] = df["nace4"].str[:2]


# --------------------------------------------------
# Print data-quality checks
# --------------------------------------------------

print("\nListing status:")
print(df["listing_status"].value_counts(dropna=False))

print("\nTotal-assets checks:")
print(f"Missing assets: {df['assets_th_usd'].isna().sum():,}")
print(f"Positive assets: {df['assets_th_usd'].gt(0).sum():,}")
print(f"Non-positive assets: {df['assets_th_usd'].le(0).sum():,}")

print("\nIndustry-code checks:")
print(f"Missing NACE 4-digit codes: {df['nace4'].isna().sum():,}")
print(f"Missing NACE 2-digit codes: {df['nace2'].isna().sum():,}")

print("\nDate checks:")
print(
    f"Missing incorporation dates: "
    f"{df['incorporation_date'].isna().sum():,}"
)
print(
    f"Missing 2023 closing dates: "
    f"{df['closing_date_2023'].isna().sum():,}"
)


# --------------------------------------------------
# Save cleaned data
# --------------------------------------------------

df.to_parquet(
    OUTPUT_FILE,
    index=False,
    engine="pyarrow",
)

print(f"\nRows saved: {len(df):,}")
print(f"Columns saved: {len(df.columns)}")
print(f"Saved cleaned data to: {OUTPUT_FILE}")