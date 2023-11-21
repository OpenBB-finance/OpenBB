---
title: atl
description: Get all time low for a coin in a given currency
keywords:
- crypto
- dd
- atl
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.atl - Reference | OpenBB SDK Docs" />

Get all time low for a coin in a given currency

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/sdk_helper.py#L96)]

```python wordwrap
openbb.crypto.dd.atl(symbol: str, currency: str = "USD")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get all time low for | None | False |
| currency | str | Currency to get all time low in | USD | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of all time low |
---

## Examples

```python
from openbb_terminal.sdk import openbb
btc_atl = openbb.crypto.dd.atl("btc")
```

---

