"""CFTC Commitment of Traders Reports Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)
from pydantic import Field


class CftcCotSearchQueryParams(CotSearchQueryParams):
    """CFTC Commitment of Traders Reports Search Query.

    Source: https://publicreporting.cftc.gov/stories/s/r4w3-av2u
    """


class CftcCotSearchData(CotSearchData):
    """CFTC Commitment of Traders Reports Search Data."""

    __alias_dict__ = {
        "code": "cftc_contract_market_code",
        "name": "contract_market_name",
        "category": "commodity_group_name",
        "subcategory": "commodity_subgroup_name",
    }

    commodity: Optional[str] = Field(default=None, description="Name of the commodity.")


class CftcCotSearchFetcher(Fetcher[CftcCotSearchQueryParams, List[CftcCotSearchData]]):
    """CFTC COT Search Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CftcCotSearchQueryParams:
        """Transform the query params."""
        return CftcCotSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CftcCotSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Search a curated list of CFTC Commitment of Traders Reports."""
        # pylint: disable=import-outside-toplevel
        from importlib.resources import files  # noqa
        from pathlib import Path
        from pandas import read_json

        assets_path = Path(str(files("openbb_cftc").joinpath("assets")))

        with open(assets_path.joinpath("cot_ids.json"), encoding="utf-8") as f:
            available_cot = read_json(f)

        query_string = query.query  # noqa
        return (
            available_cot[
                available_cot["contract_market_name"].str.contains(
                    query_string, case=False
                )
                | available_cot["cftc_contract_market_code"].str.contains(
                    query_string, case=False
                )
                | available_cot["commodity_name"].str.contains(query_string, case=False)
                | available_cot["commodity_group_name"].str.contains(
                    query_string, case=False
                )
                | available_cot["commodity_subgroup_name"].str.contains(
                    query_string, case=False
                )
            ]
            .reset_index(drop=True)
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        query: CotSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[CftcCotSearchData]:
        """Transform the data."""
        return [CftcCotSearchData.model_validate(d) for d in data]
