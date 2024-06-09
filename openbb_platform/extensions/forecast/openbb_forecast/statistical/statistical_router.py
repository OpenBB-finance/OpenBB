"""Statistical Router."""

# ruff: noqa: T201
from typing import List

from darts.ad import KMeansScorer, QuantileDetector
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from pydantic import PositiveFloat, PositiveInt
from statsforecast.core import StatsForecast
from statsforecast.models import ETS, AutoARIMA, AutoCES

from openbb_forecast import helpers
from openbb_forecast.models import (
    QuantileAnomalyModel,
    StatisticalForecastModel,
)

router = Router(prefix="/statistical")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Quantile Anomaly Detection on Time Series Data.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "result =  obb.forecast.statistical.quantile_anamoly_detection(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def quantile_anamoly_detection(
    data: List[Data],
    target_column: str = "close",
    train_split: PositiveFloat = 0.6,
) -> OBBject[QuantileAnomalyModel]:
    """Perform Quantile Anomaly Detection on Time Series Data.

    Parameters
    ----------
    data: List[Data]
        A list of data points containing time series information.
    target_column: str, optional
        The name of the column to be used as the target for forecasting. Defaults to "close".
    train_split: PositiveFloat, optional
        The ratio of the data used for training versus validation. Defaults to 0.6.

    Returns
    -------
    OBBject[QuantileAnomalyModel]
        An object containing the results of the quantile anomaly detection.

    Notes
    -----
    This function uses quantile anomaly detection with KMeansScorer and QuantileDetector
    from the darts library.

    The input data is split into training and validation sets based on the specified
    train_split ratio. KMeansScorer is then applied to the training set to score the
    data, and QuantileDetector is used to detect anomalies in the validation set.
    The results are encapsulated in a QuantileAnomalyModel object.
    """
    use_scalers = False
    _, ticker_series = helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )

    # split dataset into train and val
    train, val = ticker_series.split_before(train_split)

    scorer = KMeansScorer(k=2, window=5)
    scorer.fit(train)
    anom_score = scorer.score(val)

    detector = QuantileDetector(high_quantile=0.99)
    detector.fit(scorer.score(train))
    binary_anom = detector.detect(anom_score)

    anom_results = QuantileAnomalyModel(
        ticker_series=helpers.timeseries_to_basemodel(ticker_series),
        anomaly_score=helpers.timeseries_to_basemodel(anom_score),
        binary_anomaly_prediction=helpers.timeseries_to_basemodel(binary_anom),
    )

    return OBBject(results=anom_results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Automatic ARIMA forecasting using the StatsForecast AutoARIMA model.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "output =  obb.forecast.statistical.autoarima(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def autoarima(
    data: List[Data],
    target_column: str = "close",
    seasonal_periods: PositiveInt = 7,
    n_predict: PositiveInt = 5,
    start_window: PositiveFloat = 0.85,
    forecast_horizon: PositiveInt = 5,
) -> OBBject[StatisticalForecastModel]:
    """Perform Automatic ARIMA forecasting using the StatsForecast AutoARIMA model.

    This function serves as a wrapper around StatsForecast's AutoARIMA model for time series forecasting.
    It takes historical data as input, initializes the AutoARIMA model, performs historical backtesting,
    and generates future forecasts.

    Parameters
    ----------
    data : List[Data]
        Input data in the form of a list of Data objects.
    target_column: str, optional
        The target column in the dataset to forecast. Defaults to "close".
    seasonal_periods: PositiveInt, optional
        Number of seasonal periods in a year (e.g., 7 for daily data). If not set, it is inferred from the frequency of the series.
    n_predict: PositiveInt, optional
        Number of days to forecast into the future.
    start_window: float, optional
        Size of the sliding window from the start of the time series and onwards.
    forecast_horizon: PositiveInt, optional
        Number of days to forecast when backtesting and retraining historical data.

    Returns
    -------
    OBBject[StatisticalForecastModel]
        An object containing the results of the AutoARIMA forecasting:
        - Adjusted Data series,
        - List of historical forecast values,
        - List of predicted forecast values,
        - Optional precision (float),
        - Fitted AutoARIMA model object (StatsForecast).

    Notes
    -----
    For more detailed information on the parameters and usage of StatsForecast AutoARIMA,
    refer to the official documentation: https://nixtla.github.io/statsforecast/models.html#autoarima
    """  # noqa: E501
    use_scalers = False
    # statsforecast preprocessing when including more time series
    # the preprocessing is similar
    _, ticker_series = helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )
    freq = ticker_series.freq_str
    ticker_series = ticker_series.pd_dataframe().reset_index()
    ticker_series.columns = ["ds", "y"]
    ticker_series.insert(0, "unique_id", target_column)

    try:
        # Model Init
        model = AutoARIMA(season_length=PositiveInt(seasonal_periods))
        fcst = StatsForecast(df=ticker_series, models=[model], freq=freq, verbose=True)
    except Exception as e:  # noqa
        error = str(e)
        if "got an unexpected keyword argument" in error:
            print("Please update statsforecast to version 1.1.3 or higher.")
        else:
            print(f"{error}")
        return OBBject(results={})

    # Historical backtesting
    last_training_point = PositiveInt((len(ticker_series) - 1) * start_window)
    historical_fcast = fcst.cross_validation(
        h=PositiveInt(forecast_horizon),
        test_size=len(ticker_series) - last_training_point,
        n_windows=None,
        input_size=min(10 * forecast_horizon, len(ticker_series)),
    )

    # Train new model on entire timeseries to provide best current forecast
    # we have the historical fcast, now lets predict.
    forecast = fcst.forecast(PositiveInt(n_predict))
    y_true = historical_fcast["y"].values
    y_hat = historical_fcast["AutoARIMA"].values
    precision = helpers.mean_absolute_percentage_error(y_true, y_hat)
    print(f"AutoARIMA obtains MAPE: {precision:.2f}% \n")

    # Transform outputs to make them compatible with plots
    use_scalers = False
    _, ticker_series = helpers.convert_to_timeseries(
        ticker_series.rename(columns={"y": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, forecast = helpers.convert_to_timeseries(
        forecast.rename(columns={"AutoARIMA": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, historical_fcast = helpers.convert_to_timeseries(
        historical_fcast.groupby("ds")
        .head(1)
        .rename(columns={"AutoARIMA": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )

    results = StatisticalForecastModel(
        ticker_series=helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=helpers.timeseries_to_basemodel(historical_fcast),
        forecast=helpers.timeseries_to_basemodel(forecast),
        precision=precision,
        forecast_model=fcst,
    )

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Automatic Complex Exponential Smoothing forecasting.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "output =  obb.forecast.statistical.autoces(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def autoces(
    data: List[Data],
    target_column: str = "close",
    seasonal_periods: PositiveInt = 7,
    n_predict: PositiveInt = 5,
    start_window: PositiveFloat = 0.85,
    forecast_horizon: PositiveInt = 5,
) -> OBBject[StatisticalForecastModel]:
    """Perform Automatic Complex Exponential Smoothing forecasting.

    This is a wrapper around StatsForecast AutoCES.

    Parameters
    ----------
    data : List[Data]
        Input data in the form of a list of Data objects.
    target_column: str, optional
        The target column in the dataset to forecast. Defaults to "close".
    seasonal_periods: PositiveInt, optional
        Number of seasonal periods in a year (e.g., 7 for daily data).
        If not set, it is inferred from the frequency of the series.
    n_predict: PositiveInt, optional
        Number of days to forecast into the future.
    start_window: float, optional
        Size of the sliding window from the start of the time series and onwards.
    forecast_horizon: PositiveInt, optional
        Number of days to forecast when backtesting and retraining historical data.

    Returns
    -------
    OBBject[StatisticalForecastModel]
        Object containing the results of the forecasting process, including:
            - Adjusted Data series,
            - List of historical forecast values,
            - List of predicted forecast values,
            - Optional float - precision,
            - Fit CES model object.

    Notes
    -----
    For more detailed information on the parameters and usage of StatsForecast AutoCES,
    refer to the official documentation: https://nixtla.github.io/statsforecast/models.html#autoces
    """
    use_scalers = False
    # statsforecast preprocessing
    # when including more time series
    # the preprocessing is similar
    _, ticker_series = helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )
    freq = ticker_series.freq_str
    ticker_series = ticker_series.pd_dataframe().reset_index()
    ticker_series.columns = ["ds", "y"]
    ticker_series.insert(0, "unique_id", target_column)

    try:
        # Model Init
        model = AutoCES(
            season_length=PositiveInt(seasonal_periods),
        )
        fcst = StatsForecast(df=ticker_series, models=[model], freq=freq, verbose=True)
    except Exception as e:  # noqa
        error = str(e)
        if "got an unexpected keyword argument" in error:
            print("Please update statsforecast to version 1.1.3 or higher.")
        else:
            print(f"{error}")
        return OBBject(results={})

    # Historical backtesting
    last_training_point = PositiveInt((len(ticker_series) - 1) * start_window)
    historical_fcast = fcst.cross_validation(
        h=PositiveInt(forecast_horizon),
        test_size=len(ticker_series) - last_training_point,
        n_windows=None,
        input_size=min(10 * forecast_horizon, len(ticker_series)),
    )

    # train new model on entire timeseries to provide best current forecast
    # we have the historical fcast, now lets predict.
    forecast = fcst.forecast(PositiveInt(n_predict))
    y_true = historical_fcast["y"].values
    y_hat = historical_fcast["CES"].values
    precision = helpers.mean_absolute_percentage_error(y_true, y_hat)
    print(f"AutoCES obtains MAPE: {precision:.2f}% \n")

    # transform outputs to make them compatible with
    # plots
    use_scalers = False
    _, ticker_series = helpers.convert_to_timeseries(
        ticker_series.rename(columns={"y": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, forecast = helpers.convert_to_timeseries(
        forecast.rename(columns={"CES": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, historical_fcast = helpers.convert_to_timeseries(
        historical_fcast.groupby("ds").head(1).rename(columns={"CES": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )

    results = StatisticalForecastModel(
        ticker_series=helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=helpers.timeseries_to_basemodel(historical_fcast),
        forecast=helpers.timeseries_to_basemodel(forecast),
        precision=precision,
        forecast_model=fcst,
    )

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Automatic ETS forecasting.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "output =  obb.forecast.statistical.autoets(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def autoets(
    data: List[Data],
    target_column: str = "close",
    seasonal_periods: PositiveInt = 7,
    n_predict: PositiveInt = 5,
    start_window: PositiveFloat = 0.85,
    forecast_horizon: PositiveInt = 5,
) -> OBBject[StatisticalForecastModel]:
    """Perform Automatic ETS forecasting.

    This is a wrapper around StatsForecast ETS.

    Parameters
    ----------
    data : List[Data]
        Input data in the form of a list of Data objects.
    target_column: str, optional
        The target column in the dataset to forecast. Defaults to "close".
    seasonal_periods: PositiveInt, optional
        Number of seasonal periods in a year (e.g., 7 for daily data). If not set, it is inferred from the frequency of the series.
    n_predict: PositiveInt, optional
        Number of days to forecast into the future.
    start_window: float, optional
        Size of the sliding window from the start of the time series and onwards.
    forecast_horizon: PositiveInt, optional
        Number of days to forecast when backtesting and retraining historical data.

    Returns
    -------
    OBBject[StatisticalForecastModel]
        Object containing the results of the forecasting process, including:
            - Adjusted Data series,
            - List of historical forecast values,
            - List of predicted forecast values,
            - Optional float - precision,
            - Fit ETS model object.

    Notes
    -----
    For more detailed information on the parameters and usage of StatsForecast AutoCES,
    refer to the official documentation: https://nixtla.github.io/statsforecast/models.html#autoets
    """  # noqa: E501
    use_scalers = False
    # statsforecast preprocessing when including more time series the preprocessing is similar
    _, ticker_series = helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )
    freq = ticker_series.freq_str
    ticker_series = ticker_series.pd_dataframe().reset_index()
    ticker_series.columns = ["ds", "y"]
    ticker_series.insert(0, "unique_id", target_column)

    try:
        # Model Init
        model_ets = ETS(
            season_length=PositiveInt(seasonal_periods),
        )
        fcst = StatsForecast(
            df=ticker_series, models=[model_ets], freq=freq, verbose=True
        )
    except Exception as e:  # noqa
        error = str(e)
        if "got an unexpected keyword argument" in error:
            print("Please update statsforecast to version 1.1.3 or higher.")
        else:
            print(f"{error}")
        return OBBject(results={})

    # Historical backtesting
    last_training_point = PositiveInt((len(ticker_series) - 1) * start_window)
    historical_fcast_ets = fcst.cross_validation(
        h=PositiveInt(forecast_horizon),
        test_size=len(ticker_series) - last_training_point,
        n_windows=None,
        input_size=min(10 * forecast_horizon, len(ticker_series)),
    )

    # Train new model on entire timeseries to provide best current forecast
    # we have the historical fcast, now lets predict.
    forecast = fcst.forecast(PositiveInt(n_predict))
    y_true = historical_fcast_ets["y"].values
    y_hat = historical_fcast_ets["ETS"].values
    precision = helpers.mean_absolute_percentage_error(y_true, y_hat)
    print(f"AutoETS obtains MAPE: {precision:.2f}% \n")

    # Transform outputs to make them compatible with plots
    use_scalers = False
    _, ticker_series = helpers.convert_to_timeseries(
        ticker_series.rename(columns={"y": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, forecast = helpers.convert_to_timeseries(
        forecast.rename(columns={"ETS": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, historical_fcast_ets = helpers.convert_to_timeseries(
        historical_fcast_ets.groupby("ds")
        .head(1)
        .rename(columns={"ETS": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )

    results = StatisticalForecastModel(
        ticker_series=helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=helpers.timeseries_to_basemodel(historical_fcast_ets),
        forecast=helpers.timeseries_to_basemodel(forecast),
        precision=precision,
        forecast_model=fcst,
    )

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform MSTL forecasting.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "output =  obb.forecast.statistical.mstl(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def mstl(
    data: List[Data],
    target_column: str = "close",
    seasonal_periods: PositiveInt = 7,
    n_predict: PositiveInt = 5,
    start_window: PositiveFloat = 0.85,
    forecast_horizon: PositiveInt = 5,
) -> OBBject[StatisticalForecastModel]:
    """Perform MSTL forecasting.

    This is a wrapper around StatsForecast MSTL.

    Parameters
    ----------
    data : List[Data]
        Input data in the form of a list of Data objects.
    target_column: str, optional
        The target column in the dataset to forecast. Defaults to "close".
    seasonal_periods: PositiveInt, optional
        Number of seasonal periods in a year (e.g., 7 for daily data). If not set, it is inferred from the frequency of the series.
    n_predict: PositiveInt, optional
        Number of days to forecast into the future.
    start_window: float, optional
        Size of the sliding window from the start of the time series and onwards.
    forecast_horizon: PositiveInt, optional
        Number of days to forecast when backtesting and retraining historical data.

    Returns
    -------
    OBBject[StatisticalForecastModel]
        Object containing the results of the forecasting process, including:
            - Adjusted Data series,
            - List of historical forecast values,
            - List of predicted forecast values,
            - Optional float - precision,
            - Fit MSTL model object.

    Notes
    -----
    For more detailed information on the parameters and usage of StatsForecast MSTL,
    refer to the official documentation: https://nixtla.github.io/statsforecast/models.html#mstl
    """  # noqa: E501
    use_scalers = False
    # statsforecast preprocessing
    # when including more time series
    # the preprocessing is similar
    _, ticker_series = helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )

    freq = ticker_series.freq_str
    ticker_series = ticker_series.pd_dataframe().reset_index()
    ticker_series.columns = ["ds", "y"]
    ticker_series.insert(0, "unique_id", target_column)

    # Check MSLT availability
    try:
        from statsforecast.models import MSTL  # pylint: disable=import-outside-toplevel
    except Exception as e:
        error = str(e)
        if "cannot import name" in error:
            print("Please update statsforecast to version 1.2.0 or higher.")
        else:
            print(f"{error}")
        return OBBject(results={})

    try:
        # Model Init
        model = MSTL(
            season_length=PositiveInt(seasonal_periods),
        )
        fcst = StatsForecast(df=ticker_series, models=[model], freq=freq, verbose=True)
    except Exception as e:  # noqa
        error = str(e)
        if "got an unexpected keyword argument" in error:
            print("Please update statsforecast to version 1.1.3 or higher.")
        else:
            print(f"{error}")
        return OBBject(results={})

    # Historical backtesting
    last_training_point = PositiveInt((len(ticker_series) - 1) * start_window)
    historical_fcast = fcst.cross_validation(
        h=PositiveInt(forecast_horizon),
        test_size=len(ticker_series) - last_training_point,
        n_windows=None,
        input_size=min(10 * forecast_horizon, len(ticker_series)),
    )

    # train new model on entire timeseries to provide best current forecast
    # we have the historical fcast, now lets predict.
    forecast = fcst.forecast(PositiveInt(n_predict))
    y_true = historical_fcast["y"].values
    y_hat = historical_fcast["MSTL"].values
    precision = helpers.mean_absolute_percentage_error(y_true, y_hat)

    # transform outputs to make them compatible with
    # plots
    use_scalers = False
    _, ticker_series = helpers.convert_to_timeseries(
        ticker_series.rename(columns={"y": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, forecast = helpers.convert_to_timeseries(
        forecast.rename(columns={"MSTL": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, historical_fcast = helpers.convert_to_timeseries(
        historical_fcast.groupby("ds").head(1).rename(columns={"MSTL": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )

    results = StatisticalForecastModel(
        ticker_series=helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=helpers.timeseries_to_basemodel(historical_fcast),
        forecast=helpers.timeseries_to_basemodel(forecast),
        precision=precision,
        forecast_model=fcst,
    )

    return OBBject(results=results)
