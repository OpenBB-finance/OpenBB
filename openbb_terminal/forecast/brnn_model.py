# pylint: disable=too-many-arguments
"""RNN Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.models import BlockRNNModel
from darts.models.forecasting.torch_forecasting_model import GlobalForecastingModel
from darts.utils.likelihood_models import GaussianLikelihood

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_brnn_data(
    data: Union[pd.Series, pd.DataFrame],
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
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[type[GlobalForecastingModel]],
]:
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
    Tuple[
        List[TimeSeries],
        List[TimeSeries],
        List[TimeSeries],
        Optional[Union[float, ndarray]],
        type[GlobalForecastingModel]
    ]
        Adjusted Data series,
        Historical forecast by best RNN model,
        list of Predictions,
        Mean average precision error,
        Best BRNN Model.
    """

    # TODO Check if torch GPU AVAILABLE

    use_scalers = True
    probabilistic = False

    scaler, ticker_series = helpers.get_series(
        data, target_column, is_scaler=use_scalers
    )
    train, val = ticker_series.split_before(train_split)
    valid = helpers.check_data_length(
        train, val, input_chunk_length, output_chunk_length
    )
    if not valid:
        return [], [], [], None, None

    (
        past_covariate_whole,
        past_covariate_train,
        past_covariate_val,
    ) = helpers.past_covs(past_covariates, data, train_split, use_scalers)

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
        pl_trainer_kwargs=helpers.get_pl_kwargs(accelerator="cpu"),
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
        log_tensorboard=True,
        work_dir=get_current_user().preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    # fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        helpers.fit_model(
            brnn_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )
    best_model = BlockRNNModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir=get_current_user().preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    helpers.print_tensorboard_logs(
        model_save_name,
        str(get_current_user().preferences.USER_FORECAST_MODELS_DIRECTORY),
    )

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "Block RNN",
        probabilistic,
        use_scalers,
        scaler,
        past_covariates,
        best_model,
        ticker_series,
        past_covariate_whole,
        train_split,
        forecast_horizon,
        n_predict,
        metric,
    )
