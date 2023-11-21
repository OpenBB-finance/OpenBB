---
title: kc
description: This documentation page provides details on the Keltner Channels functionality
  implemented in the OpenBB Terminal. It includes a guide for using the Keltner Channels
  analytical model and the chart plotting function.
keywords:
- Keltner Channels
- technical analysis
- volatility model
- chart plotting
- financial data analysis
- Data visualization
- ema filter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.kc - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Keltner Channels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L101)]

```python wordwrap
openbb.ta.kc(data: pd.DataFrame, window: int = 20, scalar: float = 2, mamode: str = "ema", offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | 20 | True |
| scalar | float | Scalar value | 2 | True |
| mamode | str | Type of filter | ema | True |
| offset | int | Offset value | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of rolling kc |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots Keltner Channels Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L129)]

```python wordwrap
openbb.ta.kc_chart(data: pd.DataFrame, window: int = 20, scalar: float = 2, mamode: str = "ema", offset: int = 0, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | 20 | True |
| scalar | float | Scalar value | 2 | True |
| mamode | str | Type of filter | ema | True |
| offset | int | Offset value | 0 | True |
| symbol | str | Ticker symbol |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>