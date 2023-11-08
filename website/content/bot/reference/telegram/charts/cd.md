---
title: cd
description: This documentation page provides an understanding of how to use the 'cd'
  command to retrieve daily candlestick chart for a particular stock ticker or coin.
  Instructions for usage and examples are provided.
keywords:
- cd command
- candlestick chart
- stock ticker
- coin
- opening price
- closing price
- highs and lows
- performance analysis
- AMD ticker
- command usage
- docusaurus documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: cd - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a daily candlestick chart for a particular ticker or coin. The candlestick chart provides information about the opening and closing prices of the day, as well as the high and low prices of the day. This data can then be used to analyze the performance of the ticker/coin over time. For example, if the user provides the command "/cd AMD", the chart will be generated for the ticker AMD.

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
/cd AMD
```

---
