# Bibliometrics

Project to build and consolidate bibliometric indicators for researchers at the School of Government and Public Transformation, combining data from **Scopus**, **Google Scholar**, and **RePEc/LogEc**.

## Objective

Generate analysis-ready datasets (Python/Tableau) for:

- Scientific output by researcher (publication level).
- Citations and impact indicators.
- Collaboration signals (co-authorship/affiliations).
- Working paper performance in RePEc.

## Repository structure

```text
bibliometrics/
├── README.md
└── scopus/
    ├── scopus_publication_level_dataset.ipynb
    ├── Google_Scholar.ipynb
    ├── repec_report.ipynb
    ├── data/
    ├── scopus_out/
    ├── google_scholar/
    └── tableau/
```

## Data sources

- **Scopus API (Elsevier)**: publications by `author_id`.
- **Google Scholar (scholarly)**: profile and publications by `scholar_user_id`.
- **LogEc/RePEc**: working paper download/view statistics.
- **SJR / internal files** in `scopus/data/` for enrichment and context.

## Requirements

- Python 3.10+ (recommended 3.11)
- Jupyter Notebook / JupyterLab
- Packages:
  - `pandas`
  - `requests`
  - `openpyxl`
  - `pyarrow`
  - `scholarly`
  - `beautifulsoup4`

Quick install:

```bash
pip install pandas requests openpyxl pyarrow scholarly beautifulsoup4 jupyter
```

## How to run the project

### 1) Scopus publication dataset

Notebook: `scopus/scopus_publication_level_dataset.ipynb`

- Queries the Scopus API for each `author_id`.
- Builds a publication-level dataset by researcher.
- Saves:
  - `scopus/scopus_out/scopus_publications.csv`
  - `scopus/scopus_out/fetch_log.csv`

### 2) Google Scholar extraction

Notebook: `scopus/Google_Scholar.ipynb`

- Retrieves profile and publication history per researcher.
- Deduplicates publications per researcher.
- Saves:
  - `scopus/google_scholar/scholar_profiles_all.csv`
  - `scopus/google_scholar/scholar_publications_all.csv`
  - `scopus/google_scholar/scholar_publications_consolidated.csv`
  - `scopus/google_scholar/scholar_errors.csv`

### 3) RePEc / LogEc report

Notebook: `scopus/repec_report.ipynb`

- Downloads and parses Top working paper tables.
- Exports to Excel:
  - `scopus/data/gnt_last_3_months.xlsx`
  - `scopus/data/gnt_last_12_months.xlsx`
  - `scopus/data/gnt_total.xlsx`

## Current outputs in the repository

- `scopus/scopus_out/scopus_publications.csv`: 167 rows.
- `scopus/scopus_out/fetch_log.csv`: 21 rows.
- `scopus/google_scholar/scholar_profiles_all.csv`: 20 rows.
- `scopus/google_scholar/scholar_publications_all.csv`: 972 rows.
- `scopus/google_scholar/scholar_publications_consolidated.csv`: 972 rows.

## Visualization

- `scopus/tableau/DashboardPubs.twbx`: Tableau workbook for analysis and dashboarding.

## Important notes

- Set the Elsevier key using the `ELSEVIER_API_KEY` environment variable.
- Do not store API keys in notebooks or version control.
- Some external sources (Google Scholar / LogEc) may change format or availability.
