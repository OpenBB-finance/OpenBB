# pylint: disable=too-many-arguments
"""Nhits Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.models.forecasting.nhits import NHiTSModel
from darts.utils.likelihood_models import GaussianLikelihood

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_nhits_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    n_predict: int = 5,
    train_split: float = 0.85,
    past_covariates: Optional[str] = None,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    num_stacks: int = 3,
    num_blocks: int = 1,
    num_layers: int = 2,
    layer_widths: int = 512,
    pooling_kernel_sizes: Optional[Tuple[Tuple[int]]] = None,
    n_freq_downsample: Optional[Tuple[Tuple[int]]] = None,
    dropout: float = 0.1,
    activation: str = "ReLU",
    max_pool_1d: bool = True,
    batch_size: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    model_save_name: str = "nhits_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    metric: str = "mape",
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[type[NHiTSModel]],
]:
    """Performs Nhits forecasting

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
        The number of stacks that make up the whole model.
    num_blocks: int
        The number of blocks making up every stack.
    num_layers: int
        The number of fully connected layers preceding the final forking layers in each block
        of every stack.
    layer_widths: int
        Determines the number of neurons that make up each fully connected layer in each
        block of every stack. If a list is passed, it must have a length equal to num_stacks
        and every entry in that list corresponds to the layer width of the corresponding stack.
        If an integer is passed, every stack will have blocks with FC layers of the same width.
    pooling_kernel_size: Optional[Tuple[Tuple[int]]]:
        If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),
        specifying the kernel size for each block in each stack used for the input pooling
        layer. If left to None, some default values will be used based on input_chunk_length.
    n_freq_downsample: Optional[Tuple[Tuple[int]]]
        If set, this parameter must be a tuple of tuples, of size (num_stacks x num_blocks),
        specifying the downsampling factors before interpolation, for each block in each stack.
        If left to None, some default values will be used based on output_chunk_length.
    dropout: float
            The dropout probability to be used in fully connected layers.
    activation: str
        Supported activations: [‘ReLU’,’RReLU’, ‘PReLU’, ‘Softplus’, ‘Tanh’, ‘SELU’, ‘LeakyReLU’, ‘Sigmoid’]
    max_pool_1d: bool
        Use max_pool_1d pooling. False uses AvgPool1d.
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
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[NHiTSModel]]
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

    current_user = get_current_user()

    nhits_model = NHiTSModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        num_stacks=num_stacks,
        num_blocks=num_blocks,
        num_layers=num_layers,
        layer_widths=layer_widths,
        pooling_kernel_sizes=pooling_kernel_sizes,
        n_freq_downsample=n_freq_downsample,
        dropout=dropout,
        activation=activation,
        MaxPool1d=max_pool_1d,
        n_epochs=n_epochs,
        batch_size=batch_size,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        random_state=42,
        pl_trainer_kwargs=helpers.get_pl_kwargs(accelerator="cpu"),
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
        log_tensorboard=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    # fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        helpers.fit_model(
            nhits_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )
    best_model = NHiTSModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    helpers.print_tensorboard_logs(
        model_save_name, str(current_user.preferences.USER_FORECAST_MODELS_DIRECTORY)
    )

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "NHITS",
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
