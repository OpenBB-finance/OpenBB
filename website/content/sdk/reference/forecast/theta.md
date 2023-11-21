---
title: theta
description: This page provides detailed information on how to use the 'Theta' model
  and 'Theta' chart for financial forecasting with OpenBB. It explains various parameters
  for accurate prediction and chart display, alongside respective source code examples.
keywords:
- Theta model
- Theta chart
- Forecasting
- Financial prediction
- Source code
- Model parameters
- Chart display
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.theta - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Performs Theta forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/theta_model.py#L29)]

```python wordwrap
openbb.forecast.theta(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", seasonal: str = "M", seasonal_periods: int = 7, n_predict: int = 5, start_window: float = 0.85, forecast_horizon: int = 5, metric: str = "mape")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, np.ndarray] | Input data. | None | False |
| target_column | Optional[str]: | Target column to forecast. Defaults to "close". | close | True |
| seasonal | str | Seasonal component.  One of [N, A, M]<br/>Defaults to MULTIPLICATIVE. | M | True |
| seasonal_periods | int | Number of seasonal periods in a year<br/>If not set, inferred from frequency of the series. | 7 | True |
| n_predict | int | Number of days to forecast | 5 | True |
| start_window | float | Size of sliding window from start of timeseries and onwards | 0.85 | True |
| forecast_horizon | int | Number of days to forecast when backtesting and retraining historical data | 5 | True |
| metric | str | Metric to use when backtesting and retraining historical data. Defaults to "mape". | mape | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, float, type[Theta]] | Adjusted Data series,<br/>Historical forecast by best theta,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best Theta,<br/>Theta Model. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Theta forecast

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/theta_view.py#L19)]

```python wordwrap
openbb.forecast.theta_chart(data: Union[pd.DataFrame, pd.Series], target_column: str = "close", dataset_name: str = "", seasonal: str = "M", seasonal_periods: int = 7, n_predict: int = 5, start_window: float = 0.85, forecast_horizon: int = 5, export: str = "", sheet_name: Optional[str] = None, residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, metric: str = "mape", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, np.array] | Data to forecast | None | False |
| target_column | Optional[str]: | Target column to forecast. Defaults to "close". | close | True |
| dataset_name | str | The name of the ticker to be predicted |  | True |
| seasonal | str | Seasonal component.  One of [N, A, M]<br/>Defaults to MULTIPLICATIVE. | M | True |
| seasonal_periods | int | Number of seasonal periods in a year<br/>If not set, inferred from frequency of the series. | 7 | True |
| n_predict | int | Number of days to forecast | 5 | True |
| start_window | float | Size of sliding window from start of timeseries and onwards | 0.85 | True |
| forecast_horizon | int | Number of days to forecast when backtesting and retraining historical | 5 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| residuals | bool | Whether to show residuals for the model. Defaults to False. | False | True |
| forecast_only | bool | Whether to only show dates in the forecasting range. Defaults to False. | False | True |
| start_date | Optional[datetime] | The starting date to perform analysis, data before this is trimmed. Defaults to None. | None | True |
| end_date | Optional[datetime] | The ending date to perform analysis, data after this is trimmed. Defaults to None. | None | True |
| naive | bool | Whether to show the naive baseline. This just assumes the closing price will be the same<br/>as the previous day's closing price. Defaults to False. | False | True |
| export_pred_raw | bool | Whether to export the raw predicted values. Defaults to False. | False | True |
| metric | str | The metric to use for backtesting. Defaults to "mape". | mape | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>