"""TMX Rankings Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import literal_choices

RANKINGS = {
    "tsx30": ("GetTsx30Companies", "getTsx30Companies"),
    "venture50": ("getVenture50Companies", "getVenture50Companies"),
}


class TmxRankingsQueryParams(QueryParams):
    """TMX Rankings Query Params."""

    __json_schema_extra__ = {
        "ranking": {
            "x-widget_config": {
                "options": literal_choices(
                    ("tsx30", "venture50"),
                    tsx30="TSX 30",
                    venture50="TSX Venture 50",
                )
            }
        }
    }

    ranking: Literal["tsx30", "venture50"] = Field(
        default="tsx30",
        description="The published ranking. 'tsx30' is the Toronto Stock Exchange's"
        + " top thirty performers, 'venture50' the TSX Venture Exchange's top fifty.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " The rankings are published annually and cached for one day."
        + " To bypass, set to False.",
    )


class TmxRankingsData(Data):
    """TMX Rankings Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "share_price_appreciation": "sharePriceAppreciation",
        "market_cap_change": "marketCapChange",
        "website": "url",
        "logo_url": "logoUrl",
    }

    rank: int | None = Field(default=None, description="The position in the ranking.")
    symbol: str | None = Field(default=None, description="The ticker symbol.")
    name: str | None = Field(default=None, description="The name of the company.")
    sector: str | None = Field(default=None, description="The sector of the company.")
    industry: str | None = Field(
        default=None, description="The industry of the company."
    )
    location: str | None = Field(
        default=None, description="The province the company is headquartered in."
    )
    share_price_appreciation: float | None = Field(
        default=None,
        description="The share price appreciation over the ranking period.",
    )
    market_cap_change: float | None = Field(
        default=None,
        description="The change in market capitalization over the ranking period.",
    )
    description: str | None = Field(
        default=None, description="A description of the company."
    )
    website: str | None = Field(default=None, description="The company's website.")

    @field_validator("website", mode="before", check_fields=False)
    @classmethod
    def url_validate(cls, v):
        """Return the website as an absolute URL."""
        from openbb_tmx.utils.helpers import normalize_url

        return normalize_url(v)

    logo_url: str | None = Field(default=None, description="The company's logo.")


class TmxRankingsFetcher(Fetcher[TmxRankingsQueryParams, list[TmxRankingsData]]):
    """TMX Rankings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxRankingsQueryParams:
        """Transform the query."""
        return TmxRankingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxRankingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Read the published ranking."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        operation, key = RANKINGS[query.ranking]
        document = gql.TSX30 if query.ranking == "tsx30" else gql.VENTURE50
        response = await amake_gql_request(
            operation, document, {}, use_cache=query.use_cache
        )

        return (response or {}).get(key) or []

    @staticmethod
    def transform_data(
        query: TmxRankingsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TmxRankingsData]:
        """Flatten the localized fields and normalize the percentages.

        Raises
        ------
        EmptyDataError
            If the ranking has not been published.
        """
        if not data:
            raise EmptyDataError(f"No companies found in the {query.ranking} ranking.")

        def text(value: Any) -> str | None:
            resolved = value.get("en") if isinstance(value, dict) else value

            return resolved.strip() or None if isinstance(resolved, str) else resolved

        def percent(value: Any) -> float | None:
            if value is None:
                return None

            cleaned = str(value).replace("%", "").replace(",", "").strip()

            return float(cleaned) / 100 if cleaned else None

        results = []

        for row in data:
            record: dict = {key: text(value) for key, value in row.items()}
            record["description"] = record.pop("desc", None)
            appreciation = record.pop("sharePrice", None) or record.pop(
                "sharePriceAppreciation", None
            )
            record["sharePriceAppreciation"] = percent(appreciation)
            record["marketCapChange"] = percent(record.get("marketCapChange"))
            results.append(TmxRankingsData.model_validate(record))

        return results
