.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.tft(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    hidden_size: int = 16,
    lstm_layers: int = 1,
    num_attention_heads: int = 4,
    full_attention: bool = False,
    dropout: float = 0.1,
    hidden_continuous_size: int = 8,
    n_epochs: int = 200,
    batch_size: int = 32,
    model_save_name: str = 'tft_model',
    force_reset: bool = True,
    save_checkpoints: bool = True,
    chart: bool = False,
) -> Tuple[List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], Optional[float], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Performs Temporal Fusion Transformer forecasting
    The TFT applies multi-head attention queries on future inputs from mandatory future_covariates.
    Specifying future encoders with add_encoders (read below) can automatically generate future
    covariates and allows to use the model without having to pass any future_covariates to fit()
    and predict().

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html
    </p>

* **Parameters**

    data (Union[pd.Series, pd.DataFrame]):
        Input Data
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
    n_predict (int, optional):
        Days to predict. Defaults to 5.
    train_split (float, optional):
        Train/val split. Defaults to 0.85.
    past_covariates (str, optional):
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon (int, optional):
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length (int, optional):
        Number of past time steps that are fed to the forecasting module at prediction time.
        Defaults to 14.
    output_chunk_length (int, optional):
        The length of the forecast of the model. Defaults to 5.
    hidden_size (int, optional):
        Hidden state size of the TFT. Defaults to 16.
    lstm_layers (int, optional):
        Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16.
    num_attention_headers (int, optional):
        Number of attention heads. Defaults to 4.
    full_attention (bool, optional):
        Whether to apply a multi-head attention query. Defaults to False>
    dropout (float, optional):
        Fraction of neurons affected by dropout. Defaults to 0.1.
    hidden_continuous_size (int, optional):
        Default hidden size for processing continuous variables. Defaults to 8.
    n_epochs (int, optional):
        Number of epochs to run during training. Defaults to 200.
    batch_size (int, optional):
        Number of samples to pass through network during a single epoch. Defaults to 32.
    model_save_name (str, optional):
        The name for the model. Defaults to tft_model
    force_reset (bool, optional):
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints (bool, optional):
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    chart: *bool*
       Flag to display chart


* **Returns**

    List[float]
        Adjusted Data series
    List[float]
        List of historical fcast values
    List[float]
        List of predicted fcast values
    Optional[float]
        precision
    Any
        Fit Prob. TFT model object.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.tft(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    dataset_name: str = '',
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    hidden_size: int = 16,
    lstm_layers: int = 1,
    num_attention_heads: int = 4,
    full_attention: bool = False,
    dropout: float = 0.1,
    hidden_continuous_size: int = 8,
    n_epochs: int = 200,
    batch_size: int = 32,
    model_save_name: str = 'tft_model',
    force_reset: bool = True,
    save_checkpoints: bool = True,
    export: str = '',
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    naive: bool = False,
    export_pred_raw: bool = False,
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Temporal Fusion Transformer forecast
    </p>

* **Parameters**

    data (Union[pd.Series, pd.DataFrame]):
        Input Data
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
    dataset_name str
        The name of the ticker to be predicted
    n_predict (int, optional):
        Days to predict. Defaults to 5.
    train_split (float, optional):
        Train/val split. Defaults to 0.85.
    past_covariates (str, optional):
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon (int, optional):
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length (int, optional):
        Number of past time steps that are fed to the forecasting module at prediction time.
        Defaults to 14.
    output_chunk_length (int, optional):
        The length of the forecast of the model. Defaults to 5.
    hidden_size (int, optional):
        Hidden state size of the TFT. Defaults to 16.
    lstm_layers (int, optional):
        Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16.
    num_attention_headers (int, optional):
        Number of attention heads. Defaults to 4.
    full_attention (bool, optional):
        Whether to apply a multi-head attention query. Defaults to False>
    dropout (float, optional):
        Fraction of neurons affected by dropout. Defaults to 0.1.
    hidden_continuous_size (int, optional):
        Default hidden size for processing continuous variables. Defaults to 8.
    n_epochs (int, optional):
        Number of epochs to run during training. Defaults to 200.
    batch_size (int, optional):
        Number of samples to pass through network during a single epoch. Defaults to 32.
    model_save_name (str, optional):
        The name for the model. Defaults to tft_model
    force_reset (bool, optional):
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints (bool, optional):
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    residuals: bool
        Whether to show residuals for the model. Defaults to False.
    forecast_only: bool
        Whether to only show dates in the forecasting range. Defaults to False.
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    naive: bool
        Whether to show the naive baseline. This just assumes the closing price will be the same
        as the previous day's closing price. Defaults to False.
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart

