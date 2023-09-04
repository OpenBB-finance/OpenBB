"""ETF Holdings data model."""


from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class EtfHoldingsQueryParams(QueryParams, BaseSymbol):
    """ETF Holdings Query Params"""


class EtfHoldingsData(Data):
    """ETF Holdings Data."""
