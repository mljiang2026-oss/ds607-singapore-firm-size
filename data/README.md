# Data files

This directory contains the Orbis inputs and derived datasets used for the
DS607 Singapore firm-size project. The repository must remain private and
access must be limited to authorised project members.

## Directory structure

```text
data/
├── raw/orbis/
│   ├── orbis_sg_fy2023_part1.xlsx
│   ├── orbis_sg_fy2023_part2.xlsx
│   └── orbis_sg_fy2023_part3.xlsx
├── interim/
│   └── orbis_singapore_fy2023_merged.parquet
└── processed/
    └── orbis_singapore_fy2023_clean.parquet
```

## Reproducing the data preparation

From the repository root, create the Python environment and run:

```bash
pip install -r requirements.txt
python3 src/01_merge_orbis.py
python3 src/02_clean_data.py
```

`01_merge_orbis.py` verifies and combines the three Orbis exports.
`02_clean_data.py` standardises the variables and creates the primary
log-total-assets measure used in the downstream analysis.

The authorised Orbis export should be restricted to Singapore non-branch,
non-financial firms recorded as active and should include the FY2023 fields
listed below. NACE Section K is excluded. The three export parts must have
identical columns and non-overlapping BvD IDs.

## Analysis data dictionary

| Variable | Definition |
|---|---|
| `bvd_id` | Orbis BvD company identifier; used only for merging, duplicate checks, ownership-link exclusions, and matching audits. |
| `listing_status` / `listed` | Orbis listing status and its cleaned indicator (`Listed` = 1, `Unlisted` = 0). |
| `nace4` / `nace2` | NACE Rev. 2 four-digit core industry and constructed two-digit matching industry. |
| `consolidation_code` | Orbis financial-statement consolidation code. Matching uses its broad first character, C or U. |
| `incorporation_date` / `incorporation_year` | Orbis incorporation date and extracted year. Year-only records are retained. |
| `assets_th_usd` | FY2023 total assets in thousand USD, as supplied by Orbis. |
| `assets_usd` | Total assets converted to USD (`assets_th_usd * 1,000`). |
| `log_assets` | Natural logarithm of `assets_usd` for strictly positive assets. Primary outcome. |
| `revenue_th_usd` | FY2023 operating revenue in thousand USD. Used for outcome robustness. |
| `employees` | FY2023 employee count. Not analysed because private-firm coverage is insufficient. |
| `ish_bvd_id` | BvD ID of the immediate shareholder, where recorded. |
| `guo_bvd_id` | BvD ID of the global ultimate owner, where recorded. |
| `is_listed_subsidiary` | True for an unlisted firm whose recorded immediate shareholder or global ultimate owner is a sampled listed firm. |
| `closing_date_2023` | Firm-specific closing date associated with the FY2023 Orbis field. |

Additional raw columns are retained locally for auditing but are not needed for
the statistical analysis. Firm age, age band, and broad consolidation status
are constructed in the notebooks.

## Access restrictions

- Do not make this repository public.
- Do not share the firm-level files outside the authorised project team.
- Do not upload the firm-level files to public repositories or external AI
  systems.
- Recheck the applicable SMU and Orbis licence terms before changing access.
