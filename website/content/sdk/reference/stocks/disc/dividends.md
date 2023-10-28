---
title: dividends
description: This page provides documentation on how to access the dividend calendar
  for a given date using our OpenBB Terminal. The date represents the Ex-Dividend
  Date. Users are guided on how to use it and understand the returned DataFrame.
keywords:
- dividends
- OpenBB Terminal
- Ex-Dividend Date
- Python
- Dataframe
- dividend calendar
- documentation
- stock market
- finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="dividends - Disc - Stocks - Reference | OpenBB SDK Docs" />

Gets dividend calendar for given date.  Date represents Ex-Dividend Date

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/nasdaq_model.py#L52)]

```python
openbb.stocks.disc.dividends(date: str = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get for in format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of dividend calendar |
---
