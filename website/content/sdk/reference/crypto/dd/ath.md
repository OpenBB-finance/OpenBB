---
title: ath
description: Get all time high for a coin in a given currency
keywords:
- crypto
- dd
- ath
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.ath - Reference | OpenBB SDK Docs" />

Get all time high for a coin in a given currency

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/sdk_helper.py#L73)]

```python wordwrap
openbb.crypto.dd.ath(symbol: str, currency: str = "USD")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get all time high for | None | False |
| currency | str | Currency to get all time high in | USD | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of all time high |
---

## Examples

```python
from openbb_terminal.sdk import openbb
btc_ath = openbb.crypto.dd.ath("btc")
```

---

