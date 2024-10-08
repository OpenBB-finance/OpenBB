"""Intrinio ETF Holdings Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_request,
)
from pydantic import Field, model_validator


class IntrinioEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """
    Intrinio ETF Holdings Query Params.

    Source: https://docs.intrinio.com/documentation/web_api/get_etf_holdings_v2
    """

    __alias_dict__ = {"date": "as_of_date"}

    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )


class IntrinioEtfHoldingsData(EtfHoldingsData):
    """Intrinio ETF Holdings Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "security_type": "type",
        "unit": "quantity_units",
        "face_value": "face",
        "balance": "quantity_held",
        "value": "market_value_held",
        "derivatives_value": "notional_value",
        "units_per_share": "quantity_per_share",
        "weight": "weighting",
        "updated": "as_of_date",
        "country": "location",
        "maturity_date": "maturity",
    }

    name: Optional[str] = Field(
        default=None,
        description="The common name for the holding.",
    )
    security_type: Optional[str] = Field(
        default=None,
        description="The type of instrument for this holding. Examples(Bond='BOND', Equity='EQUI')",
    )
    isin: Optional[str] = Field(
        default=None,
        description="The International Securities Identification Number.",
    )
    ric: Optional[str] = Field(
        default=None,
        description="The Reuters Instrument Code.",
    )
    sedol: Optional[str] = Field(
        default=None,
        description="The Stock Exchange Daily Official List.",
    )
    share_class_figi: Optional[str] = Field(
        default=None,
        description="The OpenFIGI symbol for the holding.",
    )
    country: Optional[str] = Field(
        default=None,
        description="The country or region of the holding.",
    )
    maturity_date: Optional[dateType] = Field(
        default=None,
        description="The maturity date for the debt security, if available.",
    )
    contract_expiry_date: Optional[dateType] = Field(
        default=None,
        description="Expiry date for the futures contract held, if available.",
    )
    coupon: Optional[float] = Field(
        default=None,
        description="The coupon rate of the debt security, if available.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    balance: Optional[Union[int, float]] = Field(
        default=None,
        description="The number of units of the security held, if available.",
    )
    unit: Optional[str] = Field(
        default=None,
        description="The units of the 'balance' field.",
    )
    units_per_share: Optional[float] = Field(
        default=None,
        description="Number of units of the security held per share outstanding of the ETF, if available.",
    )
    face_value: Optional[float] = Field(
        default=None,
        description="The face value of the debt security, if available.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    derivatives_value: Optional[float] = Field(
        default=None,
        description="The notional value of derivatives contracts held.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    value: Optional[float] = Field(
        default=None,
        description="The market value of the holding, on the 'as_of' date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    weight: Optional[float] = Field(
        default=None,
        description="The weight of the holding, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    updated: Optional[dateType] = Field(
        default=None,
        description="The 'as_of' date for the holding.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class IntrinioEtfHoldingsFetcher(
    Fetcher[IntrinioEtfHoldingsQueryParams, List[IntrinioEtfHoldingsData]]
):
    """Intrinio ETF Holdings Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEtfHoldingsQueryParams:
        """Transform query."""
        return IntrinioEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        symbol = query.symbol + ":US" if ":" not in query.symbol else query.symbol
        URL = f"https://api-v2.intrinio.com/etfs/{symbol}/holdings?page_size=10000&api_key={api_key}"
        if query.date:
            URL += f"&as_of_date={query.date}"
        data: List = []

        async def response_callback(response: ClientResponse, session: ClientSession):
            """Async response callback."""
            results = await response.json()

            if results.get("error"):  # type: ignore
                return results

            if results.get("holdings") and len(results.get("holdings")) > 0:  # type: ignore
                data.extend(results.get("holdings"))  # type: ignore
                while results.get("next_page"):  # type: ignore
                    next_page = results["next_page"]  # type: ignore
                    next_url = f"{URL}&next_page={next_page}"
                    results = await amake_request(next_url, session=session, **kwargs)
                    if (
                        "holdings" in results
                        and len(results.get("holdings")) > 0  # type: ignore
                    ):
                        data.extend(results.get("holdings"))  # type: ignore
            return data

        return await amake_request(URL, response_callback=response_callback, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: IntrinioEtfHoldingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioEtfHoldingsData]:
        """Transform data."""
        if not data or isinstance(data, dict) and data.get("error"):
            if isinstance(data, list) and data == []:
                raise OpenBBError(
                    str(
                        f"No holdings were found for {query.symbol}, and the response from Intrinio was empty."
                    )
                )
            raise OpenBBError(str(f"{data.get('message')} {query.symbol}: {data['error']}"))  # type: ignore

        results: List[IntrinioEtfHoldingsData] = []
        for d in sorted(data, key=lambda x: x["weighting"], reverse=True):
            # This field is deprecated and is dupilcated in the response.
            _ = d.pop("composite_figi", None)
            if d.get("coupon"):
                d["coupon"] = d["coupon"] / 100
            results.append(IntrinioEtfHoldingsData.model_validate(d))

        return results
