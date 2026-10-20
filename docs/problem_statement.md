# Problem Statement

## Purpose
Understand how Ethiopia's key economic indicators have moved over time,
using public World Bank data.

## Questions
1. In which years did Ethiopia's inflation exceed 20%, and in how many years did that happen?
2. What was the average annual change in the official exchange rate, and in which year was the single largest jump?
3. Is there a relationship between inflation and GDP growth? Is average growth lower in high-inflation years than in the other years?

## Inputs
- World Bank indicator data for Ethiopia (country code: ETH), CSV format
- Indicators (first version):
  - Inflation, consumer prices (annual %), code FP.CPI.TOTL.ZG
  - Official exchange rate (LCU per US$), code PA.NUS.FCRF
  - GDP growth (annual %), code NY.GDP.MKTP.KD.ZG
- Raw files are never modified

## Outputs
- A cleaned dataset (CSV)
- A summary table answering each question above
- A notebook with charts, runnable in Jupyter and Colab

## Out of scope (for version 1)
- Other countries
- Forecasting
- Dashboards or web apps
