---
title: rating
description: Get ratings for a given ticker
keywords:
- stocks
- fa
- rating
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.rating - Reference | OpenBB SDK Docs" />

Get ratings for a given ticker. [Source: Financial Modeling Prep]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L683)]

```python wordwrap
openbb.stocks.fa.rating(symbol: str)
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
| pd.DataFrame | Rating data |
---

