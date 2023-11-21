---
title: adx
description: This page provides extensive information about the ADX technical indicator,
  including parameters, returns, and usage. It shares Python source codes for implementing
  and visualising the ADX technical indicator on OHLC price data using OpenBBTerminal.
keywords:
- ADX technical indicator
- Dataframe with OHLC price data
- Technical Analysis
- ADX chart
- Plot ADX Indicator
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.adx - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

ADX technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_model.py#L16)]

```python wordwrap
openbb.ta.adx(data: pd.DataFrame, window: int = 14, scalar: int = 100, drift: int = 1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 14 | True |
| scalar | int | Scalar variable | 100 | True |
| drift | int | Drift variable | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with adx indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots ADX indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_view.py#L18)]

```python wordwrap
openbb.ta.adx_chart(data: pd.DataFrame, window: int = 14, scalar: int = 100, drift: int = 1, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 14 | True |
| scalar | int | Scalar variable | 100 | True |
| drift | int | Drift variable | 1 | True |
| symbol | str | Ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>