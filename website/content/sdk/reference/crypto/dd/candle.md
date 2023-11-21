---
title: candle
description: This page provides documentation on how to get or chart candle for a
  chosen trading pair and time interval on Coinbase using the OpenBB crypto library.
  It includes the Python code for these functions and the parameters to use.
keywords:
- OpenBB crypto library
- candle trading pair
- time interval
- Coinbase
- Python function
- Cryptocurrency trading
- Crypto trading analysis
- Cryptocurrency pairs
- Trade charting
- Data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.candle - Reference | OpenBB SDK Docs" />

Get candles for chosen trading pair and time interval. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L143)]

```python wordwrap
openbb.crypto.dd.candle(symbol: str, interval: str = "24hour")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| interval | str | Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour, 1day | 24hour | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Candles for chosen trading pair. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.dd.candle(symbol="eth-usdt", interval="24hour")
```

---

