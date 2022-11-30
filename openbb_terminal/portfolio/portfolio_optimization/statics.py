from typing import List, Optional
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.portfolio.portfolio_optimization.parameters.Parameter import (
    Parameter,
)


PERIOD_CHOICES = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "3y",
    "5y",
    "10y",
    "ytd",
    "max",
]

MEAN_RISK_CHOICES = [
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
]

RISK_PARITY_CHOICES = [
    "MV",
    "MAD",
    "MSV",
    "FLPM",
    "SLPM",
    "CVaR",
    "EVaR",
    "CDaR",
    "EDaR",
    "UCI",
]

REL_RISK_PARITY_CHOICES = [
    "A",
    "B",
    "C",
]

HCP_CHOICES = [
    "MV",
    "MAD",
    "GMD",
    "MSV",
    "VaR",
    "CVaR",
    "TG",
    "EVaR",
    "RG",
    "CVRG",
    "TGRG",
    "WR",
    "FLPM",
    "SLPM",
    "MDD",
    "ADD",
    "DaR",
    "CDaR",
    "EDaR",
    "UCI",
    "MDD_Rel",
    "ADD_Rel",
    "DaR_Rel",
    "CDaR_Rel",
    "EDaR_Rel",
    "UCI_Rel",
]

RISK_CHOICES = {
    "mv": "MV",
    "mad": "MAD",
    "gmd": "GMD",
    "msv": "MSV",
    "var": "VaR",
    "cvar": "CVaR",
    "tg": "TG",
    "evar": "EVaR",
    "rg": "RG",
    "cvrg": "CVRG",
    "tgrg": "TGRG",
    "wr": "WR",
    "flpm": "FLPM",
    "slpm": "SLPM",
    "mdd": "MDD",
    "add": "ADD",
    "dar": "DaR",
    "cdar": "CDaR",
    "edar": "EDaR",
    "uci": "UCI",
    "mdd_rel": "MDD_Rel",
    "add_rel": "ADD_Rel",
    "dar_rel": "DaR_Rel",
    "cdar_rel": "CDaR_Rel",
    "edar_rel": "EDaR_Rel",
    "uci_rel": "UCI_Rel",
}
MEAN_CHOICES = [
    "hist",
    "ewma1",
    "ewma2",
]

CODEPENDENCE_CHOICES = [
    "pearson",
    "spearman",
    "abs_pearson",
    "abs_spearman",
    "distance",
    "mutual_info",
    "tail",
]

COVARIANCE_CHOICES = [
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
]

OBJECTIVE_CHOICES = [
    "MinRisk",
    "Utility",
    "Sharpe",
    "MaxRet",
]

NCO_OBJECTIVE_CHOICES = [
    "MinRisk",
    "Utility",
    "Sharpe",
    "ERC",
]

LINKAGE_CHOICES = [
    "single",
    "complete",
    "average",
    "weighted",
    "centroid",
    "median",
    "ward",
    "dbht",
]

BINS_CHOICES = [
    "KN",
    "FD",
    "SC",
    "HGR",
]

FREQ_CHOICES = [
    "d",
    "w",
    "m",
]

METHOD_CHOICES = [
    "linear",
    "time",
    "nearest",
    "zero",
    "slinear",
    "quadratic",
    "cubic",
    "barycentric",
]

TIME_FACTOR = {
    "D": 252.0,
    "W": 52.0,
    "M": 12.0,
}

RISK_NAMES = {
    "mv": "volatility",
    "mad": "mean absolute deviation",
    "gmd": "gini mean difference",
    "msv": "semi standard deviation",
    "var": "value at risk (VaR)",
    "cvar": "conditional value at risk (CVaR)",
    "tg": "tail gini",
    "evar": "entropic value at risk (EVaR)",
    "rg": "range",
    "cvrg": "CVaR range",
    "tgrg": "tail gini range",
    "wr": "worst realization",
    "flpm": "first lower partial moment",
    "slpm": "second lower partial moment",
    "mdd": "maximum drawdown uncompounded",
    "add": "average drawdown uncompounded",
    "dar": "drawdown at risk (DaR) uncompounded",
    "cdar": "conditional drawdown at risk (CDaR) uncompounded",
    "edar": "entropic drawdown at risk (EDaR) uncompounded",
    "uci": "ulcer index uncompounded",
    "mdd_rel": "maximum drawdown compounded",
    "add_rel": "average drawdown compounded",
    "dar_rel": "drawdown at risk (DaR) compounded",
    "cdar_rel": "conditional drawdown at risk (CDaR) compounded",
    "edar_rel": "entropic drawdown at risk (EDaR) compounded",
    "uci_rel": "ulcer index compounded",
}


