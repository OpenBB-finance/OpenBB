```text
usage: acf [-l LAGS] [-h]
```
Auto-Correlation and Partial Auto-Correlation Functions for diff and diff diff stock data, see source: http://sciencedirect.com/topics/chemistry/autocorrelation-function

The autocorrelation function (ACF) defines how data points in a time series are related, on average, to the preceding data points (Box, Jenkins, & Reinsel, 1994).

A positive autocorrelation value for a particular lag τ can be interpreted as a measure of persistence of data points separated by this lag to stay above and/or below the mean value of the signal. A negative autocorrelation indicates that data points separated by this lag tend to alternate about the mean value. An important piece of information provided by the ACF is the maximum lag τmax that still has a significant value. This lag indicates the “memory” or temporal persistence of the fluctuation series. Data points separated by time lags greater than τmax are uncoupled. The ACF is often redundantly plotted for positive and negative values of τ, although by definition it is symmetric about τ = 0.

```
optional arguments:
  -l LAGS, --lags LAGS  maximum lags to display in plots (default: 15)
  -h, --help            show this help message (default: False
```

![acf](https://user-images.githubusercontent.com/46355364/154305242-176c3ba1-ebfc-43e7-a027-46251fb02463.png)
