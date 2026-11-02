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

# Orbis records incorporation dates in mixed formats. In particular, many
# firms have only a four-digit year (for example, "2006"). A direct
# pd.to_datetime conversion can turn those values into missing dates, so keep
# the incorporation year explicitly and use 1 January as a harmless placeholder
# date when only the year is available. Downstream matching uses the year, not
# the placeholder day or month.
incorporation_text = (
    df["incorporation_date"]
    .astype("string")
    .str.strip()
)

df["incorporation_year"] = pd.to_numeric(
    incorporation_text.str.extract(r"((?:18|19|20)\d{2})", expand=False),
    errors="coerce",
).astype("Int64")

parsed_incorporation_date = pd.to_datetime(
    incorporation_text,
    errors="coerce",
)
year_start_date = pd.to_datetime(
    df["incorporation_year"].astype("string") + "-01-01",
    errors="coerce",
)
df["incorporation_date"] = parsed_incorporation_date.fillna(year_start_date)

df["closing_date_2023"] = pd.to_datetime(
    df["closing_date_2023"],
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
# Flag private subsidiaries of sampled listed firms
# --------------------------------------------------

# The proposal excludes private firms whose immediate shareholder (ISH) or
# global ultimate owner (GUO) is one of the sampled listed firms. Retaining a
# flag, rather than deleting rows here, preserves a transparent audit trail
# while allowing every downstream analysis to use the same exclusion rule.
listed_ids = set(
    df.loc[df["listed"].eq(1), "bvd_id"]
    .dropna()
    .astype("string")
)
owner_is_sampled_listed = (
    df["ish_bvd_id"].isin(listed_ids)
    | df["guo_bvd_id"].isin(listed_ids)
)
df["is_listed_subsidiary"] = (
    df["listed"].eq(0)
    & owner_is_sampled_listed
).astype("boolean")


# --------------------------------------------------
# Convert total assets from thousand USD to USD
# --------------------------------------------------

df["assets_usd"] = df["assets_th_usd"] * 1000


# --------------------------------------------------
# Construct log total assets
# --------------------------------------------------

# Take logs only for strictly positive assets. Building the output in two
# steps avoids divide-by-zero warnings while preserving non-positive values
# as missing for the downstream analysis.
positive_assets = df["assets_usd"].fillna(0).gt(0)
df["log_assets"] = np.nan
df.loc[positive_assets, "log_assets"] = np.log(
    df.loc[positive_assets, "assets_usd"].astype("float64")
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
    f"Missing incorporation years: "
    f"{df['incorporation_year'].isna().sum():,}"
)
print(
    f"Missing 2023 closing dates: "
    f"{df['closing_date_2023'].isna().sum():,}"
)

print("\nSubsidiary exclusion flag:")
print(
    "Private subsidiaries of sampled listed firms: "
    f"{df['is_listed_subsidiary'].sum():,}"
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
