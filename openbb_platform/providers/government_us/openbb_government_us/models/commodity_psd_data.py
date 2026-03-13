"""US Government Production Supply & Distribution Report Data & Time Series Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commodity_psd_data import (
    CommodityPsdData,
    CommodityPsdDataQueryParams,
)
from openbb_government_us.utils.psd_codes import (
    ATTRIBUTES,
    COMMODITIES,
    COUNTRIES,
    PSD_REPORT_NAMES,
    REGIONS,
)
from pydantic import ConfigDict, Field, field_validator, model_validator

COUNTRY_CHOICES = {
    **{k: v for k, v in COUNTRIES.items() if k != "world"},
    **REGIONS,
}


class GovernmentUsCommodityPsdDataQueryParams(CommodityPsdDataQueryParams):
    """US Government Commodity PSD Data Query Params.

    Source: https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads
    """

    __json_schema_extra__ = {
        "report_id": {
            "x-widget_config": {
                "description": "Report ID to retrieve. Gets the current report for the given commodity and subject. "
                + "Ignored if 'commodity' is provided.",
                "value": "world_crop_production_summary",
                "options": [
                    {
                        "label": name.replace("_", " ")
                        .title()
                        .replace("Eu", "EU")
                        .replace("Us", "US"),
                        "value": name,
                    }
                    for name in sorted(list(PSD_REPORT_NAMES))
                ],
                "style": {"popupWidth": 350},
                "row": 1,
            },
        },
        "commodity": {
            "x-widget_config": {
                "description": "Commodity name to filter the data. "
                + "If provided, overrides the Report ID and retrieves time series data for the given commodity.",
                "value": None,
                "options": [{"label": "Report Mode", "value": None}]
                + [
                    {"label": comm.replace("_", " ").title(), "value": comm}
                    for comm in sorted(list(COMMODITIES))
                ],
                "row": 1,
            },
        },
        "attribute": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "description": "Attribute to filter the data. Ignored when commodity is Report Mode. "
                + "If None, retrieves all available attributes for the commodity.",
                "options": [{"label": "All Attributes", "value": None}]
                + [
                    {
                        "label": attr.replace("_", " ")
                        .title()
                        .replace("Us", "US")
                        .replace("Ty", "TY")
                        .replace("Fsi", "FSI"),
                        "value": attr,
                    }
                    for attr in sorted(list(ATTRIBUTES))
                ],
                "row": 1,
            },
        },
        "country": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "description": "Country code(s) to filter the data. Ignored when commodity is Report Mode. "
                + "If None, retrieves data for all countries.",
                "options": [{"label": "All Countries", "value": None}]
                + [
                    {"label": name.replace("_", " ").title(), "value": code}
                    for name, code in COUNTRY_CHOICES.items()
                ],
                "row": 1,
            },
        },
        "start_year": {
            "x-widget_config": {
                "description": "Start year for filtering time series data. Ignored when commodity is Report Mode. "
                + "None returns from the beginning of the series.",
                "type": "number",
                "options": [{"label": "Start Year", "value": None}]
                + [
                    {"label": str(year), "value": year}
                    for year in sorted(
                        list(range(1960, datetime.now().year + 1)), reverse=True
                    )
                ],
                "row": 1,
            },
        },
        "end_year": {
            "x-widget_config": {
                "description": "End year for filtering time series data."
                + " Ignored when commodity is Report Mode. If None, returns up to the most recent year.",
                "type": "number",
                "options": [{"label": "End Year", "value": None}]
                + [
                    {"label": str(year), "value": year}
                    for year in sorted(
                        list(range(1960, datetime.now().year + 1)), reverse=True
                    )
                ],
                "row": 1,
            },
        },
        "aggregate_regions": {
            "x-widget_config": {
                "description": "Whether to include regional and world aggregates in the data."
                + " Ignored when 'commodity' is Report Mode.",
                "type": "boolean",
                "value": False,
                "row": 1,
            },
        },
    }

    report_id: str | None = Field(
        default="world_crop_production_summary",
        description="Report ID to retrieve. Gets the current report for the given commodity and subject. "
        + "These are predefined tables that are part of the PDF publication data. "
        + "This parameter is ignored if 'commodity' is provided. "
        + "Use the 'commodity' parameter for time series data. "
        + "Valid reports are:\n    "
        + ", ".join(sorted(list(PSD_REPORT_NAMES.keys())))
        + "\n",
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity name to filter the data. If provided, retrieves time series data for the given commodity. "
        + "Supplying both 'report_id' and 'commodity' will prioritize 'commodity' for time series data. "
        + "Valid commodities are:\n    "
        + ", ".join(sorted(list(COMMODITIES)))
        + "\n",
    )
    attribute: str | list[str] | None = Field(
        default=None,
        description="Attribute to filter the data. If None, retrieves all available attributes for the commodity.\n"
        + "Parameter is ignored when commodity is None. Valid attributes depend on the commodity, "
        + "an invalid choice will show the available attributes for the entered commodity.\n"
        + "All attributes choices are:\n"
        + ", ".join(sorted(list(ATTRIBUTES)))
        + "\n",
    )
    country: str | list[str] | None = Field(
        default=None,
        description="Country code(s) to filter the data. If None, retrieves data for all countries.\n"
        + "Parameter is ignored when commodity is None. Valid country codes include:\n"
        + ", ".join(
            sorted(list(COUNTRY_CHOICES)),
        )
        + "\n",
    )
    aggregate_regions: bool = Field(
        default=False,
        description="Whether to include regional and world aggregates in the data. "
        + "Parameter is ignored when 'commodity' is None.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering time series data. None returns from the beginning of the series.\n"
        + "Parameter is ignored when 'commodity' is None.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering time series data. If None, returns up to the most recent year.\n"
        + "Parameter is ignored when 'commodity' is None.",
    )

    @field_validator("report_id", mode="before", check_fields=False)
    @classmethod
    def _validate_report_id(cls, v):
        """Validate report_id."""
        if not v:
            return "world_crop_production_summary"

        if v not in PSD_REPORT_NAMES:
            raise ValueError(
                f"Invalid report_id '{v}'. Valid report IDs are: "
                + ", ".join(sorted(list(PSD_REPORT_NAMES.keys())))
            )
        return v

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity."""
        if not v:
            return None
        if v and v not in COMMODITIES:
            raise ValueError(
                f"Invalid commodity '{v}'. Valid commodities are: "
                + ", ".join(sorted(list(COMMODITIES)))
            )
        return v

    @field_validator("attribute", mode="before", check_fields=False)
    @classmethod
    def _validate_attribute(cls, v):
        """Validate attribute."""
        if not v:
            return None

        if v and isinstance(v, list) and not v[0]:
            return None

        attributes = v

        if isinstance(attributes, str):
            attributes = (
                [attributes] if "," not in attributes else attributes.split(",")
            )

        if (
            isinstance(attributes, list)
            and len(attributes) == 1
            and "," in attributes[0]
        ):
            attributes = attributes[0].split(",")

        if not isinstance(attributes, list):
            raise ValueError(
                f"Attribute must be a string or list of strings. Got {type(v)}"
            )

        invalid_attrs = [attr for attr in attributes if attr not in ATTRIBUTES]

        if invalid_attrs:
            raise ValueError(
                f"Invalid attribute(s) '{', '.join(invalid_attrs)}'. Valid attributes are: "
                + ", ".join(sorted(list(ATTRIBUTES)))
            )

        return attributes

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def _validate_country(cls, v):
        """Validate country."""
        if not v:
            return None

        if v and isinstance(v, list) and not v[0]:
            return None

        countries = v

        if isinstance(countries, str):
            countries = [countries] if "," not in countries else countries.split(",")

        if not isinstance(countries, list):
            raise ValueError(
                f"Country must be a string or list of strings. Got {type(v)}"
            )

        if isinstance(countries, list) and len(countries) == 1 and "," in countries[0]:
            countries = countries[0].split(",")

        invalid_countries = [
            country
            for country in countries
            if country
            and country not in COUNTRY_CHOICES.values()
            and country not in COUNTRY_CHOICES
        ]

        if invalid_countries:
            raise ValueError(
                f"Invalid country code(s) '{', '.join(invalid_countries)}'. Valid country codes are: "
                + ", ".join(
                    sorted(list(COUNTRY_CHOICES)),
                )
            )

        return v

    @field_validator("start_year", mode="before", check_fields=False)
    @classmethod
    def _validate_start_year(cls, v):
        """Validate start_year."""
        if v and v < 1960:
            raise ValueError("Earliest possible year is 1960.")
        return v

    @model_validator(mode="after")
    def _validate_model(self):
        """Validate that start_year is less than or equal to end_year."""
        report_id = getattr(self, "report_id", None)
        commodity = getattr(self, "commodity", None)

        if not report_id and not commodity:
            raise ValueError(
                "Either 'report_id' or 'commodity' must be provided."
                + " If both are provided, 'commodity' takes precedence."
            )

        return self


