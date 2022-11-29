---
title: price
description: OpenBB SDK Function
---

# price

Returns price and confidence interval from pyth live feed. [Source: Pyth]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/pyth_model.py#L76)]

```python
openbb.crypto.price(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol of the asset to get price and confidence interval from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[float, float, float] | Price of the asset,<br/>Confidence level,<br/>Previous price of the asset |
---

