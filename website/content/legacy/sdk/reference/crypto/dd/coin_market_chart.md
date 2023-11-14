---
title: coin_market_chart
description: The page provides details about the 'coin_market_chart' function in the
  OpenBB crypto module. This function fetches and displays coin prices based on specified
  parameters.
keywords:
- coin market chart
- cryptocurrency prices
- openbb crypto
- Python data fetching
- coin prices API
- data frame
- pycoingecko model
- currency
- coin pricing data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.coin_market_chart - Reference | OpenBB SDK Docs" />

Get prices for given coin. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/pycoingecko_model.py#L222)]

```python
openbb.crypto.dd.coin_market_chart(symbol: str = "", vs_currency: str = "usd", days: int = 30, kwargs: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| vs_currency | str | currency vs which display data | usd | True |
| days | int | number of days to display the data | 30 | True |
| kwargs | None | unspecified keyword arguments | None | None |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Prices for given coin<br/>Columns: time, price, currency |
---
