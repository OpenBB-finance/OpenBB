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
|valuation |Valuation of sectors, industries, and countries for US-listed stocks. |
|performance |Performance of sectors, industry, and countries for US-listed stocks. |
|usdli |USD Liquidity Index |

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

![Economic Calendar](https://user-images.githubusercontent.com/85772166/236106887-07732390-bee3-44e0-a69f-a71c8ee90a8e.png)

To select a specific country, attach `--countries` to the command, then press the space bar.  Use the up or down arrow keys to browse the choices.

![Economic Calendar Countries](https://user-images.githubusercontent.com/85772166/236106932-473c0f02-af80-49a6-bdb3-548ac1e689fa.png)

### overview

The `overview` fetches the headline levels and rates from the Wall Street Journal.  Choose from of the categories by attaching the `-t` argument to the command.

```console
/economy/overview -t usbonds
```

![Overview](https://user-images.githubusercontent.com/85772166/236106975-961d7163-2ac8-4e05-b8df-34f2cf4908e7.png)

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

![Debt-to-GDP](https://user-images.githubusercontent.com/85772166/236107021-231e7472-10a0-4208-a92e-fe56c81076c0.png)

### usdli

Compare the US Dollar Liquidity Index against a selection of indices published to FRED.

```console
/economy/usdli -o WILLSMLCAP
```

![USD Liquidity Index](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1a2abf90-aa81-4d02-a77a-c913bfef14d7)

The indices available to overlay are displayed in a table by adding, `--show`, to the command.

```console
/economy/usdli --show
```

### valuation

Get valuations of industries and sectors for the US equity universe.  Select the focus by using the, `-g` (`--group`), parameter.

![Valuation By Industry](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/0793bd01-95b9-46f3-90b5-5c4af851283f)

```console
valuation --group consumer_cyclical
```

![Consumer Cyclical Valuations](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/53e670fc-34cd-444f-9aa9-79fe5714e786)

### index

Major global indices are curated under the `index` command.  Adding `--show` to the command will display a table with the list.

```console
index --show
```

![Curated Index List](https://user-images.githubusercontent.com/85772166/236107143-a3e260e0-9530-4448-a552-12b46ae0aa72.png)

The cumulative returns of an index is displayed instead of the levels by attaching `-r` to the command. Multiple indices can be queried simultaneously.

```console
index sp500,sp400,sp600 --start 2023-01-01 -r
```

![Indices](https://user-images.githubusercontent.com/85772166/236107229-410673db-e1ce-4e93-9e96-7821328e04dd.png)

### fred

To lookup FRED series by keywords attach, `-q`, to the `fred` command.

```console
fred -q PCE
```

![Fred Series](https://user-images.githubusercontent.com/85772166/236107269-8f126f17-3da7-4bb3-8acb-35f3ad783f84.png)

### plot

After requesting a time series, it gets populated under `Stored datasets`.  Plot them together, on a shared or separate y-axis, by using the `plot` command.

![Multi-Axis Plots](https://user-images.githubusercontent.com/85772166/236107312-95ed4b92-e418-444c-b436-f45a1fc0a75d.png)

```console
plot --y1 PCE --y2 sp500
```

![Plot Multiple Time Series](https://user-images.githubusercontent.com/85772166/236107339-46037f4b-bc4f-458c-9f17-55a4cc6a61bc.png)
