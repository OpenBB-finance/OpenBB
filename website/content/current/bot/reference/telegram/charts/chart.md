---
title: chart
description: This documentation page provides detailed information about the Chart
  command in our tool. The command retrieves a candlestick chart based on the provided
  ticker and time interval, displaying vital trading data such as opening/closing
  prices and volume for the specified number of previous days.
keywords:
- Chart Command
- Candlestick Chart
- Stock Ticker
- Time Interval
- Opening and Closing Prices
- Trading Volume
- Past Days Display
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: chart - Telegram Reference | OpenBB Bot Docs" />

This command will retrieve a candlestick chart for the ticker/interval provided, with data for the past number of days specified. The interval provided must be a valid time interval (e.g. 5 minute, 15 minute, etc.). The chart will be displayed to the user and will contain information such as the opening and closing prices, the high and low, the volume, and any other relevant information.

### Usage

```python wordwrap
/chart ticker interval [past_days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| interval | `1m`, `5m`, `10m`, `15m`, `30m`, `60m`, `1d`, `1wk`, `1mo` Default: `15m` | False | 1d, 1wk, 1mo, 1m, 5m, 10m, 15m, 30m, 1hr |
| past_days | Past Days to Display. Default: 0 | True | None |


---

## Examples

```
/chart AMD 1d 10
```

```
/chart AMD 1d
```

---
