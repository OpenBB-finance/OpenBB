---
title: dividends
description: OpenBB SDK Function
---

# dividends

Gets dividend calendar for given date.  Date represents Ex-Dividend Date

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/nasdaq_model.py#L52)]

```python
openbb.stocks.disc.dividends(date: str = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get for in format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of dividend calendar |
---

