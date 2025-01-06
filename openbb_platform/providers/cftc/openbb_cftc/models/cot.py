"""CFTC Commitment of Traders Reports Model."""

# pylint: disable=unused-argument

from datetime import (
    datetime,
)
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot import COTData, COTQueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

reports_dict = {
    "legacy_futures_only": "6dca-aqww",
    "legacy_combined": "jun7-fc8e",
    "disaggregated_futures_only": "72hh-3qpy",
    "disaggregated_combined": "kh3c-gbw2",
    "tff_futures_only": "gpe5-46if",
    "tff_combined": "yw9f-hn96",
    "supplemental": "4zgm-a668",
}


class CftcCotQueryParams(COTQueryParams):
    """CFTC Commitment of Traders Reports Query Parameters.

    Source: https://publicreporting.cftc.gov/stories/s/r4w3-av2u
    """

    __json_schema_extra__ = {
        "report_type": {
            "multiple_items_allowed": False,
            "choices": ["legacy", "disaggregated", "financial", "supplemental"],
        }
    }

    report_type: Literal["legacy", "disaggregated", "financial", "supplemental"] = (
        Field(
            default="legacy",
            description="""The type of report to retrieve. Set `id` as 'all' to return all items in the report
            type (default date range returns the latest report). The Legacy report is broken down by exchange
            with reported open interest further broken down into three trader classifications: commercial,
            non-commercial and non-reportable. The Disaggregated reports are broken down by Agriculture and
            Natural Resource contracts. The Disaggregated reports break down reportable open interest positions
            into four classifications: Producer/Merchant, Swap Dealers, Managed Money and Other Reportables.
            The Traders in Financial Futures (TFF) report includes financial contracts. The TFF report breaks
            down the reported open interest into five classifications: Dealer, Asset Manager, Leveraged Money,
            Other Reportables and Non-Reportables.""",
        )
    )
    futures_only: bool = Field(
        default=False,
        description="Returns the futures-only report. Default is False, for the combined report.",
    )


class CftcCotData(COTData):
    """CFTC Commitment of Traders Reports Data."""

    __alias_dict__ = {
        "date": "report_date_as_yyyy_mm_dd",
        "report_week": "yyyy_report_week_ww",
        "commodity_group": "commodity_group_name",
        "commodity": "commodity_name",
        "commodity_subgroup": "commodity_subgroup_name",
    }


class CftcCotFetcher(Fetcher[CftcCotQueryParams, list[CftcCotData]]):
    """CFTC Commitment of Traders Reports Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotQueryParams:
        """Transform query parameters."""
        return CftcCotQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the CFTC API."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta  # noqa
        from openbb_core.provider.utils.helpers import amake_request

        app_token = credentials.get("cftc_app_token") if credentials else ""

        today = datetime.now()
        # If the ID is a CFTC code, we'll get the complete history by default.
        _start = (
            (today - timedelta(days=(today.weekday() - 1) % 7)).strftime("%Y-%m-%d")
            if query.id in (500, "500") or not query.id[:3].isdigit()
            else "1995-01-01"
        )
        start_date = (
            query.start_date.strftime("%Y-%m-%d") if query.start_date else _start
        )
        end_date = (
            query.end_date.strftime("%Y-%m-%d")
            if query.end_date
            else f"{today.year}-12-31"
        )
        date_range = (
            f"$where=Report_Date_as_YYYY_MM_DD between '{start_date}' AND '{end_date}'"
        )
        report_type = query.report_type.replace("financial", "tff")
        if query.futures_only is True and report_type != "supplemental":
            report_type += "_futures_only"
        elif query.futures_only is False and report_type != "supplemental":
            report_type += "_combined"

        query.id = "" if query.id == "all" else query.id
        if not query.id[:3].isdigit():
            query.id = f"%{query.id}%"
        query.id = query.id.replace("+", "%2B").replace("&", "%26")
        base_url = f"https://publicreporting.cftc.gov/resource/{reports_dict[report_type]}.json?$limit=1000000&{date_range}"
        order = "&$order=Report_Date_as_YYYY_MM_DD ASC"
        url = (
            (
                f"{base_url}"
                f" AND (UPPER(contract_market_name) like UPPER('{query.id}') "
                f"OR UPPER(commodity) like UPPER('{query.id}') "
                f"OR UPPER(cftc_contract_market_code) like UPPER('{query.id}') "
                f"OR UPPER(commodity_group_name) like UPPER('{query.id}') "
                f"OR UPPER(commodity_subgroup_name) like UPPER('{query.id}'))"
            )
            if query.id
            else base_url
        )
        url = f"{url}{order}"

        if app_token:
            url += f"&$$app_token={app_token}"

        try:
            response = await amake_request(url, **kwargs)
        except OpenBBError as error:
            raise error from error

        if not response:
            raise EmptyDataError(f"No data found for {query.id.replace('%', '')}.")

        return response  # type: ignore

    @staticmethod
    def transform_data(
        query: CftcCotQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CftcCotData]:
        """Transform and validate the data."""
        response = data.copy()
        string_cols = [
            "market_and_exchange_names",
            "cftc_contract_market_code",
            "cftc_market_code",
            "cftc_region_code",
            "cftc_commodity_code",
            "cftc_contract_market_code_quotes",
            "cftc_market_code_quotes",
            "cftc_commodity_code_quotes",
            "cftc_subgroup_code",
            "commodity_group_name",
            "commodity",
            "commodity_name",
            "commodity_subgroup_name",
            "contract_units",
            "report_date_as_yyyy_mm_dd",
            "yyyy_report_week_ww",
            "id",
            "futonly_or_combined",
        ]
        results: list[CftcCotData] = []
        for values in response:
            new_values: dict = {}
            for key, value in values.items():
                if key in string_cols and value:
                    new_values[key.lower()] = str(value)
                elif key == "report_date_as_yyyy_mm_dd":
                    new_values["report_date_as_yyyy_mm_dd"] = value.split("T")[0]
                elif key.lower().startswith("pct_") and value:
                    new_values[key.lower().replace("__", "_")] = float(value) / 100
                elif key.lower().startswith("conc_") and value:
                    new_values[key.lower().replace("__", "_")] = float(value)
                elif value:
                    try:
                        new_values[key.lower().replace("__", "_")] = int(value)
                    except ValueError:
                        new_values[key.lower().replace("__", "_")] = value

            if new_values:
                results.append(CftcCotData.model_validate(new_values))

        return results
