---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: vsurf
description: OpenBB Telegram Command
---

# vsurf

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
