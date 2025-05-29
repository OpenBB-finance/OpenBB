"""IMF Maritime Chokepoint Info Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.maritime_chokepoint_volume import (
    MaritimeChokePointVolumeData,
    MaritimeChokePointVolumeQueryParams,
)
from openbb_imf.utils.constants import CHOKEPOINTS_NAME_TO_ID, ChokepointsNames
from pydantic import ConfigDict, Field, field_validator

CHOKEPOINT_DOCSTRING = (
    "\n    - " + "\n    - ".join(list(ChokepointsNames.__args__)) + "\n\n"
)


class ImfMaritimeChokePointVolumeQueryParams(MaritimeChokePointVolumeQueryParams):
    """IMF Maritime Chokepoint Volume Query Parameters.

    Source: https://portwatch.imf.org/datasets/42132aa4e2fc4d41bdaf9a445f688931/about
    """

    __json_schema_extra__ = {
        "chokepoint": {
            "x-widget_config": {
                "options": [
                    {"label": k.replace("_", " ").title(), "value": v}
                    for k, v in CHOKEPOINTS_NAME_TO_ID.items()
                ],
                "description": "Name of the chokepoint. No selection will return data for all chokepoints.",
            },
            "multiple_items_allowed": True,
        },
    }

    chokepoint: Optional[str] = Field(
        default=None,
        description="Name of the chokepoint. Use `None` for all chokepoints."
        + f" Choices are: {CHOKEPOINT_DOCSTRING}",
    )

    @field_validator("chokepoint", mode="before")
    @classmethod
    def validate_chokepoint(cls, v):
        """Validate the chokepoint parameter."""
        if not v:
            return None

        if isinstance(v, str):
            if "," in v:
                chokepoints = v.split(",")
                for chokepoint in chokepoints:
                    if chokepoint not in list(
                        CHOKEPOINTS_NAME_TO_ID
                    ) and chokepoint not in list(CHOKEPOINTS_NAME_TO_ID.values()):
                        raise OpenBBError(
                            ValueError(
                                f"Invalid chokepoint name: {chokepoint} -> "
                                f"Expected one of {list(CHOKEPOINTS_NAME_TO_ID)}"
                                " - or chokepointN, where N is a number between 1 and 24"
                            )
                        )

                return ",".join(chokepoints) if chokepoints else None

            if (
                v
                and v not in CHOKEPOINTS_NAME_TO_ID
                and v not in list(CHOKEPOINTS_NAME_TO_ID.values())
            ):
                raise OpenBBError(
                    ValueError(
                        f"Invalid chokepoint name: {v} -> "
                        f"Expected one of {list(CHOKEPOINTS_NAME_TO_ID)}"
                        " - or chokepointN, where N is a number between 1 and 24"
                    )
                )

            return (
                v
                if v in CHOKEPOINTS_NAME_TO_ID
                or v in list(CHOKEPOINTS_NAME_TO_ID.values())
                else None
            )

        if isinstance(v, list):
            chokepoints = []
            for d in v:
                if d in CHOKEPOINTS_NAME_TO_ID:
                    chokepoints.append(CHOKEPOINTS_NAME_TO_ID[d])
                elif d in list(CHOKEPOINTS_NAME_TO_ID.values()):
                    chokepoints.append(d)

            return ",".join(chokepoints) if chokepoints else None

        raise OpenBBError(
            ValueError(
                f"Invalid chokepoint value: {v} -> "
                f"Expected a string or a list of strings from {list(CHOKEPOINTS_NAME_TO_ID)}."
                " - or chokepointN, where N is a number between 1 and 24"
            )
        )


class ImfMaritimeChokePointVolumeData(MaritimeChokePointVolumeData):
    """IMF Maritime Chokepoint Volume Data.

    Source: https://portwatch.imf.org/datasets/42132aa4e2fc4d41bdaf9a445f688931/about
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Daily Chokepoint Transit Calls and Trade Volume Estimates",
                "$.description": (
                    "Download daily chokepoint transit calls and preliminary transit"
                    " trade volume estimates for 24 major chokepoints worldwide.\n\n"
                    " These estimates are based on satellite-captured signals on"
                    " 90 thousands ships worldwide, harnessing the power of big data analytics."
                ),
                "$.refetchInterval": False,
                "$.source": ["UN Global Platform; [IMF PortWatch](portwatch.imf.org)"],
            }
        },
    )

    __alias_dict__ = {
        "chokepoint": "portname",
        "vessels_total": "n_total",
        "vessels_cargo": "n_cargo",
        "vessels_tanker": "n_tanker",
        "vessels_container": "n_container",
        "vessels_general_cargo": "n_general_cargo",
        "vessels_dry_bulk": "n_dry_bulk",
        "vessels_roro": "n_roro",
        "capacity_total": "capacity",
    }

    chokepoint: str = Field(
        description="Name of the chokepoint.",
        title="Chokepoint",
    )
    vessels_total: int = Field(
        description="Number of all ships transiting through the chokepoint on that date."
        + " The total is calculated over the sum of vessels_container, vessels_dry_bulk,"
        + " vessels_general_cargo, vessels_roro and vessels_tanker.",
        title="Total Vessels",
    )
    vessels_cargo: int = Field(
        description="Total number of ships (excluding tankers) transiting through the chokepoint at this date."
        + " This is the sum of vessels_container, vessels_dry_bulk, vessels_general_cargo and vessels_roro.",
        title="Total Cargo",
    )
    vessels_tanker: int = Field(
        description="Number of tankers transiting through the chokepoint on that date.",
        title="Tanker Vessels",
    )
    vessels_container: int = Field(
        description="Number of containers transiting through the chokepoint on that date.",
        title="Container Vessels",
    )
    vessels_general_cargo: int = Field(
        description="Number of general cargo ships transiting through the chokepoint on that date.",
        title="General Cargo Vessels",
    )
    vessels_dry_bulk: int = Field(
        description="Yearly average number of dry bulk carriers transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Dry Bulk Vessels",
    )
    vessels_roro: int = Field(
        description="Yearly average number of Ro-Ro ships transiting through the chokepoint."
        + " Estimated using AIS data beginning 2019.",
        title="Ro-Ro Vessels",
    )
    capacity_total: float = Field(
        description="Total trade volume (in metric tons) of all ships transiting through the chokepoint at this date."
        + " This is the sum of capacity_container, capacity_dry_bulk,"
        + " capacity_general_cargo, capacity_roro and capacity_tanker.",
        title="Total Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_cargo: float = Field(
        description="Total trade volume (in metric tons) of all ships (excluding tankers)"
        + " transiting through the chokepoint at this date."
        + " This is the sum of capacity_container, capacity_dry_bulk, capacity_general_cargo and capacity_roro.",
        title="Cargo Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_tanker: float = Field(
        description="Total trade volume (in metric tons) of tankers transiting through the chokepoint at this date.",
        title="Tanker Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_container: float = Field(
        description="Total trade volume (in metric tons) of containers transiting through the chokepoint at this date.",
        title="Container Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_general_cargo: float = Field(
        description="Total trade volume (in metric tons) of general cargo Vessels"
        + " transiting through the chokepoint at this date.",
        title="General Cargo Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_dry_bulk: float = Field(
        description="Total trade volume (in metric tons) of dry bulk carriers"
        + " transiting through the chokepoint at this date.",
        title="Dry Bulk Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )
    capacity_roro: float = Field(
        description="Total trade volume (in metric tons) of Ro-Ro ships transiting through the chokepoint at this date.",
        title="Ro-Ro Capacity",
        json_schema_extra={
            "x-unit_measurement": "metric_tons",
            "x-widget_config": {
                "suffix": "mt",
            },
        },
    )


class ImfMaritimeChokePointVolumeFetcher(
    Fetcher[
        ImfMaritimeChokePointVolumeQueryParams, list[ImfMaritimeChokePointVolumeData]
    ]
):
    """IMF Maritime Chokepoint Info Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> ImfMaritimeChokePointVolumeQueryParams:
        """Transform query parameters."""
        return ImfMaritimeChokePointVolumeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfMaritimeChokePointVolumeQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract the raw data from the IMF Port Watch API."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_imf.utils.port_watch_helpers import (
            get_daily_chokepoint_data,
            get_all_daily_chokepoint_activity_data,
        )

        chokepoints = (
            query.chokepoint
            if isinstance(query.chokepoint, list)
            else query.chokepoint.split(",") if query.chokepoint else []
        )

        if not chokepoints:
            try:
                return await get_all_daily_chokepoint_activity_data(
                    start_date=query.start_date, end_date=query.end_date
                )
            except Exception as e:
                raise OpenBBError(e) from e

        results: list = []

        async def get_one(chokepoint_id):
            """Get data for a single chokepoint."""
            data = await get_daily_chokepoint_data(
                chokepoint_id, query.start_date, query.end_date
            )
            if data:
                results.extend(data)

        # Accept both keys and values from CHOKEPOINTS_NAME_TO_ID
        chokepoint_ids: list = []
        for chokepoint in chokepoints:
            if chokepoint in CHOKEPOINTS_NAME_TO_ID:
                chokepoint_ids.append(CHOKEPOINTS_NAME_TO_ID[chokepoint])
            elif chokepoint in CHOKEPOINTS_NAME_TO_ID.values() or chokepoint.startswith(
                "chokepoint"
            ):
                chokepoint_ids.append(chokepoint)
            else:
                raise OpenBBError(
                    f"Invalid chokepoint name: {chokepoint}. "
                    f"Expected one of {list(CHOKEPOINTS_NAME_TO_ID.keys())}."
                )

        tasks = [
            get_one(chokepoint_id) for chokepoint_id in chokepoint_ids if chokepoint_id
        ]

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        for task_result in task_results:
            if isinstance(task_result, Exception):
                raise OpenBBError(task_result)

        if not results:
            raise OpenBBError("The response was returned empty with no error message.")

        return results

    @staticmethod
    def transform_data(
        query: ImfMaritimeChokePointVolumeQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[ImfMaritimeChokePointVolumeData]:
        """Validate and transform the raw data into the model."""
        return [ImfMaritimeChokePointVolumeData(**r) for r in data]
