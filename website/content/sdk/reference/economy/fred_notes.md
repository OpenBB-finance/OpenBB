---
title: fred_notes
description: OpenBB SDK Function
---

# fred_notes

Get series notes. [Source: FRED]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L68)]

```python
openbb.economy.fred_notes(search_query: str, limit: int = -1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| search_query | str | Text query to search on fred series notes database | None | False |
| limit | int | Maximum number of series notes to display | -1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of matched series |
---

