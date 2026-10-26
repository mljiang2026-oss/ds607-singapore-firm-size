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

## Access restrictions

- Do not make this repository public.
- Do not share the firm-level files outside the authorised project team.
- Do not upload the firm-level files to public repositories or external AI
  systems.
- Recheck the applicable SMU and Orbis licence terms before changing access.
