---
title: ratios
description: This page provides important details about the 'ratios' function in 'OpenBB
  Stocks' module which is used for fundamental analysis. Users can extract key ratios
  by providing a stock's ticker symbol and specifying other optional parameters. The
  function returns a DataFrame of key ratios.
keywords:
- OpenBB Stocks
- Fundamental Analysis
- Key Ratios
- Stock Ticker Symbol
- Quarterly Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.ratios - Reference | OpenBB SDK Docs" />

Get key ratios

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L463)]

```python
openbb.stocks.fa.ratios(symbol: str, limit: int = 5, quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | 5 | True |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key ratios |
---
