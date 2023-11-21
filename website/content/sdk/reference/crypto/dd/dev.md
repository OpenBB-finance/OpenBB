---
title: dev
description: Get developer stats for a coin
keywords:
- crypto
- dd
- dev
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.dev - Reference | OpenBB SDK Docs" />

Get developer stats for a coin

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/sdk_helper.py#L9)]

```python wordwrap
openbb.crypto.dd.dev(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get stats for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of stats |
---

## Examples

```python
from openbb_terminal.sdk import openbb
btc_dev_stats = openbb.crypto.dd.dev("btc")
```

---

