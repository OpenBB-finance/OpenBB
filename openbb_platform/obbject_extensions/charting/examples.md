---
title: Examples
sidebar_position: 1
description: This page provides examples of creating charts with the `openbb-charting` extension.
keywords:
- tutorial
- OpenBB Platform
- Python client
- Fast API
- getting started
- extensions
- charting
- view
- Plotly
- toolkits
- how-to
- generic
- figure
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Examples - OpenBB Charting - Extensions | OpenBB Platform Docs" />

## Overview

This page will walk through creating different charts using the `openbb-charting` extension.
The perspective for this content is from the Python Interface,
and the examples will assume that the OpenBB Platform is installed with all optional packages.

```python
from datetime import datetime, timedelta
from openbb import obb
```

## Cumulative Returns

The historical (equity) prices can be requested for multiple symbols.
The extension will attempt to handle variations accordingly.
By default, more than three symbols will draw the chart as cumulative returns from the beginning of the series.

### Default View

The tickers below are a collection of State Street Global Advisors SPDR funds, representing S&P 500 components.
The data is looking back five years.

```python
SPDRS = [
    "SPY",
    "XLE",
    "XLB",
    "XLI",
    "XHB",
    "XLP",
    "XLY",
    "XRT",
    "XLF",
    "XLV",
    "XLK",
    "XLC",
    "XLU",
    "XLRE",
]
start_date = (datetime.now() - timedelta(weeks=52*5)).date()
spdrs = obb.equity.price.historical(SPDRS, start_date=start_date, provider="yfinance", chart=True)

spdrs.show()
```

![SPDRs Cumulative Returns - 5 years](https://github.com/OpenBB-finance/OpenBB/assets/85772166/8884f4ed-b09c-4161-9dc6-87ad66d9fc8b)

### Redraw as YTD

The `charting` attribute of the command output has methods for creating the chart again.
The `data` parameter allows modifications to the data before creating the figure.
In this example, the length of the data is trimmed to the beginning of the year.

```python
new_data = spdrs.to_df().loc[datetime(2024,12,29).date():]
spdrs.charting.to_chart(data=new_data, title="YTD")
```

:::note
This replaces the chart that was already created.
:::

![SPDRs Cumulative Returns - YTD](https://github.com/OpenBB-finance/OpenBB/assets/85772166/22ed2588-1098-4712-aec1-54dd22c324ef)

## Price Performance Bar Chart

The `obb.equity.price.performance` endpoint will create a bar chart over intervals.

```python
price_performance = obb.equity.price.performance(SPDRS, chart=True)
price_performance.show()
```

![Price Performance](https://github.com/OpenBB-finance/OpenBB/assets/85772166/0de3260d-7fce-490b-90e1-bdfa38d6ab23)

### Create Bar Chart

This example uses the `create_bar_chart()` method, which does not replace the existing chart, in `price_performance.chart`.
It isolates the one-month performance and orients the layout as horizontal.

```python
new_data = price_performance.to_df().set_index("symbol").multiply(100).reset_index()
price_performance.charting.create_bar_chart(
    data=new_data,
    x="symbol",
    y="one_month",
    orientation="h",
    title="One Month Price Performance",
    xtitle="Percent (%)"
)
```

![Horizonontal Price Performance](https://github.com/OpenBB-finance/OpenBB/assets/85772166/8da01f73-d7a8-4168-846a-9fa9ed6a0e39)

## Create Your Own

This example analyzes the share volume turnover of the S&P 500 Energy Sector constituents, year-to-date.

```python
symbols = [
    'XOM',
    'CVX',
    'COP',
    'WMB',
    'EOG',
    'KMI',
    'OKE',
    'MPC',
    'PSX',
    'SLB',
    'VLO',
    'BKR',
    'HES',
    'TRGP',
    'EQT',
    'OXY',
    'TPL',
    'FANG',
    'EXE',
    'DVN',
    'HAL',
    'CTRA',
    'APA',
]
data = obb.equity.price.historical(symbols, start_date="2025-01-01", provider="yfinance")
create_bar_chart = data.charting.create_bar_chart
volume = data.to_df().groupby("symbol").sum()["volume"]
shares = obb.equity.profile(
    symbols, provider="yfinance"
).to_df().set_index("symbol")["shares_float"]
df = volume.to_frame().join(shares)
df["Turnover"] = (df.volume/df.shares_float).round(4)
df = df.sort_values(by="Turnover", ascending=False).reset_index()
create_bar_chart(
    data=df,
    x="symbol",
    y="Turnover",
    title="S&P Energy Sector YTD Turnover Rate",
)
```

![S&P 500 Energy Sector Turnover Rate](https://github.com/OpenBB-finance/OpenBB/assets/85772166/d29a1c17-6d3b-4925-8b7e-f661da404967)
