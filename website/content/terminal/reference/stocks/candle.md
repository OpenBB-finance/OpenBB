---
title: candle
description: This page provides a detailed guide on the usage of the 'candle' command
  in Python, a tool for displaying historic stock data. It covers functionalities
  such as plot display, data sorting and trendline addition.
keywords:
- candle command
- historic stock data
- data visualization
- data sorting
- trendlines
- interactive plotly chart
- moving average
- log scale
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/candle - Reference | OpenBB Terminal Docs" />

Shows historic data for a stock

### Usage

```python
candle [-p] [--sort {adjclose,open,close,high,low,volume,returns,logret}] [-r] [--raw] [-t] [--ma MOV_AVG] [--log]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| plotly | Flag to show interactive plotly chart | True | True | None |
| sort | Choose a column to sort by. Only works when raw data is displayed. |  | True | adjclose, open, close, high, low, volume, returns, logret |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| raw | Shows raw data instead of chart. | False | True | None |
| trendlines | Flag to add high and low trends to candle | False | True | None |
| mov_avg | Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. | None | True | None |
| logy | Plot with y axis on log scale | False | True | None |

![candle](https://user-images.githubusercontent.com/46355364/154072214-f4b49833-157f-44a7-be2d-d558ffc6f945.png)

---
