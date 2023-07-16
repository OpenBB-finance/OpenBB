---
title: Quantitative Analysis
keywords: [quantitative, analysis, qa, q/a, daily, indicators, signals, average, summary, normality, line, hist, cdf, bw, acf, qqplot, rolling, spread, quantile, skew, kurtosis, var, es, sh, so, om, raw, decompose, cusum, capm, beta, histogram, auto-correlation, value, median, crypto, forex, fx, cryptocurrency, stocks, examples, how to]
description: This guide introduces the Quantitative Analysis menu, which is common across many sections of the OpenBB Terminal, briefly describes the features, and provides examples in context.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Quantitative Analysis - Terminal | OpenBB Docs" />

<a href = "https://www.investopedia.com/terms/q/quantitativeanalysis.asp" target="_blank" rel="noreferrer noopener">Quantitative analysis (QA)</a> in finance is an approach that emphasizes mathematical and statistical analysis to help determine the value of a financial asset, such as a stock or option. The ultimate goal of financial quantitative analysis is to use quantifiable statistics and metrics to assist investors in making profitable investment decisions. Quantitative analysis is different from qualitative analysis, which looks at factors such as how companies are structured, the makeup of their management teams, and what their strengths and weaknesses are.

The Quantitative Analysis menu is a common menu to three asset classes:

- <a href = "/terminal/usage/intros/crypto/" target="_blank" rel="noreferrer noopener">Crypto</a>
- <a href = "/terminal/usage/intros/forex/" target= "_blank"  rel="noreferrer noopener">Forex</a>
- <a href = "/terminal/usage/intros/stocks/" target = "_blank"  rel="noreferrer noopener">Stocks</a>

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218976291-b31cf033-636d-4534-8327-062b8d573263.png"></img>

### How to use

Enter the menu, through one of the asset classes listed above, by entering `qa` in the Terminal. The ticker that is loaded before entering the menu will determine the timeframe for the analysis. To alter it, use the `load` function and pick a new `--start` and `--end` for the observation window. The QA functions target a specified column of the data. By default, this is returns. Use the `pick` command to chose a new target column.

The menu is divided into five categories of functions:

- Statistics
- Plots
- Rolling Metrics
- Risk
- Other

A summary of exportable statistics is displayed with the command, `summary`. The example here shows AAPL.

```
(🦋) /stocks/qa/ $ summary

                                                             Summary Statistics
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃       ┃ open    ┃ high    ┃ low     ┃ close   ┃ adjclose ┃ volume               ┃ dividends ┃ stock splits ┃ returns ┃ logret  ┃ logprice ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ count │ 758.000 │ 758.000 │ 758.000 │ 758.000 │ 758.000  │ 758.000              │ 758.000   │ 758.000      │ 758.000 │ 758.000 │ 758.000  │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ mean  │ 131.385 │ 133.089 │ 129.757 │ 131.491 │ 131.491  │ 109761415.963        │ 0.003     │ 0.005        │ 0.001   │ 0.001   │ 4.849    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ std   │ 29.088  │ 29.309  │ 28.833  │ 29.086  │ 29.086   │ 56077677.683         │ 0.027     │ 0.145        │ 0.023   │ 0.023   │ 0.258    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ min   │ 55.908  │ 56.011  │ 52.116  │ 54.999  │ 54.999   │ 35195900.000         │ 0.000     │ 0.000        │ -0.129  │ -0.138  │ 4.007    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ 10%   │ 79.502  │ 80.013  │ 79.051  │ 79.648  │ 79.648   │ 63139770.000         │ 0.000     │ 0.000        │ -0.026  │ -0.026  │ 4.378    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ 25%   │ 118.253 │ 119.721 │ 116.983 │ 118.555 │ 118.555  │ 74846950.000         │ 0.000     │ 0.000        │ -0.011  │ -0.011  │ 4.775    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ 50%   │ 136.551 │ 138.402 │ 134.433 │ 136.614 │ 136.614  │ 91962650.000         │ 0.000     │ 0.000        │ 0.001   │ 0.001   │ 4.917    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ 75%   │ 149.976 │ 151.796 │ 148.598 │ 150.446 │ 150.446  │ 124897575.000        │ 0.000     │ 0.000        │ 0.014   │ 0.014   │ 5.014    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ 90%   │ 166.432 │ 168.413 │ 164.183 │ 165.460 │ 165.460  │ 177115490.000        │ 0.000     │ 0.000        │ 0.026   │ 0.026   │ 5.109    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ max   │ 181.299 │ 181.607 │ 177.815 │ 180.684 │ 180.684  │ 426510000.000        │ 0.230     │ 4.000        │ 0.120   │ 0.113   │ 5.197    │
├───────┼─────────┼─────────┼─────────┼─────────┼──────────┼──────────────────────┼───────────┼──────────────┼─────────┼─────────┼──────────┤
│ var   │ 846.131 │ 858.993 │ 831.359 │ 845.978 │ 845.978  │ 3144705934370881.500 │ 0.001     │ 0.021        │ 0.001   │ 0.001   │ 0.067    │
└───────┴─────────┴─────────┴─────────┴─────────┴──────────┴──────────────────────┴───────────┴──────────────┴─────────┴─────────┴──────────┘
```

