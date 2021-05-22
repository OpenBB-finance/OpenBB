""" Residuals Model """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
import pmdarima
from statsmodels.tsa.arima.model import ARIMA
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def naive(
    other_args: List[str],
    stock: pd.Series,
):
    """Naive model

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    stock : pd.Series
        Stock data

    Returns
    ----------
    model_name : str
        Command line arguments to be processed with argparse
    model : pd.Series
        Model series
    residuals : List[float]
        Residuals from model fitting stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="naive",
        description="""
            Naive model
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        naive = pd.Series(stock.values[:-1], index=stock[1:].index)

        model_name = "Naive"
        model = naive
        residuals = stock[1:].values - naive.values

        return model_name, model, residuals

    except Exception as e:
        print(e, "\n")
        return "", None, list()


def arima(
    other_args: List[str],
    stock: pd.Series,
):
    """Arima model

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    stock : pd.Series
        Stock data

    Returns
    ----------
    model_name : str
        Command line arguments to be processed with argparse
    model : pd.Series
        Model series
    residuals : List[float]
        Residuals from model fitting stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="arima",
        description="""
            ARIMA model
        """,
    )
    parser.add_argument(
        "-i",
        "--ic",
        action="store",
        dest="s_ic",
        type=str,
        default="aic",
        choices=["aic", "aicc", "bic", "hqic", "oob"],
        help="information criteria.",
    )
    parser.add_argument(
        "-s",
        "--seasonal",
        action="store_true",
        default=False,
        dest="b_seasonal",
        help="Use weekly seasonal data.",
    )
    parser.add_argument(
        "-o",
        "--order",
        action="store",
        dest="s_order",
        type=str,
        help="arima model order (p,d,q) in format: pdq.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.s_order:
            t_order = tuple(int(ord) for ord in list(ns_parser.s_order))
            model_fit = ARIMA(stock.values, order=t_order).fit()
            model = pd.Series(model_fit.fittedvalues[1:], index=stock.index[1:])
            model_name = f"ARIMA {t_order}"
            residuals = model_fit.resid

        else:
            if ns_parser.b_seasonal:
                model_fit = pmdarima.auto_arima(
                    stock.values,
                    error_action="ignore",
                    seasonal=True,
                    m=5,
                    information_criteria=ns_parser.s_ic,
                )
            else:
                model_fit = pmdarima.auto_arima(
                    stock.values,
                    error_action="ignore",
                    seasonal=False,
                    information_criteria=ns_parser.s_ic,
                )

            model = pd.Series(model_fit.predict_in_sample()[1:], index=stock.index[1:])
            model_name = f"ARIMA {model_fit.order}"
            residuals = model_fit.resid()

        return model_name, model, residuals

    except Exception as e:
        print(e, "\n")
        return "", None, list()
