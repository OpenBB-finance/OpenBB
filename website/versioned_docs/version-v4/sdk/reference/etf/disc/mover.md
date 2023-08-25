---
title: mover
description: OpenBB SDK Function
---

# mover

Scrape data for top etf movers.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/discovery/wsj_model.py#L15)]

```python
openbb.etf.disc.mover(sort_type: str = "gainers", export: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort_type | str | Data to get. Can be "gainers", "decliners" or "active" | gainers | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Datafame containing the name, price, change and the volume of the etf |
---

