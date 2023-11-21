---
title: shrs
description: This page provides information about a utility that fetches shareholder
  data from Yahoo for a given stock. It includes a source code link and explains parameters
  of the utility module. Uses Python language for coding.
keywords:
- Shareholders
- Yahoo
- Stocks
- Source Code
- Parameters
- Python Coding
- Stock Ticker Symbol
- Institutional Holder
- Data frame
- Major Holders
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.shrs - Reference | OpenBB SDK Docs" />

Get shareholders from yahoo

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L75)]

```python
openbb.stocks.fa.shrs(symbol: str, holder: str = "institutional")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| holder | str | Which holder to get table for | institutional | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Major holders |
---
