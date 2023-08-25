---
title: collections
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# collections

<Tabs>
<TabItem value="model" label="Model" default>

Get nft collections [Source: https://nftpricefloor.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_model.py#L24)]

```python
openbb.crypto.nft.collections()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | nft collections |
---



</TabItem>
<TabItem value="view" label="Chart">

Display NFT collections. [Source: https://nftpricefloor.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_view.py#L27)]

```python
openbb.crypto.nft.collections_chart(show_fp: bool = False, show_sales: bool = False, limit: int = 5, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| show_fp | bool | Show NFT Price Floor for top collections | False | True |
| limit | int | Number of NFT collections to display | 5 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>