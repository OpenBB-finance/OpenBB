# pylint: disable=too-many-arguments
import warnings
from typing import List, Optional, Union

from darts.models import LinearRegressionModel, ExponentialSmoothing
from darts.utils.utils import ModelMode, SeasonalityMode


from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router

from openbb_provider.abstract.data import Data

from openbb_forecast import forecast_helpers
from openbb_forecast.forecast_models import (
    StatisticalForecastModel,
)

from pydantic import PositiveFloat


router = Router(prefix="/regression")


@router.command(methods=["POST"])
def linear_regression(
    data: List[Data],
    target_column: str = "close",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: PositiveFloat = 0.85,
    forecast_horizon: int = 5,
    output_chunk_length: int = 5,
    lags: Union[int, List[int]] = 14,
    random_state: Optional[int] = None,
    metric: str = "mape",
    model_name: str = "Logistic Regression",
) -> OBBject[StatisticalForecastModel]:
    """Perform Linear Regression Forecasting

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]
        Input Data
    target_column: str
        Target column to forecast. Defaults to "close".
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
    random_state: Optional[int]
        The state for the model
    metric: str
        The metric to use for the model. Defaults to "mape".

    Returns
    -------
    OBBject[StatisticalForecastModel]
        Object containing the following components:
            - Adjusted Data series,
            - Historical forecast by the best Linear Regression model,
            - List of Predictions,
            - Mean average precision error (float),
            - Best Linear Regression Model.
    """
    use_scalers = False
    probabilistic = True

    # Ticker series and past covariance
    scaler, ticker_series = forecast_helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )
    past_covariate_whole, _, _ = forecast_helpers.past_covs(
        past_covariates, data, train_split, use_scalers
    )

    lags_past_covariates = lags if past_covariates is not None else None

    # Linear regression model
    lin_reg_model = LinearRegressionModel(
        output_chunk_length=output_chunk_length,
        lags=lags,
        lags_past_covariates=lags_past_covariates,
        likelihood="quantile",
        quantiles=[0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95],
        random_state=random_state,
    )

    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        if past_covariates is not None:
            lin_reg_model.fit(
                series=ticker_series, past_covariates=past_covariate_whole
            )
        else:
            lin_reg_model.fit(series=ticker_series)

    # Perform prediction
    (
        ticker_series,
        historical_fcast,
        prediction,
        lin_reg_model,
    ) = forecast_helpers.model_prediction(
        model_name,
        probabilistic,
        use_scalers,
        scaler,
        past_covariates,
        lin_reg_model,
        ticker_series,
        past_covariate_whole,
        train_split,
        forecast_horizon,
        n_predict,
    )

    # Metric (precision) using validation set
    _, val = ticker_series.split_before(train_split)
    precision = forecast_helpers.calculate_precision(metric, val, historical_fcast)

    # Final results
    results = StatisticalForecastModel(
        ticker_series=forecast_helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=forecast_helpers.timeseries_to_basemodel(historical_fcast),
        forecast=forecast_helpers.timeseries_to_basemodel(prediction),
        precision=precision,
        forecast_model=lin_reg_model,
    )

    return OBBject(results=results)


@router.command(methods=["POST"])
def exponential_smoothing(
    data: List[Data],
    target_column: str = "close",
    trend: str = "A",
    seasonal: str = "A",
    seasonal_periods: int = 7,
    dampen: str = "F",
    n_predict: int = 5,
    start_window: PositiveFloat = 0.85,
    forecast_horizon: int = 5,
    metric: str = "mape",
) -> OBBject[StatisticalForecastModel]:
    """Performs Probabilistic Exponential Smoothing forecasting

    This is a wrapper around statsmodels Holt-Winters' Exponential Smoothing;
    we refer to this link for the original and more complete documentation of the parameters.
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    trend: str
        Trend component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal_periods: int
        Number of seasonal periods in a year (7 for daily data)
        If not set, inferred from frequency of the series.
    dampen: str
        Dampen the function
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
    metric: str
        Metric to use for backtesting. Defaults to MAPE.

    Returns
    -------
    OBBject[StatisticalForecastModel]
        A wrapper object containing the following:
        - Adjusted Data series,
        - List of historical forecast values,
        - List of predicted forecast values,
        - Precision (float),
        - Fit Probabilistic Exponential Smoothing model object.

    Notes
    -----
    For more detailed information on the parameters and usage of Probabilistic Exponential Smoothing,
    refer to the official documentation: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html
    """

    use_scalers = False

    _, ticker_series = forecast_helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )

    if trend == "M":
        trend_model = ModelMode.MULTIPLICATIVE
    elif trend == "N":
        trend_model = ModelMode.NONE
    else:  # Default
        trend_model = ModelMode.ADDITIVE

    if seasonal == "M":
        seasonal_model = SeasonalityMode.MULTIPLICATIVE
    elif seasonal == "N":
        seasonal_model = SeasonalityMode.NONE
    else:  # Default
        seasonal_model = SeasonalityMode.ADDITIVE

    damped = True
    if dampen == "F":
        damped = False

    # Model init
    model_es = ExponentialSmoothing(
        trend=trend_model,
        seasonal=seasonal_model,
        seasonal_periods=int(seasonal_periods),
        damped=damped,
        random_state=42,
    )

    try:
        # Historical backtesting
        historical_fcast_es = model_es.historical_forecasts(
            ticker_series,  # backtest on entire ts
            start=float(start_window),
            forecast_horizon=int(forecast_horizon),
            verbose=True,
        )
    except Exception as e:  # noqa
        error = str(e)
        # lets translate this to something everyone understands
        if "with`overlap_end` set to `False`." in error:
            print(
                "Dataset too small."
                " Please increase size to at least 100 data points."
            )
        else:
            print(f"{error}")
        return [], [], [], None, None

    # Train new model on entire timeseries to provide best current forecast
    es_model = ExponentialSmoothing(
        trend=trend_model,
        seasonal=seasonal_model,
        seasonal_periods=int(seasonal_periods),
        damped=damped,
        random_state=42,
    )

    # We have the historical fcast, now lets train on entire set and predict.
    es_model.fit(ticker_series)
    probabilistic_forecast = es_model.predict(int(n_predict), num_samples=500)

    # Metric (precision) using validation set
    precision = forecast_helpers.calculate_precision(
        metric, ticker_series, historical_fcast_es
    )

    # Final results
    results = StatisticalForecastModel(
        ticker_series=forecast_helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=forecast_helpers.timeseries_to_basemodel(
            historical_fcast_es
        ),
        forecast=forecast_helpers.timeseries_to_basemodel(probabilistic_forecast),
        precision=precision,
        forecast_model=es_model,
    )

    return OBBject(results=results)
