---
title: gtech
description: Gtech is a function used to get technology stocks with revenue and earnings
  growth exceeding 25%. The page provides source code and details about parameters
  and returns.
keywords:
- gtech
- technology stocks
- revenue growth
- earnings growth
- Yahoo Finance
- stocks discovery
- python code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.gtech - Reference | OpenBB SDK Docs" />

Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/yahoofinance_model.py#L76)]

```python
openbb.stocks.disc.gtech()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Growth technology stocks |
---
