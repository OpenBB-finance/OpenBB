"""SEC Form 13F-HR Model."""

# pylint: disable =unused-argument

import asyncio
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.form_13FHR import (
    Form13FHRData,
    Form13FHRQueryParams,
)
from openbb_sec.utils import parse_13f
from pydantic import Field


class SecForm13FHRQueryParams(Form13FHRQueryParams):
    """SEC Form 13F-HR Query Params.

    Source: https://www.sec.gov/Archives/edgar/data/
    """


class SecForm13FHRData(Form13FHRData):
    """SEC Form 13F-HR Data."""

    __alias_dict__ = {
        "issuer": "nameOfIssuer",
        "asset_class": "titleOfClass",
        "option_type": "putCall",
    }

    weight: float = Field(
        description="The weight of the security relative to the market value of all securities in the filing"
        + " , as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class SecForm13FHRFetcher(Fetcher[SecForm13FHRQueryParams, List[SecForm13FHRData]]):
    """SEC Form 13F-HR Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecForm13FHRQueryParams:
        """Transform the query."""
        return SecForm13FHRQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecForm13FHRQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the SEC endpoint."""
        symbol = query.symbol
        urls = []
        cik = symbol.isnumeric()
        filings = (
            await parse_13f.get_13f_candidates(symbol=symbol)
            if cik is False
            else await parse_13f.get_13f_candidates(cik=symbol)
        )
        if query.limit and query.date is None:
            urls = filings.iloc[: query.limit].to_list()
        if query.date is not None:
            date = parse_13f.date_to_quarter_end(query.date.strftime("%Y-%m-%d"))
            urls = [filings.loc[date]]

        results = []

        async def get_filing(url):
            """Get a single 13F-HR filing and parse it."""

            data = await parse_13f.parse_13f_hr(url)

            if len(data) > 0:
                results.extend(data.to_dict("records"))

        await asyncio.gather(*[get_filing(url) for url in urls])

        return sorted(
            results, key=lambda d: [d["period_ending"], d["weight"]], reverse=True
        )

    @staticmethod
    def transform_data(
        query: SecForm13FHRQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[SecForm13FHRData]:
        """Transform the data."""
        return [SecForm13FHRData.model_validate(d) for d in data]
