---
title: fraud
description: This is an informational page about Fetching fraud ratios based on fundamentals
  using OpenBB's stocks.fa.fraud function in Python. This function accepts a stock
  ticker symbol and returns fraud ratios in a pandas DataFrame format.
keywords:
- fraud ratios
- fundamental analysis
- stock ticker symbol
- pandas DataFrame
- OpenBB.finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.fraud - Reference | OpenBB SDK Docs" />

Get fraud ratios based on fundamentals

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L594)]

```python
openbb.stocks.fa.fraud(symbol: str, detail: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| detail | bool | Whether to provide extra m-score details | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The fraud ratios |
---
