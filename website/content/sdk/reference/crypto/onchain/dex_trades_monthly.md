---
title: dex_trades_monthly
description: Provides access to aggregated data of trades executed on Decentralized
  Exchanges. You can set the currency of trade amount, limit the number of days and
  even sort the data as required.
keywords:
- dex_trades_monthly
- Decentralized Exchanges
- Trades data
- openbb_crypto_onchain
- trade_amount_currency
- USD
- limit
- ascend
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.dex_trades_monthly - Reference | OpenBB SDK Docs" />

Get list of trades on Decentralized Exchanges monthly aggregated.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L333)]

```python
openbb.crypto.onchain.dex_trades_monthly(trade_amount_currency: str = "USD", limit: int = 90, ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | True |
| limit | int | Last n days to query data. Maximum 365 (bigger numbers can cause timeouts<br/>on server side) | 90 | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trades on Decentralized Exchanges monthly aggregated |
---
