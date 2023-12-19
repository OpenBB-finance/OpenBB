---
title: vsurf
description: This page provides a guide on how to use the 'vsurf' command to retrieve
  an options volatility surface for a ticker symbol, displaying the relationship between
  stock price and the implied volatility of options.
keywords:
- vsurf command
- options volatility surface
- ticker symbol
- implied volatilities
- stock price
- stock options
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: vsurf - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve an options volatility surface for the ticker symbol. Specifically, it will provide a surface based on implied volatilities calculated from options prices, indicating the relationship between the stock price and the implied volatility of options on the stock.

### Usage

```python wordwrap
/vsurf ticker z
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| z | iv: Volatility oi: Open Interest lp: Last Price | False | iv, oi, lp |


---

## Examples

```
/vsurf AMD iv
```
```
/vsurf AMD oi
```
---
