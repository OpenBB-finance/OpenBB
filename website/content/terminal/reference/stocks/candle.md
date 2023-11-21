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

<HeadTitle title="stocks /candle - Reference | OpenBB Terminal Docs" />

Shows historic price and volume for the asset.

### Usage

```python wordwrap
candle [-t TICKER] [-p] [--sort {open,high,low,close,adjclose,volume,dividends,stock_splits}] [-r] [--raw] [--trend] [--ma MOV_AVG] [--ha] [--log]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze. | None | True | None |
| prepost | -p  --prepost | Pre/After market hours. Only works for intraday data. | False | True | None |
| sort | --sort | Choose a column to sort by. Only works when raw data is displayed. |  | True | open, high, low, close, adjclose, volume, dividends, stock_splits |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| raw | --raw | Shows raw data instead of a chart. | False | True | None |
| trendlines | --trend | Flag to add high and low trends to candle. | False | True | None |
| mov_avg | --ma | Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. | None | True | None |
| ha | --ha | Flag to show Heikin Ashi candles. | False | True | None |
| logy | --log | Plot with y axis on log scale | False | True | None |

![candle](https://user-images.githubusercontent.com/46355364/154072214-f4b49833-157f-44a7-be2d-d558ffc6f945.png)

---
