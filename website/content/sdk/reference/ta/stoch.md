---
title: stoch
description: This page provides information on the Stochastic oscillator method used
  in the OpenBB Terminal. Here, you can find details about the parameters and function
  implementation for both the model and chart view. It presents a tutorial on how
  to plot the Stochastic oscillator signal with various parameters.
keywords:
- Stochastic oscillator
- Technical Analysis
- Python code
- Online documentation
- Model view
- Chart view
- OHLC prices
- Stock ticker symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.stoch - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Stochastic oscillator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L126)]

```python wordwrap
openbb.ta.stoch(data: pd.DataFrame, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| fastkperiod | int | Fast k period | 14 | True |
| slowdperiod | int | Slow d period | 3 | True |
| slowkperiod | int | Slow k period | 3 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots stochastic oscillator signal

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L175)]

```python wordwrap
openbb.ta.stoch_chart(data: pd.DataFrame, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| fastkperiod | int | Fast k period | 14 | True |
| slowdperiod | int | Slow d period | 3 | True |
| slowkperiod | int | Slow k period | 3 | True |
| symbol | str | Stock ticker symbol |  | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>