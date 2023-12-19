---
title: quote
description: The documentation page provides a brief explanation on how to use the
  OpenBBTerminal to fetch stock ticker quotes from FMP. It also includes the source
  code and instructions on its parameters and return type.
keywords:
- FMP
- stocks
- fundamental analysis
- ticker quote
- symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.quote - Reference | OpenBB SDK Docs" />

Gets ticker quote from FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L84)]

```python
openbb.stocks.fa.quote(symbol: str)
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
| pd.DataFrame | Dataframe of ticker quote |
---
