---
title: ftd
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ftd

<Tabs>
<TabItem value="model" label="Model" default>

Display fails-to-deliver data for a given ticker. [Source: SEC]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/sec_model.py#L60)]

```python
openbb.stocks.dps.ftd(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| start_date | Optional[str] | Start of data, in YYYY-MM-DD format | None | True |
| end_date | Optional[str] | End of data, in YYYY-MM-DD format | None | True |
| limit | int | Number of latest fails-to-deliver being printed | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Fail to deliver data |
---



</TabItem>
<TabItem value="view" label="Chart">

Display fails-to-deliver data for a given ticker. [Source: SEC]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/sec_view.py#L28)]

```python
openbb.stocks.dps.ftd_chart(symbol: str, data: pd.DataFrame = None, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 0, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| data | pd.DataFrame | Stock data | None | True |
| start_date | Optional[str] | Start of data, in YYYY-MM-DD format | None | True |
| end_date | Optional[str] | End of data, in YYYY-MM-DD format | None | True |
| limit | int | Number of latest fails-to-deliver being printed | 0 | True |
| raw | bool | Print raw data | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>