class GovernmentUsCommodityPsdData(CommodityPsdData):
    """US Government Commodity PSD Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA FAS Commodity Production Supply & Distribution Data",
                "$.description": "Predefined presentation tables, or time series data by commodity."
                + " Source: USDA Foreign Agricultural Service (FAS) Production Supply & Distribution Online.",
                "$.source": ["USDA", "FAS"],
                "$.category": "Commodity",
                "$.subCategory": "Agriculture",
                "$.runButton": True,
            },
        }
    )


class GovernmentUsCommodityPsdDataFetcher(
    Fetcher[
        GovernmentUsCommodityPsdDataQueryParams,
        list[GovernmentUsCommodityPsdData],
    ]
):
    """US Government Commodity PSD Data Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> GovernmentUsCommodityPsdDataQueryParams:
        """Transform the query parameters into the model."""
        return GovernmentUsCommodityPsdDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: GovernmentUsCommodityPsdDataQueryParams,
        credentials: dict[str, Any] | None,
        **kwargs: Any,
    ) -> list:
        """Extract data from the provider."""
        # pylint: disable=import-outside-toplevel
        from openbb_government_us.utils.psd_data_downloader import (
            get_psd_report_data,
            get_timeseries,
        )

        if query.commodity is not None:
            # Time series data
            try:
                timeseries_data = get_timeseries(
                    commodity=query.commodity,
                    attribute=query.attribute,
                    country=query.country,
                    aggregate_region=query.aggregate_regions,
                    start_year=query.start_year,
                    end_year=query.end_year,
                )
                return timeseries_data
            except (ValueError, OpenBBError) as e:
                raise OpenBBError(e) from None

        report_id = PSD_REPORT_NAMES[query.report_id or "world_crop_production_summary"]

        try:
            report_data = await get_psd_report_data(report_id)

            if not report_data.get("data", []):
                raise OpenBBError(
                    "The request was successful but no data was returned. This might be a bug or a network error."
                    + f" -> Report ID: {query.report_id}"
                )
            if report_data.get("error", ""):
                raise OpenBBError(
                    f"Error processing data: {report_data['error']} -> Report ID: {query.report_id}"
                )
        except OpenBBError as e:
            raise e from e

        return report_data.get("data", [])

    @staticmethod
    def transform_data(
        query: GovernmentUsCommodityPsdDataQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[GovernmentUsCommodityPsdData]:
        """Transform and validate the data."""
        return [GovernmentUsCommodityPsdData.model_validate(item) for item in data]
