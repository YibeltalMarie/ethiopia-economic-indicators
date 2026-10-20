# Ethiopia Economic Indicators Pipeline

A reproducible, tested pipeline that loads World Bank data for Ethiopia, cleans it
with small functions, analyzes it with NumPy, and reports the findings in a notebook.

## Questions

1. In which years did Ethiopia's inflation exceed 20%, and in how many years did that happen?
2. What was the average annual percentage change in the official exchange rate (mean and median), and in which year was the single largest jump?
3. Is there a relationship between inflation and GDP growth? Is average growth lower in high-inflation years than in the other years?

See `docs/problem_statement.md` for the full problem definition.

## Results snapshot

Computed from raw files downloaded on 2026-10-20 (World Bank source last updated
2026-10-08). Later World Bank releases can revise recent values; the notebook always
shows the current numbers.

- **Q1:** inflation was above 20% in 10 of 60 years: 1976, 1991, 2008, 2011, 2012, and 2020 to 2024.
- **Q2:** the mean yearly change in the official exchange rate was 6.3% but the median was only 0.37%, because the rate did not change in 23 of 64 years. The largest jump was 78.4% in 1993.
- **Q3:** the correlation between inflation and GDP growth is -0.13 (weak). Mean growth was 5.49% in high-inflation years and 5.33% in other years, so growth was not lower in high-inflation years. With only 10 high-inflation years and a correlation that shows association rather than cause, this is not evidence about whether inflation affects growth.

## Pipeline

    load  ->  clean  ->  process  ->  report

- `load.py`: downloads raw indicator files, makes them read-only, records provenance
- `clean.py`: small pure functions that read, filter, reshape, validate, and merge
- `process.py`: NumPy functions that answer the three questions
- `report.py`: summary text and charts, built from the computed answers

## Project structure

    data/raw/            Original World Bank files and MANIFEST.json (never edited)
    data/processed/      Cleaned output (rebuilt from raw, not committed)
    src/econ_pipeline/   load.py, clean.py, process.py, report.py
    tests/               Unit tests (pytest)
    notebooks/           The notebook that runs the whole pipeline
    docs/                Problem statement and data quality notes

## Setup

    git clone https://github.com/YibeltalMarie/ethiopia-economic-indicators.git
    cd ethiopia-economic-indicators
    python -m venv .venv
    source .venv/bin/activate        # on Windows: .venv\Scripts\activate
    pip install -r requirements.txt

To reproduce the exact tested environment (developed on Python 3.13), use
`pip install -r requirements-lock.txt` instead of the last line.

## Run the tests

    python -m pytest

## Run the notebook

Locally: `pip install jupyterlab`, then open
`notebooks/ethiopia_economic_indicators.ipynb` and run all cells.

In Google Colab: open the same notebook there. Its first code cell clones the
repository and installs `requirements.txt`.

## Data

World Bank World Development Indicators, downloaded through the World Bank's public
download endpoint. Raw files are kept exactly as received; `data/raw/MANIFEST.json`
records the source URL and download time of each. See the World Bank's terms of use
for reuse conditions. Data quality findings are in `docs/data_quality_notes.md`.

## Limitations

- Recent values can be revised in later World Bank releases.
- Correlation describes a linear pattern in these years and does not show cause.
- The exchange rate has long fixed-rate periods, so a single average blends two
  very different regimes; the median and largest jump are reported too.
- Version 1 covers one country and three indicators.

## Roadmap

- [ ] Other countries (`build_dataset` already takes a `country_code`)
- [ ] More indicators (add a line to `INDICATORS` in `load.py`)
- [ ] Report fixed-rate and floating-rate periods of the exchange rate separately
- [ ] Run the tests automatically on every push (GitHub Actions)
- [ ] A command-line entry point that runs the whole pipeline
