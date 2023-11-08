---
title: dcf
description: This page covers how to use the 'dcf' function from FMP for stocks analysis
  with the OpenBB tool. It indicates the parameters required and returns a dataframe
  of dcf data.
keywords:
- dcf
- stocks
- FMP
- fundamental analysis
- fmp model
- parameters
- returns
- stock ticker symbol
- limit
- quarterly
- dataframe
- dcf data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.dcf - Reference | OpenBB SDK Docs" />

Get stocks dcf from FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L173)]

```python
openbb.stocks.fa.dcf(symbol: str, limit: int = 5, quarterly: bool = False)
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
| pd.DataFrame | Dataframe of dcf data |
---
