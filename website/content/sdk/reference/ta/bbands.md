---
title: bbands
description: This documentation is about the 'bbands' function in the OpenBB finance
  library. It allows users to calculate and plot Bollinger Bands for financial data,
  providing multiple parameters for customization.
keywords:
- OpenBB finance library
- Bollinger Bands
- Financial data analysis
- Python financial tools
- Technical analysis
- Volatility models
- Financial chart plotting
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.bbands - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate Bollinger Bands

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L31)]

```python wordwrap
openbb.ta.bbands(data: pd.DataFrame, window: int = 15, n_std: float = 2, mamode: str = "ema")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window to calculate BB | 15 | True |
| n_std | float | Number of standard deviations to show | 2 | True |
| mamode | str | Method of calculating average | ema | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of bollinger band data |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots bollinger bands

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L24)]

```python wordwrap
openbb.ta.bbands_chart(data: pd.DataFrame, symbol: str = "", window: int = 15, n_std: float = 2, mamode: str = "sma", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol |  | True |
| window | int | Length of window to calculate BB | 15 | True |
| n_std | float | Number of standard deviations to show | 2 | True |
| mamode | str | Method of calculating average | sma | True |
| export | str | Format of export file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>