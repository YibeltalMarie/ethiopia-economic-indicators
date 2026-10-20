# Data Quality Notes

Source: World Bank World Development Indicators, raw files in `data/raw/`
(downloaded 2026-10-20, source last updated 2026-10-08; see `data/raw/MANIFEST.json`).

## Structure issues (confirmed from the raw files)

1. Metadata and blank lines come before the real header (the header is on line 5),
   so the first 4 lines must be skipped when reading.
2. The data is wide: one column per year (1960 to 2025), one row per country.
   It must be reshaped to long format (country, year, value).
3. Missing values are empty strings in the CSV and must become proper missing values (NaN).
4. Every data row ends with a trailing comma, which creates an extra empty column
   (read as "Unnamed: 70"). It must be dropped.
5. Regional and income-group aggregates (for example AFE) are mixed in with countries,
   so we must filter by country code (ETH).
6. The file starts with a byte order mark (BOM), so it must be read as utf-8-sig.

## Ethiopia-specific findings

| Indicator | Years with data | Range | Gaps inside range |
|---|---|---|---|
| Inflation (FP.CPI.TOTL.ZG) | 60 | 1966 to 2025 | none |
| Official exchange rate (PA.NUS.FCRF) | 65 | 1960 to 2024 | none |
| GDP growth (NY.GDP.MKTP.KD.ZG) | 64 | 1962 to 2025 | none |

- Each file contains exactly one Ethiopia row.
- Missing years occur only at the start or end of each series, never in the middle,
  so no interpolation is needed. Missing years are dropped, never filled.
- Overlap of inflation and GDP growth: 1966 to 2025 (60 years), used for questions 1 and 3.
- Overlap of all three indicators: 1966 to 2024 (59 years).
- Exchange rate has 65 values, so 64 year-over-year changes (question 2).
- Extremes: inflation min -9.81 (1986), max 44.36 (2008); exchange rate min 2.07 (1974),
  max 82.60 (2024); GDP growth min -11.14 (1985), max 13.86 (1987).
- The exchange rate minimum of 2.07 first appears in 1974, which suggests a long fixed-rate
  period (to be confirmed). If confirmed, many year-over-year changes are zero and the mean
  change is dominated by a few large jumps, so the median is reported alongside the mean.
- The newest values (2024, 2025) may be revised in future World Bank releases.

## Cleaning rules (each becomes a function in src/econ_pipeline/clean.py)

1. Read with skiprows=4 and encoding utf-8-sig.
2. Drop the phantom "Unnamed" column.
3. Filter to a country code (parameter, default ETH).
4. Reshape wide to long: year as int, value as float.
5. Drop rows with missing values; never fill.
6. Sort by year and keep one row per year.
7. Merge indicators on year.
8. Validate: numeric values, no duplicate years; raise an error on failure.
