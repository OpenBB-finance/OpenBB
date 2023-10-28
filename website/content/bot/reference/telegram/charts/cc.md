---
title: cc
description: This page provides information on how to utilize the /cc command, which
  generates an intraday 5 minute chart for a given stock ticker. It allows users to
  visually track the stock's performance throughout the day and aids in technical
  analysis.
keywords:
- stock ticker
- /cc command
- intraday chart
- candlestick chart
- technical analysis
- short-term price movements
- stock's performance
- extended trading hours
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: cc - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve an intraday 5 minute chart for a given ticker, /c5m also has the same effect. This chart will display the candlestick chart for the day. It will provide a visual representation of the stock's performance over the current day. This command is useful for performing technical analysis and tracking short-term price movements.

### Usage

```python wordwrap
/cc ticker [extended_hours]
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
/cc amd
```

---