DRAWDOWNS = [
    "MDD",
    "ADD",
    "DaR",
    "CDaR",
    "EDaR",
    "UCI",
    "MDD_Rel",
    "ADD_Rel",
    "DaR_Rel",
    "CDaR_Rel",
    "EDaR_Rel",
    "UCI_Rel",
]

PARAM_TYPES = {
    "interval": str,
    "start_date": str,
    "end_date": str,
    "log_returns": bool,
    "return_frequency": str,
    "maxnan": float,
    "threshold": float,
    "method": str,
    "risk_measure": str,
    "objective": str,
    "risk_free_rate": float,
    "risk_aversion": float,
    "alpha": float,
    "target_return": float,
    "target_risk": float,
    "mean": str,
    "covariance": str,
    "d_ewma": float,
    "value": float,
    "value_short": float,
}

NAN_FILL_METHOD_CHOICES = [
    "linear",
    "time",
    "nearest",
    "zero",
    "slinear",
    "quadratic",
    "cubic",
    "barycentric",
]

TECHNIQUE_CHOICES = [
    "maxsharpe",
    "minrisk",
    "maxutil",
    "maxret",
    "maxdiv",
    "maxdecorr",
    "ef",
    "equal",
    "mktcap",
    "dividend",
    "blacklitterman",
    "riskparity",
    "relriskparity",
    "hrp",
    "herc",
    "nco",
]

# Model functions
DEFAULT_PARAMETERS = {
    "interval": "3y",
    "start_date": "",
    "end_date": "",
    "log_returns": False,
    "freq": "d",
    "maxnan": 0.05,
    "threshold": 0.3,
    "method": "time",
    "risk_free_rate": get_rf(),
    "alpha": 0.05,
    "technique": "maxsharpe",
    "risk_measure": "MV",
    "target_return": -1.0,
    "target_risk": -1.0,
    "mean": "hist",
    "covariance": "hist",
    "d_ewma": 0.94,
    "value": 1.0,
    "value_short": 0.0,
    "risk_aversion": 1.0,
    "amount_portfolios": 100,
    "random_seed": 123.0,
    "tangency": False,
    "risk_contribution": None,
    "risk_parity_model": "A",
    "penal_factor": 1.0,
    "p_views": None,
    "q_views": None,
    "delta": 1.0,
    "equilibrium": True,
    "optimize": True,
    "codependence": "pearson",
    "a_sim": 100,
    "b_sim": 100,
    "beta": 0.05,
    "linkage": "single",
    "k": 10,
    "max_k": 10,
    "bins_info": "KN",
    "alpha_tail": 0.05,
    "leaf_order": True,
    "objective": "MinRisk",
}

