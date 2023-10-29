---
title: supplier
description: Detailed documentation on the supplier function of OpenBBTerminal. It
  describes how to use the function to get suppliers using a certain ticker from CSIMarket,
  the source code path, and the parameters involved.
keywords:
- supplier
- CSIMarket
- Source Code
- stocks
- due diligence
- csimarket model.py
- stocks.dd.supplier function
- symbol parameter
- limit parameter
- dataframe
- suppliers data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.supplier - Reference | OpenBB SDK Docs" />

Get suppliers from ticker provided. [Source: CSIMarket]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/csimarket_model.py#L42)]

```python
openbb.stocks.dd.supplier(symbol: str, limit: int = 50)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select suppliers from | None | False |
| limit | int | The maximum number of rows to show | 50 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |
---
