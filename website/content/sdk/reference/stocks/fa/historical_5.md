---
title: historical_5
description: Find how to get a 5 year monthly historical performance for a given ticker
  with dividends filtered using OpenBB's Python library. By analyzing ticker symbols
  with this method, get a detailed data analysis.
keywords:
- Historical performance
- 5 year monthly history
- Dividends
- Ticker symbol
- Data analysis
- Source code
- Fundamental analysis
- Pandas DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.historical_5 - Reference | OpenBB SDK Docs" />

Get 5 year monthly historical performance for a ticker with dividends filtered

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/dcf_model.py#L278)]

```python
openbb.stocks.fa.historical_5(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to be analyzed | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical data |
---
