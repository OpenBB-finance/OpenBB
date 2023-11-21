---
title: hotpenny
description: 'The page provides documentation on how to use the hotpenny function
  provided by OpenBB, which returns a DataFrame of today''s hot penny stocks with
  different columns such as Ticker, Price, Change, $ Volume, Volume, # Trades.'
keywords:
- hot penny stocks
- stocks DataFrame
- stock trading
- financial data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.hotpenny - Reference | OpenBB SDK Docs" />

Returns today hot penny stocks

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/shortinterest_model.py#L38)]

```python
openbb.stocks.disc.hotpenny()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | Today hot penny stocks DataFrame with the following columns:<br/>Ticker, Price, Change, $ Volume, Volume, # Trades |
---
