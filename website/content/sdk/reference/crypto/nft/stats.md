---
title: stats
description: This page consists of detailed guidelines on how to utilise stats and
  stats_chart functions. It shows how one can leverage these functions to get NFT
  collection stats and print tables showcasing these stats, respectively sourced from
  opensea.io.
keywords:
- stats function
- stats_chart function
- NFT collection stats
- OpenSea data
- NFT data
- slug
- data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.nft.stats - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get stats of a nft collection [Source: opensea.io]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/opensea_model.py#L17)]

```python
openbb.crypto.nft.stats(slug: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | Opensea collection slug. If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | collection stats |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing collection stats. [Source: opensea.io]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/opensea_view.py#L15)]

```python
openbb.crypto.nft.stats_chart(slug: str, export: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | Opensea collection slug.<br/>If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
