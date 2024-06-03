from typing import Any, Dict, List, Optional
from datetime import date
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_providers.utils.cramer_utils import get_cramer_picks
from pydantic import Field

class CramerQueryParams(QueryParams):
    """
    Seeking Alpha Query Parameters


    """
    lookback: Optional[int] = Field(description="lookback days for cramer recommendations.", default=3)

class CramerData(Data):
    """Sample provider data for commitment of traders.

    """

    ticker: str = Field(description="Ticker .")
    as_of_date: date = Field(description="as of date.")
    recommendation: str = Field(description="jim cramer recommendation")




class CramerFetcher(
    Fetcher[
        CramerQueryParams,
        List[CramerData],
    ]
):
    """ FMP Commitment of Traders Fetcher class.

    This class is responsible for the actual data retrieval.
    """
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CramerQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        return CramerQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CramerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Define example extract_data.

        Here we make the actual request to the data provider and receive the raw data.
        If you said your Provider class needs credentials you can get them here.
        """

        try:
            lookback = query.lookback

            response = get_cramer_picks(lookback)

            return response
        except Exception as e:
            raise Exception(str(e))

    @staticmethod
    def transform_data(
        query: CramerQueryParams, data: List[dict], **kwargs: Any
    ) -> List[CramerData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [CramerData(**d) for d in data]

