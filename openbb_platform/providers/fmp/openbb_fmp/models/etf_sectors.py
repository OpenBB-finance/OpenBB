"""FMP ETF Sector Weighting fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)


class FMPEtfSectorsQueryParams(EtfSectorsQueryParams):
    """FMP ETF Sector Weighting Params."""


class FMPEtfSectorsData(EtfSectorsData):
    """FMP ETF Sector Weighting Data."""


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
    def extract_data(
        query: FMPEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}

        for symbol in symbols:
            data = {}
            url = create_url(
                version=3,
                endpoint=f"etf-sector-weightings/{symbol}",
                api_key=api_key,
            )
            result = get_data_many(url, **kwargs)
            df = pd.DataFrame(result).set_index("sector")
            if len(df) > 0:
                for i in df.index:
                    data.update(
                        {
                            i: float(df.loc[i]["weightPercentage"].replace("%", ""))
                            * 0.01
                        }
                    )
                results.update({symbol: data})

        output = (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .fillna(0)
            .replace(0, None)
            .rename(columns={"index": "symbol"})
        ).transpose()
        output.columns = output.loc["symbol"].to_list()
        output = output.drop("symbol", axis=0).sort_values(
            by=output.columns[0], ascending=False
        )
        return (
            output.reset_index()
            .rename(columns={"index": "sector"})
            .to_dict(orient="records")
        )

    @staticmethod
    def transform_data(
        query: FMPEtfSectorsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfSectorsData]:
        """Return the transformed data."""
        return [FMPEtfSectorsData.model_validate(d) for d in data]
