"""FMP ETF Sectors Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPEtfSectorsQueryParams(EtfSectorsQueryParams):
    """FMP ETF Sectors Query."""


class FMPEtfSectorsData(EtfSectorsData):
    """FMP ETF Sectors Data."""

    __alias_dict__ = {"weight": "weightPercentage"}


class FMPEtfSectorsFetcher(
    Fetcher[
        FMPEtfSectorsQueryParams,
        List[FMPEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfSectorsQueryParams:
        """Transform the query."""
        return FMPEtfSectorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint=f"etf-sector-weightings/{query.symbol.upper()}",
            api_key=api_key,
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfSectorsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfSectorsData]:
        """Return the transformed data."""
        for d in data:
            if d["weightPercentage"] is not None and d["weightPercentage"].endswith(
                "%"
            ):
                d["weightPercentage"] = float(d["weightPercentage"][:-1]) / 100
        return [FMPEtfSectorsData.model_validate(d) for d in data]
