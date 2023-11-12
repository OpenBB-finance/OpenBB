from typing import Optional, List
import warnings

import pandas as pd

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router

from openbb_provider.abstract.data import Data

from openbb_forecast import forecast_helpers
from openbb_forecast.forecast_models import TorchForecastModel

router = Router(prefix="/torch")


@router.command(methods=["POST"])
def brnn(
    data: List[Data],
    target_column: str = "close",
    n_predict: int = 5,
    train_split: float = 0.85,
    past_covariates: Optional[str] = None,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    model_type: str = "LSTM",
    n_rnn_layers: int = 1,
    dropout: float = 0.0,
    batch_size: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    model_save_name: str = "brnn_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    metric: str = "mape",
) -> OBBject[TorchForecastModel]:
    """Performs Block RNN forecasting

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
    input_chunk_length: int
        Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 5.
    model_type: str
        Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
    n_rnn_layers: int
            Number of layers in the RNN module. Defaults to 1.
    dropout: float
        Fraction of neurons affected by Dropout. Defaults to 0.0.
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
    metric: str
        Metric to use for model selection. Defaults to "mape".

    Returns
    -------
    OBBject[StatisticalForecastModel]
        A wrapper object containing the following:
        - Adjusted Data series,
        - List of historical forecast values,
        - List of predicted forecast values,
        - Precision (float),
        - Block RNN model object.
    """

    from darts.models import BlockRNNModel
    from darts.utils.likelihood_models import GaussianLikelihood

    # TODO Check if torch GPU AVAILABLE
    # TODO replace working directory

    use_scalers = True
    probabilistic = False

    scaler, ticker_series = forecast_helpers.convert_to_timeseries(
        data, target_column, is_scaler=use_scalers
    )
    train, val = ticker_series.split_before(train_split)
    valid = forecast_helpers.check_data_length(
        train, val, input_chunk_length, output_chunk_length
    )
    if not valid:
        return [], [], [], None, None

    (
        past_covariate_whole,
        past_covariate_train,
        past_covariate_val,
    ) = forecast_helpers.past_covs(past_covariates, data, train_split, use_scalers)

    # Early Stopping
    brnn_model = BlockRNNModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        model=model_type,
        n_rnn_layers=n_rnn_layers,
        dropout=dropout,
        batch_size=batch_size,
        n_epochs=n_epochs,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        random_state=42,
        pl_trainer_kwargs=forecast_helpers.get_pl_kwargs(accelerator="cpu"),
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
        log_tensorboard=True,
        work_dir='./',
    )

    # Fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        forecast_helpers.fit_model(
            brnn_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )
    brnn_model = BlockRNNModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir='./',
    )

    # Logging
    forecast_helpers.print_tensorboard_logs(
        model_save_name,
        './',
    )

    # Showing historical backtesting without retraining model (too slow)
    (
        ticker_series,
        historical_fcast,
        prediction,
        brnn_model,
    ) = forecast_helpers.model_prediction(
        "Block RNN",
        probabilistic,
        use_scalers,
        scaler,
        past_covariates,
        brnn_model,
        ticker_series,
        past_covariate_whole,
        train_split,
        forecast_horizon,
        n_predict,
    )

    # Metric (precision) using validation set
    precision = forecast_helpers.calculate_precision(
        metric, ticker_series, historical_fcast
    )

    results = TorchForecastModel(
        ticker_series=forecast_helpers.timeseries_to_basemodel(ticker_series),
        historical_forecast=forecast_helpers.timeseries_to_basemodel(historical_fcast),
        forecast=forecast_helpers.timeseries_to_basemodel(prediction),
        precision=float(precision),
        forecast_model=brnn_model,
    )

    return OBBject(results=results)
