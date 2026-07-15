"""NSE Index Constituents Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from pydantic import Field

# Friendly index identifiers -> official NSE Indices constituent files.
# The files are published by NSE Indices Limited and refreshed on index rebalancing.
INDEX_FILE_MAP = {
    "NIFTY_50": "ind_nifty50list.csv",
    "NIFTY_100": "ind_nifty100list.csv",
    "NIFTY_200": "ind_nifty200list.csv",
    "NIFTY_500": "ind_nifty500list.csv",
    "NIFTY_NEXT_50": "ind_niftynext50list.csv",
    "NIFTY_BANK": "ind_niftybanklist.csv",
    "NIFTY_IT": "ind_niftyitlist.csv",
    "NIFTY_AUTO": "ind_niftyautolist.csv",
    "NIFTY_PHARMA": "ind_niftypharmalist.csv",
    "NIFTY_FMCG": "ind_niftyfmcglist.csv",
    "NIFTY_METAL": "ind_niftymetallist.csv",
    "NIFTY_ENERGY": "ind_niftyenergylist.csv",
    "NIFTY_FIN_SERVICE": "ind_niftyfinservicelist.csv",
    "NIFTY_MIDCAP_100": "ind_niftymidcap100list.csv",
    "NIFTY_SMALLCAP_100": "ind_niftysmallcap100list.csv",
}

BASE_URL = "https://www.niftyindices.com/IndexConstituent/"


class NseIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """NSE Index Constituents Query.

    Source: https://www.niftyindices.com

    The `symbol` is an index identifier, e.g. 'nifty_50' or 'nifty_bank'.
    """


class NseIndexConstituentsData(IndexConstituentsData):
    """NSE Index Constituents Data."""

    industry: str | None = Field(
        default=None,
        description="Industry classification of the constituent, as assigned by NSE.",
    )
    isin: str | None = Field(
        default=None,
        description="International Securities Identification Number (ISIN) of the constituent.",
    )
    series: str | None = Field(
        default=None,
        description="Trading series of the constituent on the NSE, e.g. 'EQ'.",
    )


class NseIndexConstituentsFetcher(
    Fetcher[
        NseIndexConstituentsQueryParams,
        list[NseIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the NSE Indices files."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NseIndexConstituentsQueryParams:
        """Transform the query params."""
        return NseIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NseIndexConstituentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the NSE Indices endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import BytesIO

        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import make_request
        from pandas import read_csv

        key = query.symbol.upper().replace(" ", "_").replace("-", "_")

        if key not in INDEX_FILE_MAP:
            supported = ", ".join(sorted(INDEX_FILE_MAP))
            raise ValueError(f"Unsupported index '{query.symbol}'. Supported indices are: {supported}.")

        url = BASE_URL + INDEX_FILE_MAP[key]
        # The NSE Indices host expects a browser-like User-Agent.
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        }

        response = make_request(url, headers=headers, **kwargs)

        if response.status_code != 200 or not response.content:
            raise EmptyDataError(f"No data returned for index '{query.symbol}' (HTTP {response.status_code}).")

        df = read_csv(BytesIO(response.content))
        df.columns = [str(col).strip() for col in df.columns]

        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: NseIndexConstituentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NseIndexConstituentsData]:
        """Return the transformed data."""

        def _clean(value: Any) -> str | None:
            """Strip whitespace and normalize empty values to None."""
            if value is None:
                return None
            text = str(value).strip()
            return text or None

        results: list[NseIndexConstituentsData] = []

        for row in data:
            symbol = _clean(row.get("Symbol"))
            if not symbol:
                continue
            results.append(
                NseIndexConstituentsData.model_validate(
                    {
                        "symbol": symbol,
                        "name": _clean(row.get("Company Name")),
                        "industry": _clean(row.get("Industry")),
                        "isin": _clean(row.get("ISIN Code")),
                        "series": _clean(row.get("Series")),
                    }
                )
            )

        return results
