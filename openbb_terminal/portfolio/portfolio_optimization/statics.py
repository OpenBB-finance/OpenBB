from typing import List
from openbb_terminal.helper_funcs import get_rf


PERIOD_CHOICES = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
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
    "freq": str,
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

VALID_PARAMS = {
        "historic_period": {
            "type_": str,
            "default": "3y",
            "choices": PERIOD_CHOICES,
        },
        "start_period": {
            "type_": str,
            "default": "",
        },
        "end_period": {
            "type_": str,
            "default": "",
        },
        "log_returns": {
            "type_": bool,
            "default": False,
        },
        "return_frequency": {
            "type_": str,
            "default": "d",
            "choices": FREQ_CHOICES,
        },
        "max_nan": {
            "type_": float,
            "default": 0.05,
        },
        "threshold_value": {
            "type_": float,
            "default": 0.3,
        },
        "nan_fill_method": {
            "type_": str,
            "default": "time",
            "choices": NAN_FILL_METHOD_CHOICES,
        },
        "risk_free": {
            "type_": float,
            "default": get_rf(),
        },
        "significance_level": {
            "type_": float,
            "default": 0.05,
        },
        "technique": {
            "type_": str,
            "default": "maxsharpe",
            "choices": TECHNIQUE_CHOICES,
        },
        "risk_measure": {
            "type_": str,
            "default": "MV",
            "choices": MEAN_RISK_CHOICES,
        },
        "target_return": {
            "type_": float,
            "default": -1,
        },
        "target_risk": {
            "type_": float,
            "default": -1,
        },
        "expected_return": {
            "type_": str,
            "default": "hist",
            "choices": MEAN_CHOICES,
        },
        "covariance": {
            "type_": str,
            "default": "hist",
            "choices": COVARIANCE_CHOICES,
        },
        "smoothing_factor_ewma": {
            "type_": float,
            "default": 0.94,
        },
        "long_allocation": {
            "type_": float,
            "default": 1.0,
        },
        "short_allocation": {
            "type_": float,
            "default": 0.0,
        },
        "risk_aversion": {
            "type_": float,
            "default": 1.0,
        },
        "amount_portfolios": {
            "type_": int,
            "default": 100,
        },
        "random_seed": {
            "type_": int,
            "default": 123,
        },
        "tangency": {
            "type_": bool,
            "default": False,
        },
        "risk_contribution": {
            "type_": List[str],
            "default": None,
        },
        "risk_parity_model": {
            "type_": str,
            "default": "A",
            "choices": REL_RISK_PARITY_CHOICES,
        },
        "penal_factor": {
            "type_": float,
            "default": 1.0,
        },
        "p_views": {
            "type_": List[List[float]],
            "default": None,
        },
        "q_views": {
            "type_": List[List[float]],
            "default": None,
        },
        "delta": {
            "type_": float,
            "default": 1,
        },
        "equilibrium": {
            "type_": bool,
            "default": True,
        },
        "optimize": {
            "type_": bool,
            "default": True,
        },
        "co_dependence": {
            "type_": str,
            "default": None,
            "choices": CODEPENDENCE_CHOICES,
        },
        "cvar_simulations_losses": {
            "type_": int,
            "default": 100,
        },
        "cvar_simulations_gains": {
            "type_": int,
            "default": 100,
        },
        "cvar_significance": {
            "type_": float,
            "default": 0.05,
        },
        "linkage": {
            "type_": str,
            "default": "single",
            "choices": LINKAGE_CHOICES,
        },
        "amount_clusters": {
            "type_": int,
            "default": 10,
        },
        "max_clusters": {
            "type_": int,
            "default": 10,
        },
        "amount_bins": {
            "type_": str,
            "default": 10,
            "choices": BINS_CHOICES,
        },
        "alpha_tail": {
            "type_": float,
            "default": 0.05,
        },
        "leaf_order": {
            "type_": bool,
            "default": True,
        },
        "objective": {
            "type_": str,
            "default": "MinRisk",
            "choices": OBJECTIVE_CHOICES,
        },
}
