---
title: nhits
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# nhits

<Tabs>
<TabItem value="model" label="Model" default>

Performs Nhits forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/nhits_model.py#L22)]

```python
openbb.forecast.nhits(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, train_split: float = 0.85, past_covariates: str = None, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, num_stacks: int = 3, num_blocks: int = 1, num_layers: int = 2, layer_widths: int = 512, pooling_kernel_sizes: Optional[Tuple[Tuple[int]]] = None, n_freq_downsample: Optional[Tuple[Tuple[int]]] = None, dropout: float = 0.1, activation: str = "ReLU", max_pool_1d: bool = True, batch_size: int = 32, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "brnn_model", force_reset: bool = True, save_checkpoints: bool = True)
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
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | True |
| num_stacks | int | The number of stacks that make up the whole model. | 3 | True |
| num_blocks | int | The number of blocks making up every stack. | 1 | True |
| num_layers | int | The number of fully connected layers preceding the final forking layers in each block<br/>of every stack. | 2 | True |
| layer_widths | int | Determines the number of neurons that make up each fully connected layer in each<br/>block of every stack. If a list is passed, it must have a length equal to num_stacks<br/>and every entry in that list corresponds to the layer width of the corresponding stack.<br/>If an integer is passed, every stack will have blocks with FC layers of the same width. | 512 | True |
| pooling_kernel_size | Optional[Tuple[Tuple[int]]]: | If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),<br/>specifying the kernel size for each block in each stack used for the input pooling<br/>layer. If left to None, some default values will be used based on input_chunk_length. | None | True |
| n_freq_downsample | Optional[Tuple[Tuple[int]]] | If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),<br/>specifying the downsampling factors before interpolation, for each block in each stack.<br/>If left to None, some default values will be used based on output_chunk_length. | None | True |
| dropout | float | The dropout probability to be used in fully connected layers. | 0.1 | True |
| activation | str | Supported activations: [‘ReLU’,’RReLU’, ‘PReLU’, ‘Softplus’, ‘Tanh’, ‘SELU’, ‘LeakyReLU’, ‘Sigmoid’] | ReLU | True |
| max_pool_1d | bool | Use max_pool_1d pooling. False uses AvgPool1d. | True | True |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 32 | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| learning_rate | float | Defaults to 1e-3. | 0.001 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | brnn_model | True |
| force_reset | bool | If set to True, any previously-existing model with the same name will be reset (all checkpoints will be<br/>discarded). Defaults to True. | True | True |
| save_checkpoints | bool | Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[NHiTSModel]] | Adjusted Data series,<br/>Historical forecast by best RNN model,<br/>list of Predictions,<br/>Mean average precision error,<br/>Best BRNN Model. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Nhits forecast

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/nhits_view.py#L20)]

```python
openbb.forecast.nhits_chart(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, num_stacks: int = 3, num_blocks: int = 1, num_layers: int = 2, layer_widths: int = 512, pooling_kernel_sizes: Optional[Tuple[Tuple[int]]] = None, n_freq_downsample: Optional[Tuple[Tuple[int]]] = None, dropout: float = 0.1, activation: str = "ReLU", max_pool_1d: bool = True, batch_size: int = 32, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = "rnn_model", force_reset: bool = True, save_checkpoints: bool = True, export: str = "", residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None)
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
| input_chunk_length | int | Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14. | 14 | True |
| output_chunk_length | int | The length of the forecast of the model. Defaults to 5. | 5 | True |
| num_stacks | int | The number of stacks that make up the whole model. | 3 | True |
| num_blocks | int | The number of blocks making up every stack. | 1 | True |
| num_layers | int | The number of fully connected layers preceding the final forking layers in each block<br/>of every stack. | 2 | True |
| layer_widths | int | Determines the number of neurons that make up each fully connected layer in each<br/>block of every stack. If a list is passed, it must have a length equal to num_stacks<br/>and every entry in that list corresponds to the layer width of the corresponding stack.<br/>If an integer is passed, every stack will have blocks with FC layers of the same width. | 512 | True |
| pooling_kernel_size | Optional[Tuple[Tuple[int]]] | If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),<br/>specifying the kernel size for each block in each stack used for the input pooling<br/>layer. If left to None, some default values will be used based on input_chunk_length. | None | True |
| n_freq_downsample | Optional[Tuple[Tuple[int]]] | If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),<br/>specifying the downsampling factors before interpolation, for each block in each stack.<br/>If left to None, some default values will be used based on output_chunk_length. | None | True |
| dropout | float | The dropout probability to be used in fully connected layers. | 0.1 | True |
| activation | str | Supported activations: [[‘ReLU’,’RReLU’, ‘PReLU’, ‘Softplus’, ‘Tanh’, ‘SELU’, ‘LeakyReLU’, ‘Sigmoid’] | ReLU | True |
| max_pool_1d | bool | Use max_pool_1d pooling. False uses AvgPool1d. | True | True |
| batch_size | int | Number of time series (input and output sequences) used in each training pass. Defaults to 32. | 32 | True |
| n_epochs | int | Number of epochs over which to train the model. Defaults to 100. | 100 | True |
| learning_rate | float | Defaults to 1e-3. | 0.001 | True |
| model_save_name | str | Name for model. Defaults to "brnn_model". | rnn_model | True |
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