---
title: cc
description: This documentation page provides an in-depth explanation on the /cc command
  that retrieves an intraday 5 minute chart for a given ticker. It's a useful tool
  for technical analysis and tracking short-term price movements.
keywords:
- intraday 5 minute chart
- candlestick chart
- technical analysis
- short-term price movements
- /cc command
- stock performance visualization
- extended trading hours
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: cc - Discord Reference | OpenBB Bot Docs" />

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
/cc ticker:AMD
```

---
