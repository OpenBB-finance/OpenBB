---
title: tokenomics
description: OpenBB SDK Function
---

# tokenomics

Get tokenomics for given coin. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/pycoingecko_model.py#L253)]

```python
openbb.crypto.dd.tokenomics(symbol: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | coin symbol to check tokenomics |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Metric, Value with tokenomics |
---

