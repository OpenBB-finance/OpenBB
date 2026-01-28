"""Weather Bulletin Download Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class WeatherBulletinDownloadQueryParams(QueryParams):
    """Weather Bulletin Query."""

    urls: str | dict | list = Field(
        kw_only=True,
        description="URLs for reports to download.",
    )

    @field_validator("urls", mode="before", check_fields=False)
    @classmethod
    def _validate_urls(cls, v):
        """Validate URLs input."""
        if isinstance(v, str):
            if "," in v:
                return v.split(",")
            return [v]
        if isinstance(v, dict) and "urls" in v:
            return v["urls"]
        if isinstance(v, list):
            return v
        raise ValueError("Invalid format for URLs. Must be str, dict, or list.")


class WeatherBulletinDownloadData(Data):
    """Weather Bulletin Data."""

    content: str = Field(
        description="Base64 encoded content of the weather bulletin document.",
    )
