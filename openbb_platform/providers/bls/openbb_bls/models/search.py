"""BLS Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_bls.utils.constants import SURVEY_CATEGORIES, SURVEY_CATEGORY_NAMES
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bls_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class BlsSearchQueryParams(SearchQueryParams):
    """BLS Search Query Parameters."""

    __json_schema_extra__ = {
        "category": {
            "multiple_items_allowed": False,
            "choices": list(SURVEY_CATEGORY_NAMES),
        },
    }

    category: SURVEY_CATEGORIES = Field(
        description="""The category of BLS survey to search within.
        An empty search query will return all series within the category. Options are:
        \n    cpi - Consumer Price Index
        \n    pce - Personal Consumption Expenditure
        \n    ppi - Producer Price Index
        \n    ip - Industry Productivity
        \n    jolts - Job Openings and Labor Turnover Survey
        \n    nfp - Nonfarm Payrolls
        \n    cps - Current Population Survey
        \n    lfs - Labor Force Statistics
        \n    wages - Wages
        \n    ec - Employer Costs
        \n    sla - State and Local Area Employment
        \n    bed - Business Employment Dynamics
        \n    tu - Time Use
        """,
    )
    include_extras: bool = Field(
        default=False,
        description="Include additional information in the search results."
        + " Extra fields returned are metadata and vary by survey."
        + " Fields are undefined strings that typically have names ending with '_code'.",
    )
    include_code_map: bool = Field(
        default=False,
        description="When True, includes the complete code map for eaçh survey in the category,"
        + " returned separately as a nested JSON to the `extras['results_metadata']` property of the response."
        + " Example content is the NAICS industry map for PPI surveys."
        + " Each code is a value within the 'symbol' of the time series.",
    )


class BlsSearchData(SearchData):
    """BLS Search Data."""

    __alias_dict__ = {
        "symbol": "series_id",
        "title": "series_title",
    }


class BlsSearchFetcher(Fetcher[BlsSearchQueryParams, List[BlsSearchData]]):
    """BLS Search Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlsSearchQueryParams:
        """Transform query parameters."""
        return BlsSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_bls.utils.helpers import open_asset
        from pandas import Series

        try:
            df = open_asset(f"{query.category}_series")
        except OpenBBError as e:
            raise e from e

        terms = [term.strip() for term in query.query.split(";")] if query.query else []

        if not terms:
            records = (
                df.to_dict(orient="records")
                if query.include_extras is True
                else df.filter(
                    items=["series_id", "series_title", "survey_name"], axis=1
                ).to_dict(orient="records")
            )
        else:
            combined_mask = Series([True] * len(df))
            for term in terms:
                mask = df.apply(
                    lambda row, term=term: row.astype(str).str.contains(
                        term, case=False, regex=True, na=False
                    )
                ).any(axis=1)
                combined_mask &= mask

            matches = df[combined_mask]

            if matches.empty:
                raise EmptyDataError("No results found for the provided query.")

            records = (
                matches.to_dict(orient="records")
                if query.include_extras is True
                else matches.filter(
                    items=["series_id", "series_title", "survey_name"], axis=1
                ).to_dict(orient="records")
            )

        return records

    @staticmethod
    def transform_data(
        query: BlsSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> AnnotatedResult[List[BlsSearchData]]:
        """Transform the data."""
        metadata: Dict = {}
        if query.include_code_map is True:
            # pylint: disable=import-outside-toplevel
            from openbb_bls.utils.helpers import open_asset

            try:
                metadata = open_asset(f"{query.category}_codes")
            except OpenBBError as e:
                raise e from e

        return AnnotatedResult(
            result=[BlsSearchData.model_validate(d) for d in data],
            metadata=metadata,
        )
