---
title: lasttrades
description: This page provides documentation for the 'lasttrades' function which
  fetches last government trading data. It includes parameters such as 'gov_type',
  'limit', and 'representative', and returns a pandas DataFrame.
keywords:
- lasttrades
- government trading
- quiverquant.com source
- openbb.stocks.gov.lasttrades
- congress
- senate
- house
- representative
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.lasttrades - Reference | OpenBB SDK Docs" />

Get last government trading [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L164)]

```python
openbb.stocks.gov.lasttrades(gov_type: str = "congress", limit: int = -1, representative: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between: congress, senate and house | congress | True |
| limit | int | Number of days to look back | -1 | True |
| representative | str | Specific representative to look at |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Last government trading |
---
