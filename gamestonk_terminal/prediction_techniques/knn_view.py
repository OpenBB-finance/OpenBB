""" K Nearest Neighbors View"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from sklearn import neighbors
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    get_next_stock_market_days,
)
from gamestonk_terminal.prediction_techniques.pred_helper import (
    print_pretty_prediction,
    prepare_scale_train_valid_test,
    plot_data_predictions,
)

register_matplotlib_converters()


def k_nearest_neighbors(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Train KNN model
    Parameters
    ----------
    other_args: List[str]
        List of argparse arguments
    s_ticker: str
        Ticker
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="knn",
        description="""
            K nearest neighbors is a simple algorithm that stores all
            available cases and predict the numerical target based on a similarity measure
            (e.g. distance functions).
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        action="store",
        dest="n_inputs",
        type=check_positive,
        default=40,
        help="number of days to use as input for prediction.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=5,
        help="prediction days.",
    )
    parser.add_argument(
        "-j",
        "--jumps",
        action="store",
        dest="n_jumps",
        type=check_positive,
        default=1,
        help="number of jumps in training data.",
    )
    parser.add_argument(
        "-n",
        "--neighbors",
        action="store",
        dest="n_neighbors",
        type=check_positive,
        default=20,
        help="number of neighbors to use on the algorithm.",
    )
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select for testing",
    )

    parser.add_argument(
        "-t",
        "--test_size",
        default=0.2,
        dest="valid_split",
        type=float,
        help="Percentage of data to validate in sample",
    )
    parser.add_argument(
        "-p",
        "--pp",
        action="store",
        dest="s_preprocessing",
        default="none",
        choices=["normalization", "standardization", "minmax", "none"],
        help="pre-processing data.",
    )
    parser.add_argument(
        "--no_shuffle",
        action="store_false",
        dest="no_shuffle",
        default=True,
        help="Specify if shuffling validation inputs.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        (
            X_train,
            X_valid,
            y_train,
            y_valid,
            _,
            _,
            _,
            y_dates_valid,
            forecast_data_input,
            dates_forecast_input,
            scaler,
            is_error,
        ) = prepare_scale_train_valid_test(df_stock["Adj Close"], ns_parser)
        if is_error:
            print("Error preparing data")
            return
        print(
            f"Training on {X_train.shape[0]} sequences of length {X_train.shape[1]}.  Using {X_valid.shape[0]} sequences "
            f" of length {X_valid.shape[1]} for validation"
        )
        future_dates = get_next_stock_market_days(
            dates_forecast_input[-1], n_next_days=ns_parser.n_days
        )

        # Machine Learning model
        knn = neighbors.KNeighborsRegressor(n_neighbors=ns_parser.n_neighbors)
        knn.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1]),
            y_train.reshape(y_train.shape[0], y_train.shape[1]),
        )

        preds = knn.predict(X_valid.reshape(X_valid.shape[0], X_valid.shape[1]))
        forecast_data = knn.predict(forecast_data_input.reshape(1, -1))

        forecast_data_df = pd.DataFrame(
            [i if i > 0 else 0 for i in forecast_data.T], index=future_dates
        )
        print_pretty_prediction(forecast_data_df[0], df_stock["Adj Close"].values[-1])
        plot_data_predictions(
            df_stock,
            preds,
            y_valid,
            y_dates_valid,
            scaler,
            f"KNN Model with {ns_parser.n_neighbors} Neighbors on {s_ticker}",
            forecast_data_df,
            1,
        )
        print("")

    except Exception as e:
        print(e)
        print("")
