---
title: pipo
description: This page provides information about the 'pipo' open source code which
  is used to find Past IPO dates. It includes details about the parameters used and
  the output provided by the code.
keywords:
- pipo
- past IPO dates
- open source code
- Finnhub
- dataframe
- num_days_behind
- start_date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.pipo - Reference | OpenBB SDK Docs" />

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
