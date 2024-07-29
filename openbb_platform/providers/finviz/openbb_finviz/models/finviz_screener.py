from typing import Any, Dict
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field
from finvizfinance.screener.overview import Overview
from pydantic import BaseModel, model_validator
from typing import Optional, List
import json


class FinvizScreenerQueryParams(QueryParams):
    """
    Finviz Query Parameters for finviz screener

    https://pypi.org/project/finvizfinance/

    This Screener mimics the filters you can apply on this page
    https://finviz.com/screener.ashx

    """

    presets: str = Field(description="name ofa pre-configured filter from presets config file.")

    filters: Dict[str, str] = Field(description="A dictionary of Finviz Filters.")

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class FinvizScreenerData(Data):
    """Sample provider data for finviz screener.

    """

    ticker: str = Field(description="Ticker.", alias='Ticker')
    company: str = Field(description="Company Name.", alias='Company')
    sector: str = Field(description="Company Sector.", alias='Sector')
    industry : str  = Field(description="Company Industry.", alias="Industry")
    country  : str  = Field(description="Company Country", alias="Country")
    marketcap: float = Field(description="Company Market Cap.", alias="Market Cap")
    pe: float = Field(description="P/E Ratio.", alias="P/E")
    price: float = Field(description="Current Price", alias="Price")
    change: float = Field(description="Price Change", alias="Change")
    volume: float = Field(description="Volume", alias="Volume")



class FinvizScreenerFetcher(
    Fetcher[
        FinvizScreenerQueryParams,
        List[FinvizScreenerData],
    ]
):
    """ Finviz Screener Fetcher class.

    This class is responsible for the actual data retrieval.
    """


    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizScreenerQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        return FinvizScreenerQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizScreenerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Define example extract_data.

        Here we make the actual request to the data provider and receive the raw data.
        If you said your Provider class needs credentials you can get them here.
        """
        filters = query.filters
        foverview = Overview()
        foverview.set_filter(filters_dict=filters)
        df = foverview.screener_view()
        return df.to_dict('records') if df is not None else []

    @staticmethod
    def transform_data(
        query: FinvizScreenerQueryParams, data: List[dict], **kwargs: Any
    ) -> List[FinvizScreenerData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [FinvizScreenerData(**d) for d in data]




