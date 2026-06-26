"""SEC private offering related people from Form D filings."""

from __future__ import annotations

import inspect
from datetime import date
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.models.private_offerings import load_normalized_form_d_records


class SecPrivateOfferingPeopleQueryParams(QueryParams):
    """SEC private offering people query."""

    cik: str | int | None = Field(
        default=None,
        description="Central Index Key (CIK) for the Form D issuer.",
    )
    issuer: str | None = Field(
        default=None,
        description="Search text matched against the issuer name.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for one exact Form D filing.",
    )
    start_date: date | None = Field(
        default=None,
        description="Start date for Form D filing dates.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date for Form D filing dates.",
    )
    limit: int | None = Field(
        default=100,
        description="Maximum number of Form D filings to inspect.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecPrivateOfferingPeopleData(Data):
    """SEC private offering related-person row."""

    issuer_cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for the issuer.",
    )
    issuer_name: str | None = Field(
        default=None,
        description="Name of the Form D issuer.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for the Form D filing.",
    )
    filing_date: date | None = Field(
        default=None,
        description="Date the Form D filing was submitted to EDGAR.",
    )
    person_name: str | None = Field(
        default=None,
        description="Name of the related person disclosed in Form D.",
    )
    relationship: str | None = Field(
        default=None,
        description="Relationship disclosed for the related person.",
    )
    address_city: str | None = Field(
        default=None,
        description="Related person's city when disclosed.",
    )
    address_state: str | None = Field(
        default=None,
        description="Related person's state when disclosed.",
    )
    address_country: str | None = Field(
        default=None,
        description="Related person's country or state/country description.",
    )


class SecPrivateOfferingPeopleFetcher(
    Fetcher[
        SecPrivateOfferingPeopleQueryParams,
        list[SecPrivateOfferingPeopleData],
    ]
):
    """SEC private offering people fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecPrivateOfferingPeopleQueryParams:
        """Transform query parameters."""
        return SecPrivateOfferingPeopleQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecPrivateOfferingPeopleQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return normalized Form D related-person rows."""
        loaded = load_private_offering_people_records(
            cik=query.cik,
            issuer=query.issuer,
            accession_number=query.accession_number,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit,
            use_cache=query.use_cache,
            **kwargs,
        )
        records = await loaded if inspect.isawaitable(loaded) else loaded
        return records

    @staticmethod
    def transform_data(
        query: SecPrivateOfferingPeopleQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecPrivateOfferingPeopleData]:
        """Transform raw data to the model format."""
        return [SecPrivateOfferingPeopleData.model_validate(d) for d in data]


def load_private_offering_people_records(
    *,
    cik: str | int | None = None,
    issuer: str | None = None,
    accession_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> Any:
    """Load Form D related-person records."""
    return _aload_private_offering_people_records(
        cik=cik,
        issuer=issuer,
        accession_number=accession_number,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        use_cache=use_cache,
        **kwargs,
    )


async def _aload_private_offering_people_records(
    *,
    cik: str | int | None = None,
    issuer: str | None = None,
    accession_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Load Form D related-person records from EDGAR filing documents."""
    normalized = await load_normalized_form_d_records(
        cik=cik,
        accession_number=accession_number,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        use_cache=use_cache,
        **kwargs,
    )
    rows = [person for item in normalized for person in item.people]
    if not issuer:
        return rows
    needle = issuer.casefold()
    return [
        row
        for row in rows
        if needle in str(row.get("issuer_name") or "").casefold()
    ]
