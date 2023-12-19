---
title: fred_ids
description: This page helps to understand the 'openbb.economy.fred_ids' function,
  which is a text query method for getting series IDs on FRED via OpenBB-finance.
  Includes parameters, return information and link to the source code.
keywords:
- FRED
- OpenBB-finance
- Series ID
- Information retrieval
- FRED series notes database
- openbb.economy.fred_ids
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.fred_ids - Reference | OpenBB SDK Docs" />

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
