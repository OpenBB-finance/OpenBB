"""Federal Reserve Bank of Philadelphia Nonmanufacturing Business Outlook Model."""

import re
from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/surveys-and-data/nbos/nboshistory.xlsx"

# adjustment -> (sheet, seasonal adjustment label)
_TABLES = {
    "sa": ("Responses_and_diffusion", "Seasonally Adjusted"),
    "nsa": ("NSA", "Not Seasonally Adjusted"),
}

_INDICATORS = {
    "gar": "General Activity (Region)",
    "ga": "General Activity (Firm)",
    "no": "New Orders",
    "sr": "Sales or Revenues",
    "uo": "Unfilled Orders",
    "iv": "Inventories",
    "pp": "Prices Paid",
    "pr": "Prices Received",
    "nf": "Number of Full-Time Employees",
    "np": "Number of Part-Time Employees",
    "aw": "Average Workweek",
    "wb": "Wages and Benefits",
    "cp": "Capital Expenditures - Physical Plant",
    "ce": "Capital Expenditures - Equipment and Software",
}
# The general-activity questions also carry a six-month-ahead (future) variant,
# encoded by appending ``f`` to the prefix.
_FUTURE = {"garf": "General Activity (Region)", "gaf": "General Activity (Firm)"}
_RESPONSES = {
    "inc": "increase",
    "nc": "no change",
    "dec": "decrease",
    "dif": "diffusion index",
}


def _decode(code: str) -> dict[str, str] | None:
    """Decode a ``{indicator}bn{response}`` column into labelled parts."""
    match = re.match(r"^([a-z]+?)bn(inc|nc|dec|dif)$", code.lower().split("_")[0])
    if not match:
        return None
    prefix, response = match.group(1), match.group(2)
    if prefix in _INDICATORS:
        return {
            "indicator": _INDICATORS[prefix],
            "horizon": "Current",
            "response": _RESPONSES[response],
        }
    if prefix in _FUTURE:
        return {
            "indicator": _FUTURE[prefix],
            "horizon": "Expectations (Six Months Ahead)",
            "response": _RESPONSES[response],
        }
    return None


class FederalReservePhiladelphiaNonmanufacturingQueryParams(QueryParams):
    """Philadelphia Fed Nonmanufacturing Business Outlook Query Parameters."""

    __json_schema_extra__ = {
        "adjustment": {
            "x-widget_config": {
                "options": [
                    {"label": "Seasonally Adjusted", "value": "sa"},
                    {"label": "Not Seasonally Adjusted", "value": "nsa"},
                ]
            }
        }
    }

    adjustment: Literal["sa", "nsa"] = Field(
        default="sa",
        description="The seasonally-adjusted or not-seasonally-adjusted series;"
        " each carries both the diffusion indexes and the increase/no-change/"
        "decrease response shares.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaNonmanufacturingData(Data):
    """Philadelphia Fed Nonmanufacturing Business Outlook Survey Data.

    One row per survey month, with one column per
    ``indicator - horizon - response`` series carrying that series' value for the
    selected seasonal adjustment. The series are pivoted to wide columns.
    """

    date: dateType = Field(description="The survey month, as a month-start date.")


class FederalReservePhiladelphiaNonmanufacturingFetcher(
    Fetcher[
        FederalReservePhiladelphiaNonmanufacturingQueryParams,
        list[FederalReservePhiladelphiaNonmanufacturingData],
    ]
):
    """Philadelphia Fed Nonmanufacturing Business Outlook Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaNonmanufacturingQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaNonmanufacturingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaNonmanufacturingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the nonmanufacturing survey workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "nbos_diffusion", "monthly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaNonmanufacturingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaNonmanufacturingData]:
        """Decode the sheet, then pivot the series to wide ``date`` rows."""
        from pandas import isna, to_datetime, to_numeric

        from openbb_federal_reserve.utils.philadelphia import read_workbook
        from openbb_federal_reserve.utils.workbook import pivot_wide

        sheet, _ = _TABLES[query.adjustment]
        frame = read_workbook(data[0]["_raw"], sheet)
        frame = frame.rename(columns={frame.columns[0]: "date"})
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        decoded: dict[Any, dict[str, Any]] = {}
        for column in frame.columns:
            if column == "date":
                continue
            result = _decode(str(column))
            if result:
                decoded[column] = result
        records: list[dict[str, Any]] = []
        for column, parts in decoded.items():
            series = to_numeric(frame[column], errors="coerce")
            label = f"{parts['indicator']} - {parts['horizon']} - {parts['response']}"
            for observation, value in zip(frame["date"], series):
                if query.start_date and observation < query.start_date:
                    continue
                if query.end_date and observation > query.end_date:
                    continue
                records.append(
                    {
                        "date": observation,
                        "series": label,
                        "value": None if isna(value) else float(value),
                    }
                )

        rows = pivot_wide(
            sorted(records, key=lambda r: (r["date"], r["series"])),
            index="date",
            column="series",
            value="value",
        )
        return [
            FederalReservePhiladelphiaNonmanufacturingData.model_validate(row)
            for row in rows
        ]
