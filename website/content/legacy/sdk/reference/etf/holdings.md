---
title: holdings
description: The page provides functions to fetch ETF holdings with Python using a
  specific symbol. It includes source code, parameter information, and return values
  represented in a dataframe.
keywords:
- ETF holdings
- Source Code
- Parameters
- Returns
- Symbol
- Dataframe of holdings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.holdings - Reference | OpenBB SDK Docs" />

Get ETF holdings

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L82)]

```python
openbb.etf.holdings(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get holdings for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of holdings |
---
