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

### openbbPlatformAsLLMTools

This notebook shows you how you can use OpenbB Platform as functions in an LLM by leveraging function calling.

- Create an LLM tool from an OpenBB Platform function
- Convert all OpenBB Platform functions to LLM tools
- Build a basic Langchain agent that can utilize function calling
- Run the agent

### usdLiquidityIndex

This notebook demonstrates how to query the Federal Reserve Economic Database and recreate the USD Liquidity Index.

- Search FRED for series IDs.
- Load multiple series as a single call.
- Unpacking the data response from the FRED query.
- Perform arithmetic operations on a DataFrame.
- Normalization methods for a series or DataFrame.
- Simple processes for creating charts.

### impliedEarningsMove

This notebook demonstrates how to calculate the implied earnings move using options prices from free sources.

- Get upcoming earnings calendar.
- Fetch options chains data.
- Get the last price of the underlying stock.
- Find the nearest call and put strikes to the last price of the stock.
- Calculate the implied daily move using the price of a straddle.

### streamlit/news

This is an example Streamlit dashboard for news headlines with data from Biztoc, Benzinga, FMP, Intrinio, and Tiingo.

:::warning
At least one API key is required. You can get a free Biztoc API key [here](https://rapidapi.com/thma/api/biztoc)
:::

To run, copy the file to your system, open a terminal, navigate to where the file is, and with your `obb` Python environment active, enter:

```
pip install streamlit
pip install openbb-biztoc
streamlit run news.py
```
