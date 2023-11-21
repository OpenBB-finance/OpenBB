---
title: get_towns_sold_prices
description: Get towns sold house price data
keywords:
- alt
- realestate
- get_towns_sold_prices
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.realestate.get_towns_sold_prices - Reference | OpenBB SDK Docs" />

Get towns sold house price data.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/realestate/landRegistry_model.py#L98)]

```python wordwrap
openbb.alt.realestate.get_towns_sold_prices(town: str, start_date: str, end_date: str, limit: int = 25)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| town | str | town | None | False |
| start_date | str | startDate | None | False |
| end_date | str | endDate | None | False |
| limit | int | number of rows to return | 25 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All sales for that town within the date range specified |
---

