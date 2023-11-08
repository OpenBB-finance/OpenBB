---
title: c3m
description: The documentation page for /c3m command in stock market analysis tool.
  This command retrieves a 3-minute intraday chart, which provides visual representation
  of a stock's performance during the day, particularly useful for short-term investors.
keywords:
- 3 minute intraday chart
- stock performance
- candlestick chart
- short-term investments
- /c3m command
- trading hours
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: c3m - Discord Reference | OpenBB Bot Docs" />

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
| extended_hours | Show Full 4am-8pm ET Trading Hours. Default: False | True | None |


---

## Examples

```
/c3m ticker:AMD
```

---
