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
