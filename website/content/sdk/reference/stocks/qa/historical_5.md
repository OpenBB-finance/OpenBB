---
title: historical_5
description: Historical_5 function from OpenBB provides 5 year monthly historical
  performance for a given stock ticker symbol with dividends filtered. This page gives
  a comprehensive view of the function's parameters and returns.
keywords:
- OpenBB
- stocks
- quantitative analysis
- historical_5
- performance
- ticker
- dividends
- source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="historical_5 - Qa - Stocks - Reference | OpenBB SDK Docs" />

# historical_5

Get 5 year monthly historical performance for a ticker with dividends filtered

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/quantitative_analysis/factors_model.py#L58)]

```python
openbb.stocks.qa.historical_5(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | A ticker symbol in string form | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe with historical information |
---
