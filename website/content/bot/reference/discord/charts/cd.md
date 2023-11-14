---
title: cd
description: This page provides comprehensive information about the 'cd' command,
  used to retrieve a daily candlestick chart for a specific stock ticker or coin.
  It also includes usage instructions, parameter details and examples.
keywords:
- cd command
- daily candlestick chart
- stock ticker
- coin
- opening and closing prices
- high and low prices
- performance analysis
- command usage
- parameter details
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: cd - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a daily candlestick chart for a particular ticker or coin. The candlestick chart provides information about the opening and closing prices of the day, as well as the high and low prices of the day. This data can then be used to analyze the performance of the ticker/coin over time. For example, if the user provides the command "/cd ticker:AMD", the chart will be generated for the ticker AMD.

### Usage

```python wordwrap
/cd ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/cd ticker:AMD
```

---
