---
title: candle
description: OpenBB Terminal Function
---

# candle

Shows historic data for an ETF

### Usage

```python
candle [-p] [--sort {adjclose,open,close,high,low,volume,returns,logret}] [-r] [--raw] [-n NUM] [-t] [--ma MOV_AVG]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| plotly | Flag to show interactive plotly chart. | True | True | None |
| sort | Choose a column to sort by |  | True | adjclose, open, close, high, low, volume, returns, logret |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| raw | Shows raw data instead of chart | False | True | None |
| num | Number to show if raw selected | 20 | True | None |
| trendlines | Flag to add high and low trends to candle. | False | True | None |
| mov_avg | Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. |  | True | None |

![candle](https://user-images.githubusercontent.com/46355364/154031063-090a4419-c3b1-4707-8f8e-b41c872a783a.png)

---
