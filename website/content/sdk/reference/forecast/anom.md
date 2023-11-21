---
title: anom
description: Get Quantile Anomaly Detection Data
keywords:
- forecast
- anom
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.anom - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get Quantile Anomaly Detection Data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/anom_model.py#L19)]

```python wordwrap
openbb.forecast.anom(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", train_split: float = 0.6)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] |  | None | False |
| Input Data | None |  | None | True |
| ------- | None |  | None | True |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| train_split | (float, optional) | Train/val split. Defaults to 0.85. | 0.6 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[ | List[TimeSeries],<br/>List[TimeSeries],<br/>List[TimeSeries],<br/>] |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Quantile Anomaly Detection

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/anom_view.py#L23)]

```python wordwrap
openbb.forecast.anom_chart(data: Union[pd.Series, pd.DataFrame], dataset_name: Any = "", target_column: str = "close", train_split: float = 0.6, export: str = "", start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] |  | None | False |
| Input Data | None |  | None | True |
| ---------- | None |  | None | True |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| train_split | (float, optional) | Train/val split. Defaults to 0.85. | 0.6 | True |
| export | (str, optional) | Export data to csv, jpg, png, or pdf. Defaults to "". |  | True |
| start_date | (Optional[datetime], optional) | Start date. Defaults to None. | None | True |
| end_date | (Optional[datetime], optional) | End date. Defaults to None. | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[None, go.Figure] | None if external_axes is True, otherwise the figure object |
---



</TabItem>
</Tabs>