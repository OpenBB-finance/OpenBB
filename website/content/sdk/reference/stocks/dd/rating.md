---
title: rating
description: The page provides detailed information about the OpenBBTerminal's functionality
  to fetch ratings for a given stock ticker using the Financial Modeling Prep source.
  The code is written in Python and returns data in pd.DataFrame format.
keywords:
- OpenBBTerminal
- Stock Ticker
- Ratings
- Financial Modeling Prep
- Python
- Source Code
- pd.DataFrame
- Stock Market
- Financial Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="rating - Dd - Stocks - Reference | OpenBB SDK Docs" />

# rating

Get ratings for a given ticker. [Source: Financial Modeling Prep]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/fmp_model.py#L17)]

```python
openbb.stocks.dd.rating(symbol: str)
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
