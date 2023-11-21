---
title: sector
description: Get fund, category, index sector breakdown
keywords:
- funds
- sector
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.sector - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get fund, category, index sector breakdown

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L77)]

```python wordwrap
openbb.funds.sector(loaded_funds: mstarpy.funds.Funds, asset_type: str = "equity")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.funds | class mstarpy.Funds instantiated with selected funds | None | False |
| asset_type | str | can be equity or fixed income | equity | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing sector breakdown |
---



</TabItem>
<TabItem value="view" label="Chart">

Display fund, category, index sector breakdown

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_view.py#L221)]

```python wordwrap
openbb.funds.sector_chart(loaded_funds: mstarpy.funds.Funds, asset_type: str = "equity", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.funds | class mstarpy.Funds instantiated with selected funds | None | False |
| asset_type | str | can be equity or fixed income | equity | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| plotly.graph_objects.Figure | Plotly figure object |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.sector_chart(f)
```

---



</TabItem>
</Tabs>