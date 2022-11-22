---
title: pipo
description: OpenBB SDK Function
---

# pipo

Past IPOs dates. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/finnhub_model.py#L74)]

```python
openbb.stocks.disc.pipo(num_days_behind: int = 5, start_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| num_days_behind | int | Number of days to look behind for IPOs dates | 5 | True |
| start_date | str | The starting date (format YYYY-MM-DD) to look for IPOs | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with past IPOs |
---

