---
title: profile
description: This page provides information on retrieving the ticker profile from
  FMP using the 'openbb.stocks.fa.profile' function in OpenBBTerminal. Python's pd.DataFrame
  is utilized to organize the stock ticker data.
keywords:
- FMP
- ticker profile
- stock ticker symbol
- openbb.stocks.fa.profile
- fundamental analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.profile - Reference | OpenBB SDK Docs" />

Get ticker profile from FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L56)]

```python
openbb.stocks.fa.profile(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of ticker profile |
---
