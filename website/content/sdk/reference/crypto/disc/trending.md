---
title: trending
description: This page provides detailed information on trending coins. Users can
  learn how to return and view a table of trending coins from CoinGecko using OpenBB's
  Python functions.
keywords:
- CoinGecko
- trending coins
- Python functions
- cryptocurrency
- crypto trends
- dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.trending - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns trending coins [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L317)]

```python
openbb.crypto.disc.trending()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trending Coins |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing trending coins [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_view.py#L192)]

```python
openbb.crypto.disc.trending_chart(export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
