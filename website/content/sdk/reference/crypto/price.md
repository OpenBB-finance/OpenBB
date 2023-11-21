---
title: price
description: Get the price and confidence interval from the Pyth live feed for any
  given crypto asset. It also provides the previous price of the asset for comparison.
keywords:
- price
- confidence interval
- Pyth live feed
- crypto price
- asset price
- confidence level
- previous price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.price - Reference | OpenBB SDK Docs" />

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
