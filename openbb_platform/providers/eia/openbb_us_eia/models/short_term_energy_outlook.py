"""EIA Short Term Energy Outlook Model."""

# pylint: disable=unused-argument,too-many-branches,too-many-statements,too-many-locals

from typing import Any, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.short_term_energy_outlook import (
    ShortTermEnergyOutlookData,
    ShortTermEnergyOutlookQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_us_eia.utils.constants import (
    SteoTableMap,
    SteoTableNames,
    SteoTableType,
)
from pydantic import Field


class EiaShortTermEnergyOutlookQueryParams(ShortTermEnergyOutlookQueryParams):
    """EIA Short Term Energy Outlook Query Parameters.

    Monthly short term (18 month) projections using STEO model

    Source: www.eia.gov/steo/
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
        },
        "table": {
            "multiple_items_allowed": False,
            "choices": list(SteoTableNames),
        },
        "frequency": {
            "multiple_items_allowed": False,
            "choices": ["month", "quarter", "annual"],
        },
    }
    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " If provided, overrides the 'table' parameter to return only the specified symbol from the STEO API.",
    )
    table: SteoTableType = Field(
        default="01",
        description="The specific table within the STEO dataset. Default is '01'."
        + " When 'symbol' is provided, this parameter is ignored."
        + "\n        01: US Energy Markets Summary"
        + "\n        02: Nominal Energy Prices"
        + "\n        03a: World Petroleum and Other Liquid Fuels Production, Consumption, and Inventories"
        + "\n        03b: Non-OPEC Petroleum and Other Liquid Fuels Production"
        + "\n        03c: World Petroleum and Other Liquid Fuels Production"
        + "\n        03d: World Crude Oil Production"
        + "\n        03e: World Petroleum and Other Liquid Fuels Consumption"
        + "\n        04a: US Petroleum and Other Liquid Fuels Supply, Consumption, and Inventories"
        + "\n        04b: US Hydrocarbon Gas Liquids (HGL) and Petroleum Refinery Balances"
        + "\n        04c: US Regional Motor Gasoline Prices and Inventories"
        + "\n        04d: US Biofuel Supply, Consumption, and Inventories"
        + "\n        05a: US Natural Gas Supply, Consumption, and Inventories"
        + "\n        05b: US Regional Natural Gas Prices"
        + "\n        06: US Coal Supply, Consumption, and Inventories"
        + "\n        07a: US Electricity Industry Overview"
        + "\n        07b: US Regional Electricity Retail Sales"
        + "\n        07c: US Regional Electricity Prices"
        + "\n        07d1: US Regional Electricity Generation, Electric Power Sector"
        + "\n        07d2: US Regional Electricity Generation, Electric Power Sector, continued"
        + "\n        07e: US Electricity Generating Capacity"
        + "\n        08: US Renewable Energy Consumption"
        + "\n        09a: US Macroeconomic Indicators and CO2 Emissions"
        + "\n        09b: US Regional Macroeconomic Data"
        + "\n        09c: US Regional Weather Data"
        + "\n        10a: Drilling Productivity Metrics"
        + "\n        10b: Crude Oil and Natural Gas Production from Shale and Tight Formations",
    )
    frequency: Literal["month", "quarter", "annual"] = Field(
        default="month",
        description="The frequency of the data. Default is 'month'.",
    )


class EiaShortTermEnergyOutlookData(ShortTermEnergyOutlookData):
    """EIA Short Term Energy Outlook Data Model."""

    __alias_dict__ = {
        "date": "period",
        "symbol": "seriesId",
        "title": "seriesDescription",
    }


class EiaShortTermEnergyOutlookFetcher(
    Fetcher[EiaShortTermEnergyOutlookQueryParams, list[EiaShortTermEnergyOutlookData]]
):
    """EIA Short Term Energy Outlook Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaShortTermEnergyOutlookQueryParams:
        """Transform the query parameters."""
        return EiaShortTermEnergyOutlookQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EiaShortTermEnergyOutlookQueryParams,
        credentials: Optional[dict[str, Any]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the EIA API."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_us_eia.utils.helpers import response_callback

        api_key = credentials.get("eia_api_key") if credentials else ""
        frequency_dict = {
            "month": "monthly",
            "quarter": "quarterly",
            "annual": "annual",
        }
        frequency = frequency_dict[query.frequency]
        base_url = f"https://api.eia.gov/v2/steo/data/?api_key={api_key}&frequency={frequency}&data[0]=value"
        urls: list[str] = []
        start_date: str = ""
        end_date: str = ""

        # Format the dates based on the frequency.
        def resample_to_quarter(dt) -> str:
            """Resample a date to a string formatted as 'YYYY-QX'."""
            year = dt.year
            quarter = (dt.month - 1) // 3 + 1
            return f"{year}-Q{quarter}"

        if query.start_date is not None and frequency == "monthly":
            start_date = f"&start={query.start_date.strftime('%Y-%m')}"
        elif query.start_date is not None and frequency == "quarterly":
            start_date = f"&start={resample_to_quarter(query.start_date)}"
        elif query.start_date is not None and frequency == "annual":
            start_date = f"&start={query.start_date.strftime('%Y')}"

        if query.end_date is not None and frequency == "monthly":
            end_date = f"&end={query.end_date.strftime('%Y-%m')}"
        elif query.end_date is not None and frequency == "quarterly":
            end_date = f"&end={resample_to_quarter(query.end_date)}"
        elif query.end_date is not None and frequency == "annual":
            end_date = f"&end={query.end_date.strftime('%Y')}"

        # We chunk the request to avoid pagination and make the query execution faster.
        symbols = (
            query.symbol.upper().split(",")
            if query.symbol
            else [d.upper() for d in SteoTableMap[query.table]]
        )
        seen = set()
        unique_symbols: list = []
        for symbol in symbols:
            if symbol not in seen:
                unique_symbols.append(symbol)
                seen.add(symbol)
        symbols = unique_symbols

        def encode_symbols(symbol: str):
            """Encode a chunk of symbols to be used in a URL"""
            prefix = "&facets[seriesId][]="
            return prefix + symbol.upper()

        for i in range(0, len(symbols), 10):
            url_symbols: str = ""
            symbols_chunk = symbols[i : i + 10]
            for symbol in symbols_chunk:
                url_symbols += encode_symbols(symbol)
            url = f"{base_url}{url_symbols}{start_date}{end_date}&offset=0&length=5000"
            urls.append(url)

        results: list[dict] = []
        messages: list[str] = []

        async def get_one(url):
            """Response callback function."""
            res = await amake_request(url, response_callback=response_callback)
            data = res.get("response", {}).get("data", [])  # type: ignore
            if not data:
                series_id = (
                    res.get("request", {})  # type: ignore
                    .get("params", {})
                    .get("facets", {})
                    .get("seriesId", [])
                )
                masked_url = url.replace(api_key, "API_KEY")
                messages.append(f"No data returned for {series_id or masked_url}")
            if data:
                results.extend(data)
            response_total = int(res.get("response", {}).get("total", 0))  # type: ignore
            n_results = len(data)
            # After conservatively chunking the request, we may still need to paginate.
            # This is mostly out of an abundance of caution.
            if response_total > 5000 and n_results == 5000:
                offset = 5000
                url = url.replace("&offset=0", f"&offset={offset}")
                while n_results < response_total:
                    additional_response = await amake_request(url)
                    additional_data = additional_response.get("response", {}).get(  # type: ignore
                        "data", []
                    )
                    if not additional_data:
                        series_id = (
                            res.get("request", {})  # type: ignore
                            .get("params", {})
                            .get("facets", {})
                            .get("seriesId", [])
                        )
                        masked_url = url.replace(api_key, "API_KEY")
                        messages.append(
                            f"No additional data returned for {series_id or masked_url}"
                        )
                    if additional_data:
                        results.extend(additional_data)
                    n_results += len(additional_data)
                    url = url.replace(f"&offset={offset}", f"&offset={offset+5000}")
                    offset += 5000

        try:
            await asyncio.gather(*[get_one(url) for url in urls])
        except Exception as e:
            raise OpenBBError(f"Error fetching data from the EIA API -> {e}") from e

        if not results and not messages:
            raise EmptyDataError(
                "The request was returned empty with no error messages."
            )
        if not results and messages:
            raise OpenBBError("\n".join(messages))
        if results and messages:
            warn("\n".join(messages))

        return results

    @staticmethod
    def transform_data(
        query: EiaShortTermEnergyOutlookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[EiaShortTermEnergyOutlookData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from pandas import Categorical, DataFrame, to_datetime

        symbols = (
            query.symbol.upper().split(",")
            if query.symbol
            else [d.upper() for d in SteoTableMap[query.table]]
        )
        seen = set()
        unique_symbols: list = []
        for symbol in symbols:
            if symbol not in seen:
                unique_symbols.append(symbol)
                seen.add(symbol)
        symbols = unique_symbols

        table = query.table
        df = DataFrame(data)
        df.period = to_datetime(df.period).dt.date
        df.seriesId = Categorical(df.seriesId, categories=symbols, ordered=True)
        df = df.sort_values(["period", "seriesId"])
        df = df.reset_index(drop=True)
        returned_symbols = df.seriesId.unique().tolist()
        missing_symbols = [s for s in symbols if s not in returned_symbols]

        if query.symbol and missing_symbols:
            warn(f"No data was returned for: {', '.join(missing_symbols)}")

        if not query.symbol:
            df["order"] = df.groupby("period").cumcount() + 1
            df["table"] = (
                f"STEO - {table.replace('0', '') if table[0] == '0' else table}: {SteoTableNames[table]}"
            )
        records = df.to_dict(orient="records")

        return [EiaShortTermEnergyOutlookData.model_validate(d) for d in records]
