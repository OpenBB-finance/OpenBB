---
title: trading_pair_info
description: The trading_pair_info page provides a detailed guide on how to get essential
  trading pair information from Coinbase using the OpenBB API. The tool supports all
  significant trading pairs such as ETH-USDT and UNI-ETH. Retrieve the needed data
  in a convenient DataFrame format. Check out the source code to learn more.
keywords:
- trading pair info
- coinbase
- crypto trading
- cryptocurrency trading
- API
- ETH-USDT
- UNI-ETH
- dataframe
- due diligence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.trading_pair_info - Reference | OpenBB SDK Docs" />

Get information about chosen trading pair. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L48)]

```python
openbb.crypto.dd.trading_pair_info(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Basic information about given trading pair |
---
