---
title: trading_pair_info
description: OpenBB SDK Function
---

# trading_pair_info

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

