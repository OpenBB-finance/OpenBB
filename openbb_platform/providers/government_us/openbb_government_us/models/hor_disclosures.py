from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field
import asyncio
from warnings import warn
class USHoRDisclosuresQueryParams(QueryParams):
    """US Senate Disclosures."""
    year: int = Field(description="Year of disclosures.")

class USHoRDisclosuresData(Data):
    """US Senate Disclosures Data."""
    __alias_dict__ = {
        "tx_date": "transaction_date",
        "tx_amount": "transaction_amount"
    }

class USHoRDisclosuresFetcher(
    Fetcher[
        USHoRDisclosuresQueryParams,
        List[USHoRDisclosuresData],
    ]
):
    """US Government Treasury Prices Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> USHoRDisclosuresQueryParams:
        """Transform query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import date, timedelta

        today = date.today()
        last_bd = (
            today - timedelta(today.weekday() - 4) if today.weekday() > 4 else today
        )
        if params.get("date") is None:
            params["date"] = last_bd
        return USHoRDisclosuresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: USHoRDisclosuresQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Extract the raw data from US Treasury website."""
        # pylint: disable=import-outside-toplevel
        from openbb_government_us.utils.hor_helpers import get_transactions

        year = query.year
        results = []

        async def get_one(num_records):
            """Get data for one symbol."""
            result = await get_transactions(year)
            if not result:
                warn(f"Symbol Error: No data found for Senate Disclosures")

            if result:

                results.extend(result)

        await asyncio.gather(*[get_one(year)])

        if not results:
            raise EmptyDataError("No data found for the given symbols.")
        return results


    @staticmethod
    def transform_data(
        query: USHoRDisclosuresQueryParams,
        data :List[Dict],
        **kwargs: Any,
    ) -> List[USHoRDisclosuresData]:
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
            USHoRDisclosuresData.model_validate(d)
            for d in data
        ]
