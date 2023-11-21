---
title: ycrv
description: Gets yield curve data from FRED
keywords:
- fixedincome
- ycrv
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.ycrv - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gets yield curve data from FRED.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L296)]

```python wordwrap
openbb.fixedincome.ycrv(date: str = "", return_date: bool = False, inflation_adjusted: bool = False, spot_or_par: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | str | Date to get curve for. If empty, gets most recent date (format yyyy-mm-dd) |  | True |
| return_date | bool | If True, returns date of yield curve | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | Dataframe of yields and maturities,<br/>Date for which the yield curve is obtained |
---

## Examples

```python
from openbb_terminal.sdk import openbb
ycrv_df = openbb.fixedincome.ycrv()
```

```
Since there is a delay with the data, the most recent date is returned and can be accessed with return_date=True
```
```python
ycrv_df, ycrv_date = openbb.fixedincome.ycrv(return_date=True)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display yield curve based on US Treasury rates for a specified date.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_view.py#L948)]

```python wordwrap
openbb.fixedincome.ycrv_chart(date: str = "", inflation_adjusted: bool = False, raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | str | Date to get curve for. If None, gets most recent date (format yyyy-mm-dd) |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |
| raw | bool | Output only raw data | False | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>