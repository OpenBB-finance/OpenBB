---
title: arkord
description: This page contains details about the arkord function, which returns ARK
  orders in a DataFrame. The function provides options to filter based on buys only,
  sells only, or by a specific fund. This page also lists the various columns in the
  returned DataFrame, which includes ticker, date, shares, weight, fund, and direction.
keywords:
- ARK
- Orders
- filter
- buys only
- sells only
- fund
- ARK orders data frame
- shares
- weight
- direction
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.arkord - Reference | OpenBB SDK Docs" />

Returns ARK orders in a Dataframe

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/ark_model.py#L23)]

```python
openbb.stocks.disc.arkord(buys_only: bool = False, sells_only: bool = False, fund: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| buys_only | bool | Flag to filter on buys only | False | True |
| sells_only | bool | Flag to sort on sells only | False | True |
| fund | str | Optional filter by fund |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | ARK orders data frame with the following columns -<br/>(ticker, date, shares, weight, fund, direction) |
---
