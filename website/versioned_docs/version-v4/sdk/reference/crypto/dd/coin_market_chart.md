---
title: coin_market_chart
description: OpenBB SDK Function
---

# coin_market_chart

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

