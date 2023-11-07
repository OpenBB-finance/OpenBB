---
title: growth
description: This page provides information on how to get financial statement growth
  using OpenBB's financial analysis function. Included are parameters required, return
  types and the link to the source code.
keywords:
- Financial Statement Growth
- OpenBB Finance
- OpenBBTerminal source code
- Get financial statement growth
- Stock ticker symbol
- Fundamental Analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.growth - Reference | OpenBB SDK Docs" />

Get financial statement growth

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L505)]

```python
openbb.stocks.fa.growth(symbol: str, limit: int = 5, quarterly: bool = False)
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
| pd.DataFrame | Dataframe of financial statement growth |
---
