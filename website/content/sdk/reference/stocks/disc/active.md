---
title: active
description: This page provides documentation for the 'active' function of the OpenBB
  Finance API. The function returns the most active stocks in descending order based
  on intraday trade volume.
keywords:
- OpenBB Finance API
- active function
- Stock trading
- Trading volume
- Most active stocks
- Finance
- API documentation
- Data Frame
- Yahoo Finance
- Intraday trading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.active - Reference | OpenBB SDK Docs" />

Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/yahoofinance_model.py#L97)]

```python
openbb.stocks.disc.active()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most active stocks |
---
