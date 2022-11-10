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
forecast.theta(
    data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame],
    target_column: str = 'close',
    seasonal: str = 'M',
    seasonal_periods: int = 7,
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
    chart: bool = False,
) -> Tuple[List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], float, float, Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Performs Theta forecasting
    An implementation of the 4Theta method with configurable theta parameter.

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html
    </p>

* **Parameters**

    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to MULTIPLICATIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
    chart: *bool*
       Flag to display chart


* **Returns**

    List[TimeSeries]
        Adjusted Data series
    List[TimeSeries]
        Historical forecast by best theta
    List[TimeSeries]
        list of Predictions
    float
        Mean average precision error
    float
        Best Theta
    Any
        Theta Model

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.theta(
    data: Union[pandas.core.frame.DataFrame, pandas.core.series.Series],
    target_column: str = 'close',
    dataset_name: str = '',
    seasonal: str = 'M',
    seasonal_periods: int = 7,
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
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
    Display Theta forecast
    </p>

* **Parameters**

    data : Union[pd.Series, np.array]
        Data to forecast
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
    dataset_name str
        The name of the ticker to be predicted
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to MULTIPLICATIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
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
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart

