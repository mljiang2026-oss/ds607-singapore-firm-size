from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File locations
# --------------------------------------------------

RAW_DIR = Path("data/raw/orbis")
OUTPUT_DIR = Path("data/interim")
OUTPUT_FILE = OUTPUT_DIR / "orbis_singapore_fy2023_merged.parquet"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Locate the three Orbis exports
# --------------------------------------------------

files = sorted(RAW_DIR.glob("orbis_sg_fy2023_part*.xlsx"))

if len(files) != 3:
    raise ValueError(
        f"Expected 3 Orbis Excel files, but found {len(files)}: "
        f"{[file.name for file in files]}"
    )

print("Files to be merged:")

for file in files:
    print(f"  {file.name}")


# --------------------------------------------------
# Read each Results worksheet
# --------------------------------------------------

frames = []
reference_columns = None

for file in files:
    df = pd.read_excel(
        file,
        sheet_name="Results",
        engine="calamine",
    )

    # Remove spaces before or after column names
    df.columns = df.columns.astype(str).str.strip()

    # Drop the first blank-header Orbis export sequence column
    first_column = str(df.columns[0])

    if first_column.startswith("Unnamed"):
        df = df.iloc[:, 1:].copy()

    # Check that all three exports contain identical columns
    current_columns = df.columns.tolist()

    if reference_columns is None:
        reference_columns = current_columns
    elif current_columns != reference_columns:
        raise ValueError(
            f"The columns in {file.name} do not match the first file."
        )

    # Preserve raw Orbis values consistently.
    # Numeric and date conversion will be performed in 02_clean_data.py.
    df = df.astype("string")

    # Retain source file for local auditing
    df["_source_file"] = file.name

    print(
        f"{file.name}: "
        f"{len(df):,} companies, "
        f"{len(current_columns):,} Orbis columns"
    )

    frames.append(df)


# --------------------------------------------------
# Combine the files vertically
# --------------------------------------------------

combined = pd.concat(
    frames,
    axis=0,
    ignore_index=True,
)

expected_rows = 48_995

if len(combined) != expected_rows:
    raise ValueError(
        f"Expected {expected_rows:,} rows, "
        f"but the merged data contain {len(combined):,} rows."
    )


# --------------------------------------------------
# Check company BvD identifiers
# --------------------------------------------------

# This is the sampled company's own identifier.
# ISH and GUO identifiers refer to shareholders or global owners.
id_column = "BvD ID number"

if id_column not in combined.columns:
    raise KeyError(
        f"Required identifier column was not found: {id_column}"
    )

combined[id_column] = (
    combined[id_column]
    .astype("string")
    .str.strip()
)

missing_id_count = (
    combined[id_column].isna()
    | combined[id_column].eq("")
).sum()

duplicate_count = combined.loc[
    combined[id_column].notna()
    & combined[id_column].ne(""),
    id_column,
].duplicated(keep=False).sum()

print(f"Company ID column: {id_column}")
print(f"Missing BvD IDs: {missing_id_count:,}")
print(f"Rows with duplicated BvD IDs: {duplicate_count:,}")

if missing_id_count > 0:
    raise ValueError(
        "Some companies have missing BvD ID numbers."
    )

if duplicate_count > 0:
    raise ValueError(
        "Duplicated BvD IDs were found. "
        "Check whether the export ranges overlap."
    )

# --------------------------------------------------
# Save as Parquet
# --------------------------------------------------

combined.to_parquet(
    OUTPUT_FILE,
    index=False,
    engine="pyarrow",
)

print("\nMerge completed successfully.")
print(f"Final number of companies: {len(combined):,}")
print(f"Final number of columns: {len(combined.columns):,}")
print(f"Saved locally to: {OUTPUT_FILE}")