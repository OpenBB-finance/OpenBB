---
title: sratio
description: This page provides a detailed guide on how to use OpenBB finance's sratio
  and sratio_chart functions. These functions retrieve and plot staking ratio history
  from terra blockchain which can be useful for DeFi applications.
keywords:
- terra blockchain
- staking ratio history
- OpenBB finance
- openbb crypto defi
- sratio function
- dataframe
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.sratio - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L285)]

```python wordwrap
openbb.crypto.defi.sratio(limit: int = 200)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | The number of ratios to show | 200 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | historical staking ratio |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L222)]

```python wordwrap
openbb.crypto.defi.sratio_chart(limit: int = 90, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 90 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>