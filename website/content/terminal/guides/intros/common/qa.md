---
title: Quantitative Analysis
keywords:
  [
    "quantitative",
    "analysis",
    "qa",
    "q/a",
    "daily",
    "indicators",
    "signals",
    "average",
    "summary",
    "normality",
    "line",
    "hist",
    "cdf",
    "bw",
    "acf",
    "qqplot",
    "rolling",
    "spread",
    "quantile",
    "skew",
    "kurtosis",
    "var",
    "es",
    "sh",
    "so",
    "om",
    "raw",
    "decompose",
    "cusum",
    "capm",
    "beta",
    "histogram",
    "auto-correlation",
    "value",
    "median",
    "crypto",
    "forex",
    "fx",
    "cryptocurrency",
    "stocks",
  ]
date: "2022-08-08"
type: guides
status: publish
excerpt: "This guide introduces the Quantitative Analysis menu, which is common across many sections of the OpenBB Terminal, briefly describes the features, and provides examples in context."
---

<a href = "https://www.investopedia.com/terms/q/quantitativeanalysis.asp" target="_blank" rel="noreferrer noopener">Quantitative analysis (QA)</a> in finance is an approach that emphasizes mathematical and statistical analysis to help determine the value of a financial asset, such as a stock or option. The ultimate goal of financial quantitative analysis is to use quantifiable statistics and metrics to assist investors in making profitable investment decisions. Quantitative analysis is different from qualitative analysis, which looks at factors such as how companies are structured, the makeup of their management teams, and what their strengths and weaknesses are.

The Quantitative Analysis menu is a common menu to three asset classes:

- <a href = "/terminal/guides/intros/crypto/" target="_blank" rel="noreferrer noopener">Crypto</a>
- <a href = "/terminal/guides/intros/forex/" target= "_blank"  rel="noreferrer noopener">Forex</a>
- <a href = "/terminal/guides/intros/stocks/" target = "_blank"  rel="noreferrer noopener">Stocks</a>

<img width="1110" alt="The Quantitative Analysis menu" src="https://user-images.githubusercontent.com/85772166/183483507-a4bef3e8-6603-46fb-a022-424f18af32d6.png"></img>

### How to use

Enter the menu, through one of the asset classes listed above, by entering `qa` in the Terminal. The ticker that is loaded before entering the menu will determine the timeframe for the analysis. To alter it, use the `load` function and pick a new `--start` and `--end` for the observation window. The QA functions target a specified column of the data. By default, this is returns. Use the `pick` command to chose a new target column.

<img width="358" alt="Picking a new target column" src="https://user-images.githubusercontent.com/85772166/183483572-6127eaff-69d2-4d67-8e60-8d7756a043b0.png"></img>

The menu is divided into five categories of functions:

- Statistics
- Plots
- Rolling Metrics
- Risk
- Other

A summary of exportable statistics is displayed with the command, `summary`. The example here shows $APPL.

<img width="1109" alt="QA summary for Apple" src="https://user-images.githubusercontent.com/85772166/183483647-3414adae-c4de-4b1e-81a5-04a4d8a51e19.png"></img>

A simple line chart for the target column as a time-series is called with the `line` command.

![Line chart of Apple highs over time](https://user-images.githubusercontent.com/85772166/183483733-043f9c21-c408-4526-8c39-16937a05d46a.png)

Optional arguments to this command allows the user to draw and annotate on the chart.

```
2022 Aug 08, 12:14 /stocks/qa/ $ line -h usage: line [--log] [-d] [--ml ML]
[--ms MS] [-h] [--export EXPORT]

Show line plot of selected data or highlight specific datetimes.

options: --log Plot with y on log scale (default: False) --ml ML Draw vertical
line markers to highlight certain events (default: ) --ms MS Draw scatter
markers to highlight certain events (default: ) -h, --help show this help
message (default: False) --export EXPORT Export figure into png, jpg, pdf, svg
(default: )

For more information and examples, use 'about line' to access the related guide.

2022 Aug 08, 12:20 /stocks/qa/ $ pick high

Compare the beta between the loaded asset and another, using the `-r` flag to
deviate from the defaulted comparison, $SPY.

2022 Aug 08, 12:34 /stocks/qa/ $ beta -r MSFT

Loading Daily MSFT stock with starting period 2019-08-05 for analysis.
```

<img width="762" alt="Beta of $AAPL relative to $MSFT" src="https://user-images.githubusercontent.com/85772166/183483898-dac417a8-0afe-46d2-b8e9-e855e8752fc8.png"></img>

Most outputs are equipped with an `--export` flag, allowing the user to save the tables as a CSV, JSON, or XLSX file. The exports can then be imported into other menus like <a href="/terminal/guides/intros/econometrics/" target="_blank" rel="noreferrer noopener"> Econometrics</a>. Additional information on each specific command is displayed by attaching `-h` to it.

### Examples

Box and Whisker plots for monthly and yearly scales:

```
2022 Aug 08, 12:47 /stocks/qa/ $ bw
```

![Monthly box and whisker plot for Apple](https://user-images.githubusercontent.com/85772166/183483965-a6c2d076-4896-47ec-a314-fc6a574ad8de.png)

```
2022 Aug 08, 12:47 /stocks/qa/ $ bw -y
```

![Yearly box and whisker plot for Apple](https://user-images.githubusercontent.com/85772166/183484096-73eadd0c-1618-4e95-a27b-79e81cd6afad.png)

Pick `logret` for rate of change to the returns of the asset:

```
2022 Aug 08, 12:47 /stocks/qa/ $ pick logret

2022 Aug 08, 12:51 /stocks/qa/ $ bw -y
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
