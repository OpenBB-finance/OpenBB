"""IMF Maritime Chokepoint Info Model."""

# pylint: disable=unused-argument

from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.maritime_chokepoint_info import (
    MaritimeChokePointInfoData,
    MaritimeChokePointInfoQueryParams,
)
from pydantic import ConfigDict, Field


class ImfMaritimeChokePointInfoQueryParams(MaritimeChokePointInfoQueryParams):
    """IMF Maritime Chokepoint Info Query Parameters.

    Source: https://portwatch.imf.org/pages/port-monitor
    """

    __json_schema_extra__ = {
        "theme": {"x-widget_config": {"show": False}},
    }

    theme: Optional[Literal["dark", "light"]] = Field(
        default=None,
        description="Theme for the map."
        + " Only valid if `openbb-charting` is installed and `chart` parameter is set to `true`."
        + " Default is the 'chart_style' setting in `user_settings.json`, if available, otherwise 'dark'.",
    )


class ImfMaritimeChokePointInfoData(MaritimeChokePointInfoData):
    """IMF Maritime Chokepoint Data.

    Source: https://portwatch.imf.org/pages/port-monitor
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.gridData": {
                    "h": 13,
                    "w": 40,
                    "minH": 10,
                    "minW": 30,
                    "maxW": 40,
                    "maxH": 20,
                },
                "$.name": "Global Maritime Chokepoints",
                "$.description": "Global maritime chokepoints are narrow channels along popular shipping routes.",
                "$.refetchInterval": False,
            }
        },
    )

    __alias_dict__ = {
        "chokepoint_code": "portid",
        "name": "portname",
        "vessel_count_roro": "vessel_count_RoRo",
        "latitude": "lat",
        "longitude": "lon",
    }

    name: str = Field(
        description="Port name.",
        title="Chokepoint",
    )
    latitude: float = Field(
        description="Latitude of the chokepoint location.",
        title="Latitude",
    )
    longitude: float = Field(
        description="Longitude of the chokepoint location.",
        title="Longitude",
    )
    vessel_count_total: int = Field(
        description="Yearly average number of all ships transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019."
        + " The total is calculated over the sum of vessel_count_container, vessel_count_dry_bulk,"
        + " vessel_count_general_cargo, vessel_count_roro and vessel_count_tanker.",
        title="Total Vessel Count",
    )
    vessel_count_tanker: int = Field(
        description="Yearly average number of tankers transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Tanker Vessel Count",
    )
    vessel_count_container: int = Field(
        description="Yearly average number of containers transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Container Vessel Count",
    )
    vessel_count_general_cargo: int = Field(
        description="Yearly average number of general cargo ships transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="General Cargo Vessel Count",
    )
    vessel_count_dry_bulk: int = Field(
        description="Yearly average number of dry bulk carriers transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Dry Bulk Vessel Count",
    )
    vessel_count_roro: int = Field(
        description="Yearly average number of Ro-Ro ships transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Ro-Ro Vessel Count",
    )
    industry_top1: Optional[str] = Field(
        default=None,
        description="First dominant traded industries"
        + " based on the volume of goods estimated to flow through the chokepoint.",
        title="Top Industry 1",
    )
    industry_top2: Optional[str] = Field(
        default=None,
        description="Second dominant traded industries"
        + " based on the volume of goods estimated to flow through the chokepoint.",
        title="Top Industry 2",
    )
    industry_top3: Optional[str] = Field(
        default=None,
        description="Third dominant traded industries"
        + " based on the volume of goods estimated to flow through the chokepoint.",
        title="Top Industry 3",
    )


class ImfMaritimeChokePointInfoFetcher(
    Fetcher[ImfMaritimeChokePointInfoQueryParams, list[ImfMaritimeChokePointInfoData]]
):
    """IMF Maritime Chokepoint Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfMaritimeChokePointInfoQueryParams:
        """Transform query parameters."""
        return ImfMaritimeChokePointInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfMaritimeChokePointInfoQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data from the IMF Port Watch API."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_async_requests_session

        url = (
            "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
            "PortWatch_chokepoints_database/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
        )

        try:
            async with await get_async_requests_session() as session, await session.get(
                url
            ) as response:
                if response.status != 200:
                    raise OpenBBError(f"Failed to fetch data: {response.status}")

                return await response.json()

        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: ImfMaritimeChokePointInfoQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[ImfMaritimeChokePointInfoData]:
        """Transform the raw data into a list of ImfMaritimeChokePointInfoData."""
        if not data or "features" not in data:
            raise OpenBBError("No data found in the response.")

        return [
            ImfMaritimeChokePointInfoData(**feature["properties"])
            for feature in data["features"]
        ]
