---
title: exchanges
description: OpenBB SDK Function
---

# exchanges

Show top crypto exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/sdk_helpers.py#L42)]

```python
openbb.crypto.ov.exchanges(source: str = "CoinGecko")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| source | str | Source to get exchanges, by default "CoinGecko" | CoinGecko | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with top crypto exchanges |
---

## Examples

```python
from openbb_terminal.sdk import openbb
exchanges = openbb.crypto.ov.exchanges()
```

---

