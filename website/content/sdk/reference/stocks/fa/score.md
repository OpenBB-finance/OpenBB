---
title: score
description: Documentation of 'score' function in fmp, part of the fundamental analysis
  of stocks, which retrieves the value score for a specified ticker symbol. Returns
  a np.number type value score.
keywords:
- score
- fmp
- stocks
- fundamental analysis
- value score
- ticker symbol
- np.number
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.score - Reference | OpenBB SDK Docs" />

Gets value score from fmp

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L25)]

```python
openbb.stocks.fa.score(symbol: str)
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
| np.number | Value score |
---