# Parameter template files
# TODO: Template variable names are different from functions variable names, should be the same everywhere
OPTIMIZATION_PARAMETERS = {
    "historic_period": Parameter(
        name="interval",
        type_=str,
        default=DEFAULT_PARAMETERS["interval"],
        choices=PERIOD_CHOICES,
    ),
    "start_period": Parameter(
        name="start_date",
        type_=str,
        default=DEFAULT_PARAMETERS["start_date"],
    ),
    "end_period": Parameter(
        name="end_date",
        type_=str,
        default=DEFAULT_PARAMETERS["end_date"],
    ),
    "log_returns": Parameter(
        name="log_returns",
        type_=bool,
        default=DEFAULT_PARAMETERS["log_returns"],
    ),
    "return_frequency": Parameter(
        name="return_frequency",
        type_=str,
        default=DEFAULT_PARAMETERS["freq"],
        choices=FREQ_CHOICES,
    ),
    "max_nan": Parameter(
        name="maxnan",
        type_=float,
        default=DEFAULT_PARAMETERS["maxnan"],
    ),
    "threshold_value": Parameter(
        name="threshold",
        type_=float,
        default=DEFAULT_PARAMETERS["threshold"],
    ),
    "nan_fill_method": Parameter(
        name="nan_fill_method",
        type_=str,
        default=DEFAULT_PARAMETERS["method"],
        choices=NAN_FILL_METHOD_CHOICES,
    ),
    "risk_free_rate": Parameter(
        name="risk_free_rate",
        type_=float,
        default=DEFAULT_PARAMETERS["risk_free_rate"],
    ),
    "significance_level": Parameter(
        name="significance_level",
        type_=float,
        default=DEFAULT_PARAMETERS["alpha"],
    ),
    "technique": Parameter(
        name="technique",
        type_=str,
        default=DEFAULT_PARAMETERS["technique"],
        choices=TECHNIQUE_CHOICES,
    ),
    "risk_measure": Parameter(
        name="risk_measure",
        type_=str,
        default=DEFAULT_PARAMETERS["risk_measure"],
        choices=MEAN_RISK_CHOICES,
    ),
    "target_return": Parameter(
        name="target_return",
        type_=float,
        default=DEFAULT_PARAMETERS["target_return"],
    ),
    "target_risk": Parameter(
        name="target_risk",
        type_=float,
        default=DEFAULT_PARAMETERS["target_risk"],
    ),
    "expected_return": Parameter(
        name="expected_return",
        type_=str,
        default=DEFAULT_PARAMETERS["mean"],
        choices=MEAN_CHOICES,
    ),
    "covariance": Parameter(
        name="covariance",
        type_=str,
        default=DEFAULT_PARAMETERS["covariance"],
        choices=COVARIANCE_CHOICES,
    ),
    "smoothing_factor_ewma": Parameter(
        name="smoothing_factor_ewma",
        type_=float,
        default=DEFAULT_PARAMETERS["d_ewma"],
    ),
    "long_allocation": Parameter(
        name="long_allocation",
        type_=float,
        default=DEFAULT_PARAMETERS["value"],
    ),
    "short_allocation": Parameter(
        name="short_allocation",
        type_=float,
        default=DEFAULT_PARAMETERS["value_short"],
    ),
    "risk_aversion": Parameter(
        name="risk_aversion",
        type_=float,
        default=DEFAULT_PARAMETERS["risk_aversion"],
    ),
    "amount_portfolios": Parameter(
        name="amount_portfolios",
        type_=int,
        default=DEFAULT_PARAMETERS["amount_portfolios"],
    ),
    "random_seed": Parameter(
        name="random_seed",
        type_=float,
        default=DEFAULT_PARAMETERS["random_seed"],
    ),
    "tangency": Parameter(
        name="tangency",
        type_=bool,
        default=DEFAULT_PARAMETERS["tangency"],
    ),
    "risk_contribution": Parameter(
        name="risk_contribution",
        type_=Optional[List[str]],
        default=DEFAULT_PARAMETERS["risk_contribution"],
    ),
    "risk_parity_model": Parameter(
        name="risk_parity_model",
        type_=str,
        default=DEFAULT_PARAMETERS["risk_parity_model"],
        choices=REL_RISK_PARITY_CHOICES,
    ),
    "penal_factor": Parameter(
        name="penal_factor",
        type_=float,
        default=DEFAULT_PARAMETERS["penal_factor"],
    ),
    "p_views": Parameter(
        name="p_views",
        type_=List[List[float]],
        default=DEFAULT_PARAMETERS["p_views"],
    ),
    "q_views": Parameter(
        name="q_views",
        type_=List[List[float]],
        default=DEFAULT_PARAMETERS["q_views"],
    ),
    "delta": Parameter(
        name="delta",
        type_=float,
        default=DEFAULT_PARAMETERS["delta"],
    ),
    "equilibrium": Parameter(
        name="equilibrium",
        type_=bool,
        default=DEFAULT_PARAMETERS["equilibrium"],
    ),
    "optimize": Parameter(
        name="optimize",
        type_=bool,
        default=DEFAULT_PARAMETERS["optimize"],
    ),
    "co_dependence": Parameter(
        name="co_dependence",
        type_=str,
        default=DEFAULT_PARAMETERS["codependence"],
        choices=CODEPENDENCE_CHOICES,
    ),
    "cvar_simulations_losses": Parameter(
        name="cvar_simulations_losses",
        type_=int,
        default=DEFAULT_PARAMETERS["a_sim"],
    ),
    "cvar_simulations_gains": Parameter(
        name="cvar_simulations_gains",
        type_=int,
        default=DEFAULT_PARAMETERS["b_sim"],
    ),
    "cvar_significance": Parameter(
        name="cvar_significance",
        type_=float,
        default=DEFAULT_PARAMETERS["beta"],
    ),
    "linkage": Parameter(
        name="linkage",
        type_=str,
        default=DEFAULT_PARAMETERS["linkage"],
        choices=LINKAGE_CHOICES,
    ),
    "amount_clusters": {
        "type_": int,
        "default": DEFAULT_PARAMETERS["k"],
    },
    "max_clusters": Parameter(
        name="max_clusters",
        type_=int,
        default=DEFAULT_PARAMETERS["max_k"],
    ),
    "amount_bins": Parameter(
        name="amount_bins",
        type_=str,
        default=DEFAULT_PARAMETERS["bins_info"],
        choices=BINS_CHOICES,
    ),
    "alpha_tail": Parameter(
        name="alpha_tail",
        type_=float,
        default=DEFAULT_PARAMETERS["alpha_tail"],
    ),
    "leaf_order": Parameter(
        name="leaf_order",
        type_=bool,
        default=DEFAULT_PARAMETERS["leaf_order"],
    ),
    "objective": Parameter(
        name="objective",
        type_=str,
        default=DEFAULT_PARAMETERS["objective"],
        choices=OBJECTIVE_CHOICES,
    ),
}
