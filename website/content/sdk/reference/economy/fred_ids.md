---
title: fred_ids
description: OpenBB SDK Function
---

# fred_ids

Get Series IDs. [Source: FRED]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L126)]

```python
openbb.economy.fred_ids(search_query: str, limit: int = -1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| search_query | str | Text query to search on fred series notes database | None | False |
| limit | int | Maximum number of series IDs to output | -1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with series IDs and titles |
---

