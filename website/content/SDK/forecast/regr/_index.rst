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
forecast.regr(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    output_chunk_length: int = 1,
    lags: Union[int, List[int]] = 72,
    chart: bool = False,
) -> Tuple[List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], float, Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Perform Regression Forecasting
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
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 1.
    lags: Union[int, List[int]]
        lagged target values to predict the next time step
    chart: *bool*
       Flag to display chart


* **Returns**

    List[TimeSeries]
        Adjusted Data series
    List[TimeSeries]
        Historical forecast by best RNN model
    List[TimeSeries]
        list of Predictions
    float
        Mean average precision error
    Any
        Best Regression Model

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.regr(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    dataset_name: str = '',
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    output_chunk_length: int = 1,
    lags: Union[int, List[int]] = 72,
    export: str = '',
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    naive: bool = False,
    explainability_raw: bool = False,
    export_pred_raw: bool = False,
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Regression Forecasting
    </p>

* **Parameters**

    data: Union[pd.Series, pd.DataFrame]
        Input Data
    target_column: str
        Target column to forecast. Defaults to "close".
    dataset_name: str
        The name of the ticker to be predicted
    n_predict: int
        Days to predict. Defaults to 5.
    train_split: float
        Train/val split. Defaults to 0.85.
    past_covariates: str
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: int
        Forecast horizon when performing historical forecasting. Defaults to 5.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 1.
    lags: Union[int, List[int]]
        lagged target values to predict the next time step
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

