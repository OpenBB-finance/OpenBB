---
title: fp
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fp

<Tabs>
<TabItem value="model" label="Model" default>

Get nft collections [Source: https://nftpricefloor.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_model.py#L46)]

```python
openbb.crypto.nft.fp(slug: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | nft collection slug | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | nft collections |
---



</TabItem>
<TabItem value="view" label="Chart">

Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_view.py#L88)]

```python
openbb.crypto.nft.fp_chart(slug: str, limit: int = 10, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | NFT collection slug | None | False |
| raw | bool | Flag to display raw data | False | True |
| limit | int | Number of raw data to show | 10 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>