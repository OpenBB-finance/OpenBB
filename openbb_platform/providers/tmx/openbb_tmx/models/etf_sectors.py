"""TMX ETF Sectors fetcher."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from pydantic import Field, field_validator


class TmxEtfSectorsQueryParams(EtfSectorsQueryParams):
    """TMX ETF Sectors Query Params"""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfSectorsData(EtfSectorsData):
    """TMX ETF Sectors Data."""

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent values."""
        return v / 100 if v else None


class TmxEtfSectorsFetcher(
    Fetcher[
        TmxEtfSectorsQueryParams,
        list[TmxEtfSectorsData],
    ]
):
    """TMX ETF Sectors Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEtfSectorsQueryParams:
        """Transform the query."""
        return TmxEtfSectorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfSectorsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_tmx.utils.helpers import get_all_etfs
        from pandas import DataFrame

        results: list = []
        _data = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        symbols = query.symbol.split(",")

        for symbol in symbols:
            s = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
            target = DataFrame()
            _target = _data[_data["symbol"] == s]["sectors"]

            if len(_target) > 0:
                target = DataFrame.from_records(_target.iloc[0]).rename(
                    columns={"name": "sector", "percent": "weight"}
                )
                target.loc[:, "symbol"] = symbol.upper()
                result = (
                    target[["symbol", "sector", "weight"]]
                    .replace({float("nan"): None})
                    .reset_index(drop=True)
                    .to_dict("records")
                )
                results.extend(result)
            else:
                warnings.warn(f"No sectors info found for ETF symbol: {symbol}.")

        if not results:
            raise EmptyDataError("No data found for the given ETF symbols.")

        return results

    @staticmethod
    def transform_data(
        query: TmxEtfSectorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEtfSectorsData]:
        """Return the transformed data."""
        return [TmxEtfSectorsData.model_validate(d) for d in data]
