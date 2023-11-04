---
title: fred_notes
description: Learn about OpenBB's FRED model and how it makes searching the series
  notes database easier. This page also talks about the search and limit parameters
  involved when querying the FRED database, and the DataFrame of matched series it
  returns.
keywords:
- FRED series notes
- OpenBB economy
- FRED model
- data searching
- text query
- series notes database
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.fred_notes - Reference | OpenBB SDK Docs" />

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
