"""Regression Model"""
__docformat__ = "numpy"
from typing import Tuple, List, Any, Union
import pandas as pd
from tsxv import splitTrain
from sklearn import linear_model
from sklearn import pipeline
from sklearn import preprocessing


def get_regression_model(
    values: Union[pd.Series, pd.DataFrame],
    poly_order: int,
    n_input: int,
    n_predict: int,
    n_jumps: int,
) -> Tuple[List[float], Any]:
    """Fit regression model of variable order

    Parameters
    ----------
    values : Union[pd.Series, pd.DataFrame]
        Data to fit
    poly_order : int
        Order of polynomial
    n_input : int
        Length of input sequence
    n_predict : int
        Length of prediction sequence
    n_jumps : int
        Number of jumps in data preparation

    Returns
    -------
    List[float]
        List of predicted values
    Any
        Linear model fit to data
    """
    # Split training data
    stock_x, stock_y = splitTrain.split_train(
        values.values,
        n_input,
        n_predict,
        n_jumps,
    )

    if not stock_x:
        print("Given the model parameters more training data is needed.\n")
        return [], None

    # Machine Learning model
    if poly_order == 1:
        model = linear_model.LinearRegression(n_jobs=-1)
    else:
        model = pipeline.make_pipeline(
            preprocessing.PolynomialFeatures(poly_order), linear_model.Ridge()
        )

    model.fit(stock_x, stock_y)
    l_predictions = [
        i if i > 0 else 0
        for i in model.predict(values.values[-n_input:].reshape(1, -1))[0]
    ]
    return l_predictions, model
