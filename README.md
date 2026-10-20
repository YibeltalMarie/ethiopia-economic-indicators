# Ethiopia Economic Indicators Pipeline

A reproducible pipeline that loads World Bank data for Ethiopia, cleans it with
tested functions, analyzes it with NumPy, and reports findings in a notebook.

See `docs/problem_statement.md` for the questions this project answers.

## Project structure

    data/raw/            Original World Bank files (never edited)
    data/processed/      Cleaned output (rebuilt from raw, not committed)
    src/econ_pipeline/   load.py, clean.py, process.py
    tests/               Unit tests
    notebooks/           Jupyter/Colab notebook
    docs/                Problem statement and notes

## Setup

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Status

Work in progress. Version 1 covers inflation, exchange rate, and GDP growth.
