import configparser

import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.portfolio.portfolio_optimization import excel_model
from openbb_terminal.rich_config import console

DEFAULT_RANGE = [value / 1000 for value in range(0, 1001)]

AVAILABLE_OPTIONS = {
    "historic_period": ["d", "w", "mo", "y", "ytd", "max"],
    "start_period": ["Any"],
    "end_period": ["Any"],
    "log_returns": ["0", "1"],
    "return_frequency": ["d", "w", "m"],
    "max_nan": DEFAULT_RANGE,
    "threshold_value": DEFAULT_RANGE,
    "nan_fill_method": [
        "linear",
        "time",
        "nearest",
        "zero",
        "slinear",
        "quadratic",
        "cubic",
    ],
    "risk_free": DEFAULT_RANGE,
    "significance_level": DEFAULT_RANGE,
    "risk_measure": [
        "MV",
        "MAD",
        "MSV",
        "FLPM",
        "SLPM",
        "CVaR",
        "EVaR",
        "WR",
        "ADD",
        "UCI",
        "CDaR",
        "EDaR",
        "MDD",
    ],
    "target_return": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
    "target_risk": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
    "expected_return": ["hist", "ewma1", "ewma2"],
    "covariance": [
        "hist",
        "ewma1",
        "ewma2",
        "ledoit",
        "oas",
        "shrunk",
        "gl",
        "jlogo",
        "fixed",
        "spectral",
        "shrink",
    ],
    "smoothing_factor_ewma": DEFAULT_RANGE,
    "long_allocation": DEFAULT_RANGE,
    "short_allocation": DEFAULT_RANGE,
    "risk_aversion": [value / 100 for value in range(-500, 501)],
    "amount_portfolios": range(1, 10001),
    "random_seed": range(1, 10001),
    "tangency": ["0", "1"],
    "risk_parity_model": ["A", "B", "C"],
    "penal_factor": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
    "co_dependence": [
        "pearson",
        "spearman",
        "abs_pearson",
        "abs_spearman",
        "distance",
        "mutual_info",
        "tail",
    ],
    "cvar_simulations": range(1, 10001),
    "cvar_significance": DEFAULT_RANGE,
    "linkage": [
        "single",
        "complete",
        "average",
        "weighted",
        "centroid",
        "ward",
        "dbht",
    ],
    "max_clusters": range(1, 101),
    "amount_bins": ["KN", "FD", "SC", "HGR", "Integer"],
    "alpha_tail": DEFAULT_RANGE,
    "leaf_order": ["0", "1"],
    "objective": ["MinRisk", "Utility", "Sharpe", "MaxRet"],
}

DEFAULT_PARAMETERS = [
    "historic_period",
    "start_period",
    "end_period",
    "log_returns",
    "return_frequency",
    "max_nan",
    "threshold_value",
    "nan_fill_method",
    "risk_free",
    "significance_level",
]
MODEL_PARAMS = {
    "maxsharpe": [
        "risk_measure",
        "target_return",
        "target_risk",
        "expected_return",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "short_allocation",
    ],
    "minrisk": [
        "risk_measure",
        "target_return",
        "target_risk",
        "expected_return",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "short_allocation",
    ],
    "maxutil": [
        "risk_measure",
        "target_return",
        "target_risk",
        "expected_return",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "short_allocation",
        "risk_aversion",
    ],
    "maxret": [
        "risk_measure",
        "target_return",
        "target_risk",
        "expected_return",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
    ],
    "maxdiv": ["covariance", "long_allocation"],
    "maxdecorr": ["covariance", "long_allocation"],
    "ef": [
        "risk_measure",
        "long_allocation",
        "short_allocation",
        "amount_portfolios",
        "random_seed",
        "tangency",
    ],
    "equal": ["risk_measure", "long_allocation"],
    "mktcap": ["risk_measure", "long_allocation"],
    "dividend": ["risk_measure", "long_allocation"],
    "riskparity": [
        "risk_measure",
        "target_return",
        "long_allocation",
        "risk_contribution",
    ],
    "relriskparity": [
        "risk_measure",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "risk_contribution",
        "risk_parity_model",
        "penal_factor",
    ],
    "hrp": [
        "risk_measure",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "co_dependence",
        "cvar_simulations",
        "cvar_significance",
        "linkage",
        "amount_clusters",
        "max_clusters",
        "amount_bins",
        "alpha_tail",
        "leaf_order",
        "objective",
    ],
    "herc": [
        "risk_measure",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "co_dependence",
        "cvar_simulations",
        "cvar_significance",
        "linkage",
        "amount_clusters",
        "max_clusters",
        "amount_bins",
        "alpha_tail",
        "leaf_order",
        "objective",
    ],
    "nco": [
        "risk_measure",
        "covariance",
        "smoothing_factor_ewma",
        "long_allocation",
        "co_dependence",
        "cvar_simulations",
        "cvar_significance",
        "linkage",
        "amount_clusters",
        "max_clusters",
        "amount_bins",
        "alpha_tail",
        "leaf_order",
        "objective",
    ],
}


def load_file(file_location=None):
    """
    Loads in the configuration file and return the parameters in a dictionary including the model if available.

    Parameters
    ----------
    file_location: str
        The location of the file to be loaded in either xlsx or ini.

    Returns
    -------
    Return the parameters and the model, if available.
    """
    if str(file_location).endswith(".ini"):
        params = configparser.RawConfigParser()
        params.read(file_location)
        params.optionxform = str  # type: ignore
        params = params["OPENBB"]

        if "technique" in params:
            current_model = params["technique"]
        else:
            current_model = None

    elif str(file_location).endswith(".xlsx"):
        params, _ = excel_model.load_configuration(file_location)
        current_model = params["technique"]
    else:
        console.print(
            "Can not load in the file due to not being an .ini or .xlsx file."
        )
        return None, None

    max_len = max(len(k) for k in params.keys())
    help_text = "[info]Parameters:[/info]\n"

    if current_model:
        for k, v in params.items():
            all_params = DEFAULT_PARAMETERS + MODEL_PARAMS[current_model]
            if k in all_params:
                help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
    else:
        for k, v in params.items():
            help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"

    console.print(help_text)

    return params, current_model


def show_arguments(arguments, description=None):
    """
    Show the available arguments and the choices you have for each. If available, also show
    the description of the argument.

    Parameters
    ----------
    arguments: Dictionary
        A dictionary containing the keys and the possible values.
    description: Dictionary
        A dictionary containing the keys equal to arguments and the descriptions.

    Returns
    -------
    A table containing the parameter names, possible values and (if applicable) the description.
    """
    adjusted_arguments = {}

    for variable in arguments:
        if len(arguments[variable]) > 15:
            minimum = min(arguments[variable])
            maximum = max(arguments[variable])
            adjusted_arguments[variable] = (
                f"Between {minimum} and {maximum} in steps of "
                f"{maximum / sum(x > 0 for x in arguments[variable])}"
            )
        else:
            adjusted_arguments[variable] = ", ".join(arguments[variable])

    if description:
        df = pd.DataFrame([adjusted_arguments, description]).T
        columns = ["Options", "Description"]
    else:
        df = pd.DataFrame([adjusted_arguments]).T
        columns = ["Options"]

    df = df[df.index != "technique"]

    print_rich_table(
        df, headers=list(columns), show_index=True, index_name="Parameters"
    )
