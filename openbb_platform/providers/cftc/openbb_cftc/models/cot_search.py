"""CFTC Commitment of Traders Reports Search Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class CftcCotSearchQueryParams(CotSearchQueryParams):
    """CFTC Commitment of Traders Reports Search Query.

    Source: https://publicreporting.cftc.gov/stories/s/r4w3-av2u
    """

    __json_schema_extra__ = {
        "report_type": {
            "multiple_items_allowed": False,
            "choices": ["legacy", "disaggregated", "financial", "supplemental"],
        },
        "category": {
            "multiple_items_allowed": False,
            "choices": [
                "agriculture",
                "financial_instruments",
                "natural_resources",
            ],
        },
        "subcategory": {
            "multiple_items_allowed": False,
            "choices": [
                "base_metals",
                "chemicals",
                "currency",
                "currency_non_major",
                "dairy_products",
                "digital_asset",
                "digital_asset_non_major",
                "electricity_and_sources",
                "emissions",
                "fertilizer",
                "fiber",
                "foodstuffs_softs",
                "grains",
                "interest_rate_swaps",
                "interest_rates_non_us_treasury",
                "interest_rates_us_treasury",
                "livestock_meat_products",
                "natural_gas_and_products",
                "oilseed_and_products",
                "other_agricultural",
                "other_financial_instruments",
                "petroleum_and_products",
                "precious_metals",
                "stock_indices",
                "weather",
                "wood_products",
                "yield_insurance",
            ],
        },
    }

    report_type: Literal["legacy", "disaggregated", "financial", "supplemental"] = (
        Field(
            default="legacy",
            description="The report type to search within.",
        )
    )
    futures_only: bool = Field(
        default=False,
        description="Search the futures-only report. Default is False, for the combined report.",
    )
    category: str | None = Field(
        default=None,
        description="Filter by commodity group name."
        " Underscores are replaced with spaces. E.g, 'natural_resources' -> 'NATURAL RESOURCES'.",
    )
    subcategory: str | None = Field(
        default=None,
        description="Filter by commodity subgroup name."
        " Underscores are replaced with spaces. E.g, 'precious_metals' -> 'PRECIOUS METALS'.",
    )


class CftcCotSearchData(CotSearchData):
    """CFTC Commitment of Traders Reports Search Data."""

    __alias_dict__ = {
        "code": "cftc_contract_market_code",
        "name": "contract_market_name",
        "category": "commodity_group_name",
        "subcategory": "commodity_subgroup_name",
    }

    commodity: str | None = Field(default=None, description="Name of the commodity.")


class CftcCotSearchFetcher(Fetcher[CftcCotSearchQueryParams, list[CftcCotSearchData]]):
    """CFTC COT Search Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotSearchQueryParams:
        """Transform the query params."""
        return CftcCotSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Search CFTC Commitment of Traders Reports via the live API."""
        # pylint: disable=import-outside-toplevel
        from urllib.parse import quote

        from openbb_cftc.utils import reports_dict
        from openbb_core.provider.utils.helpers import amake_request

        app_token = credentials.get("cftc_app_token") if credentials else ""

        report_type = query.report_type.replace("financial", "tff")
        if query.futures_only is True and report_type != "supplemental":
            report_type += "_futures_only"
        elif query.futures_only is False and report_type != "supplemental":
            report_type += "_combined"

        dataset_id = reports_dict[report_type]
        select_cols = (
            "cftc_contract_market_code,"
            "contract_market_name,"
            "commodity_name,"
            "commodity_group_name,"
            "commodity_subgroup_name,"
            "contract_units"
        )
        base_url = (
            f"https://publicreporting.cftc.gov/resource/{dataset_id}.json"
            f"?$select={select_cols}"
            f"&$group={select_cols}"
            "&$limit=50000"
            "&$order=commodity_group_name,commodity_subgroup_name,contract_market_name"
        )

        search_term = query.query
        where_parts: list[str] = []

        from datetime import datetime, timedelta

        cutoff = (datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d")
        where_parts.append(f"Report_Date_as_YYYY_MM_DD > '{cutoff}'")

        if search_term:
            escaped = search_term.replace("'", "''")
            where_parts.append(
                f"(UPPER(contract_market_name) like UPPER('%{escaped}%')"
                f" OR UPPER(cftc_contract_market_code) like UPPER('%{escaped}%')"
                f" OR UPPER(commodity_name) like UPPER('%{escaped}%')"
                f" OR UPPER(commodity_group_name) like UPPER('%{escaped}%')"
                f" OR UPPER(commodity_subgroup_name) like UPPER('%{escaped}%'))"
            )

        if query.category:
            cat = query.category.replace("_", " ").upper()
            where_parts.append(f"UPPER(commodity_group_name) = '{cat}'")

        if query.subcategory:
            subcategory_map = {
                "currency_non_major": "CURRENCY(NON-MAJOR)",
                "digital_asset_non_major": "DIGITAL ASSET (NON-MAJOR)",
                "foodstuffs_softs": "FOODSTUFFS/SOFTS",
                "interest_rates_non_us_treasury": "INTEREST RATES - NON U.S. TREASURY",
                "interest_rates_us_treasury": "INTEREST RATES - U.S. TREASURY",
                "livestock_meat_products": "LIVESTOCK/MEAT PRODUCTS",
                "oilseed_and_products": "OILSEED AND PRODUCTS",
            }
            sub = subcategory_map.get(
                query.subcategory,
                query.subcategory.replace("_", " ").upper(),
            )
            where_parts.append(f"UPPER(commodity_subgroup_name) = '{sub}'")

        if where_parts:
            base_url += "&$where=" + quote(" AND ".join(where_parts))

        url = f"{base_url}&$$app_token={app_token}" if app_token else base_url

        try:
            response = await amake_request(url, **kwargs)
        except OpenBBError as error:
            raise error from error

        if not response:
            raise EmptyDataError(
                f"No results found for '{search_term}'."
                if search_term
                else "No results returned from the CFTC API."
            )

        return response  # type: ignore

    @staticmethod
    def transform_data(
        query: CftcCotSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CftcCotSearchData]:
        """Transform the data."""
        results: list[CftcCotSearchData] = []
        seen: set[str] = set()
        for d in data:
            code = d.get("cftc_contract_market_code", "")
            if code and code not in seen:
                seen.add(code)
                name = d.get("commodity_name", "")

                if "commodity_group_name" not in list(
                    d
                ) and name.strip().upper().endswith("INDICES"):
                    category = "FINANCIAL INSTRUMENTS"
                    subcategory = "STOCK INDICES"
                    d["commodity_group_name"] = category
                    d["commodity_subgroup_name"] = subcategory
                elif (
                    "commodity_group_name" not in list(d)
                    and "CRYPTO" in name.strip().upper()
                ):
                    category = "FINANCIAL INSTRUMENTS"
                    subcategory = "DIGITAL ASSET (NON-MAJOR)"
                    d["commodity_group_name"] = category
                    d["commodity_subgroup_name"] = subcategory

                d["cftc_contract_market_code"] = f"CFTC_{code}"
                results.append(CftcCotSearchData.model_validate(d))

        return results
