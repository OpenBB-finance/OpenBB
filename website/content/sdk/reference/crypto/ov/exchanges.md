---
title: exchanges
description: This page provides information about how to show top crypto exchanges
  through OpenBB's API with detailed parameters, return types and examples.
keywords:
- crypto exchanges
- OpenBB API
- CoinGecko
- cryptocurrency
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.exchanges - Reference | OpenBB SDK Docs" />

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
