"""IMF Port Info Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.port_info import (
    PortInfoData,
    PortInfoQueryParams,
)
from openbb_imf.utils.constants import (
    PORT_CONTINENTS,
    PORT_COUNTRIES_CHOICES,
    PortContinents,
    PortCountries,
)
from pydantic import ConfigDict, Field, field_validator


class ImfPortInfoQueryParams(PortInfoQueryParams):
    """IMF Port Info Query Parameters.

    Source: https://portwatch.imf.org/pages/port-monitor
    """

    __json_schema_extra__ = {
        "continent": {
            "x-widget_config": {
                "options": PORT_CONTINENTS,
            }
        },
        "country": {
            "x-widget_config": {
                "options": PORT_COUNTRIES_CHOICES,
                "description": "Filter by country. This parameter supersedes `continent` if both are provided.",
                "style": {"popupWidth": 350},
            }
        },
    }

    continent: Optional[PortContinents] = Field(
        default=None,
        description="Filter by continent. This parameter is ignored when a `country` is provided.",
    )

    country: Optional[PortCountries] = Field(
        default=None,
        description="Country to focus on. Enter as a 3-letter ISO country code."
        + " This parameter supersedes `continent` if both are provided.",
    )

    limit: Optional[int] = Field(
        default=None,
        description="Limit the number of results returned."
        + " Limit is determined by the annual average number of vessels transiting through the port."
        + " If not provided, all ports are returned.",
    )


class ImfPortInfoData(PortInfoData):
    """IMF Port Info Data.

    Source: https://portwatch.imf.org/pages/port-monitor
    """

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "x-widget_config": {
                "$.gridData": {
                    "h": 25,
                    "w": 25,
                }
            }
        },
    )

    __alias_dict__ = {
        "port_code": "portid",
        "port_name": "portname",
        "port_full_name": "fullname",
        "country_code": "ISO3",
        "vessel_count_roro": "vessel_count_RoRo",
        "latitude": "lat",
        "longitude": "lon",
        "country": "countrynoaccents",
    }

    port_code: str = Field(
        description="Unique ID assigned to the port.",
        title="Port ID",
    )
    continent: str = Field(
        description="Continent where the port is located.",
        title="Continent",
    )
    country: str = Field(
        description="Country where the port is located.",
        title="Country",
    )
    country_code: str = Field(
        description="3-letter ISO code of the country where the port is located.",
        title="Country Code",
    )
    port_name: str = Field(
        description="Port name.",
        title="Port Name",
    )
    port_full_name: str = Field(
        description="Full name of the port.",
        title="Full Port Name",
    )
    latitude: float = Field(
        description="Latitude of the port.",
        title="Latitude",
    )
    longitude: float = Field(
        description="Longitude of the port.",
        title="Longitude",
    )
    vessel_count_total: int = Field(
        description="Yearly average number of all ships transiting through the port."
        + " Estimated using AIS data beginning 2019."
        + " The total is calculated over the sum of vessel_count_container, vessel_count_dry_bulk,"
        + " vessel_count_general_cargo, vessel_count_roro and vessel_count_tanker.",
        title="Total Vessel Count",
    )
    vessel_count_tanker: int = Field(
        description="Yearly average number of tankers transiting through the port."
        + " Estimated using AIS data beginning 2019.",
        title="Tanker Vessel Count",
    )
    vessel_count_container: int = Field(
        description="Yearly average number of containers transiting through the port."
        + " Estimated using AIS data beginning 2019.",
        title="Container Vessel Count",
    )
    vessel_count_general_cargo: int = Field(
        description="Yearly average number of general cargo ships transiting through the port."
        + " Estimated using AIS data beginning 2019.",
        title="General Cargo Vessel Count",
    )
    vessel_count_dry_bulk: int = Field(
        description="Yearly average number of dry bulk carriers transiting through the port."
        + " Estimated using AIS data beginning 2019.",
        title="Dry Bulk Vessel Count",
    )
    vessel_count_roro: int = Field(
        description="Yearly average number of Ro-Ro ships transiting through the port."
        + " Estimated using AIS data beginning 2019.",
        title="Ro-Ro Vessel Count",
    )
    industry_top1: Optional[str] = Field(
        default=None,
        description="First dominant traded industries"
        + " based on the volume of goods estimated to flow through the port.",
        title="Top Industry 1",
    )
    industry_top2: Optional[str] = Field(
        default=None,
        description="Second dominant traded industries"
        + " based on the volume of goods estimated to flow through the port.",
        title="Top Industry 2",
    )
    industry_top3: Optional[str] = Field(
        default=None,
        description="Third dominant traded industries"
        + " based on the volume of goods estimated to flow through the port.",
        title="Top Industry 3",
    )
    share_country_maritime_import: float = Field(
        description="Share of the total maritime imports of the country that are estimated to flow through the port.",
        title="Share of Country Maritime Imports",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    share_country_maritime_export: float = Field(
        description="Share of the total maritime exports of the country that are estimated to flow through the port.",
        title="Share of Country Maritime Exports",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )

    @field_validator("share_country_maritime_import", "share_country_maritime_export")
    @classmethod
    def _normalize_percent(cls, v):
        return v / 100 if v else None


class ImfPortInfoFetcher(Fetcher[ImfPortInfoQueryParams, list[ImfPortInfoData]]):
    """IMF Port Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfPortInfoQueryParams:
        """Transform query parameters."""
        return ImfPortInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfPortInfoQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract the raw data from the IMF Port Watch API."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_async_requests_session

        all_ports_url = (
            "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/PortWatch_ports_database/FeatureServer/0/query?"
            + "where=1%3D1&outFields=*&returnGeometry=false&outSR=&f=json"
        )
        try:
            output: list = []
            data: dict = {}

            async with await get_async_requests_session() as session:
                async with await session.get(all_ports_url) as response:
                    if response.status != 200:
                        raise OpenBBError(
                            f"Failed to fetch data: {response.status} -> {response.reason}"
                        )

                    data = await response.json()

                if "features" in data:
                    output.extend(data["features"])

                    if "exceededTransferLimit" in data:
                        while data.get("exceededTransferLimit"):
                            offset = len(output)
                            url = f"{all_ports_url}&resultOffset={offset}"

                            async with await session.get(url) as response:
                                if response.status != 200:
                                    raise OpenBBError(
                                        f"Failed to fetch data: {response.status}"
                                    )

                                data = await response.json()
                                if "features" in data:
                                    output.extend(data["features"])

            return sorted(
                output,
                key=lambda x: x["attributes"]["vessel_count_total"],
                reverse=True,
            )

        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: ImfPortInfoQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[ImfPortInfoData]:
        """Transform the raw data into a list of ImfPortInfoData."""
        results: list[ImfPortInfoData] = []

        if query.country:
            results.extend(
                [
                    ImfPortInfoData(**d["attributes"])
                    for d in sorted(
                        data,
                        key=lambda x: x["attributes"]["vessel_count_total"],
                        reverse=True,
                    )
                    if d["attributes"]["ISO3"] == query.country.upper()
                ]
            )
            if query.limit:
                results = results[: query.limit]
        elif query.continent:
            target_continent: str = ""
            for continent in PORT_CONTINENTS:
                if continent["value"] == query.continent:
                    target_continent = continent["label"]
                    break
            if target_continent:
                results.extend(
                    [
                        ImfPortInfoData(**d["attributes"])
                        for d in sorted(
                            data,
                            key=lambda x: x["attributes"]["vessel_count_total"],
                            reverse=True,
                        )
                        if d["attributes"]["continent"] == target_continent
                    ]
                )
                if query.limit:
                    results = results[: query.limit]
        else:
            results.extend(
                [
                    ImfPortInfoData(**d["attributes"])
                    for d in sorted(
                        data,
                        key=lambda x: x["attributes"]["vessel_count_total"],
                        reverse=True,
                    )
                ]
            )
            if query.limit:
                results = results[: query.limit]

        return results
