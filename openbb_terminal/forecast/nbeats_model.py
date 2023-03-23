# pylint: disable=too-many-arguments
"""NBEATS Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.models import NBEATSModel

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_NBEATS_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    num_stacks: int = 10,
    num_blocks: int = 3,
    num_layers: int = 4,
    layer_widths: int = 512,
    batch_size: int = 800,
    n_epochs: int = 300,
    learning_rate: float = 1e-3,
    model_save_name: str = "nbeats_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    metric: str = "mape",
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[type[NBEATSModel]],
]:
    """Perform NBEATS Forecasting

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
    num_stacks: int
        The number of stacks that make up the whole model. Defaults to 10.
    num_blocks: int
        The number of blocks making up every stack. Defaults to 3.
    num_layers: int
        The number of fully connected layers preceding the final forking layers in each block
        of every stack. Defaults to 4.
    layer_widths: int
        Determines the number of neurons that make up each fully connected layer in each block
        of every stack. Defaults to 512.
    batch_size: int
        Number of time series (input and output sequences) used in each training pass. Defaults to 32.
    n_epochs: int
        Number of epochs over which to train the model. Defaults to 100.
    learning_rate: float
        Defaults to 1e-3.
    model_save_name: str
        Name for model. Defaults to "brnn_model".
    force_reset: bool
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints: bool
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    metric: str
        Metric to use for model selection. Defaults to "mape".

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[NBEATSModel]]
        Adjusted Data series,
        Historical forecast by best RNN model,
        list of Predictions,
        Mean average precision error,
        Best NBEATS Model.
    """

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

    current_user = get_current_user()

    nbeats_model = NBEATSModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        generic_architecture=True,
        num_stacks=num_stacks,
        num_blocks=num_blocks,
        num_layers=num_layers,
        layer_widths=layer_widths,
        n_epochs=n_epochs,
        nr_epochs_val_period=1,
        batch_size=batch_size,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        random_state=42,
        pl_trainer_kwargs=helpers.get_pl_kwargs(accelerator="cpu"),
        log_tensorboard=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    # fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        helpers.fit_model(
            nbeats_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )

    best_model = NBEATSModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    helpers.print_tensorboard_logs(
        model_save_name, str(current_user.preferences.USER_FORECAST_MODELS_DIRECTORY)
    )

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "NBEATS",
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
