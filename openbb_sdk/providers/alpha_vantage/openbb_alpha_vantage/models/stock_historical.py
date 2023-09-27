"""Alpha Vantage Stock End of Day fetcher."""


from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Literal, Optional, get_args

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_historical import (
    StockHistoricalData,
    StockHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS
from openbb_provider.utils.helpers import get_querystring
from pydantic import (
    Field,
    NonNegativeFloat,
    PositiveFloat,
    field_validator,
    model_validator,
)


class AVStockHistoricalQueryParams(StockHistoricalQueryParams):
    """Alpha Vantage Stock End of Day Query.

    Source: https://www.alphavantage.co/documentation/
    """

    __alias_dict__ = {"function_": "function"}

    function_: Literal[
        "TIME_SERIES_INTRADAY",
        "TIME_SERIES_DAILY",
        "TIME_SERIES_WEEKLY",
        "TIME_SERIES_MONTHLY",
        "TIME_SERIES_DAILY_ADJUSTED",
        "TIME_SERIES_WEEKLY_ADJUSTED",
        "TIME_SERIES_MONTHLY_ADJUSTED",
    ] = Field(
        description="The time series of your choice. ",
        default="TIME_SERIES_DAILY",
    )
    period: Optional[Literal["intraday", "daily", "weekly", "monthly"]] = Field(
        default="daily", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    interval: Optional[Literal["1min", "5min", "15min", "30min", "60min"]] = Field(
        description="Data granularity.",
        default="60min",
        json_schema_extra=dict(
            available_on_functions=["TIME_SERIES_INTRADAY"],
            required_on_functions=["TIME_SERIES_INTRADAY"],
        ),
    )
    adjusted: Optional[bool] = Field(
        description="Output time series is adjusted by historical split and dividend events.",
        default=False,
        json_schema_extra=dict(
            available_on_functions=["TIME_SERIES_INTRADAY"],
        ),
    )
    extended_hours: Optional[bool] = Field(
        description="Extended trading hours during pre-market and after-hours.",
        default=False,
        json_schema_extra=dict(
            available_on_functions=["TIME_SERIES_INTRADAY"],
        ),
    )
    month: Optional[str] = Field(
        description="Query a specific month in history (in YYYY-MM format).",
        default=None,
        json_schema_extra=dict(
            available_on_functions=["TIME_SERIES_INTRADAY"],
        ),
    )
    outputsize: Optional[Literal["compact", "full"]] = Field(
        description="Compact returns only the latest 100 data points in the intraday "
        "time series; full returns trailing 30 days of the most recent intraday data "
        "if the month parameter (see above) is not specified, or the full intraday "
        "data for a specific month in history if the month parameter is specified.",
        default="full",
        json_schema_extra=dict(
            available_on_functions=[
                "TIME_SERIES_INTRADAY",
                "TIME_SERIES_DAILY",
                "TIME_SERIES_DAILY_ADJUSTED",
            ],
        ),
    )

    @model_validator(mode="after")
    @classmethod
    def setup_function(
        cls, values: "AVStockHistoricalQueryParams"
    ):  # pylint: disable=E0213
        """Set the function based on the period."""
        functions_based_on_period = {
            "intraday": "TIME_SERIES_INTRADAY",
            "daily": "TIME_SERIES_DAILY",
            "weekly": "TIME_SERIES_WEEKLY",
            "monthly": "TIME_SERIES_MONTHLY",
        }
        values.function_ = functions_based_on_period[values.period]
        return values

    @model_validator(mode="after")
    @classmethod
    def adjusted_function_validate(
        cls, values: "AVStockHistoricalQueryParams"
    ):  # pylint: disable=E0213
        """
        Validate that the function is adjusted if the `adjusted` parameter is set to True.
        """

        if values.function_ != "TIME_SERIES_INTRADAY" and values.adjusted:
            values.function_ = f"{values.function_}_ADJUSTED"

        return values

    @model_validator(mode="after")
    @classmethod
    def on_functions_validate(
        cls, values: "AVStockHistoricalQueryParams"
    ):  # pylint: disable=E0213
        """
        Validate that the functions used on custom extra Field attributes
        `available_on_functions` and `required_on_functions` are valid functions.
        """
        custom_attributes = ["available_on_functions", "required_on_functions"]

        available_functions = get_args(cls.__annotations__["function_"])

        if values.function_ not in available_functions:
            raise ValueError(
                f"Function {values.function_} must be on of the following: {available_functions}"
            )

        def validate_functions(functions: List[str]):
            for f in functions:
                if f not in available_functions:
                    raise ValueError(
                        f"Function {f} must be on of the following: {available_functions}"
                    )

        for field in cls.__fields__.values():
            if (extra := field.json_schema_extra) is None:
                continue
            for attr in custom_attributes:
                if functions := extra.get(attr, None):
                    validate_functions(functions)

        return values

    @model_validator(mode="after")
    @classmethod
    def on_functions_criteria_validate(
        cls, values: "AVStockHistoricalQueryParams"
    ):  # pylint: disable=E0213
        """
        Validate that the fields are set to None if the function is not available
        and that the required fields are not None if the function is required.
        """

        timeseries = values.function_

        for name, field in cls.__fields__.items():
            if (extra := field.json_schema_extra) is None:
                continue

            field_value = getattr(values, name)
            if (
                available_on_functions := extra.get("available_on_functions", None)
            ) and timeseries not in available_on_functions:
                setattr(values, name, None)
            if (
                (required_on_functions := extra.get("required_on_functions", None))
                and timeseries in required_on_functions
                and field_value is None
            ):
                raise ValueError(f"Field {name} is required on function {timeseries}")

        return values

    @field_validator("month")
    def month_validate(cls, v):  # pylint: disable=E0213
        """Validate month, check if the month is in YYYY-MM format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m")
            except ValueError as e:
                raise e
        return v


class AVStockHistoricalData(StockHistoricalData):
    """Alpha Vantage Stock End of Day Data."""

    __alias_dict__ = {"date": "timestamp", "adj_close": "adjusted_close"}

    adj_close: Optional[PositiveFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("adj_close", "")
    )
    dividend_amount: Optional[NonNegativeFloat] = Field(
        default=None,
        description="Dividend amount paid for the corresponding date.",
    )
    split_coefficient: Optional[NonNegativeFloat] = Field(
        default=None,
        description="Split coefficient for the corresponding date.",
    )


class AVStockHistoricalFetcher(
    Fetcher[
        AVStockHistoricalQueryParams,
        List[AVStockHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Alpha Vantage endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AVStockHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return AVStockHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: AVStockHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Alpha Vantage endpoint."""
        api_key = credentials.get("alpha_vantage_api_key") if credentials else ""

        query_str = get_querystring(
            query.model_dump(by_alias=True), ["start_date", "end_date"]
        )

        url = f"https://www.alphavantage.co/query?{query_str}&datatype=csv&apikey={api_key}"
        get_data = requests.get(url, timeout=10)

        if "Information" in get_data.text:
            info = get_data.json()["Information"]
            raise ValueError(f"Alpha Vantage API Error: {info}")

        data = pd.read_csv(
            StringIO(get_data.text),
            parse_dates=["timestamp"],
        )

        data["timestamp"] = pd.to_datetime(data["timestamp"])

        data = data[
            (data["timestamp"] >= pd.to_datetime(query.start_date))
            & (data["timestamp"] <= pd.to_datetime(query.end_date))
        ]

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[AVStockHistoricalData]:
        """Transform the data to the standard format."""
        return [AVStockHistoricalData.model_validate(d) for d in data]
