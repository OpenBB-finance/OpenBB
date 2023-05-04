---
title: Economy
keywords: [economy, macro, index, treasury, fred, market, econdb, index, yield, curve, economic, indicators, micro, inflation, interest rate, interest, unemployment, gdp, gross domestic product, openbb terminal, how to, example, overview, futures, econdb, fred, yahoo finance, macro, index, forecasting, quantitative]
description: A brief guide to the Economy menu. It includes an introduction to the commands, functionality, data, and provides examples for use.
---
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

`<HeadTitle title="Economny - Terminal | OpenBB Docs" />`

## Overview

The `/economy` menu provides methods for querying macroeconomic data sets from sources like FRED, OECD, and EconDB.  To get the most out of this menu, sign up for a free API key from the [Federal Reserve of St. Louis](https://fred.stlouisfed.org/), and enter it into the OpenBB Terminal from the [`/keys` menu](https://docs.openbb.co/terminal/usage/guides/api-keys).  

## The Economy Menu

The menu is divided into four general sections:

- **Broad market**: General headline statistics from the markets today.
- **Country performance**: Country-specific data published by the OECD.
- **Databases**: Query time series.
- **Stored datasets**: Compare and chart multiple time series together.

Each command is listed below, with a short description.

### Broad Market

|Function Key |Description |
|:-----|-----:|
|overview |Market overview of either indices, bonds or currencies. |
|futures |Futures and commodities overview. |
|map |S&P 500 heat map. |
|bigmac |The Economist's Big Mac Index. |
|events |The economic calendar. |
|edebt |External debt statitistics for various countries. |

### Country Performance

|Function Key |Description |
|:-----|-----:|
|gdp |Nominal Gross Domestic Product (GDP). |
|rgdp |Real Gross Domestic Product (GDP). |
|fgdp |Forecasts of nominal and real Gross Domestic Product (GDP). |
|debt |Government debt-to-GDP ratios. |
|cpi |Harmonized CPI. |
|ccpi |CPI Components. |
|balance |Government tax revenues. |
|spending |Government spending. |
|trust |Confidence in government surveys. |

### Databases

|Function Key |Description |
|:-----|-----:|
|macro |Time series data by country and indicator. |
|treasury |Historical US Treasury rates. |
|fred |Query the FRED. |
|index |Historical daily time series for most major global indices. |

### Stored Datasets

|Function Key |Description |
|:-----|-----:|
|eval |A method for performing basic `eval` operations on a time series.
|plot |Plot multiple time series together. |

## Examples

This section will demonstrate some basic operations within the menu.

### events

A morning ritual might begin with checking the economic calendar for the day's - or week's - events.  The `events` command can browse the calendar by country and date.  By default, the current day for all countries will display in a table.

```console
/economy/events
```

![Economic Calendar](economy1.png)

To select a specific country, attach `--countries` to the command, then press the space bar.  Use the up or down arrow keys to browse the choices.

![Economic Calendar Countries](economy2.png)

### overview

The `overview` fetches the headline levels and rates from the Wall Street Journal.  Choose from of the categories by attaching the `-t` argument to the command.

```console
/economy/overview -t usbonds
```

![Overview](economy3.png)

|              |   Rate (%) |   Yld (%) |   Yld Chg (%) |
|:-------------|-----------:|----------:|--------------:|
| 30-Year Bond |      3.625 |     3.686 |        -0.028 |
| 10-Year Note |      3.5   |     3.343 |        -0.085 |
| 7-Year Note  |      3.5   |     3.323 |        -0.122 |
| 5-Year Note  |      3.5   |     3.305 |        -0.162 |
| 3-Year Note  |      3.75  |     3.513 |        -0.18  |
| 2-Year Note  |      3.875 |     3.838 |        -0.144 |
| 1-Year Bill  |      0     |     4.665 |        -0.09  |
| 6-Month Bill |      0     |     4.98  |         0.005 |
| 3-Month Bill |      0     |     5.212 |         0.064 |
| 1-Month Bill |      0     |     4.452 |         0.114 |

### debt

Compare debt-to-GDP ratios between groups of countries by entering them as a comma-separated list.

```console
/economy/debt -c australia,norway,united_states,italy,japan
```

![Debt-to-GDP](economy4.png)

### index

Major global indices are curated under the `index` command.  Adding `--show` to the command will display a table with the list.

```console
index --show
```

The cumulative returns of an index is returned instead of the level by attaching `-r` to the command. Multiple indices can be queried simultaneously.

```console
index sp500,sp400,sp600 --start 2023-01-01 -r
```

![Indices](economy6.png)

### fred

Lookup FRED series by keywords by attaching `-q` to the `fred` command.

```console
fred -q PCE
```

![Fred Series](economy7.png)

### plot

After requesting a time series, it gets populated under `Stored datasets`.  Plot them together, on a shared or separate y-axis, by using the `plot` command.

![Multi-Axis Plots](economy8.png)

```console
plot --y1 PCE --y2 sp500
```

![Plot Multiple Time Series](economy9.png)