A simple line chart for the target column as a time-series is called with the `line` command, for example the `returns` column.

![Line Apple](https://user-images.githubusercontent.com/46355364/218976712-2d9c14ce-c89f-484d-81ca-a8f5d1ef6d7b.png)

Optional arguments to this command allows the user to draw and annotate on the chart.

```
(🦋) /stocks/qa/ $ line -h

usage: line [--log] [--ml ML] [--ms MS] [-h] [--export EXPORT]

Show line plot of selected data or highlight specific datetimes.

optional arguments:
  --log            Plot with y on log scale (default: False)
  --ml ML          Draw vertical line markers to highlight certain events (default: )
  --ms MS          Draw scatter markers to highlight certain events (default: )
  -h, --help       show this help message (default: False)
  --export EXPORT  Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about line' to access the related guide.


(🦋) /stocks/qa/ $

2022 Aug 08, 12:20 /stocks/qa/ $ pick high

Compare the beta between the loaded asset and another, using the `-r` flag to
deviate from the defaulted comparison, $SPY.

(🦋) /stocks/qa/ $ beta -r MSFT
```

![Beta](https://user-images.githubusercontent.com/46355364/218977134-52b00eec-a7f5-4dc9-ba62-343d0b546d30.png)

Most outputs are equipped with an `--export` flag, allowing the user to save the tables as a CSV, JSON, or XLSX file. The exports can then be imported into other menus like <a href="/terminal/usage/intros/econometrics/" target="_blank" rel="noreferrer noopener"> Econometrics</a>. Additional information on each specific command is displayed by attaching `-h` to it.

### Examples

Box and Whisker plots for monthly and yearly scales:

```
(🦋) /stocks/qa/$ bw
```

![Monthly box and whisker plot for Apple](https://user-images.githubusercontent.com/85772166/183483965-a6c2d076-4896-47ec-a314-fc6a574ad8de.png)

```
(🦋) /stocks/qa/ $ bw -y
```

![Yearly box and whisker plot for Apple](https://user-images.githubusercontent.com/85772166/183484096-73eadd0c-1618-4e95-a27b-79e81cd6afad.png)

Pick `logret` for rate of change to the returns of the asset:

```
(🦋) /stocks/qa/ $ pick logret

(🦋) /stocks/qa/ $ bw -y
```

![Yearly rate of change on returns from Apple](https://user-images.githubusercontent.com/85772166/183484172-5c001e9d-911c-44cd-848c-9ae5ec13dbc2.png)

`decompose` shows a visual representation of trend and seasonality.

![Additive Decompose of daily $AAPL data](https://user-images.githubusercontent.com/85772166/183484221-8e65e855-8a18-4bfd-8d49-b44ad50691b1.png)

`skew` shows the asymmetric distribution over a specified window (default of 14).

![Apple skewness indicator](https://user-images.githubusercontent.com/85772166/183484305-0ca714c4-a138-4c69-aee4-16fcc3aa3ac4.png)

`skew -w 5` Changing the window to five takes out some of the smoothness:

![Apple skewness indicator with a window of 5 days](https://user-images.githubusercontent.com/85772166/183484465-5c121ebc-d2d9-4f1d-a51f-10366aa4456a.png)

Sharpe Ratio over time, `sh`:

![Sharpe Ratio for Apple over time](https://user-images.githubusercontent.com/85772166/183484549-6bc723e3-42cc-4c2a-96d6-72ab96402833.png)

`cdf` calls the cumulative distribution function. Apple over the long term
exhibits a steep curve.

![Cumulative Distribution Function of Apple](https://user-images.githubusercontent.com/85772166/183484623-00e6ce46-4378-4391-94e3-9ea2045d2fb4.png)

Compared with Apple, Amazon is a more gently sloping s-curve.

![Cumulative Distribution Function of AMZN](https://user-images.githubusercontent.com/85772166/183484706-86874eb7-d454-4d38-aa78-d521fa56b1bd.png)

`capm` shows the stock's risk against the market's. $AAPL carries the risk of
whatever happens to the markets, happens to the stock.

```
2022 Aug 08, 13:51 /stocks/qa/ $ capm Beta: 1.15 Systematic Risk: 46.40%
Unsystematic Risk: 53.60%
```
