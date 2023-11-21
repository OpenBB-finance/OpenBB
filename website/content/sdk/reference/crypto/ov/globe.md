---
title: globe
description: This docusaurus page represents the 'globe' function of OpenBBTerminal
  which retrieves a DataFrame with global cryptocurrency market data from a specified
  source; default is CoinGecko.
keywords:
- crypto market data
- globe function
- CoinGecko
- coinpaprika
- global crypto data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.globe - Reference | OpenBB SDK Docs" />

Get global crypto market data.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/sdk_helpers.py#L12)]

```python wordwrap
openbb.crypto.ov.globe(source: str = "CoinGecko")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| source | str | Source of data, by default "CoinGecko" | CoinGecko | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with global crypto market data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
global_market_data = openbb.crypto.ov.globe()
```

```
To get data from CoinPaprika, use the source parameter:
```
```python
global_market_data = openbb.crypto.ov.globe(source="coinpaprika")
```

---

