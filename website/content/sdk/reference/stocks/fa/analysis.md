---
title: analysis
description: Documentation on OpenBB Terminal's feature for SEC filings analysis using
  machine learning. The page contains information on how to perform the analysis,
  parameters required, and default values.
keywords:
- SEC filings analysis
- Machine learning
- Stocks
- Fundamental analysis
- Ticker symbol
- Eclect.us
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.analysis - Reference | OpenBB SDK Docs" />

Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/eclect_us_model.py#L18)]

```python
openbb.stocks.fa.analysis(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to see analysis of filings | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | Analysis of filings text |
---
