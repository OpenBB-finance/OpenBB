---
title: indexes
description: The documentation page covers the retrieval and visualization of crypto
  indexes using the CoinGecko API in the OpenBB platform. It details parameters, source
  code, and return values for related methods.
keywords:
- CoinGecko API
- crypto indexes
- pycoingecko_model
- pycoingecko_view
- data sort
- crypto data visualization
- data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.indexes - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L350)]

```python
openbb.crypto.ov.indexes(sortby: str = "Name", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | Name | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Name, Id, Market, Last, MultiAsset |
---

</TabItem>
<TabItem value="view" label="Chart">

Shows list of crypto indexes. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L608)]

```python
openbb.crypto.ov.indexes_chart(sortby: str = "Name", ascend: bool = True, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | Name | True |
| ascend | bool | Flag to sort data descending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
