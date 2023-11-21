---
title: ipo
description: Navigate through the IPO calendar using OpenBB's Python toolkit. The
  page provides source code and parameters for IPO through start and end dates, returning
  all events in a convenient pd.DataFrame format.
keywords:
- IPO
- IPO calendar
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.ipo - Reference | OpenBB SDK Docs" />

Get IPO calendar

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/finnhub_model.py#L16)]

```python
openbb.stocks.disc.ipo(start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Optional[str] | Initial date, format YYYY-MM-DD | None | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with IPO calendar events |
---
