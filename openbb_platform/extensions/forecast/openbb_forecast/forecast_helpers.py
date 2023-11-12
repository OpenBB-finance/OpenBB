# pylint: disable=too-many-arguments,too-many-lines
import argparse
import logging
import os
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from openbb_core.app.utils import basemodel_to_df
from openbb_core.app.utils import df_to_basemodel

from openbb_provider.abstract.data import Data


import numpy as np
import pandas as pd

from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.models.forecasting.torch_forecasting_model import GlobalForecastingModel
from darts.metrics import mape, mse, rmse, smape

from pytorch_lightning.callbacks.early_stopping import EarlyStopping

from sklearn.preprocessing import MaxAbsScaler

logger = logging.getLogger(__name__)
logging.getLogger("pytorch_lightning").setLevel(logging.CRITICAL)  # No needed for now


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.number:
    """Calculate mean absolute percent error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def past_covs(
    past_covariates: Optional[str],
    data: Union[pd.DataFrame, pd.Series],
    train_split: float,
    is_scaler: bool = True,
):
    if past_covariates is not None:
        target_covariates_names = past_covariates.split(",")

        # create first covariate to then stack
        print(f"[green]Covariate #0: {target_covariates_names[0]}[/green]")
        _, past_covariate_whole = convert_to_timeseries(
            data, target_column=target_covariates_names[0], is_scaler=is_scaler
        )

        if len(target_covariates_names) > 1:
            for i, column in enumerate(target_covariates_names[1:]):
                print(f"[green]Covariate #{i+1}: {column}[/green]")
                _, _temp_new_covariate = convert_to_timeseries(
                    data,
                    target_column=target_covariates_names[i + 1],
                    is_scaler=is_scaler,
                )

                # continually stack covariates based on column names
                past_covariate_whole = past_covariate_whole.stack(_temp_new_covariate)

        # Split the full scale covariate to train and val
        (
            past_covariate_train,
            past_covariate_val,
        ) = past_covariate_whole.split_before(train_split)
        return (
            past_covariate_whole,
            past_covariate_train,
            past_covariate_val,
        )
    return None, None, None


def early_stopper(patience: int, monitor: str = "val_loss"):
    my_stopper = EarlyStopping(
        monitor=monitor,
        patience=patience,
        min_delta=0.01,
        mode="min",
    )
    return my_stopper


def get_pl_kwargs(
    patience: int = 20, monitor: str = "val_loss", accelerator: str = "cpu"
) -> Dict[str, Any]:
    my_stopper = early_stopper(patience, monitor)
    pl_trainer_kwargs = {
        "callbacks": [my_stopper],
        "accelerator": accelerator,
        # "logger": False,
        # "enable_progress_bar": False,
        "enable_model_summary": False,
    }
    return pl_trainer_kwargs


def dt_format(x) -> str:
    """Convert any Timestamp to YYYY-MM-DD
    Args:
        x: Pandas Timestamp of any length
    Returns:
        x: formatted string
    """
    x = pd.to_datetime(x)
    x = x.strftime("%Y-%m-%d")
    return x


def convert_to_timeseries(
    data: Union[pd.DataFrame, List[Data]],
    target_column: Optional[str] = None,
    is_scaler: bool = True,
    time_col: str = "date",
) -> Tuple[Optional[Scaler], TimeSeries]:
    """Converts a pandas DataFrame into a TimeSeries object, filling missing values and handling date formats.

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame containing time-series data.
    target_column : Optional[str], optional
        The name of the target column to be used as the time-series values, by default None.
    is_scaler : bool, optional
        Indicates whether scaling should be applied to the time-series data, by default True.
    time_col : str, optional
        The name of the column representing the time/date in the DataFrame, by default "date".

    Returns
    -------
    Tuple[Optional[Scaler], TimeSeries]
        A tuple containing an optional Scaler object (if is_scaler is True) and the resulting TimeSeries object.

    Raises
    ------
    ValueError
        If the DataFrame cannot be converted to a TimeSeries object.

    Notes
    -----
    This function uses a MissingValuesFiller to handle missing values in the time-series data.
    The time_col parameter specifies the column containing the time/date information, and if not provided, the function assumes evenly spaced time intervals.
    """

    # Convert to dataframe if the data is of type List[Data]
    if isinstance(data, list):
        data = basemodel_to_df(data, index="date")

    filler = MissingValuesFiller()
    filler_kwargs = dict(
        df=data,
        time_col=time_col,
        value_cols=[target_column],
        freq="B",
        fill_missing_dates=True,
    )

    try:
        # for the sdk, we must check if date is a column not an index
        # check if date is in the index, if true, reset the index
        if time_col in data.index.names:
            # # make a new column with the index
            data[time_col] = data.index
            # reset the index
            data.reset_index(drop=True, inplace=True)
            # remove 00:00:00 from 2019-11-19 00:00:00
            data[time_col] = data[time_col].apply(lambda x: dt_format(x))

        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)
    except ValueError:
        # remove business days to allow base lib to assume freq
        filler_kwargs.pop("freq")
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)
    except AttributeError:
        # Uses index if no date column
        print("Warning: no date found, assuming items evenly spaced.\n")
        filler_kwargs.pop("time_col")
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)

    if is_scaler:
        scaler = Scaler(scaler=MaxAbsScaler())
        scaled_ticker_series = scaler.fit_transform(
            filler.transform(ticker_series)
        ).astype(np.float32)
        return scaler, scaled_ticker_series

    ticker_series = filler.transform(ticker_series).astype(np.float32)
    scaler = None
    return scaler, ticker_series


def fit_model(
    model: type[GlobalForecastingModel],
    series: TimeSeries,
    val_series: Optional[TimeSeries] = None,
    past_covariates: Optional[TimeSeries] = None,
    val_past_covariates: Optional[TimeSeries] = None,
    **kwargs,
):
    fit_kwargs = dict(
        series=series,
    )
    fit_kwargs.update(kwargs)
    if val_series is not None:
        fit_kwargs["val_series"] = val_series
    if past_covariates is not None:
        fit_kwargs["past_covariates"] = past_covariates
        fit_kwargs["val_past_covariates"] = val_past_covariates

    model.fit(**fit_kwargs)


def check_parser_input(parser: argparse.ArgumentParser, datasets, *args) -> bool:
    """Check the validity of parser input for dataset processing.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The ArgumentParser instance used for command-line argument parsing.

    datasets : dict
        A dictionary containing datasets with dataset names as keys and DataFrame as values.

    *args
        Additional arguments that can be used to customize the behavior of the function.

    Returns
    -------
    bool
        True if the parser input is valid; False otherwise.
    """

    # check proper file name is provided
    if not hasattr(parser, "target_dataset"):
        return False
    if not parser.target_dataset:  # type: ignore
        print("Please select a valid dataset with the -d flag.\n")
        return False
    if "ignore_column" in args:
        return True
    if not hasattr(parser, "target_column"):
        return False

    # must check that data["date"] col is within target series
    if parser.target_column not in datasets[parser.target_dataset].columns:  # type: ignore
        print(f"The column {parser.target_column} does not exist.\n")  # type: ignore
        return False
    return True


def check_data_length(
    train, test, input_chunk_length: int, output_chunk_length: int
) -> bool:
    if input_chunk_length + output_chunk_length > len(train):
        base = "Not enough train data. Please increase the "
        print(base + "train test split or decrease input or output chunk length.\n")
        return False
    if input_chunk_length + output_chunk_length > len(test):
        base = "Not enough test data. Please decrease the "
        print(base + "train test split or decrease the input or output chunk length.\n")
        return False
    return True


def filter_dates(
    data: Union[pd.DataFrame, pd.Series],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> Union[pd.DataFrame, pd.Series]:
    if start_date and end_date and start_date >= end_date:
        print("The start date must be before the end date.\n")
        return data
    if end_date:
        if isinstance(data["date"].values[0], str):
            data = data[pd.to_datetime(data["date"]) <= end_date]
        else:
            data = data[data["date"] <= end_date]
    if start_date:
        if isinstance(data["date"].values[0], str):
            data = data[pd.to_datetime(data["date"]) >= start_date]
        else:
            data = data[data["date"] >= start_date]
    return data


def clean_data(
    data: Union[pd.DataFrame, pd.Series],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    target_column: Optional[str] = None,
    past_covariates: Optional[str] = None,
) -> Union[pd.DataFrame, pd.Series]:
    # check if target column is in data and if the target_column has any inf
    # replace all inf with nan. This is because darts does not handle inf
    # Creating a timeseries with fillna=True will replace all nan with interoplated values
    if (
        target_column
        and target_column in data.columns
        and data[target_column].isin([np.inf, -np.inf]).any()
    ):
        print(f"The target column [{target_column}] has inf values. Cleaning...\n")
        data = data.replace([np.inf, -np.inf], np.nan)

    # check if past covariates are in data and if they have any inf
    if past_covariates:
        covariates = past_covariates.split(",")
        for covariate in covariates:
            if (
                covariate in data.columns
                and data[covariate].isin([np.inf, -np.inf]).any()
            ):
                print(f"The covariate:{covariate} has inf values. Cleaning...\n")
                data = data.replace([np.inf, -np.inf], np.nan)

    if isinstance(data, pd.Series):
        col = data.name
        columns = ["date", col]
        data = pd.DataFrame(data).reset_index()
        data.columns = columns
        data = filter_dates(data, start_date, end_date)
        data = data.set_index("date")
        data = data[col]
    elif "date" in data.columns:
        data = filter_dates(data, start_date, end_date)
    elif end_date or start_date:
        print("No 'date' column specified, ignoring start end end date\n")
    return data


def clean_covariates(parser, dataset: pd.DataFrame) -> Optional[str]:
    forecast_column: str = parser.target_column
    if parser.all_past_covariates:
        data = dataset
        covs = [x for x in data.columns if x not in ["date", parser.target_column]]
        return ",".join(covs)
    covariates = parser.past_covariates
    if not covariates:
        return covariates
    covs_list = covariates.split(",")
    for covariate in covs_list:
        if covariate == forecast_column:
            covs_list.remove(covariate)
            print(
                f"Forecast target '{forecast_column}' cannot be within the past"
                " covariates. Removed the covariates from analysis\n"
            )
    if len(covariates) == 0:
        return None
    covariates = ",".join(covs_list)
    return covariates


def check_data(
    data: pd.DataFrame, target_column: str, past_covariates: Optional[str] = None
) -> bool:
    if target_column not in data.columns:
        print(
            f"Column {target_column} is not in the dataframe."
            " Change the 'target_column' parameter.\n"
        )
        return False
    if data.empty:
        print("The data provided is empty.\n")
        return False
    if past_covariates is not None:
        covariates = past_covariates.split(",")
        for covariate in covariates:
            if covariate not in data.columns:
                print(
                    f"Column {covariate} is not in the dataframe."
                    " Change the 'past_covariates' parameter.\n"
                )
                return False
    return True


def check_output(
    output_chunk_length: int, n_predict: int, past_covariates: bool
) -> int:
    if past_covariates:
        if output_chunk_length != n_predict:
            print(
                "Warning: when using past covariates n_predict must equal"
                f" output_chunk_length. We have changed your output_chunk_length to {n_predict}"
                " to match your n_predict"
            )
        return n_predict
    return output_chunk_length


def check_dates(s: pd.Series) -> bool:
    """Checks whether all hours, minutes, seconds and milliseconds are 0""" ""
    for _, value in s.items():
        try:
            if value.time() != time(0, 0, 0, 0):
                return False
        except AttributeError:
            return False
    return True


def timeseries_to_basemodel(time_series=TimeSeries) -> List[Data]:
    """Converts TimeSeries to List[Data]

    Parameters
    ----------
    time_series : _type_, optional
        _description_, by default TimeSeries

    Returns
    -------
    List[Data]
        List of values, with each value of type Data
    """

    return df_to_basemodel(time_series.pd_dataframe())


def calculate_precision(
    metric: str, actual_series: TimeSeries, pred_series: TimeSeries
) -> float:
    """Calculate precision for a given metric.

    Parameters
    ----------
    metric : str
        The evaluation metric to be used for calculating precision.
        Valid options are "rmse," "mse," "mape," or "smape."
    actual_series : TimeSeries
        The actual time series data for comparison.
    pred_series : TimeSeries
        The predicted time series data for comparison.

    Returns
    -------
    float
        The precision value calculated based on the specified metric.
    """

    if metric == "rmse":
        precision = rmse(actual_series=actual_series, pred_series=pred_series)
    elif metric == "mse":
        precision = mse(actual_series=actual_series, pred_series=pred_series)
    elif metric == "mape":
        precision = mape(actual_series=actual_series, pred_series=pred_series)
    elif metric == "smape":
        precision = smape(actual_series=actual_series, pred_series=pred_series)

    return float(precision)


def model_prediction(
    model_name: str,
    probabilistic: bool,
    use_scalers: bool,
    scaler: Optional[Scaler],
    past_covariates: Optional[str],
    model: type[GlobalForecastingModel],
    ticker_series: TimeSeries,
    past_covariate_whole: Optional[TimeSeries],
    train_split: float,
    forecast_horizon: int,
    n_predict: int,
):
    _, val = ticker_series.split_before(train_split)

    print(f"Predicting {model_name} for {n_predict} periods")
    if model_name not in ["Regression", "Logistic Regression"]:
        # need to create a new pytorch trainer for historical backtesting to remove progress bar
        model.trainer = None
        # model.trainer_params["enable_progress_bar"] = True

    # Historical backtest if with covariates
    if past_covariates is not None:
        historical_fcast = model.historical_forecasts(
            ticker_series,
            past_covariates=past_covariate_whole,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )
    # Historical backtest without covariates
    else:
        historical_fcast = model.historical_forecasts(
            ticker_series,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )

    # now predict N days in the future
    if past_covariates is not None:
        if probabilistic:
            prediction = model.predict(
                series=ticker_series,
                past_covariates=past_covariate_whole,
                n=n_predict,
                num_samples=500,
            )
        else:
            prediction = model.predict(
                series=ticker_series,
                past_covariates=past_covariate_whole,
                n=n_predict,
            )
    elif probabilistic:
        prediction = model.predict(series=ticker_series, n=n_predict, num_samples=500)
    else:
        prediction = model.predict(series=ticker_series, n=n_predict)

    # Scale back
    if use_scalers and isinstance(scaler, Scaler):
        ticker_series = scaler.inverse_transform(ticker_series)
        historical_fcast = scaler.inverse_transform(historical_fcast)
        prediction = scaler.inverse_transform(prediction)

    return ticker_series, historical_fcast, prediction, model


def print_tensorboard_logs(model_save_name: str, user_directory: str):
    tensorboard_logs_dir = os.path.join(user_directory, model_save_name, "logs")
    print(
        "This model supports Tensorboard logs. To view, open a new terminal windown and run:"
    )
    print("tensorboard --logdir=" + tensorboard_logs_dir)
    print()
