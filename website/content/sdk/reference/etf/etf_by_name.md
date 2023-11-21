---
title: etf_by_name
description: A detailed documentation page that explains how to get ETF symbol and
  name based on a string to search. The page includes a link to the source code and
  illustrates how the function 'etf_by_name' used in the StockAnalysis can be implemented
  to fetch ETF names and their corresponding symbols. This function returns a data
  frame with symbols and names.
keywords:
- ETF
- Symbol
- Name Search
- StockAnalysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.etf_by_name - Reference | OpenBB SDK Docs" />

Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L132)]

```python
openbb.etf.etf_by_name(name_to_search: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name_to_search | str | ETF name to match | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with symbols and names |
---
