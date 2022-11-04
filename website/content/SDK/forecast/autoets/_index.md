To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forecast.autoets(data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame], target_column: str = 'close', seasonal_periods: int = 7, n_predict: int = 5, start_window: float = 0.85, forecast_horizon: int = 5) -> Tuple[list[numpy.ndarray], List[numpy.ndarray], List[numpy.ndarray], Optional[float], Any]

Performs Automatic ETS forecasting
    This is a wrapper around StatsForecast ETS;
    we refer to this link for the original and more complete documentation of the parameters.


        https://nixtla.github.io/statsforecast/models.html#ets

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
    seasonal_periods: int
        Number of seasonal periods in a year (7 for daily data)
        If not set, inferred from frequency of the series.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical

    Returns
    -------
    list[float]
        Adjusted Data series
    list[float]
        List of historical fcast values
    list[float]
        List of predicted fcast values
    Optional[float]
        precision
    Any
        Fit ETS model object.

## Getting charts 
### forecast.autoets(data: Union[pandas.core.frame.DataFrame, pandas.core.series.Series], target_column: str = 'close', dataset_name: str = '', seasonal_periods: int = 7, n_predict: int = 5, start_window: float = 0.85, forecast_horizon: int = 5, export: str = '', residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None, chart=True)

Display Automatic ETS (Error, Trend, Sesonality) Model

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    dataset_name str
        The name of the ticker to be predicted
    target_column (str, optional):
        Target column to forecast. Defaults to "close".
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
