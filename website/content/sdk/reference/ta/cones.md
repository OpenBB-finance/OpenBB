---
title: cones
description: Returns a DataFrame of realized volatility quantiles
keywords:
- ta
- cones
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.cones - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns a DataFrame of realized volatility quantiles.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L566)]

```python wordwrap
openbb.ta.cones(data: pd.DataFrame, lower_q: float = 0.25, upper_q: float = 0.75, is_crypto: bool = False, model: str = "STD")
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| cones | DataFrame of realized volatility quantiles. |
---

## Examples

```python
df = openbb.stocks.load("AAPL")
cones_df = openbb.ta.cones(data = df, lower_q = 0.10, upper_q = 0.90)
```

```python
cones_df = openbb.ta.cones(df,0.15,0.85,False,"Garman-Klass")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Plots the realized volatility quantiles for the loaded ticker.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L239)]

```python wordwrap
openbb.ta.cones_chart(data: pd.DataFrame, symbol: str = "", lower_q: float = 0.25, upper_q: float = 0.75, model: str = "STD", is_crypto: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of OHLC prices. | None | False |
| symbol | str (default = "") | The ticker symbol. |  | True |
| lower_q | float (default = 0.25) | The lower quantile to calculate for. | 0.25 | True |
| upper_q | float (default = 0.75) | The upper quantile to for. | 0.75 | True |
| is_crypto | bool (default = False) | If true, volatility is calculated for 365 days instead of 252. | False | True |
| model | str (default = "STD") | The model to use for volatility calculation. Choices are:<br/>["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"]<br/><br/>    Standard deviation measures how widely returns are dispersed from the average return.<br/>    It is the most common (and biased) estimator of volatility.<br/><br/>    Parkinson volatility uses the high and low price of the day rather than just close to close prices.<br/>    It is useful for capturing large price movements during the day.<br/><br/>    Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.<br/>    As markets are most active during the opening and closing of a trading session;<br/>    it makes volatility estimation more accurate.<br/><br/>    Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.<br/>    It produces unbiased estimates and a substantial gain in efficiency.<br/><br/>    Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.<br/>    Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,<br/>    mean return not equal to zero.<br/><br/>    Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).<br/>    It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility. | STD | True |
| export | str | Format of export file |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---

## Examples


df_ta = openbb.stocks.load('XLY')
openbb.ta.cones_chart(data = df_ta, symbol = 'XLY')

df_ta = openbb.stocks.load('XLE')
openbb.ta.cones_chart(data = df_ta, symbol = "XLE", lower_q = 0.10, upper_q = 0.90)

openbb.ta.cones_chart(data = df_ta, symbol = "XLE", model = "Garman-Klass")

---



</TabItem>
</Tabs>