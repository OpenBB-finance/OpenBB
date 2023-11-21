---
title: upcoming
description: This documentation page is related to the upcoming() function in OpenBB's
  stocks discovery module which returns a DataFrame containing upcoming earnings.
  The page includes source code, function parameters, and return types.
keywords:
- OpenBB.stocks.disc.upcoming
- Upcoming earnings
- Source Code
- Number of pages
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.upcoming - Reference | OpenBB SDK Docs" />

Returns a DataFrame with upcoming earnings

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/seeking_alpha_model.py#L45)]

```python wordwrap
openbb.stocks.disc.upcoming(limit: int = 5, start_date: datetime.date = 2023-11-21)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of days to look ahead | 5 | True |
| start_date | date | Date to start from. Defaults to today | 2023-11-21 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | Upcoming earnings DataFrame |
---

