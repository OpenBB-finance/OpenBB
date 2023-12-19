---
title: c5m
description: The c5m command page details how to retrieve an intraday 5 minute chart
  for a particular stock ticker. The chart serves as a valuable tool for technical
  analysis and tracking short-term price movements.
keywords:
- c5m
- intraday chart
- 5 minute chart
- candlestick chart
- stock performance
- technical analysis
- short-term price movements
- extended hours
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: c5m - Telegram Reference | OpenBB Bot Docs" />

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
/c5m AMD
```

```
/c5m AMD true
```

---
