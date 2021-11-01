"""Arima Prediction Model"""
__docformat__ = "numpy"

from typing import Union, List, Tuple, Any
import pandas as pd
import pmdarima
from statsmodels.tsa.arima.model import ARIMA


def get_arima_model(
    values: Union[pd.Series, pd.DataFrame],
    arima_order: str,
    n_predict: int,
    seasonal: bool,
    ic: str,
) -> Tuple[List[float], Any]:
    """Get an ARIMA model for data

    Parameters
    ----------
    values : Union[pd.Series, pd.DataFrame]
        Data to fit
    arima_order : str
        String of ARIMA params in form "p,q,d"
    n_predict : int
        Days to predict
    seasonal : bool
        Flag to use seasonal model
    ic : str
        Information Criteria for model evaluation

    Returns
    -------
    List[float]
        List of predicted values
    Any
        Fit ARIMA model object.
    """
    if arima_order:
        model = ARIMA(
            values, order=tuple(int(ord) for ord in arima_order.split(","))
        ).fit()
        l_predictions = list(
            model.predict(
                start=len(values.values) + 1,
                end=len(values.values) + n_predict,
            )
        )
    else:
        if seasonal:
            model = pmdarima.auto_arima(
                values.values,
                error_action="ignore",
                seasonal=True,
                m=5,
                information_criteria=ic,
            )
        else:
            model = pmdarima.auto_arima(
                values.values,
                error_action="ignore",
                seasonal=False,
                information_criteria=ic,
            )
        l_predictions = list(model.predict(n_predict))

    return l_predictions, model
