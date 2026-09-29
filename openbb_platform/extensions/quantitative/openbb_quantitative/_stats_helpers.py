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
    """Compute the excess kurtosis."""
    return float(stats.kurtosis(data))


def skew_(data: DataFrame | Series | ndarray) -> float:
    """Compute the skewness."""
    return float(stats.skew(data))


def mean_(data: DataFrame | Series | ndarray) -> float:
    """Compute the arithmetic mean."""
    return float(mean_np(data))


def std_dev_(data: DataFrame | Series | ndarray) -> float:
    """Compute the sample standard deviation."""
    return float(std_np(data, ddof=1))


def var_(data: DataFrame | Series | ndarray) -> float:
    """Compute the sample variance."""
    return float(var_np(data, ddof=1))
