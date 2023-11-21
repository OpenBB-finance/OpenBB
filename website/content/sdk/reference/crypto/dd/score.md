---
title: score
description: Get scores for a coin from CoinGecko
keywords:
- crypto
- dd
- score
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.score - Reference | OpenBB SDK Docs" />

Get scores for a coin from CoinGecko

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/sdk_helper.py#L31)]

```python wordwrap
openbb.crypto.dd.score(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get scores for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of scores |
---

## Examples

```python
from openbb_terminal.sdk import openbb
btc_scores = openbb.crypto.dd.score("btc")
```

---

