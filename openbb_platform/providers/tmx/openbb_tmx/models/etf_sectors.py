"""TMX ETF Sectors fetcher."""

# pylint: disable=unused-argument
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from openbb_tmx.utils.helpers import get_all_etfs
from pandas import DataFrame
from pydantic import Field

_warn = warnings.warn


class TmxEtfSectorsQueryParams(EtfSectorsQueryParams):
    """TMX ETF Sectors Query Params"""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfSectorsData(EtfSectorsData):
    """TMX ETF Sectors Data."""


class TmxEtfSectorsFetcher(
    Fetcher[
        TmxEtfSectorsQueryParams,
        List[TmxEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfSectorsQueryParams:
        """Transform the query."""
        return TmxEtfSectorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        target = DataFrame()
        _data = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        _target = _data[_data["symbol"] == symbol]["sectors"]
        if len(_target) > 0:
            target = DataFrame.from_records(_target.iloc[0]).rename(
                columns={"name": "sector", "percent": "weight"}
            )
        return target.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TmxEtfSectorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxEtfSectorsData]:
        """Return the transformed data."""
        target = DataFrame(data)
        target["weight"] = target["weight"] / 100
        target["sector"] = (
            target["sector"].astype(str).str.lower().str.replace(" ", "_")
        )
        target = target.fillna(value="N/A").replace("N/A", None)
        return [
            TmxEtfSectorsData.model_validate(d)
            for d in target.to_dict(orient="records")
        ]
