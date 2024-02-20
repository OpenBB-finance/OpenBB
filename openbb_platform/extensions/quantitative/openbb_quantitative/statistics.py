"""Statistics Functions"""

from typing import Union

from numpy import (
    mean as mean_np,
    ndarray,
    std,
    var as var_np,
)
from pandas import DataFrame, Series
from scipy import stats

# Because python is weird and these being the same name as the fastapi router functions
# which overwrites the function signature, we add the _ after the function name


def kurtosis_(data: Union[DataFrame, Series, ndarray]) -> float:
    """Kurtosis is a measure of the "tailedness" of the probability distribution of a real-valued random variable."""
    return stats.kurtosis(data)


def skew_(data: Union[DataFrame, Series, ndarray]) -> float:
    """Skewness is a measure of the asymmetry of the probability distribution of a
    real-valued random variable about its mean."""
    return stats.skew(data)


def mean_(data: Union[DataFrame, Series, ndarray]) -> float:
    """Mean is the average of the numbers."""
    return mean_np(data)


def std_dev_(data: Union[DataFrame, Series, ndarray]) -> float:
    """Standard deviation is a measure of the amount of variation or dispersion of a set of values."""
    return std(data)


def var_(data: Union[DataFrame, Series, ndarray]) -> float:
    """Variance is a measure of the amount of variation or dispersion of a set of values."""
    return var_np(data)
