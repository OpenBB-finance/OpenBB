from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field
import asyncio
from warnings import warn
class USSenateDisclosuresQueryParams(QueryParams):
    """US Senate Disclosures."""
    num_reports: Optional[int] = Field(description="Number of disclosures to fetch.", default=30)

class USSenateDisclosuresData(Data):
    """US Senate Disclosures Data."""
    __alias_dict__ = {
        "tx_date": "transaction_date",
        "tx_amount": "transaction_amount"
    }

class USSenateDisclosuresFetcher(
    Fetcher[
        USSenateDisclosuresQueryParams,
        List[USSenateDisclosuresData],
    ]
):
    """US Government Treasury Prices Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> USSenateDisclosuresQueryParams:
        """Transform query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import date, timedelta

        today = date.today()
        last_bd = (
            today - timedelta(today.weekday() - 4) if today.weekday() > 4 else today
        )
        if params.get("date") is None:
            params["date"] = last_bd
        return USSenateDisclosuresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: USSenateDisclosuresQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Extract the raw data from US Treasury website."""
        # pylint: disable=import-outside-toplevel
        from openbb_government_us.utils.senate_helpers import get_transactions

        num_reports = query.num_reports
        results = []

        async def get_one(num_records):
            """Get data for one symbol."""
            result = await get_transactions(num_reports)
            if not result:
                warn(f"Symbol Error: No data found for Senate Disclosures")

            if result:
                for r in result:
                    results.append(r)

        await asyncio.gather(get_one(num_reports))

        if not results:
            raise EmptyDataError("No data found for the given symbols.")


    @staticmethod
    def transform_data(
        query: USSenateDisclosuresQueryParams,
        data :List[Dict],
        **kwargs: Any,
    ) -> List[USSenateDisclosuresData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from pandas import Index, read_csv, to_datetime  # noqa

        try:
            if not data:
                raise EmptyDataError("Data not found")
        except Exception as e:
            raise OpenBBError(e) from e

        return [
            USSenateDisclosuresData.model_validate(d)
            for d in data
        ]
