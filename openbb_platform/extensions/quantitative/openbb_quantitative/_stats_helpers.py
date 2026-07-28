"""Statistical compute helpers for the quantitative extension."""

from numpy import (
    mean as mean_np,
    ndarray,
    std as std_np,
    var as var_np,
)
from pandas import DataFrame, Series
from scipy import stats


def kurtosis_(data: DataFrame | Series | ndarray) -> float:
    """Compute kurtosis - the tailedness of a distribution."""
    return float(stats.kurtosis(data))


def skew_(data: DataFrame | Series | ndarray) -> float:
    """Compute skewness - the asymmetry of a distribution about its mean."""
    return float(stats.skew(data))


def mean_(data: DataFrame | Series | ndarray) -> float:
    """Compute the arithmetic mean."""
    return float(mean_np(data))


def std_dev_(data: DataFrame | Series | ndarray) -> float:
    """Compute the standard deviation - the dispersion of a set of values."""
    return float(std_np(data))


def var_(data: DataFrame | Series | ndarray) -> float:
    """Compute the variance - the squared dispersion of a set of values."""
    return float(var_np(data))
