""" Prediction helper functions """
__docformat__ = "numpy"

import numpy as np
import pandas as pd
from colorama import Fore, Style
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
)

from gamestonk_terminal import feature_flags as gtff


def price_prediction_color(val: float, last_val: float) -> str:
    """Set prediction to be a colored string"""
    if float(val) > last_val:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return f"{color}{val:.2f} ${Style.RESET_ALL}"


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    """Print predictions"""
    if gtff.USE_COLOR:
        print(f"Actual price: {Fore.YELLOW}{last_price:.2f} ${Style.RESET_ALL}\n")
        print("Prediction:")
        print(df_pred.apply(price_prediction_color, last_val=last_price).to_string())
    else:
        print(f"Actual price: {last_price:.2f} $\n")
        print("Prediction:")
        print(df_pred.to_string())


def print_pretty_prediction_nn(df_pred: pd.DataFrame, last_price: float):
    if gtff.USE_COLOR:
        print(f"Actual price: {Fore.YELLOW}{last_price:.2f} ${Style.RESET_ALL}\n")
        print("Prediction:")
        print(
            df_pred.applymap(
                lambda x: price_prediction_color(x, last_val=last_price)
            ).to_string()
        )
    else:
        print(f"Actual price: {last_price:.2f} $\n")
        print("Prediction:")
        print(df_pred.to_string())


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.number:
    """Calculate mean absolute percent error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def print_prediction_kpis(real: np.ndarray, pred: np.ndarray):
    """Print prediction statistics"""
    print("KPIs")
    print(f"MAPE: {mean_absolute_percentage_error(real, pred):.3f} %")
    print(f"R2: {r2_score(real, pred):.3f}")
    print(f"MAE: {mean_absolute_error(real, pred):.3f}")
    print(f"MSE: {mean_squared_error(real, pred):.3f}")
    print(f"RMSE: {mean_squared_error(real, pred, squared=False):.3f}")


def price_prediction_backtesting_color(val: list) -> str:
    """Add color to backtest data"""
    err_pct = 100 * (val[0] - val[1]) / val[1]
    if val[0] > val[1]:
        s_err_pct = f"       {Fore.GREEN} +{err_pct:.2f} %"
    else:
        s_err_pct = f"       {Fore.RED} {err_pct:.2f} %"
    return f"{val[1]:.2f}    x    {Fore.YELLOW}{val[0]:.2f}{s_err_pct}{Style.RESET_ALL}"
