# pylint: disable=too-many-arguments
"""Temporal Fusion Transformer Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.models import TFTModel
from darts.utils.likelihood_models import QuantileRegression
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

warnings.simplefilter("ignore", ConvergenceWarning)


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_tft_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    hidden_size: int = 16,
    lstm_layers: int = 1,
    num_attention_heads: int = 4,
    full_attention: bool = False,
    dropout: float = 0.1,
    hidden_continuous_size: int = 8,
    n_epochs: int = 200,
    batch_size: int = 32,
    model_save_name: str = "tft_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    metric: str = "mape",
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[type[TFTModel]],
]:
    """Performs Temporal Fusion Transformer forecasting
    The TFT applies multi-head attention queries on future inputs from mandatory future_covariates.
    Specifying future encoders with add_encoders (read below) can automatically generate future
    covariates and allows to use the model without having to pass any future_covariates to fit()
    and predict().

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html

    Parameters
    ----------
    data (Union[pd.Series, pd.DataFrame]):
        Input Data
    target_column: Optional[str]
        Target column to forecast. Defaults to "close".
    n_predict: (int, optional)
        Days to predict. Defaults to 5.
    train_split: (float, optional)
        Train/val split. Defaults to 0.85.
    past_covariates: (str, optional)
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: (int, optional)
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length: (int, optional)
        Number of past time steps that are fed to the forecasting module at prediction time.
        Defaults to 14.
    output_chunk_length: (int, optional)
        The length of the forecast of the model. Defaults to 5.
    hidden_size: (int, optional)
        Hidden state size of the TFT. Defaults to 16.
    lstm_layers: (int, optional)
        Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16.
    num_attention_headers: (int, optional)
        Number of attention heads. Defaults to 4.
    full_attention: (bool, optional)
        Whether to apply a multi-head attention query. Defaults to False>
    dropout: (float, optional)
        Fraction of neurons affected by dropout. Defaults to 0.1.
    hidden_continuous_size: (int, optional)
        Default hidden size for processing continuous variables. Defaults to 8.
    n_epochs: (int, optional)
        Number of epochs to run during training. Defaults to 200.
    batch_size: (int, optional)
        Number of samples to pass through network during a single epoch. Defaults to 32.
    model_save_name: (str, optional)
        The name for the model. Defaults to tft_model
    force_reset: (bool, optional)
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints: (bool, optional)
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    metric: (str, optional)
        Metric to use for model selection. Defaults to "mape".

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[float], type[TFTModel]]:
        Adjusted Data series,
        List of historical fcast values,
        List of predicted fcast values,
        Optional[float] - precision,
        Fit Prob. TFT model object.
    """

    use_scalers = True
    probabilistic = True

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

    quantiles = [
        0.01,
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
        0.99,
    ]

    current_user = get_current_user()

    tft_model = TFTModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        hidden_size=hidden_size,
        lstm_layers=lstm_layers,
        num_attention_heads=num_attention_heads,
        full_attention=full_attention,
        dropout=dropout,
        hidden_continuous_size=hidden_continuous_size,
        model_name=model_save_name,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        random_state=42,
        n_epochs=n_epochs,
        batch_size=batch_size,
        pl_trainer_kwargs=helpers.get_pl_kwargs(accelerator="cpu"),
        likelihood=QuantileRegression(
            quantiles=quantiles
        ),  # QuantileRegression is set per default
        add_relative_index=True,  # TODO There is a bug with this. Must fix. Should be false
        log_tensorboard=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    # fit model on train series for historical forecasting
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        helpers.fit_model(
            tft_model,
            train,
            val,
            past_covariate_train,
            past_covariate_val,
        )
    best_model = TFTModel.load_from_checkpoint(
        model_name=model_save_name,
        best=True,
        work_dir=current_user.preferences.USER_FORECAST_MODELS_DIRECTORY,
    )

    helpers.print_tensorboard_logs(
        model_save_name, str(current_user.preferences.USER_FORECAST_MODELS_DIRECTORY)
    )

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "TFT",
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
