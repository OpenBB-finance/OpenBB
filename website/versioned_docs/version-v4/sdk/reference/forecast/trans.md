---
title: trans
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# trans

<Tabs>
<TabItem value="model" label="Model" default>

Performs Transformer forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/trans_model.py#L20)]

```python
openbb.forecast.trans(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, train_split: float = 0.85, past_covariates: str = None, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, d_model: int = 64, nhead: int = 4, num_encoder_layers: int = 3, num_decoder_layers: int = 3, dim_feedforward: int = 512, activation: str = "relu", dropout: float = 0.0, batch_size: int = 32, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "trans_model", force_reset: bool = True, save_checkpoints: bool = True)
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
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | True |
| d_model | int | The number of expected features in the encoder/decoder inputs. Defaults to 64. | 64 | True |
| nhead | int | The number of heads in the multi-head attention mechanism. Defaults to 4. | 4 | True |
| num_encoder_layers | int | The number of encoder layers in the encoder. Defaults to 3. | 3 | True |
| num_decoder_layers | int | The number of decoder layers in the encoder. Defaults to 3. | 3 | True |
| dim_feedforward | int | The dimension of the feedforward network model. Defaults to 512. | 512 | True |
| activation | str | The activation function of encoder/decoder intermediate layer, ‘relu’ or ‘gelu’. Defaults to 'relu'. | relu | True |
| dropout | float | Fraction of neurons afected by Dropout. Defaults to 0.0. | 0.0 | True |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 32 | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| learning_rate | float | Defaults to 1e-3. | 0.001 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | trans_model | True |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset (all checkpoints will be<br/>discarded). Defaults to True. | True | True |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[TransformerModel]] | Adjusted Data series,<br/>Historical forecast by best RNN model,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best transformer Model. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Transformer forecast

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/trans_view.py#L20)]

```python
openbb.forecast.trans_chart(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, d_model: int = 64, nhead: int = 4, num_encoder_layers: int = 3, num_decoder_layers: int = 3, dim_feedforward: int = 512, activation: str = "relu", dropout: float = 0.1, batch_size: int = 16, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "trans_model", force_reset: bool = True, save_checkpoints: bool = True, export: str = "", residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None)
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
| past_covariates | str | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon | int | Forecast horizon when performing historical forecasting. Defaults to 5. | 5 | True |
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | True |
| d_model | int | The number of expected features in the encoder/decoder inputs. Defaults to 64. | 64 | True |
| nhead | int | The number of heads in the multi-head attention mechanism. Defaults to 4. | 4 | True |
| num_encoder_layers | int | The number of encoder layers in the encoder. Defaults to 3. | 3 | True |
| num_decoder_layers | int | The number of decoder layers in the encoder. Defaults to 3. | 3 | True |
| dim_feedforward | int | The dimension of the feedforward network model. Defaults to 512. | 512 | True |
| activation | str | The activation function of encoder/decoder intermediate layer, ‘relu’ or ‘gelu’. Defaults to 'relu'. | relu | True |
| dropout | float | Fraction of neurons affected by Dropout. Defaults to 0.1. | 0.1 | True |
| batch_size_ | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | None | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | trans_model | True |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset<br/>(all checkpoints will be discarded). Defaults to True. | True | True |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training.<br/>Defaults to True. | True | True |
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