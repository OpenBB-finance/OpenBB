"""TMX Company Filings Model"""

# pylint: disable=unused-argument
import asyncio
import json
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional

from dateutil import rrule
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field


class TmxCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """TMX Company Filings Query Parameters."""

    start_date: Optional[dateType] = Field(
        description="The start date to fetch.",
        default=None,
    )
    end_date: Optional[dateType] = Field(
        description="The end date to fetch.",
        default=None,
    )


class TmxCompanyFilingsData(CompanyFilingsData):
    """TMX Sedar Filings Data."""

    __alias_dict__ = {
        "filing_date": "filingDate",
        "report_type": "name",
        "report_url": "urlToPdf",
    }

    description: str = Field(description="The description of the filing.")
    size: str = Field(description="The file size of the PDF document.")


class TmxCompanyFilingsFetcher(
    Fetcher[TmxCompanyFilingsQueryParams, List[TmxCompanyFilingsData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxCompanyFilingsQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                datetime.now() - timedelta(weeks=16)
            ).strftime("%Y-%m-%d")
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = datetime.now().date().strftime("%Y-%m-%d")
        transformed_params["symbol"] = (
            params.get("symbol", "")
            .upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        return TmxCompanyFilingsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TmxCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        user_agent = get_random_agent()
        results: List[Dict] = []

        # Generate a list of dates from start_date to end_date with a frequency of 1 week
        dates = list(
            rrule.rrule(
                rrule.WEEKLY, interval=1, dtstart=query.start_date, until=query.end_date
            )
        )

        # Add end_date to the list if it's not there already
        if dates[-1] != query.end_date:
            dates.append(query.end_date)  # type: ignore

        # Create a list of 4-week chunks
        chunks = [
            (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
        ]

        # Adjust the end date of the last chunk to be the final end date
        chunks[-1] = (chunks[-1][0], query.end_date)  # type: ignore

        async def create_task(start, end, results):
            """Create tasks from the chunked start/end dates."""
            data = []
            payload = gql.get_company_filings_payload
            payload["variables"]["symbol"] = query.symbol
            payload["variables"]["fromDate"] = start.strftime("%Y-%m-%d")
            payload["variables"]["toDate"] = end.strftime("%Y-%m-%d")
            payload["variables"]["limit"] = 1000
            url = "https://app-money.tmx.com/graphql"

            async def try_again():
                return await get_data_from_gql(
                    method="POST",
                    url=url,
                    data=json.dumps(payload),
                    headers={
                        "authority": "app-money.tmx.com",
                        "referer": f"https://money.tmx.com/en/quote/{query.symbol}",
                        "locale": "en",
                        "Content-Type": "application/json",
                        "User-Agent": user_agent,
                        "Accept": "*/*",
                    },
                    timeout=10,
                )

            try:
                data = await get_data_from_gql(
                    method="POST",
                    url=url,
                    data=json.dumps(payload),
                    headers={
                        "authority": "app-money.tmx.com",
                        "referer": f"https://money.tmx.com/en/quote/{query.symbol}",
                        "locale": "en",
                        "Content-Type": "application/json",
                        "User-Agent": user_agent,
                        "Accept": "*/*",
                    },
                    timeout=10,
                )
            except Exception:
                data = await try_again()

            if isinstance(data, str):
                data = await try_again()

            if data != [] and data["data"].get("filings") is not None:
                results.extend(data["data"]["filings"])

            return results

        tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

        await asyncio.gather(*tasks)

        return sorted(results, key=lambda x: x["filingDate"], reverse=True)

    @staticmethod
    def transform_data(
        query: TmxCompanyFilingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxCompanyFilingsData]:
        """Return the transformed data."""
        return [TmxCompanyFilingsData.model_validate(d) for d in data]
