"""Federal Reserve Bank of Dallas Energy Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://www.dallasfed.org/~/media/Documents/research/surveys/des/documents"

# (table, transform) -> workbook filename. Price tables ignore the transform.
_FILES = {
    ("index", "quarter_over_quarter"): "index_qq.xlsx",
    ("index", "year_over_year"): "index_yy.xlsx",
    ("all_data", "quarter_over_quarter"): "all_data_qq.xlsx",
    ("all_data", "year_over_year"): "all_data_yy.xlsx",
    ("price_expectations", "quarter_over_quarter"): "all_data_price_expectations.xlsx",
    ("price_expectations", "year_over_year"): "all_data_price_expectations.xlsx",
    ("price_forecasts", "quarter_over_quarter"): "all_data_price_forecasts.xlsx",
    ("price_forecasts", "year_over_year"): "all_data_price_forecasts.xlsx",
}

_SHEETS = {
    "all": "All Firms",
    "exploration_production": "E+P Firms",
    "support_services": "O+G Support Services Firms",
}


class FederalReserveDallasEnergyQueryParams(QueryParams):
    """Dallas Fed Energy Survey Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Diffusion Indexes", "value": "index"},
                    {"label": "All Data", "value": "all_data"},
                    {"label": "Price Expectations", "value": "price_expectations"},
                    {"label": "Price Forecasts", "value": "price_forecasts"},
                ]
            }
        },
        "transform": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Quarter Over Quarter",
                        "value": "quarter_over_quarter",
                    },
                    {"label": "Year Over Year", "value": "year_over_year"},
                ]
            }
        },
        "firm_group": {
            "x-widget_config": {
                "options": [
                    {"label": sheet, "value": code} for code, sheet in _SHEETS.items()
                ]
            }
        },
    }

    table: Literal["index", "all_data", "price_expectations", "price_forecasts"] = (
        Field(
            default="index",
            description="The diffusion indexes, the full data including response"
            " shares, the oil and gas price expectations, or the price-level"
            " forecasts (reference, average, median, range).",
        )
    )
    transform: Literal["quarter_over_quarter", "year_over_year"] = Field(
        default="quarter_over_quarter",
        description="Compare to the prior quarter or to a year ago. Ignored for the"
        " price tables.",
    )
    firm_group: Literal["all", "exploration_production", "support_services"] = Field(
        default="all",
        description="The respondent firm group: all firms, exploration and"
        + " production firms, or oilfield services firms. The price forecasts cover"
        + " all firms only.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasEnergyData(Data):
    """Dallas Fed Energy Survey Data.

    One row per quarter-end date, with one column per survey indicator carrying
    that indicator's value. The indicators of the selected table, transform, and
    firm group are pivoted to wide, so the columns vary with the request.
    """

    date: dateType = Field(description="The survey quarter end date.")


class FederalReserveDallasEnergyFetcher(
    Fetcher[
        FederalReserveDallasEnergyQueryParams,
        list[FederalReserveDallasEnergyData],
    ]
):
    """Dallas Fed Energy Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasEnergyQueryParams:
        """Transform the query params."""
        return FederalReserveDallasEnergyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasEnergyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Energy Survey workbook."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        filename = _FILES[(query.table, query.transform)]

        def _producer() -> bytes:
            """Fetch the raw survey workbook bytes."""
            response = make_request(f"{BASE_URL}/{filename}")
            response.raise_for_status()
            return response.content

        content = cached(
            ("dallas_energy", filename),
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasEnergyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasEnergyData]:
        """Melt the firm group's sheet, then pivot indicators to wide rows."""
        from openbb_federal_reserve.utils.dallas_survey import parse_energy_long
        from openbb_federal_reserve.utils.workbook import pivot_wide

        # The price forecasts workbook carries only the all-firms sheet.
        sheet = _SHEETS[query.firm_group]
        if query.table == "price_forecasts":
            sheet = _SHEETS["all"]
        records = parse_energy_long(
            data[0]["_raw"],
            sheet,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(records, index="date", column="indicator", value="value")
        return [
            FederalReserveDallasEnergyData.model_validate(record) for record in rows
        ]
