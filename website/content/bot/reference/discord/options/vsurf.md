---
title: vsurf
description: This page provides instructions on how to use the 'vsurf' command to
  retrieve an options volatility surface for a specific stock ticker, detailing implied
  volatilities, open interest, and last price.
keywords:
- vsurf command
- options volatility surface
- stock ticker
- implied volatilities
- open interest
- last price
- command usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: vsurf - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve an options volatility surface for the ticker symbol. Specifically, it will provide a surface based on implied volatilities calculated from options prices, indicating the relationship between the stock price and the implied volatility of options on the stock.

### Usage

```python wordwrap
/op vsurf ticker z
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| z | The variable for the Z axis | False | Volatility (IV), Open Interest (OI), Last Price (LP) |


---

## Examples

```
/op vsurf ticker:AMD z:Volatility
```

```
/op vsurf ticker:AMD z:Open Interest
```

---
