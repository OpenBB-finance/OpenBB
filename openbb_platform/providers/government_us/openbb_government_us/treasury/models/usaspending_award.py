"""USAspending Award Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_serializer

from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

AwardSection = Literal[
    "detail",
    "transactions",
    "subawards",
    "federal_accounts",
    "funding",
    "idv_children",
]

IdvChildrenType = Literal["child_idvs", "child_awards", "grandchild_awards"]

ENDPOINTS: dict[str, str] = {
    "transactions": "transactions/",
    "subawards": "subawards/",
    "federal_accounts": "awards/accounts/",
    "funding": "awards/funding/",
    "idv_children": "idvs/awards/",
}

SECTION_MAX_LIMIT: dict[str, int] = {
    "transactions": 5000,
    "subawards": 100,
    "federal_accounts": 100,
    "funding": 100,
    "idv_children": 100,
}

SUBJECT_KEY = "_subject_award_id"

FIELD_MAP: dict[str, dict[str, str]] = {
    "detail": {
        "generated_unique_award_id": "award_id",
        "id": "internal_id",
        "category": "category",
        "type": "award_type",
        "type_description": "award_type_description",
        "description": "description",
        "piid": "piid",
        "fain": "fain",
        "uri": "uri",
        "record_type": "record_type",
        "date_signed": "date_signed",
        "total_obligation": "total_obligation",
        "base_and_all_options": "base_and_all_options",
        "base_exercised_options": "base_exercised_options",
        "total_outlay": "total_outlay",
        "total_account_obligation": "total_account_obligation",
        "total_account_outlay": "total_account_outlay",
        "subaward_count": "subaward_count",
        "total_subaward_amount": "total_subaward_amount",
        "total_subsidy_cost": "total_subsidy_cost",
        "total_loan_value": "total_loan_value",
        "non_federal_funding": "non_federal_funding",
        "total_funding": "total_funding",
        "transaction_obligated_amount": "transaction_obligated_amount",
        "period_of_performance.start_date": "period_start",
        "period_of_performance.end_date": "period_end",
        "period_of_performance.potential_end_date": "period_potential_end",
        "period_of_performance.last_modified_date": "last_modified",
        "recipient.recipient_name": "recipient_name",
        "recipient.recipient_uei": "recipient_uei",
        "recipient.parent_recipient_name": "parent_recipient_name",
        "recipient.parent_recipient_uei": "parent_recipient_uei",
        "recipient.location.city_name": "recipient_city",
        "recipient.location.state_code": "recipient_state",
        "recipient.location.zip5": "recipient_zip",
        "recipient.location.country_name": "recipient_country",
        "recipient.location.congressional_code": "recipient_congressional_district",
        "place_of_performance.city_name": "place_of_performance_city",
        "place_of_performance.state_code": "place_of_performance_state",
        "place_of_performance.country_name": "place_of_performance_country",
        "place_of_performance.congressional_code": (
            "place_of_performance_congressional_district"
        ),
        "awarding_agency.toptier_agency.name": "awarding_agency",
        "awarding_agency.subtier_agency.name": "awarding_subagency",
        "awarding_agency.office_agency_name": "awarding_office",
        "funding_agency.toptier_agency.name": "funding_agency",
        "funding_agency.subtier_agency.name": "funding_subagency",
        "funding_agency.office_agency_name": "funding_office",
        "latest_transaction_contract_data.naics": "naics",
        "latest_transaction_contract_data.naics_description": "naics_description",
        "latest_transaction_contract_data.product_or_service_code": "psc",
        "latest_transaction_contract_data.product_or_service_description": (
            "psc_description"
        ),
        "parent_award.generated_unique_award_id": "parent_award_id",
        "parent_award.piid": "parent_piid",
        "cfda_info.0.cfda_number": "cfda_number",
        "cfda_info.0.cfda_title": "cfda_title",
    },
    "transactions": {
        "id": "transaction_id",
        "type": "award_type",
        "type_description": "award_type_description",
        "action_date": "action_date",
        "action_type": "action_type",
        "action_type_description": "action_type_description",
        "modification_number": "modification_number",
        "description": "description",
        "federal_action_obligation": "federal_action_obligation",
        "face_value_loan_guarantee": "face_value_loan_guarantee",
        "original_loan_subsidy_cost": "original_loan_subsidy_cost",
        "cfda_number": "cfda_number",
    },
    "subawards": {
        "id": "subaward_id",
        "subaward_number": "subaward_number",
        "description": "description",
        "action_date": "action_date",
        "amount": "amount",
        "recipient_name": "recipient_name",
    },
    "federal_accounts": {
        "federal_account": "federal_account",
        "account_title": "account_title",
        "total_transaction_obligated_amount": "total_transaction_obligated_amount",
        "funding_agency_name": "funding_agency",
        "funding_agency_abbreviation": "funding_agency_abbreviation",
    },
    "funding": {
        "transaction_obligated_amount": "transaction_obligated_amount",
        "gross_outlay_amount": "gross_outlay_amount",
        "disaster_emergency_fund_code": "disaster_emergency_fund_code",
        "federal_account": "federal_account",
        "account_title": "account_title",
        "funding_agency_name": "funding_agency",
        "awarding_agency_name": "awarding_agency",
        "object_class": "object_class",
        "object_class_name": "object_class_name",
        "program_activity_code": "program_activity_code",
        "program_activity_name": "program_activity_name",
        "reporting_fiscal_year": "reporting_fiscal_year",
        "reporting_fiscal_quarter": "reporting_fiscal_quarter",
        "reporting_fiscal_month": "reporting_fiscal_month",
        "is_quarterly_submission": "is_quarterly_submission",
    },
    "idv_children": {
        "generated_unique_award_id": "child_award_id",
        "award_id": "internal_id",
        "award_type": "award_type_description",
        "description": "description",
        "piid": "piid",
        "obligated_amount": "obligated_amount",
        "last_date_to_order": "last_date_to_order",
        "period_of_performance_start_date": "period_start",
        "period_of_performance_current_end_date": "period_end",
        "funding_agency": "funding_agency",
        "awarding_agency": "awarding_agency",
    },
}

DATE_FIELDS = {
    "date_signed",
    "period_start",
    "period_end",
    "period_potential_end",
    "last_modified",
    "action_date",
    "last_date_to_order",
}


class _Missing:
    """Sentinel marking an absent source key."""


MISSING = _Missing()


def _get_path(row: Any, path: str) -> Any:
    """Resolve a dotted path against nested dicts and lists.

    Parameters
    ----------
    row : Any
        The source object to walk.
    path : str
        Dotted path, where an integer segment indexes a list,
        e.g. 'cfda_info.0.cfda_number'.

    Returns
    -------
    Any
        The resolved value, or MISSING when any segment is absent.
    """
    current = row

    for part in path.split("."):
        if isinstance(current, list):
            if not part.isdigit() or int(part) >= len(current):
                return MISSING
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                return MISSING
            current = current[part]
        else:
            return MISSING

    return current


def _to_date(value: Any) -> Any:
    """Truncate a date-time string to its date component.

    Parameters
    ----------
    value : Any
        A source date value. Strings may be 'YYYY-MM-DD' or
        'YYYY-MM-DD HH:MM:SS'.

    Returns
    -------
    Any
        The date portion of a string value, otherwise the value unchanged.
    """
    if not isinstance(value, str):
        return value

    return value.split(" ")[0].split("T")[0]


class UsSpendingAwardQueryParams(QueryParams):
    """USAspending Award Query Parameters.

    Source: https://api.usaspending.gov/docs/endpoints
    """

    award_id: str = Field(
        description="The award identifier, as it appears in a"
        + " usaspending.gov/award/<id> URL, e.g."
        + " 'CONT_IDV_15F06724A0000314_1549'. The internal integer award id"
        + " is also accepted.",
    )
    section: AwardSection = Field(
        default="detail",
        description="The section of the award to return. 'detail' returns the"
        + " award summary as a single row. 'idv_children' is only valid for"
        + " IDV awards.",
    )
    idv_children_type: IdvChildrenType = Field(
        default="child_awards",
        description="For section='idv_children', the relation to return."
        + " 'child_awards' are the orders placed against the vehicle,"
        + " 'child_idvs' are nested vehicles, and the two are disjoint sets.",
    )
    page: int = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("page", "The page of results to return."),
        ge=1,
    )
    limit: int = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", "The number of results to return.")
        + " Capped by the source at 5000 for 'transactions' and 100 for every"
        + " other paginated section. Ignored when section='detail'.",
        ge=1,
    )


class UsSpendingAwardData(NullTokenMixin, Data):
    """USAspending Award Data.

    A normalized union of the six award drill-down sections. Per-section source
    keys are mapped to unified names, and every row of a section serves the
    identical key set - the fields that section populates for at least one row -
    so no column is null across the result and no column is ragged. The pruning
    runs in a wrap serializer, which replaces the serialized schema with a
    free-form object, so this model carries no column definitions and column
    order follows field declaration order. All monetary values are raw USD, as
    reported.
    """

    action_date: dateType | None = Field(
        default=None,
        description="Date the transaction or subaward action was taken.",
    )
    award_id: str = Field(
        description="Identifier of the award the row belongs to.",
    )
    child_award_id: str | None = Field(
        default=None,
        description="Identifier of the child award, for section='idv_children'."
        + " Supply it back as award_id to drill into the child.",
    )
    transaction_id: str | None = Field(
        default=None,
        description="Natural identifier of the transaction,"
        + " for section='transactions'.",
    )
    modification_number: str | None = Field(
        default=None,
        description="Modification number of the transaction.",
    )
    subaward_id: int | None = Field(
        default=None,
        description="Internal identifier of the subaward,"
        + " for section='subawards'.",
    )
    subaward_number: str | None = Field(
        default=None,
        description="Subaward number as reported by the prime recipient."
        + " Not unique - it can repeat across rows.",
    )
    piid: str | None = Field(
        default=None,
        description="Procurement Instrument Identifier, for contracts and IDVs.",
    )
    fain: str | None = Field(
        default=None,
        description="Federal Award Identification Number, for assistance awards.",
    )
    uri: str | None = Field(
        default=None,
        description="Unique Record Identifier, for assistance awards.",
    )
    parent_award_id: str | None = Field(
        default=None,
        description="Identifier of the parent IDV, when the award has one.",
    )
    parent_piid: str | None = Field(
        default=None,
        description="PIID of the parent IDV, when the award has one.",
    )
    internal_id: int | None = Field(
        default=None,
        description="Internal surrogate identifier of the row's award.",
    )
    record_type: int | None = Field(
        default=None,
        description="Assistance record type - 1 is aggregate, 2 and 3 are"
        + " non-aggregate.",
    )
    category: str | None = Field(
        default=None,
        description="Award category - contract, idv, grant, loans,"
        + " direct payment, other, or insurance.",
    )
    award_type: str | None = Field(
        default=None,
        description="Award type code, e.g. 'IDV_E' or '02'.",
    )
    award_type_description: str | None = Field(
        default=None,
        description="Human readable award type, e.g. 'BPA'.",
    )
    action_type: str | None = Field(
        default=None,
        description="Action type code of the transaction, e.g. 'A' or 'G'.",
    )
    action_type_description: str | None = Field(
        default=None,
        description="Human readable action type of the transaction.",
    )
    amount: float | None = Field(
        default=None,
        description="Face value of the subaward, in dollars,"
        + " for section='subawards'.",
    )
    federal_action_obligation: float | None = Field(
        default=None,
        description="Obligation recorded by the transaction, in dollars."
        + " This is a per-modification delta and is negative for"
        + " de-obligations.",
    )
    obligated_amount: float | None = Field(
        default=None,
        description="Amount obligated to the child award, in dollars,"
        + " for section='idv_children'.",
    )
    total_obligation: float | None = Field(
        default=None,
        description="Total amount obligated to the award, in dollars."
        + " Reported as 0 for an IDV, whose obligations sit on its children.",
    )
    base_and_all_options: float | None = Field(
        default=None,
        description="Award ceiling if all options are exercised, in dollars."
        + " Null for assistance awards.",
    )
    base_exercised_options: float | None = Field(
        default=None,
        description="Award value including exercised options, in dollars.",
    )
    total_outlay: float | None = Field(
        default=None,
        description="Total amount outlayed against the award, in dollars.",
    )
    total_account_obligation: float | None = Field(
        default=None,
        description="Total obligation reported in the award's federal"
        + " account records, in dollars.",
    )
    total_account_outlay: float | None = Field(
        default=None,
        description="Total outlay reported in the award's federal"
        + " account records, in dollars.",
    )
    subaward_count: int | None = Field(
        default=None,
        description="Number of subawards reported under the award.",
    )
    total_subaward_amount: float | None = Field(
        default=None,
        description="Total value of subawards reported under the award,"
        + " in dollars. Null when there are no subawards.",
    )
    total_subsidy_cost: float | None = Field(
        default=None,
        description="Total subsidy cost, in dollars. Loans only.",
    )
    total_loan_value: float | None = Field(
        default=None,
        description="Total face value of the loan, in dollars. Loans only.",
    )
    face_value_loan_guarantee: float | None = Field(
        default=None,
        description="Face value of the loan guarantee, in dollars. Loans only.",
    )
    original_loan_subsidy_cost: float | None = Field(
        default=None,
        description="Original subsidy cost of the loan, in dollars. Loans only.",
    )
    non_federal_funding: float | None = Field(
        default=None,
        description="Non-federal funding, in dollars. Grants only.",
    )
    total_funding: float | None = Field(
        default=None,
        description="Total federal and non-federal funding, in dollars."
        + " Grants only.",
    )
    transaction_obligated_amount: float | None = Field(
        default=None,
        description="Amount obligated by the funding record, in dollars."
        + " Mutually exclusive with gross_outlay_amount on a funding row.",
    )
    gross_outlay_amount: float | None = Field(
        default=None,
        description="Amount outlayed by the funding record, in dollars."
        + " Negative values are downward adjustments. Mutually exclusive with"
        + " transaction_obligated_amount on a funding row.",
    )
    total_transaction_obligated_amount: float | None = Field(
        default=None,
        description="Amount obligated from the federal account, in dollars,"
        + " for section='federal_accounts'. Coalesced to 0 by the source when"
        + " no funding records exist.",
    )
    date_signed: dateType | None = Field(
        default=None,
        description="Date the award was signed.",
    )
    period_start: dateType | None = Field(
        default=None,
        description="Start date of the period of performance.",
    )
    period_end: dateType | None = Field(
        default=None,
        description="Current end date of the period of performance.",
    )
    period_potential_end: dateType | None = Field(
        default=None,
        description="Potential end date of the period of performance,"
        + " if all options are exercised.",
    )
    last_date_to_order: dateType | None = Field(
        default=None,
        description="Last date an order may be placed against the vehicle,"
        + " for section='idv_children'.",
    )
    last_modified: dateType | None = Field(
        default=None,
        description="Date the award record was last modified.",
    )
    recipient_name: str | None = Field(
        default=None,
        description="Name of the recipient. For section='subawards' this is"
        + " the subrecipient, otherwise the prime recipient.",
    )
    recipient_uei: str | None = Field(
        default=None,
        description="Unique Entity Identifier of the recipient.",
    )
    parent_recipient_name: str | None = Field(
        default=None,
        description="Name of the recipient's parent entity.",
    )
    parent_recipient_uei: str | None = Field(
        default=None,
        description="Unique Entity Identifier of the recipient's parent entity.",
    )
    recipient_city: str | None = Field(
        default=None,
        description="City of the recipient.",
    )
    recipient_state: str | None = Field(
        default=None,
        description="State code of the recipient.",
    )
    recipient_zip: str | None = Field(
        default=None,
        description="Five digit ZIP code of the recipient.",
    )
    recipient_country: str | None = Field(
        default=None,
        description="Country of the recipient.",
    )
    recipient_congressional_district: str | None = Field(
        default=None,
        description="Congressional district of the recipient.",
    )
    place_of_performance_city: str | None = Field(
        default=None,
        description="City where the award is performed.",
    )
    place_of_performance_state: str | None = Field(
        default=None,
        description="State code where the award is performed.",
    )
    place_of_performance_country: str | None = Field(
        default=None,
        description="Country where the award is performed.",
    )
    place_of_performance_congressional_district: str | None = Field(
        default=None,
        description="Congressional district where the award is performed.",
    )
    awarding_agency: str | None = Field(
        default=None,
        description="Name of the awarding top-tier agency.",
    )
    awarding_subagency: str | None = Field(
        default=None,
        description="Name of the awarding sub-tier agency.",
    )
    awarding_office: str | None = Field(
        default=None,
        description="Name of the awarding office.",
    )
    funding_agency: str | None = Field(
        default=None,
        description="Name of the funding top-tier agency.",
    )
    funding_subagency: str | None = Field(
        default=None,
        description="Name of the funding sub-tier agency.",
    )
    funding_office: str | None = Field(
        default=None,
        description="Name of the funding office.",
    )
    funding_agency_abbreviation: str | None = Field(
        default=None,
        description="Abbreviation of the funding agency,"
        + " for section='federal_accounts'.",
    )
    naics: str | None = Field(
        default=None,
        description="North American Industry Classification System code.",
    )
    naics_description: str | None = Field(
        default=None,
        description="Description of the NAICS code.",
    )
    psc: str | None = Field(
        default=None,
        description="Product or Service Code.",
    )
    psc_description: str | None = Field(
        default=None,
        description="Description of the Product or Service Code.",
    )
    cfda_number: str | None = Field(
        default=None,
        description="Assistance Listing (CFDA) number. Assistance awards only.",
    )
    cfda_title: str | None = Field(
        default=None,
        description="Assistance Listing (CFDA) title. Assistance awards only.",
    )
    federal_account: str | None = Field(
        default=None,
        description="Federal account identifier, as"
        + " '<agency code>-<main account code>'.",
    )
    account_title: str | None = Field(
        default=None,
        description="Title of the federal account.",
    )
    disaster_emergency_fund_code: str | None = Field(
        default=None,
        description="Disaster Emergency Fund Code, where 'Q' is"
        + " non-disaster funding.",
    )
    object_class: str | None = Field(
        default=None,
        description="Object class code, e.g. '25.1'.",
    )
    object_class_name: str | None = Field(
        default=None,
        description="Name of the object class.",
    )
    program_activity_code: str | None = Field(
        default=None,
        description="Program activity code.",
    )
    program_activity_name: str | None = Field(
        default=None,
        description="Name of the program activity.",
    )
    reporting_fiscal_year: int | None = Field(
        default=None,
        description="Federal fiscal year of the submission.",
    )
    reporting_fiscal_quarter: int | None = Field(
        default=None,
        description="Federal fiscal quarter of the submission.",
    )
    reporting_fiscal_month: int | None = Field(
        default=None,
        description="Federal fiscal month of the submission, where 1 is"
        + " October and 12 is September.",
    )
    is_quarterly_submission: bool | None = Field(
        default=None,
        description="True when the submission is quarterly, False when monthly.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the award, transaction, or subaward.",
    )

    @model_serializer(mode="wrap")
    def _serialize(self, handler) -> dict[str, Any]:
        """Emit only the fields the row was constructed with."""
        return {
            key: value
            for key, value in handler(self).items()
            if key in self.model_fields_set
        }


class UsSpendingAwardFetcher(
    Fetcher[
        UsSpendingAwardQueryParams,
        list[UsSpendingAwardData],
    ]
):
    """Fetch award drill-down sections from the USAspending API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UsSpendingAwardQueryParams:
        """Transform the query params.

        Raises
        ------
        OpenBBError
            If the limit exceeds the maximum the section allows.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        query = UsSpendingAwardQueryParams(**params)
        maximum = SECTION_MAX_LIMIT.get(query.section)

        if maximum is not None and query.limit > maximum:
            raise OpenBBError(
                f"The maximum limit for section '{query.section}' is {maximum},"
                f" but {query.limit} was requested."
            )

        return query

    @staticmethod
    async def aextract_data(
        query: UsSpendingAwardQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the USAspending API.

        Raises
        ------
        OpenBBError
            If section='idv_children' is requested for a non-IDV award.
        EmptyDataError
            If the section returns no rows.
        """
        from urllib.parse import quote

        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_government_us.treasury.utils.usaspending import (
            get_usaspending,
            post_usaspending,
        )

        subject = query.award_id

        if query.section == "detail":
            return [await get_usaspending(f"awards/{quote(subject, safe='')}/")]

        if query.section == "idv_children":
            detail = await get_usaspending(f"awards/{quote(subject, safe='')}/")
            category = detail.get("category")

            if category != "idv":
                raise OpenBBError(
                    f"Award '{subject}' has category '{category}', not 'idv'."
                    " The 'idv_children' section is only valid for Indefinite"
                    " Delivery Vehicles, whose award ids begin with 'CONT_IDV_'."
                    " The source returns an empty list, rather than an error,"
                    " for non-IDV awards."
                )

            subject = detail.get("generated_unique_award_id") or subject
            payload = {
                "award_id": query.award_id,
                "type": query.idv_children_type,
                "page": query.page,
                "limit": query.limit,
            }
        else:
            payload = {
                "award_id": query.award_id,
                "page": query.page,
                "limit": query.limit,
            }

        response = await post_usaspending(ENDPOINTS[query.section], payload)
        results = response.get("results") or []

        if not results:
            raise EmptyDataError(
                f"The request was returned empty. No '{query.section}' rows were"
                f" found for award '{subject}' at page {query.page}."
            )

        return [{**row, SUBJECT_KEY: subject} for row in results]

    @staticmethod
    def transform_data(
        query: UsSpendingAwardQueryParams, data: list[dict], **kwargs: Any
    ) -> list[UsSpendingAwardData]:
        """Transform the data."""
        mapping = FIELD_MAP[query.section]
        records: list[dict[str, Any]] = []

        for row in data:
            record: dict[str, Any] = {}

            for source, target in mapping.items():
                value = _get_path(row, source)

                if value is MISSING or value is None or is_null_token(value):
                    continue

                if target in DATE_FIELDS:
                    value = _to_date(value)

                record[target] = value

            subject = row.get(SUBJECT_KEY)

            if subject is not None:
                record["award_id"] = subject

            record.setdefault("award_id", query.award_id)
            records.append(record)

        served = [
            field
            for field in UsSpendingAwardData.model_fields
            if any(field in record for record in records)
        ]

        return [
            UsSpendingAwardData.model_validate(
                {field: record.get(field) for field in served}
            )
            for record in records
        ]
