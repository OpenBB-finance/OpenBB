---
title: oichart
description: Learn how to retrieve a chart of Total Open Interest by Strike Price
  for any given ticker symbol using the 'oichart' command. This guide covers usage,
  parameters, and examples to help you make informed decisions about the underlying
  security.
keywords:
- Open Interest Chart
- Ticker Symbol
- Strike Price
- Stock
- Expiration Date
- oichart command
- Open Interest analysis
- Stock Market Analysis
- Python command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: oichart - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve a chart of Total Open Interest by Strike Price for the given ticker symbol. This chart provides a visual representation of the open interest on various strike prices for the given ticker symbol, where the size of each point on the graph reflects the amount of open interest. This can be used to analyze the open interest on various strike prices and make informed decisions about the underlying security.

### Usage

```python wordwrap
/oichart ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (YYYY-MM-DD) - Optional | True | None |


---

## Examples

```
/oichart AMD
```

```
/oichart AMD 2022-07-29
```
---
