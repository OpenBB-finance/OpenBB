---
title: shorted
description: The page provides details about the 'shorted' function of OpenBBTerminal
  which shows the most shorted stocks according to Yahoo Finance. Details include
  the source code and parameters, if any.
keywords:
- shorted
- stock screener
- Yahoo Finance
- OpenBB finance
- stocks
- dark pool shorts
- yahoofinance model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dps.shorted - Reference | OpenBB SDK Docs" />

Get most shorted stock screener [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/yahoofinance_model.py#L16)]

```python
openbb.stocks.dps.shorted()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most Shorted Stocks |
---
