---
title: regr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# regr

<Tabs>
<TabItem value="model" label="Model" default>

Perform Regression Forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/regr_model.py#L22)]

```python
openbb.forecast.regr(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, output_chunk_length: int = 1, lags: Union[int, List[int]] = 72)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | True |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 1. | 1 | True |
| lags | Union[int, List[int]] | lagged target values to predict the next time step | 72 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, type[RegressionModel]] | Adjusted Data series,<br/>Historical forecast by best RNN model,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best Regression Model. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Regression Forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/regr_view.py#L20)]

```python
openbb.forecast.regr_chart(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, output_chunk_length: int = 1, lags: Union[int, List[int]] = 72, export: str = "", residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, explainability_raw: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| dataset_name | str | The name of the ticker to be predicted |  | True |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | True |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 1. | 1 | True |
| lags | Union[int, List[int]] | lagged target values to predict the next time step | 72 | True |
| export | str | Format to export data |  | True |
| residuals | bool | Whether to show residuals for the model. Defaults to False. | False | True |
| forecast_only | bool | Whether to only show dates in the forecasting range. Defaults to False. | False | True |
| start_date | Optional[datetime] | The starting date to perform analysis, data before this is trimmed. Defaults to None. | None | True |
| end_date | Optional[datetime] | The ending date to perform analysis, data after this is trimmed. Defaults to None. | None | True |
| naive | bool | Whether to show the naive baseline. This just assumes the closing price will be the same<br/>as the previous day's closing price. Defaults to False. | False | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>