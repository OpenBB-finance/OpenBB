"""EconDB Port Volume Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.port_volume import (
    PortVolumeData,
    PortVolumeQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class EconDbPortVolumeQueryParams(PortVolumeQueryParams):
    """EconDB Port Volume Query Parameters."""

    @field_validator("start_date", "end_date", mode="before", check_fields=False)
    @classmethod
    def validate_dates(cls, v):
        """Validate the dates."""
        if v and v < datetime(2022, 4, 4).date():
            raise OpenBBError(
                "Dates must be after 2022-04-03.",
            )
        return v if v else None


class EconDbPortVolumeData(PortVolumeData):
    """EconDB Port Volume Data."""

    export_dwell_time: Optional[float] = Field(
        default=None,
        description="EconDB model estimate for the average number of days from when a container"
        + " enters the terminal gates until it is loaded on a vessel."
        + " High dwelling times can indicate vessel delays.",
    )
    import_dwell_time: Optional[float] = Field(
        default=None,
        description="EconDB model estimate for the average number of days from when a container is discharged"
        + " from a vessel until it exits the terminal gates."
        + " High dwelling times can indicate trucking or port congestion.",
    )
    import_teu: Optional[int] = Field(
        default=None,
        description="EconDB model estimate for the number of twenty-foot equivalent units (TEUs)"
        + " of containers imported through the port.",
    )
    export_teu: Optional[int] = Field(
        default=None,
        description="EconDB model estimate for the number of twenty-foot equivalent units (TEUs)"
        + " of containers exported through the port.",
    )


class EconDbPortVolumeFetcher(
    Fetcher[EconDbPortVolumeQueryParams, List[EconDbPortVolumeData]]
):
    """EconDB Port Volume Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbPortVolumeQueryParams:
        """Transform the query."""
        return EconDbPortVolumeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EconDbPortVolumeQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        url = "https://www.econdb.com/static/openbb/shipping.json"

        try:
            response = await amake_request(url)
        except Exception as e:
            raise OpenBBError("There was an error with the HTTP request") from e

        if isinstance(response, dict):
            return response
        raise OpenBBError(
            f"Unexpected format of the response. -> Expected dict, got {str(response.__class__.__name__)}"
        )

    @staticmethod
    def transform_data(
        query: EconDbPortVolumeQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[EconDbPortVolumeData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils.helpers import COUNTRY_MAP
        from pandas import DataFrame, concat, to_datetime

        df: DataFrame = DataFrame()
        res = data.copy()

        if not res:
            raise EmptyDataError("The request was returned empty.")

        ports = res.pop("Ports", None)
        code_to_city_map = {d["locode"]: d["name"] for d in ports}
        code_to_country_map = {d["locode"]: d["iso2"] for d in ports}
        port_codes = list(code_to_city_map)

        for code in port_codes:
            new_data: List = []
            for k, v in res.items():
                new_data.extend(
                    {
                        "date": d.get("Date"),
                        "port_code": code,
                        "port_name": code_to_city_map[code],
                        "country": code_to_country_map[code],
                        "measure": k,
                        "value": d.get(code),
                    }
                    for d in res[k]
                    if d.get(code)
                )
            df = (
                DataFrame(new_data)
                .sort_values(by=["date", "measure"])
                .reset_index(drop=True)
                if df.empty
                else concat(
                    [
                        df,
                        DataFrame(new_data)
                        .sort_values(by=["date", "measure"])
                        .reset_index(drop=True),
                    ]
                )
            )

        df = df.pivot_table(
            index=["date", "port_code", "port_name", "country"],
            columns="measure",
            values="value",
            sort=False,
            observed=True,
        )
        cols_map = {
            "Dwelling times imports": "import_dwell_time",
            "Dwelling times exports": "export_dwell_time",
            "Imports": "import_teu",
            "Exports": "export_teu",
        }
        df = df.rename(columns=cols_map).reset_index().convert_dtypes()
        df.country = df.country.map(
            {v: k.replace("_", " ").title() for k, v in COUNTRY_MAP.items()}
        )
        df.date = to_datetime(df.date).dt.date

        if query.start_date:
            df = df[df.date >= query.start_date]

        if query.end_date:
            df = df[df.date <= query.end_date]

        if len(df) == 0:
            raise EmptyDataError(
                f"No data found for the provided dates. Data has a range from {df.date.min()} to {df.date.max()}."
            )

        return [
            EconDbPortVolumeData.model_validate(d) for d in df.to_dict(orient="records")
        ]
