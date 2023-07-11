"""FMP Key Executives Fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol
from openbb_provider.model.data.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from openbb_fmp.helpers import get_data


class FMPKeyExecutivesQueryParams(QueryParams, BaseSymbol):
    """FMP Key Executives QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Key-Executives

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    key_executive_name : Optional[str]
        The name of the key executive.
    key_executive_title : Optional[str]
        The title of the key executive.
    key_executive_title_since : Optional[datetime]
        The title since of the key executive.
    key_executive_year_born : Optional[datetime]
        The year born of the key executive.
    key_executive_gender: Optional[str]
        The gender of the key executive.
    """

    key_executive_name: Optional[str]
    key_executive_title: Optional[str]
    key_executive_title_since: Optional[datetime]
    key_executive_year_born: Optional[datetime]
    key_executive_gender: Optional[str]


class FMPKeyExecutivesData(Data):
    name: str
    title: str
    titleSince: Optional[datetime]
    yearBorn: Optional[datetime]
    gender: Optional[str]


class FMPKeyExecutivesFetcher(
    Fetcher[
        KeyExecutivesQueryParams,
        KeyExecutivesData,
        FMPKeyExecutivesQueryParams,
        FMPKeyExecutivesData,
    ]
):
    @staticmethod
    def transform_query(
        query: KeyExecutivesQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPKeyExecutivesQueryParams:
        return FMPKeyExecutivesQueryParams(
            symbol=query.symbol,
            key_executive_name=query.key_executive_name,
            key_executive_title=query.key_executive_title,
            key_executive_title_since=query.key_executive_title_since,
            key_executive_year_born=query.key_executive_year_born,
            key_executive_gender=query.key_executive_gender,
        )

    @staticmethod
    def extract_data(
        query: FMPKeyExecutivesQueryParams, api_key: str
    ) -> List[FMPKeyExecutivesData]:
        base_url = "https://financialmodelingprep.com/api/v3/"
        request_url = f"{base_url}key-executives/{query.symbol}?apikey={api_key}"
        data = get_data(request_url)
        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        if query.key_executive_name:
            data = [x for x in data if x["name"] == query.key_executive_name]
        if query.key_executive_title:
            data = [x for x in data if x["title"] == query.key_executive_title]
        if query.key_executive_title_since:
            data = [
                x for x in data if x["titleSince"] == query.key_executive_title_since
            ]
        if query.key_executive_year_born:
            data = [x for x in data if x["yearBorn"] == query.key_executive_year_born]
        if query.key_executive_gender:
            data = [x for x in data if x["gender"] == query.key_executive_gender]

        return [FMPKeyExecutivesData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[FMPKeyExecutivesData],
    ) -> List[KeyExecutivesData]:
        return data_transformer(data, KeyExecutivesData)
