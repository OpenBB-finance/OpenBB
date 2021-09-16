```
usage: linear [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS] [-e S_END_DATE] [-h]
usage: regression -p 1 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS] [-e S_END_DATE] [-h]
```

Regression attempts to model the relationship between two variables by fitting a linear/quadratic/cubic/other equation to observed data. One variable is considered to be an explanatory variable, and the other is considered to be a dependent variable.

```
optional arguments:
  -i N_INPUTS, --input N_INPUTS
                        number of days to use for prediction.
  -d N_DAYS, --days N_DAYS
                        prediction days.
  -j N_JUMPS, --jumps N_JUMPS
                        number of jumps in training data.
  -e S_END_DATE, --end S_END_DATE
                        The end date (format YYYY-MM-DD) to select - Backtesting
  -h, --help            show this help message
```

![linear](https://user-images.githubusercontent.com/25267873/108604948-d3cc1780-73a8-11eb-860f-49274a34038b.png)
