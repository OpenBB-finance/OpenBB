---
title: ugs
description: This page details the UGS function, which identifies stocks with excellent
  earnings growth rates and relatively low PE and PEG ratios, thus helping to discover
  undervalued stocks. Source code is also provided.
keywords:
- ugs function
- stock discovery
- earnings growth rate
- PE ratio
- PEG ratio
- undervalued stocks
- yahoofinance model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.ugs - Reference | OpenBB SDK Docs" />

Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/yahoofinance_model.py#L54)]

```python
openbb.stocks.disc.ugs()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Undervalued stocks |
---
