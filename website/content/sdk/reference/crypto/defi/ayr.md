---
title: ayr
description: This documentation page provides a detailed overview of the Anchor Yield
  Reserve's 30-day history. It provides the source code and usage for the `ayr` and
  `ayr_chart` functions from the `openbb.crypto.defi` namespace, including parameters
  and returns.
keywords:
- docusaurus
- metadata page
- Anchor Yield Reserve
- crypto
- defi
- ayr
- ayr_chart
- crypto.defi
- matplotlib
- dataframe
- parameters
- returns
- 30-day history
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.ayr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Displays the 30-day history of the Anchor Yield Reserve.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_model.py#L63)]

```python
openbb.crypto.defi.ayr()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing historical data |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots the 30-day history of the Anchor Yield Reserve.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_view.py#L85)]

```python
openbb.crypto.defi.ayr_chart(export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file, by default False |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
