---
title: brnn
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# brnn

<Tabs>
<TabItem value="model" label="Model" default>

## forecast_brnn_model.get_brnn_data

```python title='openbb_terminal/forecast/brnn_model.py'
def get_brnn_data(data: Union[pd.Series, pd.DataFrame], target_column: str, n_predict: int, train_split: float, past_covariates: str, forecast_horizon: int, input_chunk_length: int, output_chunk_length: int, model_type: str, n_rnn_layers: int, dropout: float, batch_size: int, n_epochs: int, learning_rate: float, model_save_name: str, force_reset: bool, save_checkpoints: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/brnn_model.py#L22)

Description: Performs Block RNN forecasting

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| target_column | str | Target column to forecast. Defaults to "close". | s | False |
| n_predict | int | Days to predict. Defaults to 5. | 5 | False |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | False |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | False |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | False |
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | False |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | False |
| model_type | str | Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM". | s | False |
| n_rnn_layers | int | Number of layers in the RNN module. Defaults to 1. | 1 | False |
| dropout | float | Fraction of neurons affected by Dropout. Defaults to 0.0. | 0.0 | False |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 32 | False |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | False |
| learning_rate | float | Defaults to 1e-3. | 1e-3 | False |
| model_save_name | str | Name for model. Defaults to "brnn_model". | s | False |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset (all checkpoints will be
discarded). Defaults to True. | True | False |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True. | True | False |

## Returns

| Type | Description |
| ---- | ----------- |
| list[TimeSeries] | Adjusted Data series |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forecast_brnn_view.display_brnn_forecast

```python title='openbb_terminal/forecast/brnn_view.py'
def display_brnn_forecast(data: Union[pd.Series, pd.DataFrame], target_column: str, dataset_name: str, n_predict: int, past_covariates: str, train_split: float, forecast_horizon: int, input_chunk_length: int, output_chunk_length: int, model_type: str, n_rnn_layers: int, dropout: float, batch_size: int, n_epochs: int, learning_rate: float, model_save_name: str, force_reset: bool, save_checkpoints: bool, export: str, residuals: bool, forecast_only: bool, start_date: Optional[datetime.datetime], end_date: Optional[datetime.datetime], naive: bool, export_pred_raw: bool, external_axes: Optional[List[axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/brnn_view.py#L20)

Description: Display BRNN forecast

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| target_column | str | Target column to forecast. Defaults to "close". | s | False |
| dataset_name | str | The name of the ticker to be predicted | None | False |
| n_predict | int | Days to predict. Defaults to 5. | 5 | False |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | False |
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | False |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | False |
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | False |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | False |
| model_type | str | Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM". | s | False |
| n_rnn_layers | int | Number of layers in the RNN module. Defaults to 1. | 1 | False |
| dropout | float | Fraction of neurons affected by Dropout. Defaults to 0.0. | 0.0 | False |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 32 | False |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 101. | 101 | False |
| learning_rate | float | Defaults to 1e-3. | 1e-3 | False |
| model_save_name | str | Name for model. Defaults to "brnn_model". | s | False |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset
(all checkpoints will be discarded). Defaults to True. | True | False |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training.
Defaults to True. | True | False |
| export | str | Format to export data | None | False |
| residuals | bool | Whether to show residuals for the model. Defaults to False. | False | False |
| forecast_only | bool | Whether to only show dates in the forecasting range. Defaults to False. | False | False |
| start_date | Optional[datetime] | The starting date to perform analysis, data before this is trimmed. Defaults to None. | None | False |
| end_date | Optional[datetime] | The ending date to perform analysis, data after this is trimmed. Defaults to None. | None | False |
| naive | bool | Whether to show the naive baseline. This just assumes the closing price will be the same
as the previous day's closing price. Defaults to False. | False | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>