"""EconDB Export Destinations Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from aiohttp.client_exceptions import ContentTypeError
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.export_destinations import (
    ExportDestinationsData,
    ExportDestinationsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class EconDbExportDestinationsQueryParams(ExportDestinationsQueryParams):
    """EconDB Export Destinations Query Parameters."""

    __json_schema_extra__ = {"country": {"multiple_items_allowed": True}}


class EconDbExportDestinationsData(ExportDestinationsData):
    """EconDB Export Destinations Data."""

    units: str = Field(
        description="The units of measurement for the value.",
    )
    title: str = Field(
        description="The title of the data.",
    )
    footnote: Optional[str] = Field(
        description="The footnote for the data.",
    )


class EconDbExportDestinationsFetcher(
    Fetcher[EconDbExportDestinationsQueryParams, List[EconDbExportDestinationsData]]
):
    """EconDB Export Destinations Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbExportDestinationsQueryParams:
        """Transform query parameters."""
        return EconDbExportDestinationsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EconDbExportDestinationsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from EconDB."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_econdb.utils.helpers import COUNTRY_MAP

        results: List = []
        messages: List = []
        countries = query.country.split(",")
        MAP_COUNTRY = {v: k for k, v in COUNTRY_MAP.items()}

        async def get_one_country(c):
            """Get data for one country."""
            c = c.upper() if len(c) == 2 else c.lower()
            if len(c) != 2:
                c = COUNTRY_MAP.get(c, c)
                if len(c) != 2 or c.upper() not in MAP_COUNTRY:
                    messages.append(f"Invalid country code -> {c}")
                    return

            URL = f"https://www.econdb.com/widgets/top-trade-items/data/?country={c.upper()}&split_by=country"
            result: List = []
            row: Dict = {}
            try:
                res = await amake_request(URL)
            except ContentTypeError as e:
                if len(countries) == 1:
                    raise OpenBBError(e) from e
                messages.append(f"No data available for the country -> {c}")
                return

            plots = res.get("plots", [])  # type: ignore
            data = plots[0].pop("data", []) if plots else []
            meta = plots[0] if plots else {}

            if not data or (len(data) == 1 and data[0].get("Value million USD") == 0):
                messages.append(f"No data available for the country -> {c}")
                return

            origin_country = MAP_COUNTRY.get(c, c)

            for item in data:
                row = {
                    "origin_country": origin_country.replace("_", " ").title(),
                    **item,
                    "units": (
                        meta.get("series", [])[0]
                        .get("code", "")
                        .replace("Value million", "Millions of")
                        if meta.get("series", [])
                        else ""
                    ),
                    "title": meta.get("title", ""),
                    "footnote": meta.get("footnote", ""),
                }
                result.append(
                    {
                        (
                            "value"
                            if k == "Value million USD"
                            else "destination_country" if k == "Country" else k
                        ): (
                            MAP_COUNTRY.get(v, v).replace("_", " ").title()
                            if k == "Country"
                            else v
                        )
                        for k, v in row.items()
                        if v and v != 0
                    }
                )
            if result:
                results.extend(result)
            else:
                messages.append(f"No data returned for the country -> {c}")

        await asyncio.gather(*[get_one_country(c) for c in countries])

        if not results:
            raise (
                EmptyDataError(f"{messages}")
                if messages
                else EmptyDataError(
                    f"No data returned for the given country -> {countries}"
                )
            )
        if messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: EconDbExportDestinationsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[EconDbExportDestinationsData]:
        """Transform the data."""
        return [EconDbExportDestinationsData.model_validate(d) for d in data]
