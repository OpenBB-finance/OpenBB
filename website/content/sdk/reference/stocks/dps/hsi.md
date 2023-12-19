---
title: hsi
description: 'The hsi function returns a high short interest DataFrame. This OpenBB
  finance function doesn''t require any parameters and provides key financial data
  including: Ticker, Company, Exchange, ShortInt, Float, Outstd, and Industry. Ideal
  for those interested in dark pool shorts and stock market data.'
keywords:
- hsi
- high short interest DataFrame
- OpenBB finance
- short interest
- dataframe
- dark pool shorts
- stock market
- financial data
- exchange
- company
- outstd
- industry
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dps.hsi - Reference | OpenBB SDK Docs" />

Returns a high short interest DataFrame

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/shortinterest_model.py#L18)]

```python
openbb.stocks.dps.hsi()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | High short interest Dataframe with the following columns:<br/>Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry |
---
