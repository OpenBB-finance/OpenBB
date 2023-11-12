from typing import List, Any
from pydantic import BaseModel, Field

from openbb_provider.abstract.data import Data

from pydantic import BaseModel, ConfigDict, Field


class QuantileAnomalyModel(BaseModel):
    ticker_series: List[Data]
    anomaly_score: List[Data]
    binary_anomaly_prediction: List[Data]


class StatisticalForecastModel(BaseModel):
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
    forecast_model: Any = Field(
        default=None,
        description="The model object.",
        json_schema_extra={"exclude_from_api": True},
    )
