---
title: asc
description: Documentation for OpenBB's function to get the most aggressive small
  cap stocks from Yahoo Finance with high earnings growth rates. Includes python code
  and parameters description.
keywords:
- Yahoo Finance
- small cap stocks
- earnings growth rates
- stocks
- aggressive small cap stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.asc - Reference | OpenBB SDK Docs" />

Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/yahoofinance_model.py#L138)]

```python
openbb.stocks.disc.asc()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most aggressive small cap stocks |
---
