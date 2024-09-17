"""SEC Compare Company Facts Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union
from warnings import warn

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.compare_company_facts import (
    CompareCompanyFactsData,
    CompareCompanyFactsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_sec.utils.definitions import (
    FACT_CHOICES,
    FACTS,
    FISCAL_PERIODS,
)
from pydantic import Field, field_validator


class SecCompareCompanyFactsQueryParams(CompareCompanyFactsQueryParams):
    """SEC Compare Company Facts Query.

    Source: https://www.sec.gov/edgar/sec-api-documentation

    The xbrl/frames API aggregates one fact for each reporting entity
    that is last filed that most closely fits the calendrical period requested.

    Because company financial calendars can start and end on any month or day and even change in length from quarter to
    quarter according to the day of the week, the frame data is assembled by the dates that best align with a calendar
    quarter or year. Data users should be mindful different reporting start and end dates for facts contained in a frame.
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "fact": {"multiple_items_allowed": False, "choices": sorted(FACTS)},
        "fiscal_period": {
            "multiple_items_allowed": False,
            "choices": ["fy", "q1", "q2", "q3", "q4"],
        },
    }

    fact: FACT_CHOICES = Field(
        default="Revenues",
        description="Fact or concept from the SEC taxonomy, in UpperCamelCase. Defaults to, 'Revenues'."
        + " AAPL, MSFT, GOOG, BRK-A currently report revenue as, 'RevenueFromContractWithCustomerExcludingAssessedTax'."
        + " In previous years, they have reported as 'Revenues'.",
    )
    year: Optional[int] = Field(
        default=None,
        description="The year to retrieve the data for. If not provided, the current year is used."
        + " When symbol(s) are provided, excluding the year will return all reported values for the concept.",
    )
    fiscal_period: Optional[FISCAL_PERIODS] = Field(
        default=None,
        description="The fiscal period to retrieve the data for."
        + " If not provided, the most recent quarter is used."
        + " This parameter is ignored when a symbol is supplied.",
    )
    instantaneous: bool = Field(
        default=False,
        description="Whether to retrieve instantaneous data. See the notes above for more information."
        + " Defaults to False. Some facts are only available as instantaneous data."
        + "\nThe function will automatically attempt the inverse of this parameter"
        + " if the initial fiscal quarter request fails."
        + " This parameter is ignored when a symbol is supplied.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cache for the request. Defaults to True.",
    )

    @field_validator("fact", mode="before", check_fields=False)
    @classmethod
    def validate_fact(cls, v):
        """Set the default state."""
        if not v or v == "":
            return "Revenues"
        return v


class SecCompareCompanyFactsData(CompareCompanyFactsData):
    """SEC Compare Company Facts Data."""

    __alias_dict__ = {
        "reported_date": "filed",
        "period_beginning": "start",
        "period_ending": "end",
        "fiscal_year": "fy",
        "fiscal_period": "fp",
        "name": "entityName",
        "accession": "accn",
        "value": "val",
        "location": "loc",
    }

    cik: Union[str, int] = Field(
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    location: Optional[str] = Field(
        default=None,
        description="Geographic location of the reporting entity.",
    )
    form: Optional[str] = Field(
        default=None,
        description="The SEC form associated with the fact or concept.",
    )
    frame: Optional[str] = Field(
        default=None,
        description="The frame ID associated with the fact or concept, if applicable.",
    )
    accession: str = Field(
        description="SEC filing accession number associated with the reported fact or concept.",
    )
    fact: str = Field(
        description="The display name of the fact or concept.",
    )
    unit: str = Field(
        default=None,
        description="The unit of measurement for the fact or concept.",
    )


class SecCompareCompanyFactsFetcher(
    Fetcher[SecCompareCompanyFactsQueryParams, List[SecCompareCompanyFactsData]]
):
    """SEC Compare Company Facts Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecCompareCompanyFactsQueryParams:
        """Transform the query."""
        return SecCompareCompanyFactsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCompareCompanyFactsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.frames import get_concept, get_frame

        results: Dict = {}
        if not query.symbol:
            results = await get_frame(
                fact=query.fact,
                year=query.year,
                fiscal_period=query.fiscal_period,
                instantaneous=query.instantaneous,
                use_cache=query.use_cache,
            )
        if query.symbol is not None:
            if query.instantaneous is True:
                warn(
                    "The 'instantaneous' parameter is ignored when a symbol is supplied."
                )
            if query.fiscal_period is not None:
                warn(
                    "The 'fiscal_period' parameter is ignored when a symbol is supplied."
                )
            results = await get_concept(
                symbol=query.symbol,
                fact=query.fact,
                year=query.year,
                use_cache=query.use_cache,
            )
        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: SecCompareCompanyFactsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[SecCompareCompanyFactsData]]:
        """Transform the data and validate the model."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        metadata = data.get("metadata")
        results_data = data.get("data", [])
        return AnnotatedResult(
            result=[SecCompareCompanyFactsData.model_validate(d) for d in results_data],  # type: ignore
            metadata=metadata,
        )
