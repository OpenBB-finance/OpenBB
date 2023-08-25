---
title: lasttrades
description: OpenBB SDK Function
---

# lasttrades

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

