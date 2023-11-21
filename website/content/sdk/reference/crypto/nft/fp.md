---
title: fp
description: The page provides detailed documentation on the functionality of nftpricefloor
  model and view. The model helps to fetch NFT collections and the view function displays
  the collection's floor price overtime.
keywords:
- NFT collection
- nftpricefloor
- openbb.crypto.nft.fp
- openbb.crypto.nft.fp_chart
- Data Visualization
- Data Modelling
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.nft.fp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get nft collections [Source: https://nftpricefloor.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_model.py#L47)]

```python wordwrap
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_view.py#L96)]

```python wordwrap
openbb.crypto.nft.fp_chart(slug: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False, raw: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | NFT collection slug | None | False |
| raw | bool | Flag to display raw data | False | True |
| limit | int | Number of raw data to show | 10 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>