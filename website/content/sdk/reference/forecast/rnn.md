---
title: rnn
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rnn

<Tabs>
<TabItem value="model" label="Model" default>

Perform RNN forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/rnn_model.py#L21)]

```python
openbb.forecast.rnn(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, train_split: float = 0.85, forecast_horizon: int = 5, model_type: str = "LSTM", hidden_dim: int = 20, dropout: float = 0.0, batch_size: int = 16, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "rnn_model", training_length: int = 20, input_chunk_size: int = 14, force_reset: bool = True, save_checkpoints: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| model_type | str | Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM". | LSTM | True |
| hidden_dim | int | Size for feature maps for each hidden RNN layer.. Defaults to 20. | 20 | True |
| dropout | float | Fraction of neurons affected by Dropout. Defaults to 0.0. | 0.0 | True |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 16 | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| learning_rate | float | Defaults to 1e-3. | 0.001 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | rnn_model | True |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset<br/>(all checkpoints will be discarded). Defaults to True. | True | True |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training.<br/>Defaults to True. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[RNNModel]] | Adjusted Data series,<br/>Historical forecast by best RNN model,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best RNN Model |
---



</TabItem>
<TabItem value="view" label="Chart">

Display RNN forecast

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/rnn_view.py#L20)]

```python
openbb.forecast.rnn_chart(data: Union[pd.DataFrame, pd.Series], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, train_split: float = 0.85, forecast_horizon: int = 5, model_type: str = "LSTM", hidden_dim: int = 20, dropout: float = 0.0, batch_size: int = 16, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "rnn_model", training_length: int = 20, input_chunk_size: int = 14, force_reset: bool = True, save_checkpoints: bool = True, export: str = "", residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | Union[pd.Series, pd.DataFrame] | Input Data | None | False |
| dataset_name | str | The name of the ticker to be predicted |  | True |
| n_predict | int | Days to predict. Defaults to 5. | 5 | True |
| target_column | str | Target column to forecast. Defaults to "close". | close | True |
| train_split | float | Train/val split. Defaults to 0.85. | 0.85 | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| model_type | str | Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM". | LSTM | True |
| hidden_dim | int | Size for feature maps for each hidden RNN layer.. Defaults to 20. | 20 | True |
| dropout | float | Fraction of neurons affected by Dropout. Defaults to 0.0. | 0.0 | True |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 16 | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| learning_rate | float | Defaults to 1e-3. | 0.001 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | rnn_model | True |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset<br/>(all checkpoints will be discarded). Defaults to True. | True | True |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True. | True | True |
| forecast_only | bool | Whether to only show dates in the forecasting range. Defaults to False. | False | True |
| export | str | Format to export data |  | True |
| residuals | bool | Whether to show residuals for the model. Defaults to False. | False | True |
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