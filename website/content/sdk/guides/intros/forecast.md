---
title: Forecast
keywords: ["machine, learning, prediction, forecasting, neural, network, linear, regression, time, series, scripts, data, mining, cleaning, transformer, analyst, equity, research, api, sdk, application, python, notebook, jupyter"]
excerpt: "This guide introduces the Forecast SDK in the context of the OpenBB SDK."

---

The Forecast module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.forecast`
​
## How to Use
​
The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​
```python
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib inline
```
​
A brief description below highlights the main Functions and Modules available in the ETF SDK

|Path |Type | Description |
| :--------- | :---------: | ----------: |
|openbb.forecast.load |Function |Show the data selected data on a chart |
|openbb.forecast.plot |Function |Plot a specific column of a loaded dataset |
|openbb.forecast.clean |Function |Clean a dataset by filling or dropping NaNs |
|openbb.forecast.combine |Function |Combine columns from different datasets |
|openbb.forecast.desc |Function |Show descriptive statistics of a dataset |
|openbb.forecast.corr |Function |Plot the correlation coefficients for dataset features |
|openbb.forecast.season |Function |Plot the seasonality for a dataset column |
|openbb.forecast.delete |Function |Delete columns from dataset |
|openbb.forecast.rename |Function |Rename columns from dataset |
|openbb.forecast.export |Function |Export a processed dataset |
|openbb.forecast.signal |Function |Add Price Signal (short vs. long term) |
|openbb.forecast.atr |Function |Add Average True Range |
|openbb.forecast.ema |Function |Add Exponentially Weighted Moving Average |
|openbb.forecast.sto |Function |Add Stochastic Oscillator %K and %D |
|openbb.forecast.rsi |Function |Add Relative Strength Index |
|openbb.forecast.roc |Function |Add Rate of Change |
|openbb.forecast.mom |Function |Add Momentum |
|openbb.forecast.delta |Function |Add % Change |
|openbb.forecast.autoces |Function |Automatic Complex Exponential Smoothing Model |
|openbb.forecast.autoets |Function |Automatic ETS (Error, Trend, Seasonality) Model |
|openbb.forecast.seasonalnaive |Function |Seasonal Naive Model |
|openbb.forecast.expo |Function |Probabilistic Exponential Smoothing |
|openbb.forecast.theta |Function |Theta Method |
|openbb.forecast.linregr |Function |Probabilistic Linear Regression (feat. Past covariates and Explainability) |
|openbb.forecast.regr |Function |Regression (feat. Past covariates and Explainability) |
|openbb.forecast.rnn |Function |Probabilistic Recurrent Neural Network (RNN, LSTM, GRU) |
|openbb.forecast.brnn |Function |Block Recurrent Neural Network (RNN, LSTM, GRU) (feat. Past covariates) |
|openbb.forecast.nbeats |Function |Neural Bayesian Estimation (feat. Past covariates) |
|openbb.forecast.tcn |Function |Temporal Convolutional Neural Network (feat. Past covariates) |
|openbb.forecast.trans |Function |Transformer Network (feat. Past covariates) |
|openbb.forecast.tft |Function |Temporal Fusion Transformer Network(feat. Past covariates) |
|openbb.forecast.nhits |Function |Neural Hierarchical Interpolation (feat. Past covariates) |
|openbb.forecast.rwd |Function |Random Walk with Drift Model  |
|openbb.forecast.autoselect |Function |Select best statistical model from AutoARIMA, AutoETS, AutoCES, MSTL, etc. |

Alteratively you can print the contents of the Forecast SDK with:
​
```python
help(openbb.forecast)
```

## Examples

### corr
​
Shows a correlation matrix between columns in dataset
​
```python
df = pd.read_csv(ANDREW_REPLACE)
openbb.forecast.corr_view(df)
```
![Corr View](https://user-images.githubusercontent.com/72827203/202424217-b549b6e7-b121-4273-a7d9-b478e89cd65a.png)

​
### season
​
This command allows you to see seasonality patterns in your data

```python
df = pd.read_csv(ANDREW_REPLACE)
openbb.forecast.season(df, "Close")
```
​

![Season View](https://user-images.githubusercontent.com/72827203/202426763-ae0b5e49-a570-47d8-9558-3b3530e72b0d.png)
​
### expo

Predicts the future value of time series data using exponential smoothing
​
```python
df = pd.read_csv(ANDREW_REPLACE)
openbb.forecast.expo(df, "Close")
```
​
Here was can now see a chart and table with the expected values, and historic data. The chart also tells us how our backtesing performed, so that we can know the accuracy of our prediction.
​

![Expo View](https://user-images.githubusercontent.com/72827203/202429347-b3ab488d-d4f6-42bb-80d1-c66b3c5a92df.png)
​
