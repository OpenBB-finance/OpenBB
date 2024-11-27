"""Form 13f Model."""

import asyncio
from datetime import date as dateType, datetime
from typing import Any, Dict, List, Optional
from warnings import warn

from pydantic import Field

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.form_13FHR import (
    Form13FHRData,
    Form13FHRQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback


class FMPForm13FHRQueryParams(Form13FHRQueryParams):
    """Form 13f Query Parameters.

    Source: https://financialmodelingprep.com/api/v3/form-thirteen/0001388838?date=2021-09-30
    """


class FMPForm13FHRData(Form13FHRData):
    """Form13 FHR Data Model."""

    __alias_dict__ = {
        "period_ending": "date",
        "issuer": "nameOfIssuer",
        "principal_amount": "shares",
        "asset_class": "titleOfClass",
        "filling_date": "fillingDate",
        "accepted_date": "acceptedDate",
        "symbol": "tickercusip",
        "final_link": "finalLink",
    }
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    filling_date: Optional[dateType] = Field(
        default=None, description="Date when the filing was submitted to the SEC."
    )
    accepted_date: Optional[dateType] = Field(
        default=None, description="Date when the filing was accepted by the SEC."
    )
    link: Optional[str] = Field(
        default=None, description="URL link to the SEC filing on the SEC website."
    )
    final_link: Optional[str] = Field(
        default=None,
        description="URL link to the XML information table of the SEC filing.",
    )


class FMPForm13FHRFetcher(
    Fetcher[
        FMPForm13FHRQueryParams,
        List[FMPForm13FHRData],
    ]
):
    """Fetches and transforms data from the Form 13f endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForm13FHRQueryParams:
        """Transform the query params."""
        return FMPForm13FHRQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPForm13FHRQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Form 13f endpoint."""
        """Return the raw data from the Form 13f endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbol = query.symbol
        if symbol.isnumeric():
            cik = symbol
        else:
            query.includeCurrentQuarter = "false"
            cik_url = create_url(
                4,
                f"institutional-ownership/symbol-ownership",
                api_key,
                query,
                exclude=["limit"],
            )
            cik = await amake_request(cik_url, response_callback=response_callback, **kwargs)
            if len(cik) == 0:
                raise EmptyDataError("Can't get cik for the given symbol.")
            cik = cik[0]["cik"]
            del query.includeCurrentQuarter
        date_url = create_url(
            3,
            f"form-thirteen-date/{cik}",
            api_key,
            query,
            exclude=["symbol", "limit"],
        )
        dates = await amake_request(date_url, response_callback=response_callback, **kwargs)
        if not dates:
            raise EmptyDataError("No data returned for the given symbol.")
        if not dates or len(dates) == 0:
            warn(f"Symbol Error: No data found for symbol {symbol}")
        results: List[Dict] = []

        async def get_one(date):
            """Get data for the given date."""
            date = datetime.strptime(date, "%Y-%m-%d").date()
            query.date = date
            url = create_url(
                3,
                f"form-thirteen/{cik}",
                api_key,
                query,
                exclude=["symbol", "limit"],
            )
            result = await amake_request(url, response_callback=response_callback, **kwargs)
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(date) for date in dates])

        if not results:
            raise EmptyDataError("No data returned for the given symbol.")
        if query.limit:
            return results[:query.limit]
        return results

    @staticmethod
    def transform_data(
        query: FMPForm13FHRQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPForm13FHRData]:
        """Return the transformed data."""
        if query.symbol.isnumeric():
            [d.pop("cik", None) for d in data]
        return [FMPForm13FHRData(**d) for d in data]
