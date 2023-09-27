# Jupyter Notebook Examples Using the OpenBB SDK

This folder is a collection of example notebooks that demonstrate some of the ways to get started using the OpenBB SDK.  To run them, ensure that the active kernel selected is the same Python virtual environment where OpenBB was installed.

## Table of Contents

### loadHistoricalPriceData

This notebook walks through collecting historical price data using a variety of methods and sources.

- Loading data with different intervals, and changing sources.
- A brief explanation of ticker symbology.
- Using other functions and modules to load data with besides `openbb.stocks.load()`.
- Gang-loading a list of tickers' price data in a single call.
- Drawing candle and line charts.

### copperToGoldRatio

This notebook explains how to calculate and plot the Copper-to-Gold ratio.

- Loading historical front-month futures prices.
- Getting the historical series from FRED for the 10-year constant maturity US treasury bill.
- Performing basic DataFrame operations.
- Creating OpenBB Figure objects, and plotting on two y-axis.

### realizedVolatilityModels

This notebook demonstrates the six, realized volatility models with in the Technical Analysis module.

- Explore differences between:
  - Standard Deviation
  - Parkinson
  - Hodges-Tompkins
  - Garman-Klass
  - Rogers-Satchell
  - Yang-Zhang
- Creating and plotting realized volatility cones.
- Overlaying multiple time series.
- Use the calculated outputs as inputs to a forecast model.

### usdLiquidityIndex

This notebook demonstrates how to query the Federal Reserve Economic Database and recreate the USD Liquidity Index.

- Search FRED for series IDs.
- Load multiple series as a single call.
- Unpacking the data response from the FRED query.
- Perform arithmetic operations on a DataFrame.
- Normalization methods for a series or DataFrame.
- Simple processes for creating charts.

### optionsChains

This notebook demonstrates how to fetch and work with options chains data.

- Use the new method for loading options chains data.
- Examine the differences of the data, between sources.
- Calculate and visualize volume and open interest by strike and expiration.
- Calculate and visualize the Net Delta Exposure, in dollars, by strike and expiration.
- Visualize the term structure of the implied volatility skew.
- Get tables with multiple single-leg options strategies.

### googleColabInstallation

This notebook demonstrates how to install the OpenBB SDK within Google Colab.


### volumeAtPrice

Volume-at-price is a chart used by technical analysts as a visual gauge to where the trading levels are concentrated, relative to price and volume.  In short, it is the sum of volume at different price levels.  This notebook utilizes individual components of the OpenBB SDK and combines them to build a new view.

- Price
- Volume
- VWAP
- SMA
- OpenBBFigure
