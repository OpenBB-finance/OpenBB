---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: vsurf
description: OpenBB Discord Command
---

# vsurf

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
