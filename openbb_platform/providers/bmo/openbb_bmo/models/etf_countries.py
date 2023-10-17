"""BMO ETF Countries fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_bmo.utils.helpers import get_all_etfs, get_fund_properties
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)


class BmoEtfCountriesQueryParams(EtfCountriesQueryParams):
    """BMO ETF Countries Query Params"""


class BmoEtfCountriesData(EtfCountriesData):
    """BMO ETF Countries Data."""


class BmoEtfCountriesFetcher(
    Fetcher[
        BmoEtfCountriesQueryParams,
        List[BmoEtfCountriesData],
    ]
):
    """Transform the query, extract and transform the data from the BMO endpoint."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfCountriesQueryParams:
        """Transform the query."""
        return BmoEtfCountriesQueryParams(**params)

    @staticmethod
    def extract_countries(symbol: str) -> Dict:
        """Extract the countries data from the fund info."""

        data = pd.DataFrame()
        _data = get_fund_properties(symbol)
        result = {}
        if len(_data) > 0 and "allocations" in _data[0]:
            _data = _data[0]
            key = -1
            # Find the correct position in the data for the geographic allocations.
            for i in range(0, len(_data["allocations"])):
                if _data["allocations"][i]["code"] == "holdings_geography":
                    key = i
            if key != -1:
                data = (
                    pd.DataFrame(_data["allocations"][key]["values"])
                    .rename(columns={"label": "country", "value": "weight"})
                    .set_index("country")
                )
                data = data.transpose()
                data.columns = [c.lower().replace(" ", "_") for c in data.columns]
                data = data.transpose()
                for i in data.index:
                    result.update({i: data.loc[i]["weight"]})
        return result

    @staticmethod
    def extract_data(
        query: BmoEtfCountriesQueryParams,
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
                result = BmoEtfCountriesFetcher.extract_countries(symbol)
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
    ) -> List[BmoEtfCountriesData]:
        """Transform the data."""
        return [BmoEtfCountriesData.model_validate(d) for d in data]
