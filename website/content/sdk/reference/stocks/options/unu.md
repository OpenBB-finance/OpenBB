---
title: unu
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# unu

<Tabs>
<TabItem value="model" label="Model" default>

Get unusual option activity from fdscanner.com

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/fdscanner_model.py#L19)]

```python
openbb.stocks.options.unu(limit: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number to show | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.Timestamp] | Dataframe containing options information, Timestamp indicated when data was updated from website |
---

## Examples

```python
from openbb_terminal.sdk import openbb
unu_df = openbb.stocks.options.unu()
```

---



</TabItem>
<TabItem value="view" label="Chart">

Displays the unusual options table

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/fdscanner_view.py#L15)]

```python
openbb.stocks.options.unu_chart(limit: int = 20, sortby: str = "Vol/OI", ascend: bool = False, calls_only: bool = False, puts_only: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of rows to show | 20 | True |
| sortby | str | Data column to sort on | Vol/OI | True |
| ascend | bool | Whether to sort in ascend order | False | True |
| calls_only | bool | Flag to only show calls | False | True |
| puts_only | bool | Flag to show puts only | False | True |
| export | str | File type to export |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>