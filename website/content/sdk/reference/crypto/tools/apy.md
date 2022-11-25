---
title: apy
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# apy

<Tabs>
<TabItem value="model" label="Model" default>

Converts apr into apy

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/tools/tools_model.py#L19)]

```python
openbb.crypto.tools.apy(apr: float, compounding_times: int)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| apr | float | value in percentage | None | False |
| compounding_times | int | number of compounded periods in a year | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | - pd.DataFrame: dataframe with results<br/>- str: narrative version of results |
---



</TabItem>
<TabItem value="view" label="Chart">

Displays APY value converted from APR

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/tools/tools_view.py#L16)]

```python
openbb.crypto.tools.apy_chart(apr: float, compounding_times: int, narrative: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| apr | float | value in percentage | None | False |
| compounding_times | int | number of compounded periods in a year | None | False |
| narrative | str | display narrative version instead of dataframe | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>