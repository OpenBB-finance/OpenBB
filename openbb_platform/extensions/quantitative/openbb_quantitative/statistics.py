"""Statistics Functions"""

from typing import Union

from numpy import (
    mean as mean_,
    ndarray,
    std,
    var as var_,
)
from pandas import DataFrame, Series
from scipy import stats


def kurtosis(data: Union[DataFrame, Series, ndarray]) -> float:
    """Kurtosis is a measure of the "tailedness" of the probability distribution of a real-valued random variable."""
    return stats.kurtosis(data)


def skew(data: Union[DataFrame, Series, ndarray]) -> float:
    """Skewness is a measure of the asymmetry of the probability distribution of a
    real-valued random variable about its mean."""
    return stats.skew(data)


def mean(data: Union[DataFrame, Series, ndarray]) -> float:
    """Mean is the average of the numbers."""
    return mean_(data)


def std_dev(data: Union[DataFrame, Series, ndarray]) -> float:
    """Standard deviation is a measure of the amount of variation or dispersion of a set of values."""
    return std(data)


def var(data: Union[DataFrame, Series, ndarray]) -> float:
    """Variance is a measure of the amount of variation or dispersion of a set of values."""
    return var_(data)
