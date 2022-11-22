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
forecast.trans(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    n_predict: int = 5,
    train_split: float = 0.85,
    past_covariates: str = None,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    d_model: int = 64,
    nhead: int = 4,
    num_encoder_layers: int = 3,
    num_decoder_layers: int = 3,
    dim_feedforward: int = 512,
    activation: str = 'relu',
    dropout: float = 0.0,
    batch_size: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 0.001,
    model_save_name: str = 'trans_model',
    force_reset: bool = True,
    save_checkpoints: bool = True,
    chart: bool = False,
) -> Tuple[List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], Optional[float], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Performs Transformer forecasting
    </p>

* **Parameters**

    data: Union[pd.Series, pd.DataFrame]
        Input Data
    n_predict: int
        Days to predict. Defaults to 5.
    target_column: str
        Target column to forecast. Defaults to "close".
    train_split: float
        Train/val split. Defaults to 0.85.
    past_covariates: str
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: int
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length: int
        Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 5.
    d_model: int
        The number of expected features in the encoder/decoder inputs. Defaults to 64.
    nhead: int
        The number of heads in the multi-head attention mechanism. Defaults to 4.
    num_encoder_layers: int
        The number of encoder layers in the encoder. Defaults to 3.
    num_decoder_layers: int
        The number of decoder layers in the encoder. Defaults to 3.
    dim_feedforward: int
        The dimension of the feedforward network model. Defaults to 512.
    activation: str
        The activation function of encoder/decoder intermediate layer, ‘relu’ or ‘gelu’. Defaults to 'relu'.
    dropout: float
        Fraction of neurons afected by Dropout. Defaults to 0.0.
    batch_size: int
        Number of time series (input and output sequences) used in each training pass. Defaults to 32.
    n_epochs: int
        Number of epochs over which to train the model. Defaults to 100.
    learning_rate: float
        Defaults to 1e-3.
    model_save_name: str
        Name for model. Defaults to "brnn_model".
    force_reset: bool
        If set to True, any previously-existing model with the same name will be reset (all checkpoints will be
        discarded). Defaults to True.
    save_checkpoints: bool
        Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True.
    chart: *bool*
       Flag to display chart


* **Returns**

    List[TimeSeries]
        Adjusted Data series
    List[TimeSeries]
        Historical forecast by best RNN model
    List[TimeSeries]
        list of Predictions
    Optional[float]
        Mean average precision error
    Any
        Best transformer Model

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.trans(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    dataset_name: str = '',
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    d_model: int = 64,
    nhead: int = 4,
    num_encoder_layers: int = 3,
    num_decoder_layers: int = 3,
    dim_feedforward: int = 512,
    activation: str = 'relu',
    dropout: float = 0.1,
    batch_size: int = 16,
    n_epochs: int = 100,
    learning_rate: float = 0.001,
    model_save_name: str = 'trans_model',
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
    Display Transformer forecast
    </p>

* **Parameters**

    data: Union[pd.Series, pd.DataFrame]
        Input Data
    dataset_name: str
        The name of the ticker to be predicted
    n_predict: int
        Days to predict. Defaults to 5.
    target_column: str
        Target column to forecast. Defaults to "close".
    train_split: float
        Train/val split. Defaults to 0.85.
    past_covariates: str
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: int
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length: int
        Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 5.
    d_model: int
        The number of expected features in the encoder/decoder inputs. Defaults to 64.
    nhead: int
        The number of heads in the multi-head attention mechanism. Defaults to 4.
    num_encoder_layers: int
        The number of encoder layers in the encoder. Defaults to 3.
    num_decoder_layers: int
        The number of decoder layers in the encoder. Defaults to 3.
    dim_feedforward: int
        The dimension of the feedforward network model. Defaults to 512.
    activation: str
        The activation function of encoder/decoder intermediate layer, ‘relu’ or ‘gelu’. Defaults to 'relu'.
    dropout: float
        Fraction of neurons affected by Dropout. Defaults to 0.1.
    batch_size\_: int
        Number of time series (input and output sequences) used in each training pass. Defaults to 32.
    n_epochs: int
        Number of epochs over which to train the model. Defaults to 100.
    model_save_name: str
        Name for model. Defaults to "brnn_model".
    force_reset: bool
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints: bool
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    export: str
        Format to export data
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
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart

