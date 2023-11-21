---
title: ad
description: This page provides information about how to implement and plot the AD
  (Accumulation/Distribution Line) technical indicator using OpenBB's Python module.
  It includes the source code, required parameters, and the outputs from these functions.
keywords:
- Docusaurus
- Metadata
- Technical Indicator
- AD indicator
- Pandas DataFrame
- Chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.ad - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate AD technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_model.py#L17)]

```python wordwrap
openbb.ta.ad(data: pd.DataFrame, use_open: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of prices with OHLC and Volume | None | False |
| use_open | bool | Whether to use open prices | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots AD technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_view.py#L20)]

```python wordwrap
openbb.ta.ad_chart(data: pd.DataFrame, use_open: bool = False, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| use_open | bool | Whether to use open prices in calculation | False | True |
| symbol | str | Ticker symbol |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data as |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>