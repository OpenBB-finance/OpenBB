"""Banxico historical USD/MXN FIX exchange-rate model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from dateutil.relativedelta import relativedelta
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import field_validator

BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
USD_MXN_FIX_SERIES_ID = "SF43718"


class BanxicoCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Banxico historical USD/MXN FIX exchange-rate query.

    Banxico's SF43718 series is the official Mexican peso per U.S. dollar FIX
    exchange rate.
    """

    @field_validator("symbol", mode="after")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        """Restrict the first version of this provider to the supported pair."""
        value = value.upper().replace("-", "")
        if value != "USDMXN":
            raise ValueError("Banxico currently supports only the USDMXN currency pair.")
        return value


class BanxicoCurrencyHistoricalData(CurrencyHistoricalData):
    """Banxico historical USD/MXN FIX exchange-rate data."""


class BanxicoCurrencyHistoricalFetcher(
    Fetcher[
        BanxicoCurrencyHistoricalQueryParams,
        list[BanxicoCurrencyHistoricalData],
    ]
):
    """Fetch and normalize Banxico's historical USD/MXN FIX exchange rate."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> BanxicoCurrencyHistoricalQueryParams:
        """Validate query parameters and apply a one-year default date range."""
        transformed_params = params.copy()
        today = datetime.now().date()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = today - relativedelta(years=1)
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = today
        return BanxicoCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: BanxicoCurrencyHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Request raw observations from Banxico's SIE REST API."""
        api_key = credentials.get("banxico_api_key") if credentials else ""
        if not api_key:
            raise OpenBBError(
                "A Banxico API token is required. Configure the 'banxico_api_key' credential before making this request."
            )

        start_date = query.start_date.isoformat() if query.start_date else ""
        end_date = query.end_date.isoformat() if query.end_date else ""
        url = f"{BASE_URL}/{USD_MXN_FIX_SERIES_ID}/datos/{start_date}/{end_date}"
        response = make_request(url, headers={"Bmx-Token": api_key})

        if response.status_code != 200:
            raise OpenBBError(f"Failed to fetch data from Banxico. Status code: {response.status_code}.")

        try:
            series = response.json()["bmx"]["series"]
            return series[0]["datos"]
        except (IndexError, KeyError, TypeError, ValueError) as error:
            raise OpenBBError("Banxico returned an unexpected response format.") from error

    @staticmethod
    def transform_data(
        query: BanxicoCurrencyHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[BanxicoCurrencyHistoricalData]:
        """Map Banxico's Spanish response fields to OpenBB's standard schema."""
        return [
            BanxicoCurrencyHistoricalData.model_validate(
                {
                    "date": datetime.strptime(observation["fecha"], "%d/%m/%Y").date(),
                    "close": observation["dato"],
                }
            )
            for observation in data
            if observation.get("dato") not in {None, "N/E"}
        ]
