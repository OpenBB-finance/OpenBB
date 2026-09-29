"""US Government Production Supply & Distribution Report Data & Time Series Model."""

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commodity_psd_data import (
    CommodityPsdData,
    CommodityPsdDataQueryParams,
)
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.psd_codes import (
    ATTRIBUTES,
    COMMODITIES,
    COUNTRIES,
    PSD_REPORT_NAMES,
    REGIONS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

COUNTRY_CHOICES = {
    **{k: v for k, v in COUNTRIES.items() if k != "world"},
    **REGIONS,
}


class UsdaCommodityPsdDataQueryParams(CommodityPsdDataQueryParams):
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
                "multiSelect": False,
                "multiple": False,
                "description": "Attribute to filter the data. Ignored when commodity is Report Mode. "
                + "If None, retrieves all available attributes for the commodity. "
                + "The choices are scoped to the selected commodity.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/psd_data_attributes",
                "optionsParams": {"commodity": "$commodity"},
                "style": {"popupWidth": 320},
                "row": 1,
            },
        },
        "country": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "multiSelect": False,
                "multiple": False,
                "description": "Country code(s) to filter the data. Ignored when commodity is Report Mode. "
                + "If None, retrieves data for all countries. "
                + "The choices are scoped to the selected commodity.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/psd_data_countries",
                "optionsParams": {"commodity": "$commodity"},
                "style": {"popupWidth": 320},
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


class UsdaCommodityPsdData(NullTokenMixin, CommodityPsdData):
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
            "region": {"x-widget_config": {"headerName": "Region", "pinned": "left"}},
            "country": {"x-widget_config": {"headerName": "Country", "pinned": "left"}},
            "commodity": {"x-widget_config": {"headerName": "Commodity"}},
            "attribute": {"x-widget_config": {"headerName": "Attribute"}},
            "unit": {"x-widget_config": {"headerName": "Unit"}},
            "marketing_year": {"x-widget_config": {"exclude": True}},
            "value": {"x-widget_config": {"exclude": True}},
        }
    )

    marketing_year: str | None = Field(
        default=None,
        description="Marketing year for the commodity.",
        exclude=True,
    )
    value: float | int | None = Field(
        default=None,
        description="Value for the commodity attribute in the given marketing year.",
        exclude=True,
    )


class UsdaCommodityPsdDataFetcher(
    Fetcher[
        UsdaCommodityPsdDataQueryParams,
        list[UsdaCommodityPsdData],
    ]
):
    """US Government Commodity PSD Data Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> UsdaCommodityPsdDataQueryParams:
        """Transform the query parameters into the model."""
        return UsdaCommodityPsdDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsdaCommodityPsdDataQueryParams,
        credentials: dict[str, Any] | None,
        **kwargs: Any,
    ) -> list:
        """Extract data from the provider."""
        from openbb_government_us.usda.utils.psd_data_downloader import (
            get_psd_report_data,
            get_timeseries,
        )

        if query.commodity is not None:
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
        query: UsdaCommodityPsdDataQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[UsdaCommodityPsdData]:
        """Pivot the marketing-year observations into columns and validate."""
        pivoted: dict[tuple, dict] = {}
        for order, item in enumerate(data):
            key = (
                item.get("region"),
                item.get("country"),
                item.get("commodity"),
                item.get("attribute"),
                item.get("unit"),
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": order,
                    "region": item.get("region"),
                    "country": item.get("country"),
                    "commodity": item.get("commodity"),
                    "attribute": item.get("attribute"),
                    "unit": item.get("unit"),
                }
                pivoted[key] = row
            marketing_year = item.get("marketing_year")
            if marketing_year is not None:
                row[str(marketing_year)] = item.get("value")
        results = sorted(pivoted.values(), key=lambda row: row["_order"])
        return [
            UsdaCommodityPsdData.model_validate(
                {k: v for k, v in row.items() if k != "_order"}
            )
            for row in results
        ]
