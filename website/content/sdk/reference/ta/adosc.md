---
title: adosc
description: Technical page discussing the calculation and plotting of the AD Oscillator
  technical indicator. The page also includes links to source code and parameter descriptions.
keywords:
- AD Oscillator
- technical indicator
- parameter description
- calculate
- plot
- technical analysis
- fast value
- slow value
- volume model
- TabItem
- docusaurus
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.adosc - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate AD oscillator technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_model.py#L46)]

```python wordwrap
openbb.ta.adosc(data: pd.DataFrame, use_open: bool = False, fast: int = 3, slow: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| use_open | bool | Whether to use open prices | False | True |
| fast | int | Fast value | 3 | True |
| slow | int | Slow value | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots AD Osc Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_view.py#L64)]

```python wordwrap
openbb.ta.adosc_chart(data: pd.DataFrame, fast: int = 3, slow: int = 10, use_open: bool = False, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| use_open | bool | Whether to use open prices in calculation | False | True |
| fast | int | Length of fast window | 3 | True |
| slow | int | Length of slow window | 10 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>