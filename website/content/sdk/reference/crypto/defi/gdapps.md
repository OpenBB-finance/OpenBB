---
title: gdapps
description: This page presents features such as the displaying and plotting of top
  dApps by TVL, which are part of the DeFi module of the openbb crypto module. Detailed
  guides on how to use these features with service parameters such as limit, export
  type, and others are included. Links to source code are also provided.
keywords:
- dApps
- TVL
- gdapps
- openbb.crypto.defi
- DeFi protocols
- Chart
- matplotlib
- Export dataframe
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.gdapps - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Display top dApps (in terms of TVL) grouped by chain.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_model.py#L149)]

```python
openbb.crypto.defi.gdapps(limit: int = 50)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of top dApps to display | 50 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Information about DeFi protocols grouped by chain |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots top dApps (in terms of TVL) grouped by chain.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_view.py#L28)]

```python
openbb.crypto.defi.gdapps_chart(limit: int = 50, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| num | int | Number of top dApps to display | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
