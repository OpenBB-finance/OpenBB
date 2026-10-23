"""TMX Insider Transactions Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import literal_choices

DURATIONS = {"3m": 3, "6m": 6, "12m": 12, "24m": 24, "36m": 36, "60m": 60, "120m": 120}


class TmxInsiderTransactionsQueryParams(QueryParams):
    """TMX Insider Transactions Query Params."""

    __json_schema_extra__ = {
        "period": {
            "x-widget_config": {
                "options": literal_choices(
                    ("3m", "6m", "12m", "24m", "36m", "60m", "120m"),
                    **{
                        "3m": "3 Months",
                        "6m": "6 Months",
                        "12m": "1 Year",
                        "24m": "2 Years",
                        "36m": "3 Years",
                        "60m": "5 Years",
                        "120m": "10 Years",
                    },
                )
            }
        }
    }

    symbol: str = Field(description="The company symbol.")
    period: Literal["3m", "6m", "12m", "24m", "36m", "60m", "120m"] = Field(
        default="12m",
        description="How far back to read filings.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Filings are cached for one day. To bypass, set to False.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert the symbol to uppercase."""
        return v.upper()


class TmxInsiderTransactionsData(Data):
    """TMX Insider Transactions Data."""

    __alias_dict__ = {
        "owner_name": "filer",
        "transaction_date": "date",
        "filing_date": "filingdate",
        "transaction_type": "type",
        "transaction_type_code": "transactionTypeCode",
        "securities_transacted": "amount",
        "securities_owned": "amountowned",
        "ownership_type": "amounttype",
        "price": "pricefrom",
        "currency": "pricefromcurrency",
        "market_value": "marketvalue",
        "security_type": "securitydesignation",
        "underlying_security_type": "underlyingsecuritydesignation",
        "underlying_shares": "equivalentunderlying",
        "insider_since": "insiderstartdate",
        "filing_id": "transactionid",
        "issuer_number": "issuernumber",
        "insider_number": "insiderNumber",
    }

    owner_name: str | None = Field(default=None, description="The name of the insider.")
    relationship: str | None = Field(
        default=None, description="The insider's relationship to the issuer."
    )
    transaction_date: dateType | None = Field(
        default=None, description="The date of the transaction."
    )
    filing_date: dateType | None = Field(
        default=None, description="The date the transaction was filed to SEDI."
    )
    transaction_type: str | None = Field(
        default=None, description="The nature of the transaction."
    )
    transaction_type_code: int | None = Field(
        default=None, description="The SEDI code for the nature of the transaction."
    )
    securities_transacted: float | None = Field(
        default=None, description="The number of securities transacted."
    )
    securities_owned: float | None = Field(
        default=None, description="The number of securities held after the transaction."
    )
    ownership_type: str | None = Field(
        default=None, description="Whether the holding is direct or indirect."
    )
    price: float | None = Field(
        default=None, description="The price the securities were transacted at."
    )
    currency: str | None = Field(default=None, description="The currency of the price.")
    market_value: float | None = Field(
        default=None, description="The value of the transaction."
    )
    security_type: str | None = Field(
        default=None, description="The designation of the security transacted."
    )
    underlying_security_type: str | None = Field(
        default=None, description="The designation of the underlying security."
    )
    underlying_shares: float | None = Field(
        default=None, description="The number of underlying shares represented."
    )
    insider_since: dateType | None = Field(
        default=None, description="The date the filer became an insider."
    )
    filing_id: int | None = Field(default=None, description="The SEDI transaction ID.")
    issuer_number: str | None = Field(
        default=None, description="The SEDI issuer number."
    )
    insider_number: str | None = Field(
        default=None, description="The SEDI insider number."
    )


class TmxInsiderTransactionsFetcher(
    Fetcher[TmxInsiderTransactionsQueryParams, list[TmxInsiderTransactionsData]]
):
    """TMX Insider Transactions Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxInsiderTransactionsQueryParams:
        """Transform the query."""
        return TmxInsiderTransactionsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxInsiderTransactionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Read the filings published for the symbol."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        response = await amake_gql_request(
            "getInsiderTransactions",
            gql.INSIDER_TRANSACTIONS,
            {"symbol": query.symbol, "monthDuration": DURATIONS[query.period]},
            symbol=query.symbol,
            use_cache=query.use_cache,
        )
        filings = (response or {}).get("getInsiderTransactions")

        return filings if isinstance(filings, list) else []

    @staticmethod
    def transform_data(
        query: TmxInsiderTransactionsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TmxInsiderTransactionsData]:
        """Return the filings newest first.

        Raises
        ------
        EmptyDataError
            If no filings were published over the window.
        """
        if not data:
            raise EmptyDataError(f"No insider filings found for {query.symbol}")

        published = set(TmxInsiderTransactionsData.__alias_dict__.values()) | {
            "relationship"
        }

        return [
            TmxInsiderTransactionsData.model_validate(
                {k: v for k, v in row.items() if k in published}
            )
            for row in sorted(data, key=lambda row: str(row.get("date")), reverse=True)
        ]
