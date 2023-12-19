# Jupyter Notebook Examples Using the OpenBB Platform

This folder is a collection of example notebooks that demonstrate some of the ways to get started with using the OpenBB Platform.  To run them, ensure that the active kernel selected is the same Python virtual environment where OpenBB was installed.

## Table of Contents

### googleColab

This notebook installs the OpenBB Platform in a Google Colab environment with examples for:

- Logging into OpenBB Hub
- Setting the output preference
- Fetching options and company fundamentals data
- Creating bar chart visualizations

### findSymbols

This notebook provides an introduction to discovering, finding, and searching ticker symbols.

- Search
- Find company and institutional filings
- Screen stocks by region and metrics

### loadHistoricalPriceData

This notebook walks through collecting historical price data, at different intervals, using a variety of sources.

- Loading data with different intervals, and changing sources
- A brief explanation of ticker symbology
- Resampling a time series index
- Some differences between providers, and comparing outputs

### financialStatements

This set of examples introduces financial statements in the OpenBB Platform and compares the free cash flow yields of large-cap retail industry companies.

- Financial statements
- What to expect with data from different sources
- Financial attributes
- Ratios and other metrics

### copperToGoldRatio

This notebook explains how to calculate and plot the Copper-to-Gold ratio.

- Loading historical front-month futures prices.
- Getting the historical series from FRED for the 10-year constant maturity US treasury bill.
- Performing basic DataFrame operations.
- Creating charts with Plotly Graph Objects.
