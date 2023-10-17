"""BMO ETF Sectors fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_bmo.utils.helpers import get_all_etfs, get_fund_properties
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)


class BmoEtfSectorsQueryParams(EtfSectorsQueryParams):
    """BMO ETF Sectors Query Params"""


class BmoEtfSectorsData(EtfSectorsData):
    """BMO ETF Sectors Data."""

    __alias_dict__ = {
        "technology": "information_technology",
        "health_care": "health_care",
        "financial_services": "financials",
        "consumer_cyclical": "consumer_discretionary",
        "consumer_defensive": "consumer_staples",
    }


class BmoEtfSectorsFetcher(
    Fetcher[
        BmoEtfSectorsQueryParams,
        List[BmoEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the BMO endpoint."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfSectorsQueryParams:
        """Transform the query."""
        return BmoEtfSectorsQueryParams(**params)

    @staticmethod
    def extract_sectors(symbol: str) -> Dict:
        """Extract the sectors data from the fund info."""

        data = pd.DataFrame()
        _data = get_fund_properties(symbol)
        result = {}
        if len(_data) > 0 and "allocations" in _data[0]:
            _data = _data[0]
            key = -1
            # Find the correct position in the data for the geographic allocations.
            for i in range(0, len(_data["allocations"])):
                if _data["allocations"][i]["code"] == "holdings_sector_mjr":
                    key = i
            if key != -1:
                data = (
                    pd.DataFrame(_data["allocations"][key]["values"])
                    .rename(columns={"label": "sector", "value": "weight"})
                    .set_index("sector")
                )
                data = data.transpose()
                data.columns = [
                    c.lower()
                    .replace(" ", "_")
                    .replace("&", "")
                    .replace(",", "")
                    .replace("__", "_")
                    for c in data.columns
                ]
                data = data.transpose()
                for i in data.index:
                    result.update({i: data.loc[i]["weight"]})
        return result

    @staticmethod
    def extract_data(
        query: BmoEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BMO endpoint."""

        results = {}
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        etfs = get_all_etfs()["symbol"].to_list()

        for symbol in symbols:
            result = {}
            symbol = (  # noqa
                symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")
            )
            if symbol in etfs:
                result = BmoEtfSectorsFetcher.extract_sectors(symbol)
            if result != {}:
                results.update({symbol: result})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .fillna(value=0)
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[BmoEtfSectorsData]:
        """Transform the data."""
        return [BmoEtfSectorsData.model_validate(d) for d in data]
