"""FINRA Bond Historical Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator


class FinraBondHistoricalQueryParams(QueryParams):
    """FINRA Bond Historical Query."""

    __json_schema_extra__ = {"cusip": {"multiple_items_allowed": True}}

    cusip: str = Field(description="The CUSIP or FINRA symbol of the bond.")
    start_date: dateType | None = Field(
        default=None,
        description="The first trade date. Five years before the end date when empty.",
    )
    end_date: dateType | None = Field(
        default=None, description="The last trade date. Today when empty."
    )

    @field_validator("cusip", mode="before", check_fields=False)
    @classmethod
    def _upper(cls, value):
        """Upper-case the identifiers."""
        return value.upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def _dates(self):
        """Fill the date window and check its order.

        Raises
        ------
        ValueError
            If the start date is after the end date.
        """
        from datetime import date, timedelta

        from openbb_finra.utils.constants import HISTORY_DAYS

        self.end_date = self.end_date or date.today()
        self.start_date = self.start_date or self.end_date - timedelta(
            days=HISTORY_DAYS
        )

        if self.start_date > self.end_date:
            raise ValueError("The start date must not be after the end date.")

        return self


class FinraBondHistoricalData(Data):
    """FINRA Bond Historical Data."""

    __alias_dict__ = {
        "date": "tradeDate",
        "symbol": "issueSymbolIdentifier",
        "finra_security_id": "finraSecurityIdentifier",
        "price": "lastSalePrice",
        "yield_direction": "dailyLastSaleYieldDirection",
    }

    date: dateType = Field(description="The trade date.")
    cusip: str = Field(description="The CUSIP of the bond.")
    symbol: str | None = Field(
        default=None, description="The FINRA symbol of the bond."
    )
    finra_security_id: str | None = Field(
        default=None, description="The FINRA security identifier."
    )
    product_type: str | None = Field(
        default=None,
        description="The TRACE product - Corporate and Agency, Securitized Products,"
        + " or U.S. Treasury.",
    )
    price: float | None = Field(
        default=None, description="The price of the last sale of the day."
    )
    last_sale_yield: float | None = Field(
        default=None,
        description="The yield of the last sale of the day, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    yield_direction: str | None = Field(
        default=None, description="The direction of the day's yield change."
    )


class FinraBondHistoricalFetcher(
    Fetcher[FinraBondHistoricalQueryParams, list[FinraBondHistoricalData]]
):
    """Transform the query, extract and transform the data from FINRA TRACE."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraBondHistoricalQueryParams:
        """Transform the query."""
        return FinraBondHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraBondHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the end-of-day prices and yields from FINRA TRACE.

        Raises
        ------
        EmptyDataError
            If no bond resolved, or none traded within the window.
        """
        import asyncio

        from openbb_finra.utils.client import trace_session
        from openbb_finra.utils.constants import HISTORY_DATASETS
        from openbb_finra.utils.helpers import normalize_trace_record, split_symbols
        from openbb_finra.utils.trace import resolve_bonds

        async with trace_session() as trace:
            found = await resolve_bonds(trace, split_symbols(query.cusip))

            if not found:
                raise EmptyDataError(f"No TRACE-reported bond matched {query.cusip}.")

            groups: dict[str, list[str]] = {}

            for record in found:
                key = "TS" if record["bondType"] == "TS" else "OTHER"
                groups.setdefault(key, []).append(record["cusip"])

            pages = await asyncio.gather(
                *(
                    trace.query(
                        HISTORY_DATASETS[key]["dataset"],
                        {
                            "fields": HISTORY_DATASETS[key]["fields"],
                            "domainFilters": [{"fieldName": "cusip", "values": cusips}],
                            "dateRangeFilters": [
                                {
                                    "fieldName": "tradeDate",
                                    "startDate": str(query.start_date),
                                    "endDate": str(query.end_date),
                                }
                            ],
                            "sortFields": ["tradeDate"],
                        },
                    )
                    for key, cusips in groups.items()
                )
            )

        rows = [
            normalize_trace_record(
                {**row, **({"productType": "TS"} if key == "TS" else {})}
            )
            for key, page in zip(groups, pages)
            for row in page
        ]

        if not rows:
            raise EmptyDataError(
                f"No end-of-day price was reported for {query.cusip} between"
                f" {query.start_date} and {query.end_date}."
            )

        return rows

    @staticmethod
    def transform_data(
        query: FinraBondHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraBondHistoricalData]:
        """Transform the data to the model."""
        return [
            FinraBondHistoricalData.model_validate(row)
            for row in sorted(
                data, key=lambda row: (str(row.get("tradeDate")), str(row.get("cusip")))
            )
        ]
