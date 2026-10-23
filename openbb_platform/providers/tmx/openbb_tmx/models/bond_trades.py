"""TMX Bond Trades Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bond_trades import (
    BondTradesData,
    BondTradesQueryParams,
)
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import literal_choices


def _parse_file_date(value) -> str | None:
    """Return the CIRO submission date key as an ISO date."""
    text = str(value or "").strip()

    return f"{text[:4]}-{text[4:6]}-{text[6:8]}" if len(text) == 8 else None


def _as_float(value) -> float | None:
    """Return a float, treating the source placeholders as missing."""
    if value is None or str(value).strip() in ("", "N/A", "-"):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class TmxBondTradesQueryParams(BondTradesQueryParams):
    """TMX Bond Trades Query."""

    __json_schema_extra__ = {
        "issuer_type": {
            "x-widget_config": {
                "options": literal_choices(("government", "corporate", "municipal"))
            }
        },
        "account_type": {
            "x-widget_config": {
                "options": literal_choices(("all", "retail", "institutional"))
            }
        },
    }

    cusip: str | None = Field(
        default=None,
        description="CUSIP of the bond. One of cusip, isin, or figi is required.",
    )
    figi: str | None = Field(default=None, description="FIGI of the bond.")
    account_type: Literal["all", "retail", "institutional"] = Field(
        default="all",
        description="Restrict to trades booked to one account type.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk bond master. Set to False to bypass.",
    )

    @field_validator("cusip", "figi", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert the identifier to uppercase."""
        return v.upper() if v else None


class TmxBondTradesData(BondTradesData):
    """TMX Bond Trades Data."""

    trade_date: datetime | None = Field(
        default=None, description="Execution date and time of the trade."
    )
    settlement_date: dateType | None = Field(
        default=None, description="Settlement date of the trade."
    )
    issuer: str | None = Field(default=None, description="The issuer of the bond.")
    maturity_date: dateType | None = Field(
        default=None, description="Maturity date of the bond."
    )
    transaction_type: str | None = Field(
        default=None, description="The type of transaction reported."
    )
    account_type: str | None = Field(
        default=None, description="The account type the trade was booked to."
    )
    commission: bool | None = Field(
        default=None, description="Whether a commission was charged."
    )
    volume_capped: bool | None = Field(
        default=None,
        description="Whether the reported volume is capped at the disclosure limit.",
    )
    reported_date: dateType | None = Field(
        default=None,
        description="The date the trade was submitted to CIRO, which is later than"
        + " the execution date when a trade is reported late or amended.",
    )
    record_id: str | None = Field(
        default=None, description="CIRO's unique identifier for the trade record."
    )

    @field_validator("commission", mode="before", check_fields=False)
    @classmethod
    def parse_commission(cls, v):
        """Return the commission flag as a boolean."""
        return None if v is None else str(v).strip().lower() == "yes"


class TmxBondTradesFetcher(Fetcher[TmxBondTradesQueryParams, list[TmxBondTradesData]]):
    """TMX Bond Trades Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxBondTradesQueryParams:
        """Transform the query."""
        return TmxBondTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxBondTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the CIRO endpoint.

        Raises
        ------
        OpenBBError
            If no identifier is supplied or none matches a listed bond.
        """
        from datetime import date as date_type

        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.ciro import get_bond_trades
        from openbb_tmx.utils.helpers import get_all_bonds

        identifiers = {
            "cusip": query.cusip,
            "isin": query.isin,
            "figi": query.figi,
        }
        supplied = {k: v for k, v in identifiers.items() if v}

        if not supplied:
            raise OpenBBError(
                "One of cusip, isin, or figi is required to identify the bond."
            )

        bonds = await get_all_bonds(use_cache=query.use_cache)
        mask = None

        for column, value in supplied.items():
            match = bonds[column].astype(str).str.upper() == value
            mask = match if mask is None else (mask | match)

        matches = bonds[mask]

        if matches.empty:
            raise EmptyDataError(f"No CIRO-designated bond matches {supplied}.")

        bond = matches.iloc[0]
        start = query.start_date or bond.get("originalIssueDate") or "1990-01-01"
        end = query.end_date or date_type.today()

        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()

        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()

        trades = await get_bond_trades(
            str(bond["secKey"]), start, end, account_type=query.account_type
        )

        if not trades:
            raise EmptyDataError(f"No trades were reported for {supplied}.")

        return [
            {
                **trade,
                "issuer": bond.get("issuer"),
                "maturityDate": bond.get("maturityDate"),
                "couponRate": bond.get("couponRate"),
            }
            for trade in trades
        ]

    @staticmethod
    def transform_data(
        query: TmxBondTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxBondTradesData]:
        """Transform the data and validate the model."""
        from openbb_tmx.utils.ciro import ACCOUNT_TYPE_LABELS

        results: list[TmxBondTradesData] = []

        for trade in data:
            execution = f"{trade.get('execDate')} {trade.get('execTime')}".strip()
            yield_ = _as_float(trade.get("yield"))
            coupon = _as_float(trade.get("couponRate"))
            price = _as_float(trade.get("price"))
            results.append(
                TmxBondTradesData.model_validate(
                    {
                        "trade_date": execution or None,
                        "settlement_date": trade.get("settlementDate"),
                        "isin": trade.get("isin"),
                        "figi": trade.get("figi"),
                        "cusip": trade.get("cusip"),
                        "issuer": trade.get("issuer"),
                        "maturity_date": trade.get("maturityDate"),
                        "price": price,
                        "current_yield": yield_ / 100 if yield_ is not None else None,
                        "coupon_rate": coupon / 100 if coupon is not None else None,
                        "volume": trade.get("volume"),
                        "transaction_type": trade.get("txnType"),
                        "account_type": ACCOUNT_TYPE_LABELS.get(
                            trade.get("acctType"), trade.get("acctType")
                        ),
                        "commission": trade.get("commission"),
                        "volume_capped": trade.get("cap") == "+",
                        "reported_date": _parse_file_date(trade.get("fileSubDateKey")),
                        "record_id": trade.get("debtStatsKey"),
                    }
                )
            )

        return results
