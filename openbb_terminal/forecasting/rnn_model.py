"""RNN Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


# import torch
# import torch.nn as nn
# import torch.optim as optim
import numpy as np
import pandas as pd

from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.metrics import mape
from pytorch_lightning.callbacks.early_stopping import EarlyStopping

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rnn_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int = 5,
    target_col: str = "close",
    start_window: float = 0.85,
    forecast_horizon: int = 3,
) -> Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, Any]:

    """Performs Recurrent Neural Network Forcasting forecasting

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical

    Returns
    -------
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
    """
    filler = MissingValuesFiller()
    scaler = Scaler()

    # TODO add proper doc string
    # TODO Check if torch GPU AVAILABLE
    # TODO add in covariates
    # todo add in all possible parameters for training

    scaled_ticker_series = scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                data,
                time_col="date",
                value_cols=[target_col],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_train, scaled_val = scaled_ticker_series.split_before(float(start_window))

    # Early Stopping
    my_stopper = EarlyStopping(
        monitor="val_loss",
        patience=5,
        min_delta=0,
        mode="min",
    )
    pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}

    rnn_model = RNNModel(
        model="LSTM",
        hidden_dim=20,
        dropout=0,
        batch_size=16,
        n_epochs=50,
        optimizer_kwargs={"lr": 1e-3},
        model_name="rnn_model",
        log_tensorboard=True,  # TODO Not sure..
        random_state=42,
        training_length=20,
        input_chunk_length=14,
        pl_trainer_kwargs=pl_trainer_kwargs,
        force_reset=True,
        save_checkpoints=True,  # TODO - where to save?
    )

    # fit model on train series for historical forecasting
    rnn_model.fit(series=scaled_train, val_series=scaled_val)

    # Showing historical backtesting without retraining model (too slow)
    scaled_historical_fcast = rnn_model.historical_forecasts(
        scaled_ticker_series,
        start=float(start_window),
        forecast_horizon=int(forecast_horizon),
        retrain=False,  # MUST TRAIN BEFORE HISTORICAL FCAST
        verbose=True,
    )

    # Show we retrain a new model before predicting??
    best_model = RNNModel.load_from_checkpoint(model_name="rnn_model", best=True)
    # Predict N timesteps in the future
    scaled_prediction = best_model.predict(
        series=scaled_ticker_series, n=int(n_predict)
    )

    precision = mape(
        actual_series=scaled_ticker_series, pred_series=scaled_historical_fcast
    )  # mape = mean average precision error
    console.print(f"RNN model obtains MAPE: {precision:.2f}% \n")

    # scale back
    ticker_series = scaler.inverse_transform(scaled_ticker_series)
    historical_fcast = scaler.inverse_transform(scaled_historical_fcast)
    prediction = scaler.inverse_transform(scaled_prediction)

    return (
        ticker_series,
        historical_fcast,
        prediction,
        precision,
        rnn_model,
    )
