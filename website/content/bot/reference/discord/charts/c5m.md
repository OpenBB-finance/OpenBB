---
title: c5m
description: Learn how to use the c5m command to retrieve an intraday 5 minute chart
  for a given ticker. This tool aids in performing technical analysis and monitoring
  short-term stock price movements.
keywords:
- c5m command
- intraday 5 minute chart
- technical analysis
- stock performance
- candlestick chart
- short-term price movements
- stock ticker
- trading hours
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: c5m - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve an intraday 5 minute chart for a given ticker. This chart will display the candlestick chart for the day. It will provide a visual representation of the stock's performance over the current day. This command is useful for performing technical analysis and tracking short-term price movements.

### Usage

```python wordwrap
/c5m ticker [extended_hours]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| extended_hours | Show Full 4am-8pm ET Trading Hours. Default: False | True | None |


---

## Examples

```
/c5m ticker:AMD
```

---
