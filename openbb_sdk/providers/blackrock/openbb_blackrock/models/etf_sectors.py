"""Blackrock ETF Sectors fetcher."""

from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from pydantic import Field

from openbb_blackrock.models.etf_holdings import (
    blackrock_america_holdings,
    blackrock_canada_holdings,
)
from openbb_blackrock.utils.helpers import COUNTRIES, America, Canada


class BlackrockEtfSectorsQueryParams(EtfSectorsQueryParams):
    """Blackrock ETF Info Query Params"""

    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.  Symbol suffix with `.TO` can be used as a proxy for Canada.",
        default="america",
    )
    date: Optional[str] = Field(description="The as-of date for the data.")


class BlackrockEtfSectorsData(EtfSectorsData):
    """Blackrock ETF Info Data."""

    class Config:
        fields = {
            "energy": "Energy",
            "materials": "Basic Materials",
            "industrials": "Industrials",
            "consumer_cyclical": "Consumer Discretionary",
            "consumer_defensive": "Consumer Staples",
            "financial_services": "Financials",
            "technology": "Information Technology",
            "health_care": "Healthcare",
            "communication_services": "Communication",
            "utilities": "Utilities",
            "real_estate": "Real Estate",
        }

    cash_or_derivatives: Optional[float] = Field(
        description="Cash and/or derivatives.", alias="Cash and/or Derivatives"
    )


class BlackrockEtfSectorsFetcher(
    Fetcher[
        BlackrockEtfSectorsQueryParams,
        List[BlackrockEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the Blackrock endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfSectorsQueryParams:
        """Transform the query."""
        return BlackrockEtfSectorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Blackrock endpoint."""
        country = query.country

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}

        for symbol in symbols:
            coutry = query.country  # noqa
            data = {}
            if ".TO" in symbol or query.country == "canada":
                symbol = symbol.replace(".TO", "")  # noqa
                country = "canada"
            _etfs = (
                America.get_all_etfs()
                if country == "america"
                else Canada.get_all_etfs()
            )
            if symbol in _etfs["symbol"].to_list():
                r = (
                    blackrock_america_holdings.get(
                        url=America.generate_holdings_url(symbol, query.date),  # type: ignore
                    )
                    if country == "america"
                    else blackrock_canada_holdings.get(
                        url=Canada.generate_holdings_url(symbol, query.date),  # type: ignore
                    )
                )
                if r.status_code != 200:
                    raise RuntimeError(
                        "Error with Blackrock endpoint ->" + str(r.status_code)
                    )

                indexed = pd.read_csv(StringIO(r.text), usecols=[0])
                target = (
                    "Ticker" if "Name" not in indexed.iloc[:, 0].to_list() else "Name"
                )
                idx = []
                idx = indexed[indexed.iloc[:, 0] == target].index.tolist()
                idx_value = idx[1] if len(idx) > 1 else idx[0]
                _holdings = pd.read_csv(
                    StringIO(r.text), header=idx_value, thousands=","
                )
                _holdings = _holdings.reset_index()
                columns = _holdings.iloc[0, :].values.tolist()
                _holdings.columns = columns
                holdings = (
                    _holdings.iloc[1:-1, :]
                    if query.country == "canada"
                    else _holdings.iloc[1:-2, :]
                )
                holdings = holdings.convert_dtypes().fillna("0")
                _sectors = holdings[["Name", "Sector", "Weight (%)"]]
                _sectors = _sectors.rename(
                    columns={"Weight (%)": "weight", "Sector": "sector"}
                )
                _sectors["weight"] = _sectors["weight"].astype(float)
                sectors = (
                    _sectors.groupby("sector")[["weight"]]
                    .sum()
                    .sort_values(by="weight", ascending=False)
                )
                sectors = sectors.rename(
                    index={
                        "Telecommunication Services": "communication_services",
                        "-": "other",
                    }
                )
                for i in sectors.index:
                    data.update({i: sectors.loc[i]["weight"]})
                    if data != {}:
                        results.update({symbol: data})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BlackrockEtfSectorsData]:
        """Return the transformed data."""
        return [BlackrockEtfSectorsData(**d) for d in data]
