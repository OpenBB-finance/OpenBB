"""SEC Compare Company Facts Model."""

from typing import Any
from warnings import warn

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.compare_company_facts import (
    CompareCompanyFactsData,
    CompareCompanyFactsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_sec.utils.definitions import (
    CALENDAR_PERIODS,
    FACT_CHOICES,
    FACTS,
)


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
        "calendar_period": {
            "multiple_items_allowed": False,
            "choices": ["fy", "q1", "q2", "q3", "q4"],
        },
    }

    fact: FACT_CHOICES = Field(
        default="Revenues",
        description="Fact or concept from the SEC taxonomy, in UpperCamelCase. Defaults to, 'Revenues'."
        + " AAPL, MSFT, GOOG, BRK-A currently report revenue as, 'RevenueFromContractWithCustomerExcludingAssessedTax'."
        + " In previous years, they have reported as 'Revenues'."
        + "\nFacts fall into two groups. Instantaneous balance-sheet concepts are measured at a"
        + " point in time (e.g. 'Assets', 'Liabilities', 'StockholdersEquity', 'Goodwill', 'LongTermDebt');"
        + " the full set is openbb_sec.utils.definitions.INSTANT_FACTS. Everything else is a flow concept"
        + " from the income or cash-flow statement, measured over a period"
        + " (e.g. 'Revenues', 'NetIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities')."
        + " The 'instantaneous' parameter and the standalone-Q4 derivation apply only to flow concepts;"
        + " balance-sheet concepts are always point-in-time, including the year-end (Q4) value.",
    )
    year: int | None = Field(
        default=None,
        description="The calendar year to retrieve the data for. If not provided, the current year is used."
        + " When symbol(s) are provided, excluding the year will return all reported values for the concept."
        + " Values are aligned by the calendar quarter/year of the period end, not the fiscal calendar.",
    )
    calendar_period: CALENDAR_PERIODS | None = Field(
        default=None,
        description="The calendar period to retrieve the data for."
        + " Periods are aligned to the calendar quarter/year of the report period end, not the"
        + " filer's fiscal calendar, so off-calendar filers stay comparable."
        + " If not provided, the most recent quarter is used."
        + " 'q1'-'q4' return standalone (3-month) quarters; the fourth quarter is derived as FY - 9-month."
        + " When a symbol is supplied, cumulative year-to-date values are reduced to standalone quarters.",
    )
    instantaneous: bool = Field(
        default=False,
        description="Whether to retrieve instantaneous data. See the notes above for more information."
        + " Defaults to False. Some facts are only available as instantaneous data."
        + "\nThe function will automatically attempt the inverse of this parameter"
        + " if the initial calendar quarter request fails."
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

    cik: str | int = Field(
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    location: str | None = Field(
        default=None,
        description="Geographic location of the reporting entity.",
    )
    form: str | None = Field(
        default=None,
        description="The SEC form associated with the fact or concept.",
    )
    frame: str | None = Field(
        default=None,
        description="The frame ID associated with the fact or concept, if applicable.",
    )
    accession: str = Field(
        description="SEC filing accession number associated with the reported fact or concept.",
    )
    fact: str = Field(
        description="The display name of the fact or concept.",
    )
    unit: str | None = Field(
        default=None,
        description="The unit of measurement for the fact or concept.",
    )
    calendar_year: int | None = Field(
        default=None,
        description="Calendar year the value is aligned to"
        + " (by the calendar quarter/year of the period end, not the fiscal calendar).",
    )
    calendar_period: str | None = Field(
        default=None,
        description="Calendar period the value is aligned to: 'FY' or 'Q1'-'Q4'.",
    )


class SecCompareCompanyFactsFetcher(
    Fetcher[SecCompareCompanyFactsQueryParams, list[SecCompareCompanyFactsData]]
):
    """SEC Compare Company Facts Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecCompareCompanyFactsQueryParams:
        """Transform the query."""
        return SecCompareCompanyFactsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCompareCompanyFactsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the SEC endpoint."""
        from openbb_sec.utils.frames import (
            get_concept,
            get_frame,
            get_universe_quarter4,
        )

        results: dict = {}
        if not query.symbol:
            if query.calendar_period == "q4" and not query.instantaneous:
                # No standalone Q4 duration frame exists; derive FY - (Q1+Q2+Q3).
                results = await get_universe_quarter4(
                    fact=query.fact,
                    year=query.year,
                    use_cache=query.use_cache,
                )
            else:
                results = await get_frame(
                    fact=query.fact,
                    year=query.year,
                    calendar_period=query.calendar_period,
                    instantaneous=query.instantaneous,
                    use_cache=query.use_cache,
                )
        if query.symbol is not None:
            if query.instantaneous is True:
                warn(
                    "The 'instantaneous' parameter is ignored when a symbol is supplied."
                )
            results = await get_concept(
                symbol=query.symbol,
                fact=query.fact,
                year=query.year,
                calendar_period=query.calendar_period,
                use_cache=query.use_cache,
            )
        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: SecCompareCompanyFactsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[SecCompareCompanyFactsData]]:
        """Transform the data and validate the model."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        metadata = data.get("metadata")
        results_data = data.get("data", [])
        return AnnotatedResult(
            result=[SecCompareCompanyFactsData.model_validate(d) for d in results_data],
            metadata=metadata,
        )
