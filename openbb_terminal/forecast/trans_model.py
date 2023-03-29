# pylint: disable=too-many-arguments
"""Transformer Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.models import TransformerModel

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_trans_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    n_predict: int = 5,
    train_split: float = 0.85,
    past_covariates: Optional[str] = None,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    d_model: int = 64,
    nhead: int = 4,
    num_encoder_layers: int = 3,
    num_decoder_layers: int = 3,
    dim_feedforward: int = 512,
    activation: str = "relu",
    dropout: float = 0.0,
    batch_size: int = 32,
    n_epochs: int = 300,
    learning_rate: float = 1e-3,
    model_save_name: str = "trans_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    metric: str = "mape",
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[type[TransformerModel]],
]:
    """Performs Transformer forecasting

    Parameters
    ----------
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
    metric: str
        Metric to use for model selection. Defaults to "mape".

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[TransformerModel]]
        Adjusted Data series,
        Historical forecast by best RNN model,
        list of Predictions,
        Mean average precision error,
        Best transformer Model.
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

    current_user = get_current_user()

    trans_model = TransformerModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        d_model=d_model,
        nhead=nhead,
        num_encoder_layers=num_encoder_layers,
        num_decoder_layers=num_decoder_layers,
        dim_feedforward=dim_feedforward,
        activation=activation,
        dropout=dropout,
        batch_size=batch_size,
        n_epochs=n_epochs,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        random_state=42,
        pl_trainer_kwargs=helpers.get_pl_kwargs(accelerator="cpu"),
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        log_tensorboard=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    # fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        helpers.fit_model(
            trans_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )
    best_model = TransformerModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    helpers.print_tensorboard_logs(
        model_save_name, str(current_user.preferences.USER_FORECAST_MODELS_DIRECTORY)
    )

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "Transformer",
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
