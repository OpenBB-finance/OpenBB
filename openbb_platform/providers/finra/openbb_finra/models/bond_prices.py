"""FINRA Bond Prices Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bond_prices import (
    BondPricesData,
    BondPricesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_finra.utils.constants import BondTypes

UNSUPPORTED = (
    "country",
    "isin",
    "lei",
    "currency",
    "issued_amount_min",
    "issued_amount_max",
)


class FinraBondPricesQueryParams(BondPricesQueryParams):
    """FINRA Bond Prices Query."""

    __json_schema_extra__ = {
        "cusip": {"multiple_items_allowed": True},
        **{name: {"x-widget_config": {"exclude": True}} for name in UNSUPPORTED},
    }

    cusip: str | None = Field(
        default=None,
        description="The CUSIP or FINRA symbol of the bond. The bond type is"
        + " detected when it is not given.",
    )
    bond_type: BondTypes | None = Field(
        default=None,
        description="The TRACE product - CA (corporate and agency), TS (U.S. Treasury),"
        + " TBA, MBS, ABS, or CMO. Corporate and agency when neither this nor a cusip"
        + " is given. Issuer names match the issuing agency for TBA and MBS.",
    )
    include_matured: bool = Field(
        default=False, description="Include the bonds that have matured."
    )
    limit: int | None = Field(
        default=None, ge=1, description="The most bonds to return. All when empty."
    )

    @field_validator("cusip", mode="before", check_fields=False)
    @classmethod
    def _upper(cls, value):
        """Upper-case the identifiers."""
        return value.upper() if isinstance(value, str) else value


class FinraBondPricesData(BondPricesData):
    """FINRA Bond Prices Data."""

    __alias_dict__ = {
        "price": "lastSalePrice",
        "call_date": "nextCallDate",
        "symbol": "issueSymbolIdentifier",
        "finra_security_id": "finraSecurityIdentifier",
        "product_sub_type": "productSubTypeCode",
        "grade": "traceGradeCode",
        "moodys_rating_date": "moodyRatingDate",
        "sp_rating": "standardAndPoorsRating",
        "sp_rating_date": "standardAndPoorsRatingDate",
        "benchmark_term": "benchmarkTermCode",
        "is_144a": "is144A",
        "price_change": "priceChangeNumber",
        "price_change_percent": "priceChangePercent",
        "settlement_month": "settlementDateMonth",
        "reference_data_id": "referenceDataIdentifier",
        "loan_to_value": "loanToValueRatio",
    }

    coupon_rate: float | None = Field(
        default=None,
        description="The coupon rate of the bond, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    price: float | None = Field(
        default=None, description="The price of the last reported sale."
    )
    bond_type: str = Field(
        description="The TRACE product of the bond - Corporate & Agency, U.S. Treasury,"
        + " To-Be-Announced MBS, Mortgage-Backed, Asset-Backed, or Collateralized"
        + " Mortgage Obligations."
    )
    symbol: str | None = Field(
        default=None, description="The FINRA symbol of the bond."
    )
    finra_security_id: str | None = Field(
        default=None, description="The FINRA security identifier."
    )
    issuer_name: str | None = Field(default=None, description="The name of the issuer.")
    issuing_agency: str | None = Field(
        default=None, description="The issuing agency, or trust, of the security."
    )
    issue_description: str | None = Field(
        default=None, description="The description of the issue."
    )
    security_description: str | None = Field(
        default=None, description="The description of the security."
    )
    product_type: str | None = Field(default=None, description="The product type.")
    product_sub_type: str | None = Field(
        default=None, description="The product sub-type code."
    )
    sub_product_type: str | None = Field(
        default=None, description="The sub-product type."
    )
    coupon_type: str | None = Field(default=None, description="The coupon type.")
    interest_type: str | None = Field(
        default=None, description="The interest type code of an asset-backed tranche."
    )
    is_perpetual: bool | None = Field(
        default=None, description="Whether the bond has no maturity date."
    )
    is_callable: bool | None = Field(
        default=None, description="Whether the bond is callable."
    )
    is_convertible: bool | None = Field(
        default=None, description="Whether the bond is convertible."
    )
    is_144a: bool | None = Field(
        default=None, description="Whether the bond is a Rule 144A security."
    )
    industry_group: str | None = Field(
        default=None, description="The industry group of the issuer."
    )
    grade: str | None = Field(
        default=None, description="The TRACE grade - investment grade or high yield."
    )
    moodys_rating: str | None = Field(default=None, description="The Moody's rating.")
    moodys_rating_date: dateType | None = Field(
        default=None, description="The date of the Moody's rating."
    )
    sp_rating: str | None = Field(default=None, description="The S&P rating.")
    sp_rating_date: dateType | None = Field(
        default=None, description="The date of the S&P rating."
    )
    benchmark_term: str | None = Field(
        default=None, description="The benchmark term of a Treasury security."
    )
    price_type: str | None = Field(
        default=None,
        description="How the last sale was priced - Decimal, Yield, or Negative Yield.",
    )
    last_sale_yield: float | None = Field(
        default=None,
        description="The yield of the last reported sale, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    last_trade_date: dateType | None = Field(
        default=None, description="The date of the last reported sale."
    )
    last_trade_time: str | None = Field(
        default=None, description="The time of the last reported sale."
    )
    price_change: float | None = Field(
        default=None, description="The change in the last sale price."
    )
    price_change_percent: float | None = Field(
        default=None,
        description="The change in the last sale price, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    settlement_month: str | None = Field(
        default=None, description="The settlement month of a TBA contract."
    )
    pool_number: str | None = Field(
        default=None, description="The pool number of a mortgage-backed security."
    )
    reference_data_id: str | None = Field(
        default=None, description="The reference data identifier of the pool."
    )
    mortgage_product: str | None = Field(
        default=None, description="The mortgage product code."
    )
    amortization_type: str | None = Field(
        default=None, description="The amortization type code."
    )
    original_maturity_term: float | None = Field(
        default=None, description="The original maturity term of the pool, in months."
    )
    weighted_average_coupon: float | None = Field(
        default=None,
        description="The weighted average coupon of the pool, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    weighted_average_maturity: float | None = Field(
        default=None,
        description="The weighted average maturity of the pool, in months.",
    )
    weighted_average_loan_age: float | None = Field(
        default=None,
        description="The weighted average loan age of the pool, in months.",
    )
    loan_to_value: float | None = Field(
        default=None, description="The loan-to-value ratio of the pool, as a percent."
    )
    average_loan_size: float | None = Field(
        default=None, description="The average loan size of the pool."
    )
    deal_id: str | None = Field(default=None, description="The deal identifier.")
    tranche_id: str | None = Field(default=None, description="The tranche identifier.")


def _filters(query: FinraBondPricesQueryParams, bond_type: str, lookup: bool) -> dict:
    """Return the TRACE filters for one bond type."""
    from datetime import date

    from openbb_finra.utils.trace import match_filters

    compare: list[dict] = []
    payload: dict = {}

    def bound(field: str, value: Any, operator: str) -> None:
        if value is not None:
            compare.append(
                {"fieldName": field, "fieldValue": str(value), "compareType": operator}
            )

    bound("couponRate", query.coupon_min, "GTE")
    bound("couponRate", query.coupon_max, "LTE")
    bound("lastSaleYield", query.ytm_min, "GTE")
    bound("lastSaleYield", query.ytm_max, "LTE")

    if bond_type != "TBA":
        bound("maturityDate", query.maturity_date_min, "GTE")
        bound("maturityDate", query.maturity_date_max, "LTE")

        if not (query.include_matured or lookup):
            payload["orFilters"] = [
                {
                    "compareFilters": [
                        {
                            "fieldName": "maturityDate",
                            "fieldValue": date.today().isoformat(),
                            "compareType": "GREATER",
                        },
                        {
                            "fieldName": "maturityDate",
                            "fieldValue": None,
                            "compareType": "EQUAL",
                        },
                    ]
                }
            ]

    if bond_type == "ABS":
        compare.append(
            {
                "fieldName": "finraSecurityIdentifier",
                "fieldValue": None,
                "compareType": "NOT_EQUAL",
            }
        )

    if query.issuer_name:
        payload["multiFieldMatchFilters"] = match_filters(
            query.issuer_name,
            "issuingAgency" if bond_type in ("TBA", "MBS") else "issuerName",
        )

    if compare:
        payload["compareFilters"] = compare

    return payload


async def read_bonds(
    trace: Any, query: FinraBondPricesQueryParams, bond_type: str, cusips: list[str]
) -> list[dict]:
    """Return the TRACE records of one bond type that match a query.

    Parameters
    ----------
    trace : TraceSession
        The open TRACE session.
    query : FinraBondPricesQueryParams
        The filters to apply.
    bond_type : str
        The TRACE product to read.
    cusips : list[str]
        Restrict the read to these CUSIPs. All bonds when empty.

    Returns
    -------
    list[dict]
        The normalized records, tagged with their bond type.
    """
    from openbb_finra.utils.constants import BOND_TYPES
    from openbb_finra.utils.helpers import normalize_trace_record

    payload = {
        "fields": BOND_TYPES[bond_type]["fields"],
        "sortFields": ["finraSecurityIdentifier"],
        **_filters(query, bond_type, bool(cusips)),
    }

    if cusips:
        payload["domainFilters"] = [{"fieldName": "cusip", "values": cusips}]

    rows = await trace.query(
        BOND_TYPES[bond_type]["dataset"], payload, max_rows=query.limit
    )

    return [
        {
            **normalize_trace_record(row, bond_type),
            "bondType": BOND_TYPES[bond_type]["label"],
        }
        for row in rows
    ]


def distinct_bonds(pages: list[list[dict]]) -> list[dict]:
    """Return the records of every page, once per FINRA security.

    Parameters
    ----------
    pages : list[list[dict]]
        The records read for each bond type.

    Returns
    -------
    list[dict]
        The first record of each security, in page order.
    """
    records: dict[str, dict] = {}

    for page in pages:
        for row in page:
            key = row.get("finraSecurityIdentifier") or row.get("cusip")
            records.setdefault(str(key), row)

    return list(records.values())


class FinraBondPricesFetcher(
    Fetcher[FinraBondPricesQueryParams, list[FinraBondPricesData]]
):
    """Transform the query, extract and transform the data from FINRA TRACE."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraBondPricesQueryParams:
        """Transform the query.

        Raises
        ------
        OpenBBError
            If a parameter TRACE does not publish is given.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        given = [name for name in UNSUPPORTED if params.get(name) not in (None, "")]

        if given:
            raise OpenBBError(
                f"FINRA TRACE does not publish {', '.join(given)}. Remove "
                + ("it." if len(given) == 1 else "them.")
            )

        return FinraBondPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraBondPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the bond reference and last-sale records from FINRA TRACE.

        Raises
        ------
        OpenBBError
            If an unbounded query would read an entire mortgage universe.
        EmptyDataError
            If no bond matched the query.
        """
        import asyncio

        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_finra.utils.client import trace_session
        from openbb_finra.utils.constants import BOND_TYPES, UNFILTERED_BOND_TYPES
        from openbb_finra.utils.helpers import split_symbols
        from openbb_finra.utils.trace import resolve_bonds

        async with trace_session() as trace:
            if query.cusip:
                found = await resolve_bonds(trace, split_symbols(query.cusip))
                groups: dict[str, list[str]] = {}

                for record in found:
                    if query.bond_type in (None, record["bondType"]):
                        groups.setdefault(record["bondType"], []).append(
                            record["cusip"]
                        )
            else:
                bond_type = query.bond_type or "CA"
                filtered = any(
                    value is not None
                    for value in (
                        query.issuer_name,
                        query.coupon_min,
                        query.coupon_max,
                        query.maturity_date_min,
                        query.maturity_date_max,
                        query.ytm_min,
                        query.ytm_max,
                    )
                )

                if bond_type not in UNFILTERED_BOND_TYPES and not (
                    filtered or query.limit
                ):
                    raise OpenBBError(
                        f"The {BOND_TYPES[bond_type]['label']} universe holds millions"
                        + " of securities. Filter by issuer, coupon, maturity, or yield,"
                        + " or set a limit."
                    )

                groups = {bond_type: []}

            pages = await asyncio.gather(
                *(
                    read_bonds(trace, query, bond_type, cusips)
                    for bond_type, cusips in groups.items()
                )
            )

        values = distinct_bonds(pages)

        if not values:
            raise EmptyDataError("No TRACE-reported bond matched the query.")

        return values[: query.limit] if query.limit else values

    @staticmethod
    def transform_data(
        query: FinraBondPricesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraBondPricesData]:
        """Transform the data to the model."""
        return [FinraBondPricesData.model_validate(record) for record in data]
