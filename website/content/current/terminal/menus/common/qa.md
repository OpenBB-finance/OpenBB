---
title: Quantitative Analysis
description: The page provides an overview of Quantitative Analysis in finance and
  its application in different asset classes like Crypto, Forex, and Stocks. It also
  highlights its usage in making profitable investment decisions, the use of terminal
  commands for analyzing data, and the export of data for further analysis.
keywords:
- Quantitative analysis
- Asset classes
- Finance
- Crypto
- Forex
- Stocks
- Terminal
- Financial quantitative analysis
- Investment decisions
- Statistics
- Metrics
- Risk
- Investors
- Quantifiable statistics
- Command summary
- Line chart
- Target column
- Observation window
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Quantitative Analysis - Common Menus | OpenBB Terminal Docs" />

<a href = "https://www.investopedia.com/terms/q/quantitativeanalysis.asp" target="_blank" rel="noreferrer noopener">Quantitative analysis (QA)</a> in finance is an approach that emphasizes mathematical and statistical analysis to help determine the value of a financial asset, such as a stock or option. The ultimate goal of financial quantitative analysis is to use quantifiable statistics and metrics to assist investors in making profitable investment decisions. Quantitative analysis is different from qualitative analysis, which looks at factors such as how companies are structured, the makeup of their management teams, and what their strengths and weaknesses are.

The Quantitative Analysis menu is a common menu to three asset classes:

- <a href = "/terminal/usage/intros/crypto/" target="_blank" rel="noreferrer noopener">Crypto</a>
- <a href = "/terminal/usage/intros/forex/" target= "_blank"  rel="noreferrer noopener">Forex</a>
- <a href = "/terminal/usage/intros/stocks/" target = "_blank"  rel="noreferrer noopener">Stocks</a>


![Screenshot 2023-10-30 at 11 15 59 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/e191455f-e626-486b-ae22-4da8e9fd6811)

## Usage

Enter the menu, through one of the asset classes listed above, by entering `qa` in the Terminal. The ticker that is loaded before entering the menu will determine the timeframe for the analysis. To alter it, use the `load` function and pick a new `--start` and `--end` for the observation window. The QA functions target a specified column of the data. By default, this is returns. Use the `pick` command to chose a new target column.

The menu is divided into five categories of functions:

- Statistics
- Rolling Metrics
- Risk
- Other

### Summary

A summary of exportable statistics is displayed with the command, `summary`. The example here shows AAPL.

```console
stocks
load aapl
qa
summary
```

![summary](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/16fc2132-765e-4b1b-9461-8e365551b278)

### Line

A simple line chart for the target column as a time-series is called with the `line` command, for example the `returns` column.

To use the same data and target column, enter:

```console
line
```

![line](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f0407a98-f88b-4880-a2f4-53c2b0b62418)

### Beta

The `beta` command shows the beta of the loaded asset with respect to another.  Use the `-r` parameter to select the asset to compare against.

```console
beta -r xlk
```

![Screenshot 2023-10-30 at 11 48 31 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/4df72127-c766-4099-ba89-1eed0e274f4c)

### Pick

To select a different target, like log returns, use the `pick` command.

```console
pick -t logret
```

![Screenshot 2023-10-30 at 11 38 58 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/93faab58-659b-45a0-aeaf-bed95cb511e3)

The choice will be reflected on-screen after the menu is refreshed, `?`, `h`, `help` - with no command attached.

### Rolling

The `rolling` command plots the rolling mean and standard deviation of the target column over a selectable window of time.

```console
pick -t close
rolling --windows 30
```

![Screenshot 2023-10-30 at 12 04 15 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b0de1f0c-7e1d-4fad-9546-075b2024a8b3)

### CDF

The Cumulative Distribution Function (`cdf`) displays the probabilities with quantiles.

```console
load aapl --start 2004-10-30 --monthly
pick -t returns
cdf
```

![Screenshot 2023-10-30 at 12 14 20 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/54e84236-e730-4083-9e27-c3a44e84e3ee)

### Skew

The `skew` command shows the asymmetric distribution over a specified window.  Adjust this window to suit the interval of data loaded.  With monthly data, a window of 12 represents one-year.

```console
skew
```

![Screenshot 2023-10-30 at 12 23 19 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f1e7e0e5-79fe-4ac7-8a4f-dbbb32793c50)


### CAPM

The `capm` command uses the Fama French Factors to determine market risk against the loaded asset.  The output of this function is printed directly to the screen.

```console
capm
```

```console
Beta:                   1.24
Systematic Risk:        63.63%
Unsystematic Risk:      36.37%
```
