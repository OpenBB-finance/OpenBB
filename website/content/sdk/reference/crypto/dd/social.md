---
title: social
description: Get social media stats for a coin
keywords:
- crypto
- dd
- social
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.social - Reference | OpenBB SDK Docs" />

Get social media stats for a coin

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/sdk_helper.py#L52)]

```python wordwrap
openbb.crypto.dd.social(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get social stats for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of social stats |
---

## Examples

```python
from openbb_terminal.sdk import openbb
btc_socials = openbb.crypto.dd.social("btc")
```

---

