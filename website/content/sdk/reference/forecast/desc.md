---
title: desc
description: Detailed information on how to use the 'desc' function of the OpenBB
  finance package in Python. The function returns statistics for a specified data
  frame.
keywords:
- OpenBB finance package
- data frame
- statistics
- forecasting
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.desc - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns statistics for a given df

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L504)]

```python
openbb.forecast.desc(data: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The df to produce statistics for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The df with the new data |
---

</TabItem>
<TabItem value="view" label="Chart">

None

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L257)]

```python
openbb.forecast.desc_chart(data: pd.DataFrame, name: str = "", export: str = "")
```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
