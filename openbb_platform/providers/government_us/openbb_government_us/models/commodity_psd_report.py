"""US Government Production Supply & Distribution Publications Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commodity_psd_report import (
    CommodityPsdReportData,
    CommodityPsdReportQueryParams,
)
from pydantic import Field, field_validator

COMMODITIES = {
    "citrus": "Citrus",
    "coffee": "Coffee",
    "cotton": "Cotton",
    "dairy": "Dairy",
    "fruit": "Fruit",
    "grain": "Grain",
    "livestock": "Livestock_poultry",
    "oilseeds": "Oilseeds",
    "stone_fruit": "StoneFruit",
    "sugar": "Sugar",
    "tree_nuts": "TreeNuts",
    "world_production": "production",
}


class GovernmentUsCommodityPsdReportQueryParams(CommodityPsdReportQueryParams):
    """US Government Commodity PSD Report Query Params.

    Source: https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads
    """

    __json_schema_extra__ = {
        "year": {
            "x-widget_config": {
                "description": "Year of the report to retrieve. Data is available from 2006 onwards.",
                "type": "number",
                "row": 1,
            }
        },
        "month": {
            "x-widget_config": {
                "description": "Month of the report to retrieve.",
                "row": 1,
                "options": [
                    {"value": i, "label": month}
                    for i, month in enumerate(
                        [
                            "January",
                            "February",
                            "March",
                            "April",
                            "May",
                            "June",
                            "July",
                            "August",
                            "September",
                            "October",
                            "November",
                            "December",
                        ],
                        start=1,
                    )
                ],
            }
        },
        "commodity": {
            "multiple_items_allowed": False,
            "choices": list(COMMODITIES),
            "x-widget_config": {
                "row": 1,
                "description": "Commodity for the report to retrieve.",
                "options": [
                    {"value": commodity, "label": commodity.replace("_", " ").title()}
                    for commodity in COMMODITIES
                ],
            },
        },
    }

    @field_validator("year", mode="before", check_fields=False)
    @classmethod
    def _validate_year(cls, v):
        """Validate year is >= 2006."""
        if v < 2006:
            raise OpenBBError(ValueError("Data is only available from 2006 onwards."))
        return v

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity is in the list."""
        if v.lower() not in COMMODITIES:
            raise OpenBBError(
                ValueError(
                    f"Commodity '{v}' is not supported. "
                    + "Please choose from the available commodities -> "
                    + f"{', '.join(COMMODITIES.keys())}"
                )
            )
        return v.lower()


class GovernmentUsCommodityPsdReportData(CommodityPsdReportData):
    """US Government Commodity PSD Report Data."""

    data_format: dict[str, str] = Field(
        description="Data format information.",
        default_factory=lambda: {
            "data_type": "pdf",
            "filename": "commodity_psd_report.pdf",
        },
    )


class GovernmentUsCommodityPsdReportFetcher(
    Fetcher[
        GovernmentUsCommodityPsdReportQueryParams,
        GovernmentUsCommodityPsdReportData,
    ]
):
    """US Government Commodity PSD Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> GovernmentUsCommodityPsdReportQueryParams:
        """Transform params into the query params model."""
        return GovernmentUsCommodityPsdReportQueryParams(**params)

    @staticmethod
    def extract_data(
        query: GovernmentUsCommodityPsdReportQueryParams,
        credentials: dict[str, Any] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract data from the provider."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        api_commodity = COMMODITIES.get(query.commodity.lower(), query.commodity)
        month = f"{query.month:02d}"
        url = f"https://apps.fas.usda.gov/PSDOnline/CircularDownloader.ashx?year={query.year}&month={month}&commodity={api_commodity}"
        output = b""

        try:
            response = make_request(url)

            if response.status_code == 404 or not response.content:
                raise OpenBBError(
                    ValueError(
                        "No data found for the given parameters. Please check the commodity, year, and month."
                    )
                )

            if response.status_code == 200 and response.content[:4] == b"%PDF":
                output = response.content
            else:
                raise OpenBBError(
                    ValueError(
                        "Failed to retrieve data. Unexpected response from the server."
                        + f" Status code: {response.status_code} -> "
                        + f"Response content: {response.content.decode('utf-8', errors='ignore')}"
                    )
                )
        except Exception as e:
            raise OpenBBError(e) from e

        return {"content": output}

    @staticmethod
    def transform_data(
        query: GovernmentUsCommodityPsdReportQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> GovernmentUsCommodityPsdReportData:
        """Transform data into the encoded format."""
        # pylint: disable=import-outside-toplevel
        import base64

        if not data:
            raise OpenBBError("The request was successful but no data was returned.")

        encoded_content = base64.b64encode(data.get("content", b"")).decode("utf-8")  # type: ignore
        filename = f"psd_report_{query.commodity}_{query.year}_{query.month:02d}.pdf"
        data_format = {
            "data_type": "pdf",
            "filename": filename,
        }

        return GovernmentUsCommodityPsdReportData(
            content=encoded_content, data_format=data_format
        )
