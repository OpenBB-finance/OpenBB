---
title: fgdp
description: Real gross domestic product (GDP) is GDP given in constant prices and
keywords:
- economy
- fgdp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.fgdp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Real gross domestic product (GDP) is GDP given in constant prices and

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L656)]

```python wordwrap
openbb.economy.fgdp(countries: Optional[List[str]], types: str = "real", units: str = "Q", start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| type | str | Type of GDP to get data for. Either 'real' or 'nominal'.<br/>Default s real GDP (real). | None | True |
| units | str | Units to get data in. Either 'Q' or 'A.<br/>Default is Quarterly (Q). | Q | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with the gdp data |
---



</TabItem>
<TabItem value="view" label="Chart">

Real gross domestic product (GDP) is GDP given in constant prices and

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L238)]

```python wordwrap
openbb.economy.fgdp_chart(countries: Optional[List[str]], types: str = "real", quarterly: bool = False, start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| type | str | Type of GDP to get data for. Either 'real' or 'nominal'.<br/>Default s real GDP (real). | None | True |
| quarterly | bool | Whether to get quarterly results. | False | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |
| raw | bool | Whether to display raw data in a table | False | True |
| export | str | Format to export data |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[OpenBBFigure, None] | OpenBBFigure object if external_axes is True, else None (opens plot in a window) |
---



</TabItem>
</Tabs>