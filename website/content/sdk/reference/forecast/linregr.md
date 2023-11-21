---
title: linregr
description: Perform or display linear regression forecasting with OpenBB. The page
  provides the function parameters and their explanations, as well as the return values.
keywords:
- linear regression
- forecasting
- data analysis
- parameters
- returns
- prediction
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.linregr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Perform Linear Regression Forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/linregr_model.py#L20)]

```python wordwrap
openbb.forecast.linregr(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, past_covariates: Optional[str] = None, train_split: float = 0.85, forecast_horizon: int = 5, output_chunk_length: int = 5, lags: Union[int, List[int]] = 14, random_state: Optional[int] = None, metric: str = "mape")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | True |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 1. | 5 | True |
| lags | Union[int, List[int]] | lagged target values to predict the next time step | 14 | True |
| random_state | Optional[int] | The state for the model | None | True |
| metric | str | The metric to use for the model. Defaults to "mape". | mape | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, LinearRegressionModel] | Adjusted Data series,<br/>Historical forecast by best RNN model,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best Linear Regression Model. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Linear Regression Forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/linregr_view.py#L18)]

```python wordwrap
openbb.forecast.linregr_chart(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, past_covariates: Optional[str] = None, train_split: float = 0.85, forecast_horizon: int = 5, output_chunk_length: int = 5, lags: Union[int, List[int]] = 14, export: str = "", sheet_name: Optional[str] = None, residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, explainability_raw: bool = False, export_pred_raw: bool = False, metric: str = "mape", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| dataset_name | str | The name of the ticker to be predicted |  | True |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| target_col | str | Target column to forecast. Defaults to "close". | None | True |
| train_split | (float, optional) | Train/val split. Defaults to 0.85. | 0.85 | True |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 1. | 5 | True |
| lags | Union[int, List[int]] | lagged target values to predict the next time step | 14 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| residuals | bool | Whether to show residuals for the model. Defaults to False. | False | True |
| forecast_only | bool | Whether to only show dates in the forecasting range. Defaults to False. | False | True |
| start_date | Optional[datetime] | The starting date to perform analysis, data before this is trimmed. Defaults to None. | None | True |
| end_date | Optional[datetime] | The ending date to perform analysis, data after this is trimmed. Defaults to None. | None | True |
| naive | bool | Whether to show the naive baseline. This just assumes the closing price will be the<br/>same as the previous day's closing price. Defaults to False. | False | True |
| explainability_raw | bool | Whether to show the raw explainability data. Defaults to False. | False | True |
| export_pred_raw | bool | Whether to export the raw prediction data. Defaults to False. | False | True |
| metric | str | The metric to use for the model. Defaults to "mape". | mape | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>