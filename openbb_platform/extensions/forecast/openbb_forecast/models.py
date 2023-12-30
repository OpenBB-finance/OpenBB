"""Forecast Models."""
from typing import Any, List

from openbb_core.provider.abstract.data import Data
from pydantic import BaseModel, Field


class QuantileAnomalyModel(BaseModel):
    """Pydantic model for quantile anomaly detection."""

    ticker_series: List[Data]
    anomaly_score: List[Data]
    binary_anomaly_prediction: List[Data]


class StatisticalForecastModel(BaseModel):
    """Pydantic model for forecasting based on statistical analysis."""

    ticker_series: List[Data]
    historical_forecast: List[Data]
    forecast: List[Data]
    precision: float
    forecast_model: Any = Field(
        default=None,
        description="The model object.",
        json_schema_extra={"exclude_from_api": True},
    )


class TorchForecastModel(StatisticalForecastModel):
    """Pydantic model for forecasting based on learning models."""

    forecast_model: Any = Field(
        default=None,
        description="The model object.",
        json_schema_extra={"exclude_from_api": True},
    )
