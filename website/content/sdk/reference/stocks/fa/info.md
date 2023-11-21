---
title: info
description: This page provides information on retrieving ticker symbol information
  using OpenBB.fa.info method, leveraging yfinance data.
keywords:
- fa.info method
- yfinance data
- stock ticker symbol
- Pandas DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.info - Reference | OpenBB SDK Docs" />

Gets ticker symbol info

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L31)]

```python
openbb.stocks.fa.info(symbol: str)
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
| pd.DataFrame | DataFrame of yfinance information |
---
