---
title: garch
description: Calculates volatility forecasts based on GARCH
keywords:
- econometrics
- garch
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.garch - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculates volatility forecasts based on GARCH.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L337)]

```python wordwrap
openbb.econometrics.garch(data: pd.Series, p: int = 1, o: int = 0, q: int = 1, mean: str = "constant", horizon: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | The time series (often returns) to estimate volatility from | None | False |
| p | int | Lag order of the symmetric innovation | 1 | True |
| o | int | Lag order of the asymmetric innovation | 0 | True |
| q | int | Lag order of lagged volatility or equivalent | 1 | True |
| mean | str | The name of the mean model | constant | True |
| horizon | int | The horizon of the forecast | 100 | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.econometrics.garch(openbb.stocks.load("AAPL").iloc[:, 0].pct_change()*100)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Plots the volatility forecasts based on GARCH

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L337)]

```python wordwrap
openbb.econometrics.garch_chart(dataset: pd.DataFrame, column: str, p: int = 1, o: int = 0, q: int = 1, mean: str = "constant", horizon: int = 1, detailed: bool = False, export: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataframe to use | None | False |
| column | str | The column of the dataframe to use | None | False |
| p | int | Lag order of the symmetric innovation | 1 | True |
| o | int | Lag order of the asymmetric innovation | 0 | True |
| q | int | Lag order of lagged volatility or equivalent | 1 | True |
| mean | str | The name of the mean model | constant | True |
| horizon | int | The horizon of the forecast | 1 | True |
| detailed | bool | Whether to display the details about the parameter fit, for instance the confidence interval | False | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>