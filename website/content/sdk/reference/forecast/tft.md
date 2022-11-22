---
title: tft
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# tft

<Tabs>
<TabItem value="model" label="Model" default>

Performs Temporal Fusion Transformer forecasting

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/tft_model.py#L26)]

```python
openbb.forecast.tft(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, hidden_size: int = 16, lstm_layers: int = 1, num_attention_heads: int = 4, full_attention: bool = False, dropout: float = 0.1, hidden_continuous_size: int = 8, n_epochs: int = 200, batch_size: int = 32, model_save_name: str = "tft_model", force_reset: bool = True, save_checkpoints: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data (Union[pd.Series, pd.DataFrame]) |  | Input Data | None | True |
| target_column | Optional[str]: | Target column to forecast. Defaults to "close". | close | True |
| n_predict (int, optional) |  | Days to predict. Defaults to 5. | None | True |
| train_split (float, optional) |  | Train/val split. Defaults to 0.85. | None | True |
| past_covariates (str, optional) |  | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon (int, optional) |  | Forecast horizon when performing historical forecasting. Defaults to 5. | None | True |
| input_chunk_length (int, optional) |  | Number of past time steps that are fed to the forecasting module at prediction time.<br/>Defaults to 14. | None | True |
| output_chunk_length (int, optional) |  | The length of the forecast of the model. Defaults to 5. | None | True |
| hidden_size (int, optional) |  | Hidden state size of the TFT. Defaults to 16. | None | True |
| lstm_layers (int, optional) |  | Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16. | None | True |
| num_attention_headers (int, optional) |  | Number of attention heads. Defaults to 4. | None | True |
| full_attention (bool, optional) |  | Whether to apply a multi-head attention query. Defaults to False> | None | True |
| dropout (float, optional) |  | Fraction of neurons affected by dropout. Defaults to 0.1. | None | True |
| hidden_continuous_size (int, optional) |  | Default hidden size for processing continuous variables. Defaults to 8. | None | True |
| n_epochs (int, optional) |  | Number of epochs to run during training. Defaults to 200. | None | True |
| batch_size (int, optional) |  | Number of samples to pass through network during a single epoch. Defaults to 32. | None | True |
| model_save_name (str, optional) |  | The name for the model. Defaults to tft_model | None | True |
| force_reset (bool, optional) |  | If set to True, any previously-existing model with the same name will be reset<br/>(all checkpoints will be discarded). Defaults to True. | None | True |
| save_checkpoints (bool, optional) |  | Whether or not to automatically save the untrained model and checkpoints from training.<br/>Defaults to True. | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
|  | Adjusted Data series,<br/>List of historical fcast values,<br/>List of predicted fcast values,<br/>Optional[float] - precision,<br/>Fit Prob. TFT model object. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Temporal Fusion Transformer forecast

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/tft_view.py#L20)]

```python
openbb.forecast.tft_chart(data: Union[pd.Series, pd.DataFrame], target_column: str = "close", dataset_name: str = "", n_predict: int = 5, past_covariates: str = None, train_split: float = 0.85, forecast_horizon: int = 5, input_chunk_length: int = 14, output_chunk_length: int = 5, hidden_size: int = 16, lstm_layers: int = 1, num_attention_heads: int = 4, full_attention: bool = False, dropout: float = 0.1, hidden_continuous_size: int = 8, n_epochs: int = 200, batch_size: int = 32, model_save_name: str = "tft_model", force_reset: bool = True, save_checkpoints: bool = True, export: str = "", residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data (Union[pd.Series, pd.DataFrame]) |  | Input Data | None | True |
| target_column | Optional[str]: | Target column to forecast. Defaults to "close". | close | True |
| dataset_name str | None | The name of the ticker to be predicted | None | True |
| n_predict (int, optional) |  | Days to predict. Defaults to 5. | None | True |
| train_split (float, optional) |  | Train/val split. Defaults to 0.85. | None | True |
| past_covariates (str, optional) |  | Multiple secondary columns to factor in when forecasting. Defaults to None. | None | True |
| forecast_horizon (int, optional) |  | Forecast horizon when performing historical forecasting. Defaults to 5. | None | True |
| input_chunk_length (int, optional) |  | Number of past time steps that are fed to the forecasting module at prediction time.<br/>Defaults to 14. | None | True |
| output_chunk_length (int, optional) |  | The length of the forecast of the model. Defaults to 5. | None | True |
| hidden_size (int, optional) |  | Hidden state size of the TFT. Defaults to 16. | None | True |
| lstm_layers (int, optional) |  | Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16. | None | True |
| num_attention_headers (int, optional) |  | Number of attention heads. Defaults to 4. | None | True |
| full_attention (bool, optional) |  | Whether to apply a multi-head attention query. Defaults to False> | None | True |
| dropout (float, optional) |  | Fraction of neurons affected by dropout. Defaults to 0.1. | None | True |
| hidden_continuous_size (int, optional) |  | Default hidden size for processing continuous variables. Defaults to 8. | None | True |
| n_epochs (int, optional) |  | Number of epochs to run during training. Defaults to 200. | None | True |
| batch_size (int, optional) |  | Number of samples to pass through network during a single epoch. Defaults to 32. | None | True |
| model_save_name (str, optional) |  | The name for the model. Defaults to tft_model | None | True |
| force_reset (bool, optional) |  | If set to True, any previously-existing model with the same name will be reset<br/>(all checkpoints will be discarded). Defaults to True. | None | True |
| save_checkpoints (bool, optional) |  | Whether or not to automatically save the untrained model and checkpoints from training.<br/>Defaults to True. | None | True |
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