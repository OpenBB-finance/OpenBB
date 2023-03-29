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


# Parameter template files
OPTIMIZATION_PARAMETERS = {
    "historic_period": Parameter(
        name="historic_period",
        type_=str,
        default="3y",
        choices=PERIOD_CHOICES,
    ),
    "start_period": Parameter(
        name="start_period",
        type_=str,
        default="",
    ),
    "end_period": Parameter(
        name="end_period",
        type_=str,
        default="",
    ),
    "log_returns": Parameter(
        name="log_returns",
        type_=bool,
        default=False,
    ),
    "return_frequency": Parameter(
        name="return_frequency",
        type_=str,
        default="d",
        choices=FREQ_CHOICES,
    ),
    "max_nan": Parameter(
        name="max_nan",
        type_=float,
        default=0.05,
    ),
    "threshold_value": Parameter(
        name="threshold_value",
        type_=float,
        default=0.3,
    ),
    "nan_fill_method": Parameter(
        name="nan_fill_method",
        type_=str,
        default="time",
        choices=NAN_FILL_METHOD_CHOICES,
    ),
    "risk_free": Parameter(
        name="risk_free",
        type_=float,
        default=get_rf(),
    ),
    "significance_level": Parameter(
        name="significance_level",
        type_=float,
        default=0.05,
    ),
    "technique": Parameter(
        name="technique",
        type_=str,
        default="maxsharpe",
        choices=TECHNIQUE_CHOICES,
    ),
    "risk_measure": Parameter(
        name="risk_measure",
        type_=str,
        default="MV",
        choices=MEAN_RISK_CHOICES + RISK_PARITY_CHOICES + HCP_CHOICES,
    ),
    "target_return": Parameter(
        name="target_return",
        type_=float,
        default=-1.0,
    ),
    "target_risk": Parameter(
        name="target_risk",
        type_=float,
        default=-1.0,
    ),
    "expected_return": Parameter(
        name="expected_return",
        type_=str,
        default="hist",
        choices=MEAN_CHOICES,
    ),
    "covariance": Parameter(
        name="covariance",
        type_=str,
        default="hist",
        choices=COVARIANCE_CHOICES,
    ),
    "smoothing_factor_ewma": Parameter(
        name="smoothing_factor_ewma",
        type_=float,
        default=0.94,
    ),
    "long_allocation": Parameter(
        name="long_allocation",
        type_=float,
        default=1.0,
    ),
    "short_allocation": Parameter(
        name="short_allocation",
        type_=float,
        default=0.0,
    ),
    "risk_aversion": Parameter(
        name="risk_aversion",
        type_=float,
        default=1.0,
    ),
    "amount_portfolios": Parameter(
        name="amount_portfolios",
        type_=int,
        default=100,
    ),
    "random_seed": Parameter(
        name="random_seed",
        type_=int,
        default=123,
    ),
    "tangency": Parameter(
        name="tangency",
        type_=bool,
        default=False,
    ),
    "risk_contribution": Parameter(
        name="risk_contribution",
        type_=Optional[List[str]],  # type: ignore
        default=None,
    ),
    "risk_parity_model": Parameter(
        name="risk_parity_model",
        type_=str,
        default="A",
        choices=REL_RISK_PARITY_CHOICES,
    ),
    "penal_factor": Parameter(
        name="penal_factor",
        type_=float,
        default=1.0,
    ),
    "p_views": Parameter(
        name="p_views",
        type_=Optional[List[List[float]]],  # type: ignore
        default=None,
    ),
    "q_views": Parameter(
        name="q_views",
        type_=Optional[List[List[float]]],  # type: ignore
        default=None,
    ),
    "delta": Parameter(
        name="delta",
        type_=Optional[float],  # type: ignore
        default=None,
    ),
    "equilibrium": Parameter(
        name="equilibrium",
        type_=bool,
        default=True,
    ),
    "optimize": Parameter(
        name="optimize",
        type_=bool,
        default=True,
    ),
    "co_dependence": Parameter(
        name="co_dependence",
        type_=str,
        default="pearson",
        choices=CODEPENDENCE_CHOICES,
    ),
    "cvar_simulations_losses": Parameter(
        name="cvar_simulations_losses",
        type_=int,
        default=100,
    ),
    "cvar_simulations_gains": Parameter(
        name="cvar_simulations_gains",
        type_=Optional[int],  # type: ignore
        default=None,
    ),
    "cvar_significance": Parameter(
        name="cvar_significance",
        type_=Optional[float],  # type: ignore
        default=None,
    ),
    "linkage": Parameter(
        name="linkage",
        type_=str,
        default="single",
        choices=LINKAGE_CHOICES,
    ),
    "amount_clusters": Parameter(
        name="amount_clusters",
        type_=Optional[int],  # type: ignore
        default=None,
    ),
    "max_clusters": Parameter(
        name="max_clusters",
        type_=int,
        default=10,
    ),
    "amount_bins": Parameter(
        name="amount_bins",
        type_=str,
        default="KN",
        choices=BINS_CHOICES,
    ),
    "alpha_tail": Parameter(
        name="alpha_tail",
        type_=float,
        default=0.05,
    ),
    "leaf_order": Parameter(
        name="leaf_order",
        type_=bool,
        default=True,
    ),
    "objective": Parameter(
        name="objective",
        type_=str,
        default="MinRisk",
        choices=OBJECTIVE_CHOICES + NCO_OBJECTIVE_CHOICES,
    ),
}

# Model functions
# TODO: The dictionary below should not be needed, we can input defaults in the Parameter directly
# But since template variable names are different from functions argument variable names
# we need to map them before removing this dictionary. When we standardize the names, we can remove this.

TERMINAL_TEMPLATE_MAP = {
    "a_sim": "cvar_simulations_losses",
    "alpha": "significance_level",
    "alpha_tail": "alpha_tail",
    "n_portfolios": "amount_portfolios",
    "b_sim": "cvar_simulations_gains",
    "beta": "cvar_significance",
    "bins_info": "amount_bins",
    "codependence": "co_dependence",
    "covariance": "covariance",
    "d_ewma": "smoothing_factor_ewma",
    "delta": "delta",
    "end_date": "end_period",
    "equilibrium": "equilibrium",
    "freq": "return_frequency",
    "interval": "historic_period",
    "k": "amount_clusters",
    "leaf_order": "leaf_order",
    "linkage": "linkage",
    "log_returns": "log_returns",
    "max_k": "max_clusters",
    "maxnan": "max_nan",
    "mean": "expected_return",
    "method": "nan_fill_method",
    "objective": "objective",
    "optimize": "optimize",
    "p_views": "p_views",
    "penal_factor": "penal_factor",
    "q_views": "q_views",
    "seed": "random_seed",
    "risk_aversion": "risk_aversion",
    "risk_cont": "risk_contribution",
    "risk_free_rate": "risk_free",
    "risk_measure": "risk_measure",
    "version": "risk_parity_model",
    "start_date": "start_period",
    "tangency": "tangency",
    "target_return": "target_return",
    "target_risk": "target_risk",
    "technique": "technique",
    "threshold": "threshold_value",
    "value": "long_allocation",
    "value_short": "short_allocation",
}
