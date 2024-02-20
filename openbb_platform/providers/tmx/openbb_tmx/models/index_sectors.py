"""TMX Index Sectors fetcher."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_sectors import (
    IndexSectorsData,
    IndexSectorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils.helpers import get_data_from_url, tmx_indices_backend
from pydantic import Field, field_validator


class TmxIndexSectorsQueryParams(IndexSectorsQueryParams):
    """TMX Index Sectors Query Params"""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All Index data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 1 day.",
    )


class TmxIndexSectorsData(IndexSectorsData):
    """TMX Index Sectors Data."""

    @field_validator("weight", mode="after", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxIndexSectorsFetcher(
    Fetcher[
        TmxIndexSectorsQueryParams,
        List[TmxIndexSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxIndexSectorsQueryParams:
        """Transform the query."""
        return TmxIndexSectorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the TMX endpoint."""

        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"

        data = await get_data_from_url(
            url,
            use_cache=query.use_cache,
            backend=tmx_indices_backend,
        )

        return data

    @staticmethod
    def transform_data(
        query: TmxIndexSectorsQueryParams, data: Dict, **kwargs: Any
    ) -> List[TmxIndexSectorsData]:
        """Return the transformed data."""
        results = []
        data = data.copy()
        if data == {}:
            raise EmptyDataError
        if (
            query.symbol in data["indices"]
            and "sectors" in data["indices"][query.symbol]
        ):
            temp = data["indices"][query.symbol].get("sectors")
            results = [
                {
                    "sector": d.get("name").lower().replace(" ", "_"),
                    "weight": d.get("weight"),
                }
                for d in temp
                if temp is not None
            ]

        return [TmxIndexSectorsData.model_validate(d) for d in results]
