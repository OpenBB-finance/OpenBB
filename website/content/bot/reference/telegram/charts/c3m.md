---
title: c3m
description: The c3m command allows users to generate a 3-minute intraday chart for
  the provided ticker, offering a visual representation of stock performance for short-term
  investors. The page also covers usage details, parameters, and example commands.
keywords:
- c3m command
- candlestick chart
- intraday chart
- stock performance
- short-term investors
- stock ticker
- trading hours
- AMD
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: c3m - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve a 3-minute intraday chart for the given ticker. This chart will display the candlestick chart for the day. It will provide a visual representation of the stock's performance over the current day, making it helpful for short-term investors.

### Usage

```python wordwrap
/c3m ticker [extended_hours]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| extended_hours | Show Full 4am-8pm ET Trading Hours. True/False Default: False | True | None |


---

## Examples

```
/c3m AMD
```

```
/c3m AMD true
```

---
