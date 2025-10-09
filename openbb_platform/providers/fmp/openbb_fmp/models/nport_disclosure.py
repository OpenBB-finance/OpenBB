"""FMP ETF Holdings Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.nport_disclosure import (
    NportDisclosureData,
    NportDisclosureQueryParams,
)
from pydantic import Field, field_validator


class FMPNportDisclosureQueryParams(NportDisclosureQueryParams):
    """FMP ETF Holdings Query.

    Source: https://site.financialmodelingprep.com/developer/docs#holdings
    """


class FMPNportDisclosureData(NportDisclosureData):
    """FMP ETF Holdings Data."""

    __alias_dict__ = {
        "weight": "pctVal",
        "value": "valUsd",
        "asset_category": "assetCat",
        "issuer_category": "issuerCat",
        "country": "invCountry",
        "currency": "cur_cd",
        "as_of": "date",
        "is_restricted": "isRestrictedSec",
        "fair_value_level": "fairValLevel",
    }

    as_of: dateType | None = Field(
        description="The acceptance datetime of the filing.",
        default=None,
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) / 100 if v else None

    @field_validator(
        "cusip",
        "isin",
        "balance",
        "name",
        "symbol",
        "value",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def replace_empty(cls, v):
        """Replace empty strings and 0s with None."""
        if isinstance(v, str):
            return v if v not in ("", "0", "-", "N/A") else None
        if isinstance(v, (float, int)):
            return v if v and v not in (0.0, 0) else None
        return v if v else None


class FMPNportDisclosureFetcher(
    Fetcher[
        FMPNportDisclosureQueryParams,
        list[FMPNportDisclosureData],
    ]
):
    """FMP NPORT Disclosure Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPNportDisclosureQueryParams:
        """Transform the query."""
        return FMPNportDisclosureQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPNportDisclosureQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many
        from pandas import Timestamp

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = "https://financialmodelingprep.com/stable/funds/disclosure?"

        if query.symbol.isnumeric():
            url += f"cik={query.symbol}"
        else:
            url += f"symbol={query.symbol}"

        now = Timestamp("now")

        if not query.year:
            query.year = now.year
        if not query.quarter:
            if now.quarter == 1:
                query.year -= 1
                query.quarter = 4
            else:
                query.quarter = now.quarter - 1

        url += f"&year={query.year}&quarter={query.quarter}&apikey={api_key}"

        return await get_data_many(url, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPNportDisclosureQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPNportDisclosureData]:
        """Return the transformed data."""
        results: list[FMPNportDisclosureData] = []
        for d in data:
            new_d = {k: v for k, v in d.items() if k not in ("cik", "acceptedDate")}
            results.append(FMPNportDisclosureData.model_validate(new_d))

        return sorted(results, key=lambda x: (x.weight or 0), reverse=True)
